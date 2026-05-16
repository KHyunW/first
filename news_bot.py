import requests
from bs4 import BeautifulSoup

# 1. 텔레그램 봇 정보 설정 (발급받은 정보로 수정하세요)
BOT_TOKEN = '8683553129:AAExK4UB-8fq45WexyzW5h2SVCv056qLbOo'
CHAT_ID = '6123388676'

def get_economic_news():
    # 구글 뉴스 RSS (한국어, '경제' 키워드 검색 결과)
    url = "https://news.google.com/rss/search?q=경제&hl=ko&gl=KR&ceid=KR:ko"
    response = requests.get(url)
    
    # XML 데이터 파싱
    soup = BeautifulSoup(response.content, 'xml')
    
    # 최신 뉴스 5개만 가져오기
    items = soup.find_all('item', limit=5)
    
    news_list = []
    for item in items:
        title = item.title.text
        link = item.link.text
        news_list.append(f"📰 {title}\n🔗 {link}\n")
        
    return "\n".join(news_list)

def send_telegram_message(text):
    # 텔레그램 API를 이용해 메시지 전송
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'HTML' # 굵은 글씨 등 HTML 태그 적용을 위해
    }
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        print("메시지 전송 성공!")
    else:
        print("메시지 전송 실패:", response.text)

if __name__ == "__main__":
    # 보낼 메시지 구성
    message_text = "<b>[오늘의 아침 경제 뉴스]</b>\n\n" + get_economic_news()
    
    # 텔레그램으로 전송
    send_telegram_message(message_text)