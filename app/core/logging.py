import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Добавляем дополнительные поля если они есть
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
            
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging():
    """Настройка логирования для всего приложения"""
    
    # Создаем директорию для логов если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Основной логгер
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    
    # Форматтер
    formatter = JSONFormatter()
    
    # Файловый обработчик с ротацией
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Устанавливаем уровень для сторонних библиотек
    logging.getLogger("telethon").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
    
    return logger

# Глобальный логгер
logger = logging.getLogger("app")