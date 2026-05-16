import os
import requests

from bs4 import BeautifulSoup
from collections import defaultdict
from dotenv import load_dotenv
from html import escape

# =========================
# 환경변수 로드
# =========================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# =========================
# 환경변수 검증
# =========================
if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN 또는 CHAT_ID가 없습니다.")

# =========================
# 뉴스 키워드
# =========================
STOCK_KEYWORDS = {
    "삼성": "삼성전자",
    "반도체": "삼성전자",
    "HBM": "SK하이닉스",
    "메모리": "SK하이닉스",
    "전기차": "현대차",
    "자동차": "기아",
    "배터리": "LG에너지솔루션",
    "AI": "NAVER",
    "플랫폼": "카카오",
    "바이오": "셀트리온",
    "엔비디아": "SK하이닉스"
}

# =========================
# 뉴스 수집
# =========================
def get_news():

    url = (
        "https://news.google.com/rss/search"
        "?q=경제&hl=ko&gl=KR&ceid=KR:ko"
    )

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

    except requests.RequestException as e:
        print("뉴스 요청 실패:", e)
        return []

    soup = BeautifulSoup(response.content, "xml")

    items = soup.find_all("item", limit=10)

    news_data = []

    for item in items:

        try:

            title = item.title.text.strip()
            link = item.link.text.strip()

            news_data.append({
                "title": title,
                "link": link
            })

        except Exception:
            continue

    return news_data

# =========================
# 종목 분석
# =========================
def analyze_stocks(news_data):

    stock_scores = defaultdict(int)

    for news in news_data:

        title = news["title"]

        for keyword, stock in STOCK_KEYWORDS.items():

            if keyword.lower() in title.lower():
                stock_scores[stock] += 1

    return stock_scores

# =========================
# 추천 종목 생성
# =========================
def generate_recommendation(stock_scores):

    if not stock_scores:
        return "추천 종목 없음"

    sorted_stocks = sorted(
        stock_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    result = "📈 오늘의 추천 종목\n\n"

    for idx, (stock, score) in enumerate(sorted_stocks[:3], start=1):

        result += (
            f"{idx}. {escape(stock)}\n"
            f"🔥 언급 점수: {score}\n\n"
        )

    return result

# =========================
# 뉴스 메시지 생성
# =========================
def make_news_message(news_data):

    result = "📰 오늘의 경제 뉴스\n\n"

    for idx, news in enumerate(news_data[:5], start=1):

        result += (
            f"{idx}. {escape(news['title'])}\n"
            f"🔗 {news['link']}\n\n"
        )

    return result

# =========================
# 텔레그램 전송
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
def main():

    news_data = get_news()

    if not news_data:
        send_telegram_message("뉴스 데이터를 가져오지 못했습니다.")
        return

    stock_scores = analyze_stocks(news_data)

    recommendation = generate_recommendation(stock_scores)

    news_message = make_news_message(news_data)

    final_message = (
        "<b>📊 AI 경제 뉴스 브리핑</b>\n\n"
        + news_message
        + "\n"
        + recommendation
    )

    send_telegram_message(final_message)

# =========================
# 실행
# =========================
if __name__ == "__main__":
    main()
