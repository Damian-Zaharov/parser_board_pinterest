import csv
import logging
import requests
from typing import List
from tqdm import tqdm
from selenium.webdriver.remote.webdriver import WebDriver

from src.config.settings import config
from src.models.pin import PinMetadata



logger = logging.getLogger(__name__)


class ImageDownloader:
    def __init__(self, driver: WebDriver) -> None:
        self.session = requests.Session()
        self._transfer_cookies(driver)

        # Создаем папку для скачивания, если её нет
        config.DEST_DIR.mkdir(parents=True, exist_ok=True)

    def _transfer_cookies(self, driver: WebDriver) -> None:
        """Переносит куки из активной сессии Selenium в сессию Requests."""
        logger.info("Перенос куки-файлов из Selenium в Requests сессию...")
        selenium_cookies = driver.get_cookies()
        for cookie in selenium_cookies:
            self.session.cookies.set(cookie['name'], cookie['value'])
        logger.info("Куки успешно перенесены.")

    def download_images(self, pins_metadata: List[PinMetadata]) -> None:
        """Скачивает картинки на диск на основе собранных метаданных."""
        logger.info(f"Начало скачивания картинок. Всего к обработке: {len(pins_metadata)}")

        # Используем tqdm для красивого индикатора выполнения в консоли
        for pin in tqdm(pins_metadata, desc="Скачивание пинов", unit="img"):
            if not pin.image_url or pin.status != "ready_to_download":
                continue

            file_path = config.DEST_DIR / pin.filename

            # Проверяем, возможно файл уже был скачан ранее
            if file_path.exists():
                pin.status = "already_exists"
                continue

            try:
                response = self.session.get(pin.image_url, timeout=config.TIMEOUT)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    pin.status = "downloaded"
                else:
                    pin.status = f"failed_status_{response.status_code}"
                    logger.error(f"Не удалось скачать {pin.image_url}. Статус: {response.status_code}")
            except Exception as e:
                pin.status = "download_error"
                logger.error(f"Ошибка при скачивании файла {pin.image_url}: {e}")

    def save_metadata_to_csv(self, pins_metadata: List[PinMetadata], filename: str = "metadata_pins.csv") -> None:
        """Сохраняет собранные метаданные в CSV файл (замена Pandas на чистый CSV)."""
        logger.info(f"Сохранение метаданных в файл: {filename}")

        if not pins_metadata:
            logger.warning("Нет метаданных для сохранения.")
            return

        try:
            # Берем ключи из первого объекта в качестве заголовков колонок
            headers = list(pins_metadata[0].to_dict().keys())

            with open(filename, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for pin in pins_metadata:
                    writer.writerow(pin.to_dict())

            logger.info("Метаданные успешно сохранены.")
        except Exception as e:
            logger.error(f"Ошибка при записи CSV файла: {e}")

