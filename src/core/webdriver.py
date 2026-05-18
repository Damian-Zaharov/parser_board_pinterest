import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from src.config.settings import config

logger = logging.getLogger(__name__)


class WebDriverFactory:
    @staticmethod
    def create_chrome_driver() -> webdriver.Chrome:
        """Создает и настраивает экземпляр Chrome WebDriver."""
        logger.info("Инициализация Chrome WebDriver...")

        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-notifications')
        options.add_argument('--window-size=1200,1000')

        if config.HEADLESS:
            logger.info("Запуск браузера в безголовом (Headless) режиме.")
            options.add_argument('--headless=new')

        try:
            # В 4+ Service() без параметров автоматически задействуем встроенный Selenium Manager
            driver = webdriver.Chrome(service=Service(), options=options)
            driver.set_page_load_timeout(60)
            logger.info("WebDriver успешно создан.")
            return driver
        except Exception as e:
            logger.error(f"Ошибка при создании WebDriver: {e}")
            raise e
