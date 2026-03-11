"""
配置管理
统一从项目根目录的 .env 文件加载配置
"""

import os
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
# 路径: MiroFish/.env (相对于 backend/app/config.py)
project_root_env = os.path.join(os.path.dirname(__file__), '../../.env')

if os.path.exists(project_root_env):
    load_dotenv(project_root_env, override=True)
else:
    # 如果根目录没有 .env，尝试加载环境变量（用于生产环境）
    load_dotenv(override=True)


def _env(*names, default=None):
    """Return the first configured environment variable from the provided aliases."""
    for name in names:
        value = os.environ.get(name)
        if value not in (None, ''):
            return value
    return default


def _int_env(name, default):
    """Parse integer environment variables without crashing module import."""
    raw_value = os.environ.get(name)
    if raw_value in (None, ''):
        return default
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return default


def _float_env(name, default):
    """Parse float environment variables without crashing module import."""
    raw_value = os.environ.get(name)
    if raw_value in (None, ''):
        return default
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return default


@dataclass
class ConfigValidationResult:
    """Structured config validation output."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        self.info.append(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
        }


class Config:
    """Flask配置类"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mirofish-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # JSON配置 - 禁用ASCII转义，让中文直接显示（而不是 \uXXXX 格式）
    JSON_AS_ASCII = False
    
    # LLM配置（统一使用OpenAI格式）
    LLM_API_KEY = _env('LLM_API_KEY', 'OPENAI_API_KEY')
    LLM_BASE_URL = _env(
        'LLM_BASE_URL',
        'OPENAI_BASE_URL',
        'OPENAI_API_BASE_URL',
        default='https://api.openai.com/v1',
    )
    LLM_MODEL_NAME = _env('LLM_MODEL_NAME', 'OPENAI_MODEL', default='gpt-4o-mini')
    LLM_MAX_TOKENS = _int_env('LLM_MAX_TOKENS', 4096)
    
    # Zep配置
    ZEP_API_KEY = os.environ.get('ZEP_API_KEY')
    ZEP_RETRY_MAX_ATTEMPTS = _int_env('ZEP_RETRY_MAX_ATTEMPTS', 3)
    ZEP_RETRY_BASE_DELAY_SECONDS = _float_env('ZEP_RETRY_BASE_DELAY_SECONDS', 2.0)
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}
    
    # 文本处理配置
    DEFAULT_CHUNK_SIZE = 500  # 默认切块大小
    DEFAULT_CHUNK_OVERLAP = 50  # 默认重叠大小
    
    # OASIS模拟配置
    OASIS_DEFAULT_MAX_ROUNDS = _int_env('OASIS_DEFAULT_MAX_ROUNDS', 10)
    OASIS_SIMULATION_DATA_DIR = os.path.join(os.path.dirname(__file__), '../uploads/simulations')
    
    # OASIS平台可用动作配置
    OASIS_TWITTER_ACTIONS = [
        'CREATE_POST', 'LIKE_POST', 'REPOST', 'FOLLOW', 'DO_NOTHING', 'QUOTE_POST'
    ]
    OASIS_REDDIT_ACTIONS = [
        'LIKE_POST', 'DISLIKE_POST', 'CREATE_POST', 'CREATE_COMMENT',
        'LIKE_COMMENT', 'DISLIKE_COMMENT', 'SEARCH_POSTS', 'SEARCH_USER',
        'TREND', 'REFRESH', 'DO_NOTHING', 'FOLLOW', 'MUTE'
    ]
    
    # Report Agent配置
    REPORT_AGENT_MAX_TOOL_CALLS = _int_env('REPORT_AGENT_MAX_TOOL_CALLS', 5)
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = _int_env('REPORT_AGENT_MAX_REFLECTION_ROUNDS', 2)
    REPORT_AGENT_TEMPERATURE = _float_env('REPORT_AGENT_TEMPERATURE', 0.5)

    @classmethod
    def validate(cls):
        """验证必要配置"""
        return cls.validate_comprehensive().errors

    @classmethod
    def validate_comprehensive(cls):
        """Validate configuration without changing startup behavior."""
        result = ConfigValidationResult()

        if not cls.LLM_API_KEY:
            result.add_error("LLM_API_KEY / OPENAI_API_KEY 未配置")
        if not cls.ZEP_API_KEY:
            result.add_error("ZEP_API_KEY 未配置")

        cls._validate_url(
            result,
            "LLM_BASE_URL / OPENAI_BASE_URL / OPENAI_API_BASE_URL",
            cls.LLM_BASE_URL,
        )
        cls._validate_numeric_env(result, "LLM_MAX_TOKENS", minimum=1)
        cls._validate_numeric_env(result, "OASIS_DEFAULT_MAX_ROUNDS", minimum=1)
        cls._validate_numeric_env(result, "REPORT_AGENT_MAX_TOOL_CALLS", minimum=1)
        cls._validate_numeric_env(result, "REPORT_AGENT_MAX_REFLECTION_ROUNDS", minimum=0)
        cls._validate_numeric_env(
            result,
            "REPORT_AGENT_TEMPERATURE",
            minimum=0,
            maximum=2,
            parser=float,
        )
        cls._validate_numeric_env(result, "ZEP_RETRY_MAX_ATTEMPTS", minimum=1)
        cls._validate_numeric_env(
            result,
            "ZEP_RETRY_BASE_DELAY_SECONDS",
            minimum=0,
            parser=float,
        )

        if cls.DEBUG:
            result.add_warning("FLASK_DEBUG=True; 不建议在生产环境启用 DEBUG")
        if cls.SECRET_KEY == 'mirofish-secret-key':
            result.add_warning("SECRET_KEY 使用默认值；生产环境应覆盖")
        if not os.path.isdir(cls.UPLOAD_FOLDER):
            result.add_info(f"UPLOAD_FOLDER 尚不存在，将在运行时按需创建: {cls.UPLOAD_FOLDER}")
        if cls.LLM_MODEL_NAME:
            result.add_info(f"LLM_MODEL_NAME={cls.LLM_MODEL_NAME}")

        return result

    @classmethod
    def get_config_summary(cls):
        """Return a non-sensitive config snapshot for diagnostics."""
        return {
            'llm': {
                'base_url': cls.LLM_BASE_URL,
                'model': cls.LLM_MODEL_NAME,
                'max_tokens': cls.LLM_MAX_TOKENS,
                'configured': bool(cls.LLM_API_KEY),
            },
            'zep': {
                'configured': bool(cls.ZEP_API_KEY),
                'retry_max_attempts': cls.ZEP_RETRY_MAX_ATTEMPTS,
                'retry_base_delay_seconds': cls.ZEP_RETRY_BASE_DELAY_SECONDS,
            },
            'simulation': {
                'default_max_rounds': cls.OASIS_DEFAULT_MAX_ROUNDS,
                'data_dir': cls.OASIS_SIMULATION_DATA_DIR,
            },
            'report_agent': {
                'max_tool_calls': cls.REPORT_AGENT_MAX_TOOL_CALLS,
                'max_reflection_rounds': cls.REPORT_AGENT_MAX_REFLECTION_ROUNDS,
                'temperature': cls.REPORT_AGENT_TEMPERATURE,
            },
            'debug': cls.DEBUG,
        }

    @classmethod
    def _validate_url(cls, result, name, value):
        if not value:
            result.add_error(f"{name} 未配置")
            return
        parsed = urlparse(value)
        if parsed.scheme not in {'http', 'https'}:
            result.add_error(f"{name} 必须使用 http/https: {value}")
            return
        if not parsed.netloc:
            result.add_error(f"{name} 缺少主机名: {value}")

    @classmethod
    def _validate_numeric_env(cls, result, name, minimum=None, maximum=None, parser=int):
        raw_value = os.environ.get(name)
        if raw_value in (None, ''):
            return
        try:
            value = parser(raw_value)
        except (TypeError, ValueError):
            result.add_error(f"{name} 必须是合法数字，当前值: {raw_value}")
            return
        if minimum is not None and value < minimum:
            result.add_error(f"{name} 必须 >= {minimum}，当前值: {raw_value}")
        if maximum is not None and value > maximum:
            result.add_error(f"{name} 必须 <= {maximum}，当前值: {raw_value}")


def validate_on_startup():
    """Compatibility helper for explicit startup validation hooks."""
    return Config.validate_comprehensive().is_valid
