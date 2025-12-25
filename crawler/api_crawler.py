"""
카드고릴라 삼성카드 API 크롤러
- Playwright 없이 requests만 사용
- 리스트 API + 상세 API 조합으로 전체 혜택 수집
"""

import json
import time
import requests
from pathlib import Path
from html import unescape
import re

# 설정
API_BASE = "https://api.card-gorilla.com:8080/v1"
LIST_API = f"{API_BASE}/cards"
DETAIL_API = f"{API_BASE}/cards"  # /cards/{card_id}
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "samsung_cards.json"
REQUEST_DELAY = 0.5  # API 호출 간 딜레이 (초)
TIMEOUT = 10  # 개별 요청 타임아웃

# 공통 헤더
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.card-gorilla.com/"
}


def strip_html(text: str) -> str:
    """HTML 태그 제거 및 텍스트 정리"""
    if not text:
        return ""
    # HTML 엔티티 디코딩
    text = unescape(text)
    # 태그 제거
    text = re.sub(r'<[^>]+>', ' ', text)
    # 연속 공백 정리
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_number(text: str) -> int | None:
    """텍스트에서 숫자 추출"""
    if not text:
        return None
    match = re.search(r'[\d,]+', text.replace(',', ''))
    return int(match.group().replace(',', '')) if match else None


def get_card_list() -> list[int]:
    """삼성카드 전체 리스트 조회 (corp=1)"""
    print("[1/2] 카드 리스트 조회 중...")
    
    params = {
        "corp": 1,  # 삼성카드
        "perPage": 200,  # 충분히 큰 값
        "is_discon": 0,  # 활성 카드만
        "p": 1
    }
    
    try:
        resp = requests.get(LIST_API, params=params, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        
        card_ids = [card["cid"] for card in data.get("data", [])]
        total = data.get("total", len(card_ids))
        
        print(f"  - 총 {total}개 카드 발견, {len(card_ids)}개 ID 수집")
        return card_ids
        
    except Exception as e:
        print(f"[ERROR] 리스트 조회 실패: {e}")
        return []


def get_card_detail(card_id: int) -> dict | None:
    """개별 카드 상세 정보 조회"""
    try:
        url = f"{DETAIL_API}/{card_id}"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  [WARN] 카드 {card_id} 조회 실패: {e}")
        return None


def parse_card_data(raw: dict) -> dict:
    """API 응답을 정리된 형식으로 변환"""
    card = {
        "id": str(raw.get("cid", "")),
        "name": raw.get("name", "Unknown"),
        "detail_url": f"https://www.card-gorilla.com/card/detail/{raw.get('cid', '')}",
        "image_url": None,
        "annual_fee": None,
        "min_spending": None,
        "benefits": []
    }
    
    # 이미지 URL
    card_img = raw.get("card_img")
    if card_img and isinstance(card_img, dict):
        card["image_url"] = card_img.get("url")
    elif card_img and isinstance(card_img, str):
        card["image_url"] = card_img
    
    # 연회비
    annual_fee_basic = raw.get("annual_fee_basic", "")
    annual_fee_detail = raw.get("annual_fee_detail", "")
    if annual_fee_basic or annual_fee_detail:
        card["annual_fee"] = {
            "domestic": extract_number(annual_fee_basic),
            "raw": annual_fee_basic or annual_fee_detail
        }
    
    # 전월 실적
    pre_month = raw.get("pre_month_money")
    if pre_month:
        card["min_spending"] = int(pre_month) if isinstance(pre_month, (int, float)) else extract_number(str(pre_month))
    
    # 혜택 정보 파싱
    key_benefits = raw.get("key_benefit", [])
    
    # 카테고리 키워드 매핑
    category_keywords = {
        "커피": ["스타벅스", "커피", "카페", "투썸", "이디야", "메가커피"],
        "교통": ["교통", "버스", "지하철", "택시", "대중교통"],
        "주유": ["주유", "SK", "GS", "S-OIL", "현대오일뱅크", "정유"],
        "쇼핑": ["쇼핑", "백화점", "마트", "이마트", "홈플러스", "쿠팡", "SSG", "온라인몰"],
        "편의점": ["편의점", "CU", "GS25", "세븐일레븐", "이마트24"],
        "통신": ["통신", "SKT", "KT", "LG U+", "휴대폰", "이동통신"],
        "영화": ["영화", "CGV", "메가박스", "롯데시네마"],
        "음식": ["배달", "요기요", "배민", "음식", "식당", "음식점"],
        "항공": ["항공", "마일리지", "대한항공", "아시아나", "스카이패스"],
        "스트리밍": ["넷플릭스", "유튜브", "웨이브", "왓챠", "디즈니", "OTT"],
    }
    
    for benefit in key_benefits:
        title = benefit.get("title", "")
        comment = benefit.get("comment", "")
        info_html = benefit.get("info", "")
        info_text = strip_html(info_html)
        
        # 전체 텍스트
        full_text = f"{title} {comment} {info_text}"
        
        # 카테고리 추정
        category = None
        for cat, keywords in category_keywords.items():
            if any(kw in full_text for kw in keywords):
                category = cat
                break
        
        # 할인 정보 파싱
        discount = {"type": None, "value": None, "raw": comment}
        if '%' in comment:
            discount["type"] = "percent"
            match = re.search(r'(\d+(?:\.\d+)?)\s*%', comment)
            if match:
                discount["value"] = float(match.group(1))
        elif '원' in comment:
            discount["type"] = "won"
            discount["value"] = extract_number(comment)
        
        # 선택형 여부 확인
        is_select = "[SELECT" in comment or "택 1" in comment or "선택" in title
        
        card["benefits"].append({
            "category": category,
            "title": title,
            "description": comment[:300] if comment else title,
            "detail": info_text[:500] if info_text else None,
            "discount": discount,
            "is_select_option": is_select
        })
    
    return card


def main():
    """메인 크롤링 함수"""
    start_time = time.time()
    print("=" * 50)
    print("삼성카드 API 크롤러 시작")
    print("=" * 50)
    
    # 출력 디렉토리 생성
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. 카드 리스트 수집
    card_ids = get_card_list()
    if not card_ids:
        print("[ERROR] 카드 ID를 수집하지 못했습니다.")
        return
    
    # 2. 상세 정보 수집
    print(f"\n[2/2] 상세 정보 수집 중... (총 {len(card_ids)}개)")
    
    cards = []
    all_categories = set()
    
    for i, card_id in enumerate(card_ids):
        print(f"  - [{i+1}/{len(card_ids)}] 카드 ID: {card_id}", end="")
        
        raw_data = get_card_detail(card_id)
        if raw_data:
            card = parse_card_data(raw_data)
            cards.append(card)
            
            # 카테고리 수집
            for benefit in card.get("benefits", []):
                if benefit.get("category"):
                    all_categories.add(benefit["category"])
            
            print(f" - {card['name'][:20]}... ({len(card['benefits'])}개 혜택)")
        else:
            print(" - 실패")
        
        time.sleep(REQUEST_DELAY)
    
    # 3. 결과 저장
    result = {
        "crawled_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": "card-gorilla API",
        "total_cards": len(cards),
        "categories": sorted(list(all_categories)),
        "cards": cards
    }
    
    print(f"\n[저장 중] {OUTPUT_PATH}")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    elapsed = time.time() - start_time
    print(f"\n{'=' * 50}")
    print(f"[완료] 크롤링 성공!")
    print(f"  - 수집된 카드: {len(cards)}개")
    print(f"  - 카테고리: {len(all_categories)}개")
    print(f"  - 소요 시간: {elapsed:.1f}초")
    print(f"  - 저장 위치: {OUTPUT_PATH}")
    print("=" * 50)


if __name__ == "__main__":
    main()
