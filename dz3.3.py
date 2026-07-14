from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import divan_parser


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "divan_kids_furniture_all_pages.csv"
CLEANED_FILE = BASE_DIR / "divan_kids_furniture_cleaned.csv"
HISTOGRAM_FILE = BASE_DIR / "divan_price_histogram.png"


def ensure_source_csv():
    if INPUT_FILE.is_file():
        print(f"Файл найден: {INPUT_FILE.name}")
    else:
        print(f"Файл {INPUT_FILE.name} не найден. Запускаю divan_parser.py ...")
        divan_parser.main()


def main():
    ensure_source_csv()

    print("\nОбработка CSV...")
    df = pd.read_csv(INPUT_FILE)

    df["price"] = df["price"].fillna("").astype(str).str.strip()
    df = df[df["price"] != ""]

    df["price_num"] = df["price"].str.replace(r"[^0-9]", "", regex=True)
    df["price_num"] = pd.to_numeric(df["price_num"], errors="coerce")
    df = df.dropna(subset=["price_num"])

    average_price = df["price_num"].mean()

    print(f"Количество товаров с ценой: {len(df)}")
    print(f"Средняя цена: {average_price:.2f} руб.")

    df.to_csv(CLEANED_FILE, index=False, encoding="utf-8-sig")
    print(f"Очищенный CSV сохранён: {CLEANED_FILE.name}")

    plt.figure(figsize=(12, 6))
    plt.hist(df["price_num"], bins=20, edgecolor="black")
    plt.title("Гистограмма цен на товары Divan.ru")
    plt.xlabel("Цена, руб.")
    plt.ylabel("Количество товаров")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(HISTOGRAM_FILE, dpi=150)
    print(f"Гистограмма сохранена: {HISTOGRAM_FILE.name}")

    plt.show()


if __name__ == "__main__":
    main()