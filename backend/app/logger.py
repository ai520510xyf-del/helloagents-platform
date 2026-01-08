"""
统一日志配置模块

使用 structlog 实现结构化日志，支持 JSON 格式输出和日志轮转。
集成 Sentry 用于生产环境错误追踪。
"""

import os
import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
import structlog
from structlog.types import Processor
from typing import Any, Dict


# ===========================
# 日志配置常量
# ===========================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "helloagents.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5  # 保留5个备份文件


# ===========================
# 日志过滤器 - 移除敏感信息
# ===========================

SENSITIVE_KEYS = [
    "password",
    "token",
    "api_key",
    "secret",
    "authorization",
    "cookie",
    "session",
    "deepseek_api_key",
    "anthropic_api_key",
    "sentry_dsn",
]


def filter_sensitive_data(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    过滤日志中的敏感信息

    将密码、API密钥等敏感字段替换为 ***REDACTED***
    """
    def _filter_dict(data: Any) -> Any:
        if isinstance(data, dict):
            return {
                key: "***REDACTED***" if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS)
                else _filter_dict(value)
                for key, value in data.items()
            }
        elif isinstance(data, (list, tuple)):
            return [_filter_dict(item) for item in data]
        return data

    return _filter_dict(event_dict)


# ===========================
# 自定义日志处理器
# ===========================

def add_app_context(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    添加应用上下文信息
    """
    event_dict["app"] = "helloagents"
    event_dict["environment"] = os.getenv("ENVIRONMENT", "development")
    return event_dict


def add_exception_info(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    为异常日志添加详细信息
    """
    if "exception" in event_dict or event_dict.get("level") in ["error", "critical"]:
        # structlog 的 format_exc_info 会自动处理异常信息
        pass
    return event_dict


# ===========================
# 配置标准库 logging
# ===========================

def setup_stdlib_logging():
    """
    配置标准库 logging

    创建日志目录和文件，配置轮转处理器
    """
    # 创建日志目录
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # 移除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 文件处理器（带日志轮转）
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(LOG_LEVEL)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)

    # 添加处理器到根记录器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


# ===========================
# 配置 structlog
# ===========================

def configure_structlog():
    """
    配置 structlog 日志处理器链

    处理器链顺序很重要，从上到下依次执行
    """
    # 根据环境选择不同的处理器
    is_development = os.getenv("ENVIRONMENT", "development") == "development"

    # 基础处理器链
    processors: list[Processor] = [
        # 添加日志级别
        structlog.stdlib.add_log_level,

        # 添加日志记录器名称
        structlog.stdlib.add_logger_name,

        # 添加调用者信息（文件名、行号、函数名）
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            ]
        ),

        # 添加时间戳
        structlog.processors.TimeStamper(fmt="iso", utc=True),

        # 添加应用上下文
        add_app_context,

        # 过滤敏感信息
        filter_sensitive_data,

        # 添加异常信息
        add_exception_info,

        # 格式化异常堆栈
        structlog.processors.format_exc_info,

        # 解包字典参数
        structlog.processors.UnicodeDecoder(),
    ]

    # 开发环境使用彩色输出，生产环境使用 JSON
    if is_development:
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    # 配置 structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# ===========================
# 初始化日志系统
# ===========================

def init_logging():
    """
    初始化日志系统

    同时配置标准库 logging 和 structlog
    """
    setup_stdlib_logging()
    configure_structlog()


# ===========================
# 获取 logger 实例
# ===========================

def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """
    获取 structlog logger 实例

    Args:
        name: 日志记录器名称，通常使用 __name__

    Returns:
        structlog BoundLogger 实例

    使用示例:
        logger = get_logger(__name__)
        logger.info("user_login", user_id=123, username="alice")
        logger.error("api_error", error="Connection timeout", endpoint="/api/users")
    """
    return structlog.get_logger(name)


# ===========================
# 日志辅助函数
# ===========================

def log_execution_time(logger: structlog.stdlib.BoundLogger, operation: str):
    """
    装饰器：记录函数执行时间

    使用示例:
        @log_execution_time(logger, "fetch_user_data")
        def fetch_user(user_id: int):
            # ...
            pass
    """
    import time
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    "operation_completed",
                    operation=operation,
                    execution_time_ms=round(execution_time * 1000, 2),
                    success=True
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    "operation_failed",
                    operation=operation,
                    execution_time_ms=round(execution_time * 1000, 2),
                    success=False,
                    error=str(e),
                    exc_info=True
                )
                raise
        return wrapper
    return decorator


# ===========================
# 模块级初始化
# ===========================

# 初始化日志系统
init_logging()

# 创建默认 logger
logger = get_logger(__name__)

# 记录日志系统启动
logger.info(
    "logging_system_initialized",
    log_level=LOG_LEVEL,
    log_file=str(LOG_FILE),
    max_log_size_mb=MAX_LOG_SIZE / (1024 * 1024),
    backup_count=BACKUP_COUNT,
    environment=os.getenv("ENVIRONMENT", "development")
)
