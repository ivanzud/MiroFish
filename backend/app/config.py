"""
配置管理
统一从项目根目录的 .env 文件加载配置
"""

import os
import secrets
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - allows config preflight in minimal shells
    def load_dotenv(*_args, **_kwargs):
        return False

try:
    from .i18n import tr
except ImportError:  # pragma: no cover - compatibility for direct module loading in tests
    from app.i18n import tr

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


def _configured_env_name(*names):
    """Return the first configured environment variable name from the provided aliases."""
    for name in names:
        value = os.environ.get(name)
        if value not in (None, ''):
            return name
    return None


def _configured_env_entries(*names):
    """Return configured environment variable name/value pairs in priority order."""
    entries = []
    for name in names:
        value = os.environ.get(name)
        if value not in (None, ''):
            entries.append((name, value))
    return entries


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


def _csv_env(name, default=None):
    """Parse comma-separated environment variables into a normalized list."""
    raw_value = os.environ.get(name)
    if raw_value in (None, ''):
        return list(default or [])
    return [item.strip() for item in raw_value.split(',') if item.strip()]


def _bool_env(name, default=False):
    """Parse boolean environment variables using common truthy spellings."""
    raw_value = os.environ.get(name)
    if raw_value in (None, ''):
        return default
    return raw_value.strip().lower() in {'1', 'true', 'yes', 'on'}


def _load_secret_key():
    """Use the configured SECRET_KEY or generate an ephemeral fallback."""
    configured = os.environ.get('SECRET_KEY')
    if configured not in (None, ''):
        return configured, False
    return secrets.token_hex(32), True


def _default_cors_origins():
    """Keep default CORS permissive for local development without allowing every origin."""
    return [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:4173',
        'http://127.0.0.1:4173',
        'http://localhost:5173',
        'http://127.0.0.1:5173',
    ]


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
    SECRET_KEY, SECRET_KEY_IS_GENERATED = _load_secret_key()
    DEBUG = _bool_env('FLASK_DEBUG', default=False)
    CORS_ALLOWED_ORIGINS = _csv_env('CORS_ALLOWED_ORIGINS', default=_default_cors_origins())
    CORS_ALLOW_METHODS = _csv_env(
        'CORS_ALLOW_METHODS',
        default=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    )
    CORS_ALLOW_HEADERS = _csv_env(
        'CORS_ALLOW_HEADERS',
        default=['Content-Type', 'Authorization', 'X-Locale'],
    )
    
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
    ZEP_RETRY_MAX_DELAY_SECONDS = _float_env('ZEP_RETRY_MAX_DELAY_SECONDS', 60.0)
    
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
    INTERVIEW_AGENT_TIMEOUT_SECONDS = _float_env('INTERVIEW_AGENT_TIMEOUT_SECONDS', 120.0)
    INTERVIEW_BATCH_TIMEOUT_SECONDS = _float_env('INTERVIEW_BATCH_TIMEOUT_SECONDS', 240.0)
    INTERVIEW_ALL_TIMEOUT_SECONDS = _float_env('INTERVIEW_ALL_TIMEOUT_SECONDS', 300.0)
    
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
    LLM_BASE_URL_ENV_NAMES = ('LLM_BASE_URL', 'OPENAI_BASE_URL', 'OPENAI_API_BASE_URL')

    @classmethod
    def validate(cls, locale='zh'):
        """验证必要配置"""
        return cls.validate_comprehensive(locale=locale).errors

    @classmethod
    def validate_comprehensive(cls, locale='zh'):
        """Validate configuration without changing startup behavior."""
        result = ConfigValidationResult()

        if not cls.LLM_API_KEY:
            result.add_error(tr("config.key_missing", locale, name="LLM_API_KEY / OPENAI_API_KEY"))
        if not cls.ZEP_API_KEY:
            result.add_error(tr("config.key_missing", locale, name="ZEP_API_KEY"))

        cls._validate_url(
            result,
            "LLM_BASE_URL / OPENAI_BASE_URL / OPENAI_API_BASE_URL",
            cls.LLM_BASE_URL,
            locale=locale,
        )
        base_url_conflict = cls._get_alias_conflict(*cls.LLM_BASE_URL_ENV_NAMES)
        if base_url_conflict:
            result.add_warning(
                tr(
                    "config.alias_conflict",
                    locale,
                    group=" / ".join(cls.LLM_BASE_URL_ENV_NAMES),
                    selected=base_url_conflict["selected_env"],
                    value=base_url_conflict["selected_value"],
                )
            )
        cls._validate_numeric_env(result, "LLM_MAX_TOKENS", minimum=1, locale=locale)
        cls._validate_numeric_env(result, "OASIS_DEFAULT_MAX_ROUNDS", minimum=1, locale=locale)
        cls._validate_numeric_env(result, "INTERVIEW_AGENT_TIMEOUT_SECONDS", minimum=1, parser=float, locale=locale)
        cls._validate_numeric_env(result, "INTERVIEW_BATCH_TIMEOUT_SECONDS", minimum=1, parser=float, locale=locale)
        cls._validate_numeric_env(result, "INTERVIEW_ALL_TIMEOUT_SECONDS", minimum=1, parser=float, locale=locale)
        cls._validate_numeric_env(result, "REPORT_AGENT_MAX_TOOL_CALLS", minimum=1, locale=locale)
        cls._validate_numeric_env(result, "REPORT_AGENT_MAX_REFLECTION_ROUNDS", minimum=0, locale=locale)
        cls._validate_numeric_env(
            result,
            "REPORT_AGENT_TEMPERATURE",
            minimum=0,
            maximum=2,
            parser=float,
            locale=locale,
        )
        cls._validate_numeric_env(result, "ZEP_RETRY_MAX_ATTEMPTS", minimum=1, locale=locale)
        cls._validate_numeric_env(
            result,
            "ZEP_RETRY_BASE_DELAY_SECONDS",
            minimum=0,
            parser=float,
            locale=locale,
        )
        cls._validate_numeric_env(
            result,
            "ZEP_RETRY_MAX_DELAY_SECONDS",
            minimum=0,
            parser=float,
            locale=locale,
        )

        if cls.DEBUG:
            result.add_warning(tr("config.debug_warning", locale))
        if cls.SECRET_KEY_IS_GENERATED:
            result.add_warning(tr("config.secret_key_warning", locale))
        if not os.path.isdir(cls.UPLOAD_FOLDER):
            result.add_info(tr("config.upload_folder_info", locale, path=cls.UPLOAD_FOLDER))
        if cls.LLM_MODEL_NAME:
            result.add_info(tr("config.model_info", locale, model=cls.LLM_MODEL_NAME))

        return result

    @classmethod
    def get_config_summary(cls):
        """Return a non-sensitive config snapshot for diagnostics."""
        llm_api_key_source = _configured_env_name('LLM_API_KEY', 'OPENAI_API_KEY')
        llm_base_url_source = _configured_env_name(*cls.LLM_BASE_URL_ENV_NAMES)
        llm_model_source = _configured_env_name('LLM_MODEL_NAME', 'OPENAI_MODEL')
        base_url_conflict = cls._get_alias_conflict(*cls.LLM_BASE_URL_ENV_NAMES)

        return {
            'cors': {
                'allowed_origins': cls.CORS_ALLOWED_ORIGINS,
                'allow_methods': cls.CORS_ALLOW_METHODS,
                'allow_headers': cls.CORS_ALLOW_HEADERS,
            },
            'llm': {
                'backend_mode': 'openai_compatible',
                'base_url': cls.LLM_BASE_URL,
                'model': cls.LLM_MODEL_NAME,
                'max_tokens': cls.LLM_MAX_TOKENS,
                'configured': bool(cls.LLM_API_KEY),
                'sources': {
                    'api_key_env': llm_api_key_source,
                    'base_url_env': llm_base_url_source,
                    'model_env': llm_model_source,
                    'base_url_conflict': base_url_conflict,
                    'uses_project_aliases': any(
                        source and source.startswith('LLM_')
                        for source in (llm_api_key_source, llm_base_url_source, llm_model_source)
                    ),
                    'uses_openai_aliases': any(
                        source and source.startswith('OPENAI_')
                        for source in (llm_api_key_source, llm_base_url_source, llm_model_source)
                    ),
                },
            },
            'zep': {
                'configured': bool(cls.ZEP_API_KEY),
                'retry_max_attempts': cls.ZEP_RETRY_MAX_ATTEMPTS,
                'retry_base_delay_seconds': cls.ZEP_RETRY_BASE_DELAY_SECONDS,
            },
            'simulation': {
                'default_max_rounds': cls.OASIS_DEFAULT_MAX_ROUNDS,
                'data_dir': cls.OASIS_SIMULATION_DATA_DIR,
                'interview_timeouts': {
                    'single_seconds': cls.INTERVIEW_AGENT_TIMEOUT_SECONDS,
                    'batch_seconds': cls.INTERVIEW_BATCH_TIMEOUT_SECONDS,
                    'all_seconds': cls.INTERVIEW_ALL_TIMEOUT_SECONDS,
                },
            },
            'report_agent': {
                'max_tool_calls': cls.REPORT_AGENT_MAX_TOOL_CALLS,
                'max_reflection_rounds': cls.REPORT_AGENT_MAX_REFLECTION_ROUNDS,
                'temperature': cls.REPORT_AGENT_TEMPERATURE,
            },
            'debug': cls.DEBUG,
            'security': {
                'secret_key_source': 'generated' if cls.SECRET_KEY_IS_GENERATED else 'env',
            },
        }

    @classmethod
    def get_cors_resources(cls):
        """Return Flask-CORS resource options from env-backed config."""
        return {
            'origins': cls.CORS_ALLOWED_ORIGINS or ['*'],
            'methods': cls.CORS_ALLOW_METHODS,
            'allow_headers': cls.CORS_ALLOW_HEADERS,
        }

    @classmethod
    def _validate_url(cls, result, name, value, locale='zh'):
        if not value:
            result.add_error(tr("config.key_missing", locale, name=name))
            return
        parsed = urlparse(value)
        if parsed.scheme not in {'http', 'https'}:
            result.add_error(tr("config.url_invalid_scheme", locale, name=name, value=value))
            return
        if not parsed.netloc:
            result.add_error(tr("config.url_missing_host", locale, name=name, value=value))

    @classmethod
    def _validate_numeric_env(cls, result, name, minimum=None, maximum=None, parser=int, locale='zh'):
        raw_value = os.environ.get(name)
        if raw_value in (None, ''):
            return
        try:
            value = parser(raw_value)
        except (TypeError, ValueError):
            result.add_error(tr("config.numeric_invalid", locale, name=name, value=raw_value))
            return
        if minimum is not None and value < minimum:
            result.add_error(tr("config.numeric_min", locale, name=name, minimum=minimum, value=raw_value))
        if maximum is not None and value > maximum:
            result.add_error(tr("config.numeric_max", locale, name=name, maximum=maximum, value=raw_value))

    @classmethod
    def _get_alias_conflict(cls, *names):
        entries = _configured_env_entries(*names)
        if len(entries) < 2:
            return None

        distinct_values = {value for _, value in entries}
        if len(distinct_values) <= 1:
            return None

        selected_env = entries[0][0]
        selected_value = entries[0][1]
        return {
            'has_conflict': True,
            'selected_env': selected_env,
            'selected_value': selected_value,
            'configured_envs': [
                {'name': name, 'value': value}
                for name, value in entries
            ],
        }


def validate_on_startup():
    """Compatibility helper for explicit startup validation hooks."""
    return Config.validate_comprehensive().is_valid
