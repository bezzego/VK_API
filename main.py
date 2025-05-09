import requests
from urllib.parse import urlparse
import os
import argparse
from dotenv import load_dotenv


def is_shorten_link(url):
    parsed = urlparse(url)
    return parsed.netloc == "vk.cc"


def shorten_link(token, url):

    params = {"access_token": token, "v": "5.131", "url": url}

    response = requests.get(
        "https://api.vk.com/method/utils.getShortLink", params=params
    )
    response.raise_for_status()
    shorten_response = response.json()

    if "error" not in shorten_response:
        return shorten_response["response"]["short_url"]

    error_msg = shorten_response["error"].get("error_msg", "Неизвестная ошибка")
    raise ValueError(f"Ошибка от VK API: {error_msg}")


def count_clicks(token, short_url):

    path = urlparse(short_url).path
    key = path.strip("/")

    params = {"access_token": token, "v": "5.131", "key": key}

    response = requests.get(
        "https://api.vk.com/method/utils.getLinkStats", params=params
    )
    response.raise_for_status()
    stats_response = response.json()

    if "error" not in stats_response:
        total_clicks = stats_response["response"]["stats"]
        return sum(day["views"] for day in total_clicks)

    error_msg = stats_response["error"].get("error_msg", "Неизвестная ошибка")
    raise ValueError(f"Ошибка от VK API: {error_msg}")


def main():
    load_dotenv()
    token = os.getenv("VK_TOKEN")
    if not token:
        raise EnvironmentError("Переменная окружения VK_TOKEN не установлена")

    parser = argparse.ArgumentParser(
        description="Сокращение ссылки или подсчёт кликов с помощью VK API"
    )
    parser.add_argument("url", help="URL-адрес для сокращения или анализа")
    args = parser.parse_args()
    url = args.url

    try:
        shorten = is_shorten_link(url)
    except requests.RequestException as re:
        print("Ошибка сетевого запроса при проверке ссылки:", re)
        return

    if shorten:
        try:
            clicks = count_clicks(token, url)
            print("Количество переходов по ссылке:", clicks)
        except ValueError as ve:
            print("Ошибка при получении статистики по ссылке:", ve)
        except requests.RequestException as re:
            print("Ошибка сетевого запроса при получении статистики:", re)
    else:
        try:
            short = shorten_link(token, url)
            print("Сокращенная ссылка:", short)
        except ValueError as ve:
            print("Ошибка при сокращении ссылки:", ve)
        except requests.RequestException as re:
            print("Ошибка сетевого запроса при сокращении ссылки:", re)


if __name__ == "__main__":
    main()
