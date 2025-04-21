import requests
from urllib.parse import urlparse
import os
from dotenv import load_dotenv


def is_shorten_link(url):

    parsed_url = urlparse(url)
    return parsed_url.netloc == "vk.cc"


def shorten_link(token, url):

    params = {"access_token": token, "v": "5.131", "url": url}

    response = requests.get(
        "https://api.vk.com/method/utils.getShortLink", params=params
    )
    data = response.json()

    if "error" in data:
        error_msg = data["error"].get("error_msg", "Неизвестная ошибка")
        raise ValueError(f"Ошибка от VK API: {error_msg}")
    elif "response" in data:
        return data["response"]["short_url"]
    else:
        raise Exception(f"Непредвиденный ответ от VK API: {data}")


def count_clicks(token, short_url):

    path = urlparse(short_url).path
    key = path.strip("/")

    params = {"access_token": token, "v": "5.131", "key": key}

    response = requests.get(
        "https://api.vk.com/method/utils.getLinkStats", params=params
    )
    data = response.json()

    if "error" in data:
        error_msg = data["error"].get("error_msg", "Неизвестная ошибка")
        raise ValueError(f"Ошибка от VK API: {error_msg}")
    elif "response" in data:
        total_clicks = data["response"]["stats"]
        return sum(day["views"] for day in total_clicks)
    else:
        raise Exception(f"Непредвиденный ответ от VK API: {data}")


def main():
    load_dotenv()
    token = os.getenv("VK_TOKEN")
    if not token:
        raise EnvironmentError("Переменная окружения VK_TOKEN не установлена")

    url = input("Введите ссылку для сокращения: ")

    try:
        if is_shorten_link(url):
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
    except Exception as e:
        print("Не удалось сократить ссылку или получить статистику:", e)


if __name__ == "__main__":
    main()
