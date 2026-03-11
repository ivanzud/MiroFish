"""
图谱构建服务
接口2：使用Zep API构建Standalone Graph
"""

import os
import uuid
import time
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

from zep_cloud.client import Zep
from zep_cloud import EpisodeData, EntityEdgeSourceTarget

from ..config import Config
from ..i18n import get_locale, tr
from ..models.task import TaskManager, TaskStatus
from ..utils.logger import get_logger
from ..utils.zep_paging import fetch_all_nodes, fetch_all_edges
from .text_processor import TextProcessor


@dataclass
class GraphInfo:
    """图谱信息"""
    graph_id: str
    node_count: int
    edge_count: int
    entity_types: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "entity_types": self.entity_types,
        }


class GraphBuilderService:
    """
    图谱构建服务
    负责调用Zep API构建知识图谱
    """
    
    def __init__(self, api_key: Optional[str] = None, locale: Optional[str] = None):
        self.api_key = api_key or Config.ZEP_API_KEY
        self.locale = locale or get_locale()
        if not self.api_key:
            raise ValueError(tr("config.key_missing", self.locale, name="ZEP_API_KEY"))
        
        self.client = Zep(api_key=self.api_key)
        self.task_manager = TaskManager()
        self.logger = get_logger('mirofish.graph_builder')

    @staticmethod
    def _is_retryable_zep_error(error: Exception) -> bool:
        """Return whether a Zep operation failure looks transient and safe to retry."""
        status_code = getattr(error, "status_code", None)
        if status_code in {408, 409, 423, 425, 429, 500, 502, 503, 504}:
            return True

        error_text = str(error).lower()
        retry_signals = (
            "429",
            "too many requests",
            "rate limit",
            "timeout",
            "timed out",
            "temporarily unavailable",
            "service unavailable",
            "bad gateway",
            "gateway timeout",
            "connection reset",
            "connection aborted",
            "connection error",
            "remote disconnected",
        )
        return any(signal in error_text for signal in retry_signals)

    def _retry_zep_operation(
        self,
        operation_name: str,
        func: Callable[[], Any],
        *,
        max_retries: Optional[int] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None,
        progress_message: Optional[Callable[[int, int, float], str]] = None,
        progress_value: float = 0,
    ) -> Any:
        """Retry transient Zep failures with backoff while surfacing progress updates."""
        max_attempts = max_retries or Config.ZEP_RETRY_MAX_ATTEMPTS
        base_delay = Config.ZEP_RETRY_BASE_DELAY_SECONDS

        for attempt in range(max_attempts):
            try:
                return func()
            except Exception as error:
                should_retry = attempt < max_attempts - 1 and self._is_retryable_zep_error(error)
                if not should_retry:
                    raise

                wait_time = base_delay * (2 ** attempt)
                self.logger.warning(
                    "%s failed on attempt %s/%s, retrying in %.1fs: %s",
                    operation_name,
                    attempt + 1,
                    max_attempts,
                    wait_time,
                    error,
                )
                if progress_callback and progress_message:
                    progress_callback(progress_message(attempt + 1, max_attempts, wait_time), progress_value)
                time.sleep(wait_time)

    def format_user_facing_error(self, error: Exception) -> str:
        """Collapse noisy provider exceptions into actionable graph-build messages."""
        status_code = getattr(error, "status_code", None)
        error_text = self._normalize_error_text(error)
        lowered = error_text.lower()

        if status_code == 401 or ("401" in lowered and "unauthorized" in lowered):
            return tr("graph.zep_auth_failed", self.locale)

        if status_code == 403 or "forbidden" in lowered:
            return tr("graph.zep_permission_denied", self.locale)

        if "invalid api key" in lowered or "authentication" in lowered:
            return tr("graph.zep_auth_failed", self.locale)

        return error_text or error.__class__.__name__

    @staticmethod
    def _normalize_error_text(error: Exception) -> str:
        """Strip traceback noise from SDK/provider exceptions before surfacing them."""
        error_text = str(error).strip()
        if "Traceback (most recent call last):" not in error_text:
            return error_text

        cleaned_lines: List[str] = []
        for raw_line in error_text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if (
                line.startswith("Traceback (most recent call last):")
                or line.startswith('File "')
                or line.startswith("^")
                or line.startswith("During handling of the above exception")
            ):
                continue
            cleaned_lines.append(line)

        # Prefer the last meaningful line once stack frames are removed.
        if cleaned_lines:
            return cleaned_lines[-1]

        return error_text
    
    def build_graph_async(
        self,
        text: str,
        ontology: Dict[str, Any],
        graph_name: str = "MiroFish Graph",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        batch_size: int = 3
    ) -> str:
        """
        异步构建图谱
        
        Args:
            text: 输入文本
            ontology: 本体定义（来自接口1的输出）
            graph_name: 图谱名称
            chunk_size: 文本块大小
            chunk_overlap: 块重叠大小
            batch_size: 每批发送的块数量
            
        Returns:
            任务ID
        """
        # 创建任务
        task_id = self.task_manager.create_task(
            task_type="graph_build",
            metadata={
                "graph_name": graph_name,
                "chunk_size": chunk_size,
                "text_length": len(text),
            }
        )
        
        # 在后台线程中执行构建
        thread = threading.Thread(
            target=self._build_graph_worker,
            args=(task_id, text, ontology, graph_name, chunk_size, chunk_overlap, batch_size)
        )
        thread.daemon = True
        thread.start()
        
        return task_id
    
    def _build_graph_worker(
        self,
        task_id: str,
        text: str,
        ontology: Dict[str, Any],
        graph_name: str,
        chunk_size: int,
        chunk_overlap: int,
        batch_size: int
    ):
        """图谱构建工作线程"""
        try:
            self.task_manager.update_task(
                task_id,
                status=TaskStatus.PROCESSING,
                progress=5,
                message="开始构建图谱..."
            )
            
            # 1. 创建图谱
            graph_id = self.create_graph(graph_name)
            self.task_manager.update_task(
                task_id,
                progress=10,
                message=f"图谱已创建: {graph_id}"
            )
            
            # 2. 设置本体
            self.set_ontology(graph_id, ontology)
            self.task_manager.update_task(
                task_id,
                progress=15,
                message="本体已设置"
            )
            
            # 3. 文本分块
            chunks = TextProcessor.split_text(text, chunk_size, chunk_overlap)
            total_chunks = len(chunks)
            self.task_manager.update_task(
                task_id,
                progress=20,
                message=f"文本已分割为 {total_chunks} 个块"
            )
            
            # 4. 分批发送数据
            episode_uuids = self.add_text_batches(
                graph_id, chunks, batch_size,
                lambda msg, prog: self.task_manager.update_task(
                    task_id,
                    progress=20 + int(prog * 0.4),  # 20-60%
                    message=msg
                )
            )
            
            # 5. 等待Zep处理完成
            self.task_manager.update_task(
                task_id,
                progress=60,
                message="等待Zep处理数据..."
            )
            
            self._wait_for_episodes(
                episode_uuids,
                lambda msg, prog: self.task_manager.update_task(
                    task_id,
                    progress=60 + int(prog * 0.3),  # 60-90%
                    message=msg
                )
            )
            
            # 6. 获取图谱信息
            self.task_manager.update_task(
                task_id,
                progress=90,
                message="获取图谱信息..."
            )
            
            graph_info = self._get_graph_info(graph_id)
            
            # 完成
            self.task_manager.complete_task(task_id, {
                "graph_id": graph_id,
                "graph_info": graph_info.to_dict(),
                "chunks_processed": total_chunks,
            }, locale=self.locale)
            
        except Exception as e:
            import traceback
            self.logger.error("Graph build worker failed: %s", e)
            self.logger.debug(traceback.format_exc())
            self.task_manager.fail_task(task_id, self.format_user_facing_error(e), locale=self.locale)
    
    def create_graph(self, name: str, max_retries: Optional[int] = None) -> str:
        """创建Zep图谱（公开方法）"""
        graph_id = f"mirofish_{uuid.uuid4().hex[:16]}"

        self._retry_zep_operation(
            "create_graph",
            lambda: self.client.graph.create(
                graph_id=graph_id,
                name=name,
                description="MiroFish Social Simulation Graph"
            ),
            max_retries=max_retries,
        )
        
        return graph_id
    
    def set_ontology(self, graph_id: str, ontology: Dict[str, Any], max_retries: Optional[int] = None):
        """设置图谱本体（公开方法）"""
        import warnings
        from typing import Optional
        from pydantic import Field
        from zep_cloud.external_clients.ontology import EntityModel, EntityText, EdgeModel
        
        # 抑制 Pydantic v2 关于 Field(default=None) 的警告
        # 这是 Zep SDK 要求的用法，警告来自动态类创建，可以安全忽略
        warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')
        
        # Zep 保留名称，不能作为属性名
        RESERVED_NAMES = {'uuid', 'name', 'group_id', 'name_embedding', 'summary', 'created_at'}
        
        def safe_attr_name(attr_name: str) -> str:
            """将保留名称转换为安全名称"""
            if attr_name.lower() in RESERVED_NAMES:
                return f"entity_{attr_name}"
            return attr_name

        def normalized_attributes(owner_name: str, attributes: Any) -> List[Dict[str, str]]:
            """Accept string-style attributes from loose LLM output and skip unusable entries."""
            normalized: List[Dict[str, str]] = []
            for attr_def in attributes or []:
                if isinstance(attr_def, str):
                    attr_name = attr_def.strip()
                    if attr_name:
                        normalized.append({"name": attr_name, "description": attr_name})
                    continue
                if not isinstance(attr_def, dict):
                    self.logger.warning("Skipping invalid ontology attribute for %s: %r", owner_name, attr_def)
                    continue

                attr_name = str(attr_def.get("name", "")).strip()
                if not attr_name:
                    self.logger.warning("Skipping ontology attribute without name for %s: %r", owner_name, attr_def)
                    continue

                description = str(attr_def.get("description") or attr_name).strip() or attr_name
                normalized.append({"name": attr_name, "description": description})
            return normalized
        
        # 动态创建实体类型
        entity_types = {}
        for entity_def in ontology.get("entity_types", []):
            name = entity_def["name"]
            description = entity_def.get("description", f"A {name} entity.")
            
            # 创建属性字典和类型注解（Pydantic v2 需要）
            attrs = {"__doc__": description}
            annotations = {}
            
            for attr_def in normalized_attributes(name, entity_def.get("attributes", [])):
                attr_name = safe_attr_name(attr_def["name"])  # 使用安全名称
                attr_desc = attr_def.get("description", attr_name)
                # Zep API 需要 Field 的 description，这是必需的
                attrs[attr_name] = Field(description=attr_desc, default=None)
                annotations[attr_name] = Optional[EntityText]  # 类型注解
            
            attrs["__annotations__"] = annotations
            
            # 动态创建类
            entity_class = type(name, (EntityModel,), attrs)
            entity_class.__doc__ = description
            entity_types[name] = entity_class
        
        # 动态创建边类型
        edge_definitions = {}
        for edge_def in ontology.get("edge_types", []):
            name = edge_def["name"]
            description = edge_def.get("description", f"A {name} relationship.")
            
            # 创建属性字典和类型注解
            attrs = {"__doc__": description}
            annotations = {}
            
            for attr_def in normalized_attributes(name, edge_def.get("attributes", [])):
                attr_name = safe_attr_name(attr_def["name"])  # 使用安全名称
                attr_desc = attr_def.get("description", attr_name)
                # Zep API 需要 Field 的 description，这是必需的
                attrs[attr_name] = Field(description=attr_desc, default=None)
                annotations[attr_name] = Optional[str]  # 边属性用str类型
            
            attrs["__annotations__"] = annotations
            
            # 动态创建类
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            edge_class = type(class_name, (EdgeModel,), attrs)
            edge_class.__doc__ = description
            
            # 构建source_targets
            source_targets = []
            for st in edge_def.get("source_targets", []):
                source_targets.append(
                    EntityEdgeSourceTarget(
                        source=st.get("source", "Entity"),
                        target=st.get("target", "Entity")
                    )
                )
            
            if source_targets:
                edge_definitions[name] = (edge_class, source_targets)
        
        # 调用Zep API设置本体
        if entity_types or edge_definitions:
            self._retry_zep_operation(
                "set_ontology",
                lambda: self.client.graph.set_ontology(
                    graph_ids=[graph_id],
                    entities=entity_types if entity_types else None,
                    edges=edge_definitions if edge_definitions else None,
                ),
                max_retries=max_retries,
            )
    
    def add_text_batches(
        self,
        graph_id: str,
        chunks: List[str],
        batch_size: int = 3,
        progress_callback: Optional[Callable] = None
    ) -> List[str]:
        """分批添加文本到图谱，返回所有 episode 的 uuid 列表"""
        episode_uuids = []
        total_chunks = len(chunks)
        
        for i in range(0, total_chunks, batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_chunks + batch_size - 1) // batch_size
            
            if progress_callback:
                progress = (i + len(batch_chunks)) / total_chunks
                progress_callback(
                    f"发送第 {batch_num}/{total_batches} 批数据 ({len(batch_chunks)} 块)...",
                    progress
                )
            
            # 构建episode数据
            episodes = [
                EpisodeData(data=chunk, type="text")
                for chunk in batch_chunks
            ]
            
            def send_batch():
                return self.client.graph.add_batch(
                    graph_id=graph_id,
                    episodes=episodes
                )

            batch_result = self._retry_zep_operation(
                f"add_batch[{batch_num}]",
                send_batch,
                progress_callback=progress_callback,
                progress_message=lambda attempt, total, wait_time: (
                    f"批次 {batch_num} 发送失败，{wait_time:.0f}秒后重试 ({attempt}/{total})..."
                ),
                progress_value=(i + len(batch_chunks)) / total_chunks,
            )

            # 收集返回的 episode uuid
            if batch_result and isinstance(batch_result, list):
                for ep in batch_result:
                    ep_uuid = getattr(ep, 'uuid_', None) or getattr(ep, 'uuid', None)
                    if ep_uuid:
                        episode_uuids.append(ep_uuid)

            # 避免请求过快
            time.sleep(1)
        
        return episode_uuids
    
    def _wait_for_episodes(
        self,
        episode_uuids: List[str],
        progress_callback: Optional[Callable] = None,
        timeout: int = 600
    ):
        """等待所有 episode 处理完成（通过查询每个 episode 的 processed 状态）"""
        if not episode_uuids:
            if progress_callback:
                progress_callback("无需等待（没有 episode）", 1.0)
            return
        
        start_time = time.time()
        pending_episodes = set(episode_uuids)
        completed_count = 0
        total_episodes = len(episode_uuids)
        
        if progress_callback:
            progress_callback(f"开始等待 {total_episodes} 个文本块处理...", 0)
        
        while pending_episodes:
            if time.time() - start_time > timeout:
                if progress_callback:
                    progress_callback(
                        f"部分文本块超时，已完成 {completed_count}/{total_episodes}",
                        completed_count / total_episodes
                    )
                break
            
            # 检查每个 episode 的处理状态
            for ep_uuid in list(pending_episodes):
                try:
                    episode = self.client.graph.episode.get(uuid_=ep_uuid)
                    is_processed = getattr(episode, 'processed', False)
                    
                    if is_processed:
                        pending_episodes.remove(ep_uuid)
                        completed_count += 1
                        
                except Exception as e:
                    # 忽略单个查询错误，继续
                    pass
            
            elapsed = int(time.time() - start_time)
            if progress_callback:
                progress_callback(
                    f"Zep处理中... {completed_count}/{total_episodes} 完成, {len(pending_episodes)} 待处理 ({elapsed}秒)",
                    completed_count / total_episodes if total_episodes > 0 else 0
                )
            
            if pending_episodes:
                time.sleep(3)  # 每3秒检查一次
        
        if progress_callback:
            progress_callback(f"处理完成: {completed_count}/{total_episodes}", 1.0)
    
    def _get_graph_info(self, graph_id: str) -> GraphInfo:
        """获取图谱信息"""
        # 获取节点（分页）
        nodes = fetch_all_nodes(self.client, graph_id)

        # 获取边（分页）
        edges = fetch_all_edges(self.client, graph_id)

        # 统计实体类型
        entity_types = set()
        for node in nodes:
            if node.labels:
                for label in node.labels:
                    if label not in ["Entity", "Node"]:
                        entity_types.add(label)

        return GraphInfo(
            graph_id=graph_id,
            node_count=len(nodes),
            edge_count=len(edges),
            entity_types=list(entity_types)
        )
    
    def get_graph_data(self, graph_id: str) -> Dict[str, Any]:
        """
        获取完整图谱数据（包含详细信息）
        
        Args:
            graph_id: 图谱ID
            
        Returns:
            包含nodes和edges的字典，包括时间信息、属性等详细数据
        """
        nodes = fetch_all_nodes(self.client, graph_id)
        edges = fetch_all_edges(self.client, graph_id)

        # 创建节点映射用于获取节点名称
        node_map = {}
        for node in nodes:
            node_map[node.uuid_] = node.name or ""
        
        nodes_data = []
        for node in nodes:
            # 获取创建时间
            created_at = getattr(node, 'created_at', None)
            if created_at:
                created_at = str(created_at)
            
            nodes_data.append({
                "uuid": node.uuid_,
                "name": node.name,
                "labels": node.labels or [],
                "summary": node.summary or "",
                "attributes": node.attributes or {},
                "created_at": created_at,
            })
        
        edges_data = []
        for edge in edges:
            # 获取时间信息
            created_at = getattr(edge, 'created_at', None)
            valid_at = getattr(edge, 'valid_at', None)
            invalid_at = getattr(edge, 'invalid_at', None)
            expired_at = getattr(edge, 'expired_at', None)
            
            # 获取 episodes
            episodes = getattr(edge, 'episodes', None) or getattr(edge, 'episode_ids', None)
            if episodes and not isinstance(episodes, list):
                episodes = [str(episodes)]
            elif episodes:
                episodes = [str(e) for e in episodes]
            
            # 获取 fact_type
            fact_type = getattr(edge, 'fact_type', None) or edge.name or ""
            
            edges_data.append({
                "uuid": edge.uuid_,
                "name": edge.name or "",
                "fact": edge.fact or "",
                "fact_type": fact_type,
                "source_node_uuid": edge.source_node_uuid,
                "target_node_uuid": edge.target_node_uuid,
                "source_node_name": node_map.get(edge.source_node_uuid, ""),
                "target_node_name": node_map.get(edge.target_node_uuid, ""),
                "attributes": edge.attributes or {},
                "created_at": str(created_at) if created_at else None,
                "valid_at": str(valid_at) if valid_at else None,
                "invalid_at": str(invalid_at) if invalid_at else None,
                "expired_at": str(expired_at) if expired_at else None,
                "episodes": episodes or [],
            })
        
        return {
            "graph_id": graph_id,
            "nodes": nodes_data,
            "edges": edges_data,
            "node_count": len(nodes_data),
            "edge_count": len(edges_data),
        }
    
    def delete_graph(self, graph_id: str):
        """删除图谱"""
        self.client.graph.delete(graph_id=graph_id)
