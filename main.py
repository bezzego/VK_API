import requests
from urllib.parse import urlparse
import os
from dotenv import load_dotenv


def is_shorten_link(url):
    """
    Проверяет, является ли ссылка короткой ссылкой vk.cc
    """
    parsed_url = urlparse(url)
    return parsed_url.netloc == "vk.cc"


def shorten_link(token, url):
    """
    Отправляет запрос к VK API и возвращает сокращённую ссылку.
    """
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
    """
    Получает количество переходов по короткой ссылке VK.
    """
    # Извлекаем ключ ссылки (например, "cvPDMl" из "https://vk.cc/cvPDMl")
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
    load_dotenv()  # Загружаем переменные окружения из .env
    token = os.getenv("VK_TOKEN")
    if not token:
        raise EnvironmentError("Переменная окружения VK_TOKEN не установлена")

    url = input("Введите ссылку для сокращения: ")

    try:
        if is_shorten_link(url):
            clicks = count_clicks(token, url)
            print("Количество переходов по ссылке:", clicks)
        else:
            short = shorten_link(token, url)
            print("Сокращенная ссылка:", short)
    except Exception as e:
        print("Не удалось сократить ссылку или получить статистику:", e)


if __name__ == "__main__":
    main()
