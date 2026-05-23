import logging
import sys
from pathlib import Path
import structlog
from structlog.types import Processor


def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
    ]

    structlog.configure(
        processors=processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer() if not sys.stderr.isatty() else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    # Standard logging configuration for other libraries
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    
    # Silence some noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)


logger = structlog.get_logger()
