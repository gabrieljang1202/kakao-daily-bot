import requests
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup

KAKAO_REST_API_KEY = "6e9c0f38c0007caa3874adadf29c6f67"
KAKAO_CLIENT_SECRET = os.environ["KAKAO_CLIENT_SECRET"]
KAKAO_REFRESH_TOKEN = os.environ["KAKAO_REFRESH_TOKEN"]

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

def get_bestsellers():
    url = "https://www.kyobobook.co.kr/bestSellerNew/bestseller.laf?mallGb=KOR&orderClick=LAG"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    books = []
    items = soup.select("ul.list_type01 li")[:5]
    for i, item in enumerate(items, 1):
        title_el = item.select_one(".title")
        author_el = item.select_one(".author")
        title = title_el.get_text(strip=True) if title_el else "제목 없음"
        author = author_el.get_text(strip=True).split("/")[0].strip() if author_el else ""
        books.append(f"{i}위. {title}" + (f" - {author}" if author else ""))

    return "\n".join(books) if books else None

def get_bestsellers_yes24():
    url = "https://www.yes24.com/Product/Category/BestSeller?categoryNumber=001&pageNumber=1&pageSize=5"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    books = []
    items = soup.select(".gd_name")[:5]
    for i, item in enumerate(items, 1):
        title = item.get_text(strip=True)
        books.append(f"{i}위. {title}")

    return "\n".join(books) if books else None

def send_kakao_message(access_token, message):
    template = {
        "object_type": "text",
        "text": message,
        "link": {
            "web_url": "https://www.kyobobook.co.kr",
            "mobile_web_url": "https://www.kyobobook.co.kr"
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

    print("베스트셀러 가져오는 중...")
    books = get_bestsellers()
    if not books:
        print("교보문고 실패, YES24 시도...")
        books = get_bestsellers_yes24()
    if not books:
        books = "오늘은 도서 정보를 가져오지 못했어요 😅"

    message = f"📚 {today} 베스트셀러 TOP 5\n\n{books}\n\n재혁님, 오늘도 책 한 페이지 어때요? 📖"
    print(f"전송할 메시지:\n{message}")

    result = send_kakao_message(access_token, message)
    print(f"전송 결과: {result}")
