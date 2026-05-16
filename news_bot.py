import os
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from html import escape

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_news():

    url = (
        "https://news.google.com/rss/search"
        "?q=경제&hl=ko&gl=KR&ceid=KR:ko"
    )

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    soup = BeautifulSoup(response.content, "xml")

    items = soup.find_all("item", limit=5)

    news_list = []

    for idx, item in enumerate(items, start=1):

        title = item.title.text.strip()
        link = item.link.text.strip()

        news_text = (
            f"{idx}. 📰 {escape(title)}\n"
            f"🔗 {link}\n"
        )

        news_list.append(news_text)

    return "\n".join(news_list)

def send_telegram_message(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    response = requests.post(
        url,
        data=payload,
        timeout=10
    )

    if response.status_code == 200:
        print("전송 성공")
    else:
        print("전송 실패")
        print(response.text)

if __name__ == "__main__":

    message = (
        "<b>📊 오늘의 경제 뉴스</b>\n\n"
        + get_news()
    )

    send_telegram_message(message)
