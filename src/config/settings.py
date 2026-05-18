import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


class Settings:
    # Аутентификация
    PINTEREST_EMAIL: str = os.getenv("PINTEREST_EMAIL", "")
    PINTEREST_PASSWORD: str = os.getenv("PINTEREST_PASSWORD", "")
    BOARD_URL: str = os.getenv("BOARD_URL", "")

    # Пути
    DEST_DIR: Path = Path(os.getenv("DEST_DIR", "./downloads"))

    # Настройки скрапинга
    EXPECTED_PINS: int = int(os.getenv("EXPECTED_PINS", 100))
    HEADLESS: bool = os.getenv("HEADLESS", "False").lower() in ("true", "1", "t")
    SCROLL_PAUSE: float = float(os.getenv("SCROLL_PAUSE", 1.0))
    MAX_SCROLL_ITER: int = int(os.getenv("MAX_SCROLL_ITER", 1000))
    DOWNLOAD_RETRIES: int = int(os.getenv("DOWNLOAD_RETRIES", 3))
    TIMEOUT: int = int(os.getenv("TIMEOUT", 20))

    @classmethod
    def setup_logging(cls) -> None:
        """Настройка стандартного логирования для всего проекта."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.StreamHandler(),  # Вывод в консоль
                logging.FileHandler("parser.log", encoding="utf-8")  # Запись в файл
            ]
        )


# Создаем синглтон конфигурации для импорта в другие модули
config = Settings()
