import csv
import time
from urllib.parse import urljoin
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://www.divan.ru/category/mebel-dla-detskoj"
OUTPUT_FILE = "divan_kids_furniture_all_pages.csv"

CARD_SELECTOR = '[class*="CatalogContent-module__"][class*="__item"]'
IMG_SELECTOR = 'img[class*="Img-module__"][class*="__image"][class*="ProductImage-module__"]'
PRICE_SELECTOR = '[class*="ui-LD-ZU"][class*="FullPrice-module__"]'
NAME_SELECTOR = '[class*="Name-module__"][class*="__name"][class*="ProductName"][class*="ActiveProduct"]'
LINK_SELECTOR = 'a[class*="ui-GPFV8"]'
PAGINATION_SELECTOR = 'a[href*="/category/mebel-dla-detskoj/page-"]'


def log_time(stage_name, start_time):
    elapsed = time.perf_counter() - start_time
    print(f"[TIME] {stage_name}: {elapsed:.3f} сек.")


def setup_driver():
    start = time.perf_counter()

    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.page_load_strategy = "eager"

    prefs = {
        "profile.managed_default_content_settings.images": 2
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)

    log_time("Инициализация драйвера", start)
    return driver


def safe_find_text(parent, selector):
    elements = parent.find_elements(By.CSS_SELECTOR, selector)
    return elements[0].text.strip() if elements else ""


def safe_find_attr(parent, selector, attr):
    elements = parent.find_elements(By.CSS_SELECTOR, selector)
    if not elements:
        return ""
    value = elements[0].get_attribute(attr)
    return value.strip() if value else ""


def get_total_pages(driver):
    start = time.perf_counter()

    links = driver.find_elements(By.CSS_SELECTOR, PAGINATION_SELECTOR)
    page_numbers = [1]

    for link in links:
        href = (link.get_attribute("href") or "").strip()
        text = (link.text or "").strip()

        if text.isdigit():
            page_numbers.append(int(text))
            continue

        if "/page-" in href:
            tail = href.rstrip("/").split("/page-")[-1]
            if tail.isdigit():
                page_numbers.append(int(tail))

    total_pages = max(page_numbers)
    log_time(f"Определение количества страниц ({total_pages})", start)
    return total_pages


def parse_page(driver, url, page_num):
    total_start = time.perf_counter()

    start = time.perf_counter()
    driver.get(url)
    log_time(f"Страница {page_num}: driver.get()", start)

    start = time.perf_counter()
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, CARD_SELECTOR)))
    log_time(f"Страница {page_num}: ожидание карточек", start)

    start = time.perf_counter()
    cards = driver.find_elements(By.CSS_SELECTOR, CARD_SELECTOR)
    log_time(f"Страница {page_num}: поиск карточек ({len(cards)} шт.)", start)

    start = time.perf_counter()
    results = []

    for card in cards:
        product_url = safe_find_attr(card, LINK_SELECTOR, "href")
        name = safe_find_text(card, NAME_SELECTOR)
        price = safe_find_text(card, PRICE_SELECTOR)
        image_url = safe_find_attr(card, IMG_SELECTOR, "src")

        if image_url.startswith("//"):
            image_url = "https:" + image_url
        elif image_url.startswith("/"):
            image_url = urljoin(BASE_URL, image_url)

        if product_url.startswith("/"):
            product_url = urljoin(BASE_URL, product_url)

        if name or price or product_url or image_url:
            results.append({
                "name": name,
                "price": price,
                "product_url": product_url,
                "image_url": image_url,
                "page": page_num,
            })

    log_time(f"Страница {page_num}: обработка карточек", start)
    log_time(f"Страница {page_num}: полностью", total_start)

    return results


def deduplicate_items(items):
    start = time.perf_counter()

    unique_items = []
    seen = set()

    for item in items:
        key = item["product_url"] or (item["name"], item["price"], item["page"])
        if key not in seen:
            seen.add(key)
            unique_items.append(item)

    log_time("Удаление дублей", start)
    return unique_items


def save_to_csv(data, filename):
    start = time.perf_counter()

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["page", "name", "price", "product_url", "image_url"]
        )
        writer.writeheader()
        writer.writerows(data)

    log_time("Сохранение в CSV", start)


def main():
    script_start = time.perf_counter()
    driver = setup_driver()
    all_data = []

    try:
        start = time.perf_counter()
        driver.get(BASE_URL)
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, CARD_SELECTOR))
        )
        log_time("Первичная загрузка стартовой страницы", start)

        total_pages = get_total_pages(driver)
        print(f"Найдено страниц: {total_pages}")

        for page_num in range(1, total_pages + 1):
            page_start = time.perf_counter()

            url = BASE_URL if page_num == 1 else f"{BASE_URL}/page-{page_num}"
            print(f"\nПарсинг страницы {page_num}: {url}")

            page_data = parse_page(driver, url, page_num)
            all_data.extend(page_data)

            log_time(f"Страница {page_num}: итоговый цикл", page_start)

        unique_data = deduplicate_items(all_data)
        save_to_csv(unique_data, OUTPUT_FILE)

        print(f"\nСохранено уникальных товаров: {len(unique_data)}")
        print(f"Файл: {OUTPUT_FILE}")

    finally:
        start = time.perf_counter()
        driver.quit()
        log_time("Закрытие драйвера", start)

    log_time("Весь скрипт", script_start)


if __name__ == "__main__":
    main()