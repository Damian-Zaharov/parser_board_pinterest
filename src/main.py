import logging
import sys
from typing import List

from src.config.settings import config
from src.core.webdriver import WebDriverFactory
from src.core.parser import PinterestBoardParser
from src.core.downloader import ImageDownloader
from src.models.pin import PinMetadata
import time



# Настраиваем логирование при старте модуля
config.setup_logging()
logger = logging.getLogger("main")


def main() -> None:
    logger.info("=== Запуск парсера Pinterest Board ===")

    # 1. Проверяем обязательные настройки
    if not config.PINTEREST_EMAIL or not config.PINTEREST_PASSWORD:
        logger.error("Критические настройки отсутствуют! Заполните PINTEREST_EMAIL и PINTEREST_PASSWORD в .env файле.")
        sys.exit(1)

    # 2. Инициализируем WebDriver
    driver = None
    try:
        driver = WebDriverFactory.create_chrome_driver()
        logger.info("Авторизация успешна. Ожидание сохранения сессии...")
        time.sleep(3)
        # 3. Создаем экземпляр парсера и проходим авторизацию
        parser = PinterestBoardParser(driver)

        if not parser.login():
            logger.error("Процесс остановлен, так как авторизация не удалась.")
            return

        # 4. Собираем уникальные ссылки на пины с доски
        pin_urls = parser.collect_pin_urls()
        if not pin_urls:
            logger.warning("Не найдено ни одной ссылки на пины. Завершение работы.")
            return

        # 5. Проходим по каждой ссылке и извлекаем прямые URL картинок
        logger.info(f"Начало извлечения прямых URL картинок для {len(pin_urls)} пинов...")
        pins_metadata: List[PinMetadata] = []
        total_pins = len(pin_urls)

        # Передаем индекс (idx) и общее количество (total_pins) в метод
        for idx, url in enumerate(pin_urls, 1):
            metadata = parser.extract_direct_image_url(url, current_index=idx, total_count=total_pins)
            pins_metadata.append(metadata)

        # 6. Инициализируем загрузчик и передаем ему куки из Selenium
        downloader = ImageDownloader(driver)

        # 7. Скачиваем картинки
        downloader.download_images(pins_metadata)

        # 8. Сохраняем отчет со статусами в CSV
        downloader.save_metadata_to_csv(pins_metadata, filename="pinterest_metadata.csv")

        logger.info("=== Работа парсера успешно завершена! ===")

    except KeyboardInterrupt:
        logger.warning("\nПроцесс был прерван пользователем (Ctrl+C).")
    except Exception as e:
        logger.critical(f"Непредвиденная критическая ошибка в главном цикле: {e}", exc_info=True)
    finally:
        # Гарантируем закрытие браузера в любом сценарии
        if driver:
            logger.info("Закрытие WebDriver...")
            driver.quit()
            logger.info("WebDriver успешно закрыт.")


if __name__ == "__main__":
    main()
