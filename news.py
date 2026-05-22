import requests
import os
import json
from datetime import datetime

KAKAO_REST_API_KEY = "6e9c0f38c0007caa3874adadf29c6f67"
KAKAO_CLIENT_SECRET = os.environ["KAKAO_CLIENT_SECRET"]
KAKAO_REFRESH_TOKEN = os.environ["KAKAO_REFRESH_TOKEN"]
MY_NAME = os.environ["MY_NAME"]

def refresh_access_token():
    response = requests.post("https://kauth.kakao.com/oauth/token", data={
        "grant_type": "refresh_token",
        "client_id": KAKAO_REST_API_KEY,
        "refresh_token": KAKAO_REFRESH_TOKEN,
        "client_secret": KAKAO_CLIENT_SECRET
    })
    data = response.json()
    if "access_token" not in data:
        raise Exception(f"토큰 갱신 실패: {data}")
    return data["access_token"]

def get_news():
    import feedparser
    feed = feedparser.parse("https://feeds.bbci.co.uk/korean/rss.xml")
    if not feed.entries:
        feed = feedparser.parse("https://www.yonhapnewstv.co.kr/browse/feed/")
    news_list = []
    for entry in feed.entries[:5]:
        title = entry.title.strip()
        news_list.append(f"• {title}")
    return "\n".join(news_list)

def send_kakao_message(access_token, message):
    template = {
        "object_type": "text",
        "text": message,
        "link": {
            "web_url": "https://news.naver.com",
            "mobile_web_url": "https://news.naver.com"
        }
    }
    response = requests.post(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        headers={"Authorization": f"Bearer {access_token}"},
        data={"template_object": json.dumps(template)}
    )
    return response.json()

if __name__ == "__main__":
    today = datetime.now().strftime("%Y년 %m월 %d일")
    print("토큰 갱신 중...")
    access_token = refresh_access_token()

    print("뉴스 가져오는 중...")
    news = get_news()

    message = f"📰 {MY_NAME}님을 위한 {today} 주요 뉴스\n\n{news}"
    print(f"전송할 메시지:\n{message}")

    result = send_kakao_message(access_token, message)
    print(f"전송 결과: {result}")
