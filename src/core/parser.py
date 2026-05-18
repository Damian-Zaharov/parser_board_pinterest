import logging
import time
from typing import Set
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver

from src.config.settings import config
from src.models.pin import PinMetadata

import random
import time



logger = logging.getLogger(__name__)


class PinterestBoardParser:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, config.TIMEOUT)

    # def login(self) -> bool:
    #     """Выполняет авторизацию на Pinterest."""
    #     logger.info("Переход на страницу авторизации Pinterest...")
    #     self.driver.get("https://pinterest.com")
    #
    #     try:
    #         # Ожидание и ввод Email
    #         email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
    #         email_field.clear()
    #         email_field.send_keys(config.PINTEREST_EMAIL)
    #
    #         # Ожидание и ввод Пароля
    #         password_field = self.driver.find_element(By.ID, "password")
    #         password_field.clear()
    #         password_field.send_keys(config.PINTEREST_PASSWORD)
    #
    #         # Клик по кнопке Войти (ищем по тегу button с типом submit)
    #         login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
    #         login_button.click()
    #
    #         logger.info("Данные авторизации отправлены. Ожидание завершения входа...")
    #         # Ждем появления элемента, который доступен только авторизованным юзерам (например, поисковая строка)
    #         self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-test-id="search-box-input"]')))
    #         logger.info("Авторизация успешно пройдена!")
    #         return True
    #
    #     except Exception as e:
    #         logger.error(f"Не удалось авторизоваться: {e}")
    #         return False
    def login(self) -> bool:
        """Выполняет стабильную авторизацию на Pinterest на правильном поддомене."""
        from urllib.parse import urlparse
        from selenium.webdriver.common.keys import Keys
        import random

        # Извлекаем базовый домен из ссылки на доску (например, https://pinterest.com)
        # Это нужно, чтобы логиниться на том же поддомене, где лежит доска, избегая разлогина
        try:
            parsed_url = urlparse(config.BOARD_URL)
            base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        except Exception:
            base_domain = "https://pinterest.com"

        login_url = f"{base_domain}/login/"
        logger.info(f"Переход на локальную страницу авторизации: {login_url}")
        self.driver.get(login_url)

        try:
            # 1. Ожидание и посимвольный ввод Email
            email_field = self.wait.until(EC.element_to_be_clickable((By.ID, "email")))
            email_field.clear()
            for char in config.PINTEREST_EMAIL:
                email_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.12))  # Имитация человеческой печати

            time.sleep(random.uniform(0.3, 0.6))

            # 2. Поиск и посимвольный ввод Пароля
            password_field = self.wait.until(EC.element_to_be_clickable((By.ID, "password")))
            password_field.clear()
            for char in config.PINTEREST_PASSWORD:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.12))

            time.sleep(random.uniform(0.5, 1.0))

            # 3. Отправка формы через клавишу ENTER (надежнее, чем клик по кнопке)
            logger.info("Отправка формы через нажатие Enter...")
            password_field.send_keys(Keys.ENTER)

            logger.info("Данные отправлены. Ожидание завершения входа (макс. 45 сек)...")

            # 4. Проверяем успешность входа по появлению главного элемента интерфейса.
            # Таймаут увеличен: если появится капча, вы успеете нажать ее руками!
            smart_wait = WebDriverWait(self.driver, 45)
            smart_wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-test-id="search-box-input"]'))
            )

            logger.info("Авторизация успешно пройдена!")
            return True

        except Exception as e:
            logger.error(f"Не удалось авторизоваться: {e}")
            # Сохраняем скриншот при падении — это стандарт разработки автотестов
            screenshot_path = "auth_error.png"
            self.driver.save_screenshot(screenshot_path)
            logger.error(f"Скриншот страницы в момент ошибки сохранен в '{screenshot_path}'")
            return False

    # def collect_pin_urls(self) -> Set[str]:
    #     """Скроллит доску и собирает уникальные ссылки на пины с защитой от зависания загрузки."""
    #     if not config.BOARD_URL:
    #         raise ValueError("BOARD_URL не задан в конфигурации (.env)")
    #
    #     # logger.info(f"Переход к доске: {config.BOARD_URL}")
    #     # self.driver.get(config.BOARD_URL)
    #     logger.info(f"Синхронный переход к доске: {config.BOARD_URL}")
    #     self.driver.execute_script(f"window.location.href = '{config.BOARD_URL}';")
    #
    #     # Даем странице доски начать загрузку
    #     time.sleep(3)
    #
    #     try:
    #         self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-test-id="pin"]')))
    #     except Exception:
    #         logger.warning("Сетка пинов не обнаружилась сразу, пробуем начать скроллинг.")
    #
    #     pin_urls: Set[str] = set()
    #     last_height = self.driver.execute_script("return document.body.scrollHeight")
    #     no_change_count = 0
    #     max_no_change_attempts = 8  # Middle-решение: даем Pinterest до 8 попыток (около 8 секунд) на подгрузку контента
    #
    #     logger.info(f"Начало сбора ссылок. Цель: {config.EXPECTED_PINS} шт.")
    #
    #     for iteration in range(config.MAX_SCROLL_ITER):
    #         elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-test-id="pin"] a')
    #         for elem in elements:
    #             href = elem.get_attribute("href")
    #             if href and "/pin/" in href:
    #                 clean_url = href.split('?')[0]
    #                 pin_urls.add(clean_url)
    #
    #         current_count = len(pin_urls)
    #         logger.info(f"Итерация {iteration + 1}: Собрано ссылок: {current_count}/{config.EXPECTED_PINS}")
    #
    #         if current_count >= config.EXPECTED_PINS:
    #             logger.info(f"Достигнуто целевое количество пинов: {current_count}")
    #             break
    #
    #         # Скроллим вниз
    #         self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #         time.sleep(config.SCROLL_PAUSE)
    #
    #         # Проверяем высоту страницы
    #         new_height = self.driver.execute_script("return document.body.scrollHeight")
    #
    #         if new_height == last_height:
    #             no_change_count += 1
    #             # Имитируем поведение человека: если страница зависла, скроллим чуть-чуть вверх и снова вниз
    #             if no_change_count == 3:
    #                 logger.info("Страница подзависла. Пробуем 'растолкать' скроллинг...")
    #                 self.driver.execute_script("window.scrollBy(0, -500);")
    #                 time.sleep(0.5)
    #                 self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #
    #             if no_change_count >= max_no_change_attempts:
    #                 logger.info(f"Достигнут реальный конец доски после {max_no_change_attempts} попыток ожидания.")
    #                 break
    #         else:
    #             last_height = new_height
    #             no_change_count = 0
    #
    #     return pin_urls

    def collect_pin_urls(self) -> Set[str]:
        """Скроллит доску и собирает уникальные ссылки на пины с защитой сессии."""
        if not config.BOARD_URL:
            raise ValueError("BOARD_URL не задан в конфигурации (.env)")

        # 1. Сохраняем куки успешной авторизации из Selenium в память
        logger.info("Сохранение авторизационных кук перед переходом...")
        saved_cookies = self.driver.get_cookies()

        # 2. Переходим на страницу доски
        logger.info(f"Переход к доске: {config.BOARD_URL}")
        self.driver.get(config.BOARD_URL)
        time.sleep(3)

        # 3. Middle-проверка: проверяем, не выкинуло ли нас на страницу логина
        if "login" in self.driver.current_url or not self.driver.find_elements(By.CSS_SELECTOR, '[data-test-id="pin"]'):
            logger.warning("Обнаружен сброс сессии (разлогин)! Принудительно внедряем куки...")

            # Очищаем битые куки и вставляем сохраненные
            self.driver.delete_all_cookies()
            for cookie in saved_cookies:
                # На всякий случай убираем привязку к конкретному сайту, чтобы куки подошли к любому поддомену Pinterest
                if 'expiry' in cookie:
                    del cookie['expiry']
                self.driver.add_cookie(cookie)

            # Перезагружаем страницу уже с правильными куками
            logger.info("Куки внедрены. Перезагрузка страницы...")
            self.driver.refresh()
            time.sleep(4)

        # 4. Проверяем, помогло ли внедрение кук
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-test-id="pin"]')))
            logger.info("Доска успешно загружена в авторизованном режиме.")
        except Exception:
            logger.error(
                "Защита Pinterest отклонила куки. Попробуйте отключить HEADLESS режим в .env, чтобы пройти проверку визуально.")

        # --- Далее идет твой стабильный цикл скроллинга (оставляем без изменений) ---
        pin_urls: Set[str] = set()
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        no_change_count = 0
        max_no_change_attempts = 8

        logger.info(f"Начало сбора ссылок. Цель: {config.EXPECTED_PINS} шт.")

        for iteration in range(config.MAX_SCROLL_ITER):
            elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-test-id="pin"] a')
            for elem in elements:
                href = elem.get_attribute("href")
                if href and "/pin/" in href:
                    clean_url = href.split('?')[0]
                    pin_urls.add(clean_url)

            current_count = len(pin_urls)
            logger.info(f"Итерация {iteration + 1}: Собрано ссылок: {current_count}/{config.EXPECTED_PINS}")

            if current_count >= config.EXPECTED_PINS:
                logger.info(f"Достигнуто целевое количество пинов: {current_count}")
                break

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(config.SCROLL_PAUSE)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                no_change_count += 1
                if no_change_count == 3:
                    logger.info("Страница подзависла. Пробуем 'растолкать' скроллинг...")
                    self.driver.execute_script("window.scrollBy(0, -500);")
                    time.sleep(0.5)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                if no_change_count >= max_no_change_attempts:
                    logger.info(f"Достигнут реальный конец доски после {max_no_change_attempts} попыток ожидания.")
                    break
            else:
                last_height = new_height
                no_change_count = 0

        return pin_urls

    def extract_direct_image_url(self, pin_url: str, current_index: int, total_count: int) -> PinMetadata:
        """Заходит на страницу конкретного пина и вытягивает ссылку на картинку в максимальном качестве."""
        metadata = PinMetadata(pin_url=pin_url)
        pin_id = pin_url.rstrip('/').split('/')[-1]
        try:
            self.driver.get(pin_url)

            # Набор селекторов
            selectors = [
                'img[elementtiming="closeup-image-main-MainPinImage"]',
                'img.iFOUS5',
                'main [data-test-id="pin-detail-image"] img'
            ]

            img_element = None
            for selector in selectors:
                try:
                    img_element = WebDriverWait(self.driver, 4).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if img_element:
                        break
                except Exception:
                    continue

            if img_element:
                srcset = img_element.get_attribute("srcset")
                img_src = None

                if srcset:
                    urls = [parts.strip().split() for parts in srcset.split(',')]
                    if urls:
                        img_src = urls[-1][0]

                if not img_src:
                    img_src = img_element.get_attribute("src")

                if img_src:
                    metadata.image_url = img_src
                    metadata.status = "ready_to_download"
                    metadata.filename = f"{pin_id}.jpg"
                    # ОБНОВЛЕННЫЙ ЛОГ: выводим прогресс в формате nn/xx
                    logger.info(f"[{current_index}/{total_count}] Успешно найден URL картинки для пина {pin_id}")
                    return metadata

            metadata.status = "no_image_found"
            logger.warning(f"[{current_index}/{total_count}] Не удалось найти элемент картинки на странице {pin_url}")

        except Exception as e:
            metadata.status = "failed_to_extract"
            logger.error(f"[{current_index}/{total_count}] Ошибка при обработке страницы пина {pin_id}: {e}")

        return metadata



