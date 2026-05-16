import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from html import escape

# =========================
# 환경변수 로드
# =========================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# =========================
# RSS 목록
# =========================
RSS_FEEDS = {
    "한국경제": "https://www.hankyung.com/feed/economy",
    "매일경제": "https://www.mk.co.kr/rss/30100041/",
    "연합뉴스": "https://www.yna.co.kr/rss/economy.xml"
}

# =========================
# (비동기) 개별 RSS 뉴스 가져오기
# =========================
async def fetch_news_async(session, company, rss_url, limit=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        async with session.get(rss_url, headers=headers, timeout=10) as response:
            response.raise_for_status()
            # 비동기로 페이지 데이터 읽기
            content = await response.read()
    except Exception as e:
        return company, [f"뉴스 요청 실패: {e}"]

    soup = BeautifulSoup(content, "xml")
    items = soup.find_all("item", limit=limit)
    news_list = []

    for idx, item in enumerate(items, start=1):
        try:
            title = item.title.text.strip()
            link = item.link.text.strip()
            news_text = f"{idx}. 📰 {escape(title)}\n🔗 {link}"
            news_list.append(news_text)
        except Exception:
            continue

    if not news_list:
        return company, ["뉴스 데이터 없음"]

    return company, news_list

# =========================
# (비동기) 전체 뉴스 메시지 생성
# =========================
async def make_news_message_async():
    final_message = "<b>📊 오늘의 경제 뉴스 브리핑</b>\n\n"
    
    # aiohttp 세션을 열고 동시에 요청을 보냄
    async with aiohttp.ClientSession() as session:
        tasks = []
        for company, rss_url in RSS_FEEDS.items():
            # 3개의 작업(Task)을 리스트에 담기
            tasks.append(fetch_news_async(session, company, rss_url, limit=10))
        
        # gather를 통해 모든 작업을 동시에 실행하고 결과를 기다림 (가장 핵심!)
        results = await asyncio.gather(*tasks)

    # 모인 결과를 순서대로 합치기
    for company, news_items in results:
        final_message += f"<b>🗞 {company}</b>\n\n"
        final_message += "\n\n".join(news_items)
        final_message += "\n\n"

    return final_message

# =========================
# (비동기) 텔레그램 메시지 전송
# =========================
async def send_telegram_message_async(text):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(telegram_url, data=payload, timeout=10) as response:
                response.raise_for_status()
                print("텔레그램 전송 성공")
        except Exception as e:
            print("텔레그램 전송 실패:", e)

# =========================
# 메인 실행
# =========================
async def main():
    print("뉴스 수집 시작...")
    message = await make_news_message_async()
    
    print("텔레그램 전송 중...")
    await send_telegram_message_async(message)
    print("모든 작업 완료!")

if __name__ == "__main__":
    # 비동기 이벤트 루프 실행
    asyncio.run(main())import os
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from html import escape

# =========================
# 환경변수 로드
# =========================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# =========================
# RSS 목록
# =========================
RSS_FEEDS = {
    "한국경제": "https://www.hankyung.com/feed/economy",
    "매일경제": "https://www.mk.co.kr/rss/30100041/",
    "연합뉴스": "https://www.yna.co.kr/rss/economy.xml"
}

# =========================
# RSS 뉴스 가져오기
# =========================
def fetch_news(rss_url, limit=10):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64)"
        )
    }

    try:

        response = requests.get(
            rss_url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

    except requests.RequestException as e:
        return [f"뉴스 요청 실패: {e}"]

    soup = BeautifulSoup(response.content, "xml")

    items = soup.find_all("item", limit=limit)

    news_list = []

    for idx, item in enumerate(items, start=1):

        try:

            title = item.title.text.strip()
            link = item.link.text.strip()

            news_text = (
                f"{idx}. 📰 {escape(title)}\n"
                f"🔗 {link}"
            )

            news_list.append(news_text)

        except Exception:
            continue

    if not news_list:
        return ["뉴스 데이터 없음"]

    return news_list

# =========================
# 전체 뉴스 메시지 생성
# =========================
def make_news_message():

    final_message = "<b>📊 오늘의 경제 뉴스 브리핑</b>\n\n"

    for company, rss_url in RSS_FEEDS.items():

        final_message += f"<b>🗞 {company}</b>\n\n"

        news_items = fetch_news(rss_url, limit=10)

        final_message += "\n\n".join(news_items)

        final_message += "\n\n"

    return final_message

# =========================
# 텔레그램 메시지 전송
# =========================
def send_telegram_message(text):

    telegram_url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:

        response = requests.post(
            telegram_url,
            data=payload,
            timeout=10
        )

        response.raise_for_status()

        print("텔레그램 전송 성공")

    except requests.RequestException as e:
        print("텔레그램 전송 실패:", e)

# =========================
# 메인 실행
# =========================
if __name__ == "__main__":

    message = make_news_message()

    send_telegram_message(message)
