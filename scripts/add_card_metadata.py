"""
107개 삼성카드에 색상(primary/secondary) 및 특징 문구(tagline) 자동 생성
"""
import json
import os

# 카드 이름별 색상 및 tagline 매핑 (특수 카드)
CARD_METADATA = {
    # taptap 시리즈 - 핑크 계열
    "삼성카드 taptap O": {"colors": ["#e91e63", "#f48fb1"], "tagline": "다양한 혜택을 한 장에!"},
    "삼성카드 taptap S": {"colors": ["#e91e63", "#f48fb1"], "tagline": "스마트한 일상의 시작"},
    "taptap DIGITAL": {"colors": ["#7c4dff", "#b388ff"], "tagline": "디지털 라이프 필수템"},
    "taptap DRIVE": {"colors": ["#0277bd", "#4fc3f7"], "tagline": "드라이버를 위한 스마트 혜택"},
    "taptap SHOPPING": {"colors": ["#ff5722", "#ff8a65"], "tagline": "쇼핑의 즐거움을 더하다"},
    "삼성페이 삼성카드 taptap": {"colors": ["#e91e63", "#f48fb1"], "tagline": "삼성페이와 함께하는 혜택"},
    "네이버페이 taptap": {"colors": ["#03c75a", "#00e676"], "tagline": "네이버와 함께하는 스마트 페이"},
    "CU·배달의민족 삼성카드 taptap": {"colors": ["#3bb7c8", "#81d4fa"], "tagline": "편의점과 배달의 꿀조합"},
    
    # iD 시리즈 - 삼성 블루 계열
    "삼성 iD SELECT ALL 카드": {"colors": ["#1428a0", "#2d4de0"], "tagline": "선택이 곧 혜택"},
    "삼성 iD SELECT ON 카드": {"colors": ["#1428a0", "#2d4de0"], "tagline": "나만의 혜택을 선택하다"},
    "삼성 iD SIMPLE 카드": {"colors": ["#333333", "#666666"], "tagline": "심플하게, 알차게"},
    "삼성 iD ENERGY 카드": {"colors": ["#f57c00", "#ffb74d"], "tagline": "에너지 넘치는 혜택"},
    "삼성 iD ON 카드": {"colors": ["#5c6bc0", "#9fa8da"], "tagline": "언제나 켜져있는 혜택"},
    "삼성 iD PLUG-IN 카드": {"colors": ["#26a69a", "#80cbc4"], "tagline": "일상에 혜택을 플러그인"},
    "삼성 iD ALL 카드": {"colors": ["#1428a0", "#2d4de0"], "tagline": "모든 혜택을 한 장에"},
    "삼성 iD GLOBAL 카드": {"colors": ["#1e3a5f", "#3d5a80"], "tagline": "해외에서 빛나는 혜택"},
    "삼성 iD VITA 카드": {"colors": ["#ec407a", "#f48fb1"], "tagline": "건강한 라이프 파트너"},
    "삼성 iD PET 카드": {"colors": ["#8d6e63", "#bcaaa4"], "tagline": "반려동물과 함께하는 혜택"},
    "삼성 iD ONE 카드": {"colors": ["#1428a0", "#2d4de0"], "tagline": "하나로 충분한 혜택"},
    "삼성 iD STATION 카드 (GS칼텍스)": {"colors": ["#ff6f00", "#ffab40"], "tagline": "주유할 때마다 스마트하게"},
    "삼성 iD STATION 카드 (SK에너지)": {"colors": ["#d32f2f", "#ef5350"], "tagline": "SK와 함께하는 주유 혜택"},
    "삼성 iD NOMAD 카드": {"colors": ["#00897b", "#4db6ac"], "tagline": "자유로운 라이프를 위한 카드"},
    
    # 모니모 시리즈 - 하늘색 계열
    "모니모카드": {"colors": ["#0096d6", "#00c3ff"], "tagline": "모이는 금융 커지는 혜택"},
    "모니모A 카드": {"colors": ["#00bcd4", "#4dd0e1"], "tagline": "모니모로 시작하는 금융"},
    
    # 프리미엄 카드 - 다크 계열
    "THE iD. PLATINUM (포인트)": {"colors": ["#424242", "#757575"], "tagline": "프리미엄 라이프의 시작"},
    "THE iD. 1st": {"colors": ["#212121", "#424242"], "tagline": "최고를 위한 선택"},
    "THE 1 (스카이패스)": {"colors": ["#1a237e", "#3949ab"], "tagline": "여행의 품격을 높이다"},
    "BIZ THE iD. PLATINUM (포인트)": {"colors": ["#37474f", "#607d8b"], "tagline": "비즈니스 프리미엄 파트너"},
    
    # 아멕스 카드
    "아메리칸 엑스프레스 블루": {"colors": ["#006fcf", "#00a1e4"], "tagline": "글로벌 프리미엄 혜택"},
    "아메리칸 엑스프레스 리저브": {"colors": ["#1a1a1a", "#4a4a4a"], "tagline": "럭셔리 라이프의 정수"},
    
    # 마일리지 카드
    "삼성카드 & MILEAGE PLATINUM (스카이패스)": {"colors": ["#0d47a1", "#1976d2"], "tagline": "하늘을 향한 마일리지"},
    "삼성카드 스페셜마일리지 (스카이패스)": {"colors": ["#1565c0", "#42a5f5"], "tagline": "특별한 마일리지 적립"},
    
    # 제휴 카드 - 신세계/이마트
    "신세계이마트 삼성카드 7": {"colors": ["#fbc02d", "#fff176"], "tagline": "장보기가 즐거워지는 혜택"},
    "트레이더스 신세계 삼성카드": {"colors": ["#f9a825", "#ffee58"], "tagline": "대용량 쇼핑의 스마트 파트너"},
    "이마트신세계 삼성카드": {"colors": ["#fdd835", "#fff59d"], "tagline": "쇼핑 라이프의 필수 카드"},
    
    # 제휴 카드 - 기타
    "하나투어 삼성카드": {"colors": ["#0288d1", "#4fc3f7"], "tagline": "여행의 시작과 끝"},
    "롯데월드카드 (삼성카드)": {"colors": ["#e53935", "#ef5350"], "tagline": "놀이동산이 즐거워지는 카드"},
    "에버랜드 삼성카드": {"colors": ["#43a047", "#81c784"], "tagline": "에버랜드와 함께하는 즐거움"},
    "알라딘 만권당 삼성카드": {"colors": ["#5d4037", "#8d6e63"], "tagline": "책과 함께하는 지적 라이프"},
    "다이소 삼성카드": {"colors": ["#ff7043", "#ffab91"], "tagline": "알뜰 쇼핑의 필수템"},
    "KTX 삼성카드": {"colors": ["#ff5722", "#ff8a65"], "tagline": "빠른 이동, 빠른 혜택"},
    
    # 교통 카드
    "K-패스 삼성카드": {"colors": ["#00acc1", "#4dd0e1"], "tagline": "대중교통 필수 동반자"},
    "기후동행 삼성카드": {"colors": ["#66bb6a", "#a5d6a7"], "tagline": "친환경 교통의 시작"},
    
    # 교육 카드
    "단비교육 삼성카드": {"colors": ["#7cb342", "#aed581"], "tagline": "아이 교육의 든든한 파트너"},
    "엠베스트 엘리하이 삼성카드": {"colors": ["#ff9800", "#ffcc80"], "tagline": "자녀 학습을 위한 스마트 선택"},
    
    # BIZ 카드
    "삼성카드 BIZ LEADERS": {"colors": ["#37474f", "#78909c"], "tagline": "비즈니스 리더를 위한 카드"},
    "삼성 BIZ iD BENEFIT 카드": {"colors": ["#455a64", "#90a4ae"], "tagline": "사업자를 위한 맞춤 혜택"},
    
    # 주유/자동차 카드
    "MY S-OIL 삼성카드": {"colors": ["#ffc107", "#ffe082"], "tagline": "주유가 즐거워지는 카드"},
    "삼성카앤모아카드": {"colors": ["#546e7a", "#90a4ae"], "tagline": "차량 생활의 모든 것"},
    
    # 복지 카드
    "국민행복 삼성카드 V2": {"colors": ["#4caf50", "#81c784"], "tagline": "국민과 함께하는 행복 혜택"},
}

# 기본 색상 (삼성 브랜드 블루)
DEFAULT_COLORS = ["#1428a0", "#2d4de0"]

# 키워드 기반 색상 매핑
KEYWORD_COLORS = {
    "주유": ["#ff6f00", "#ffab40"],
    "DRIVE": ["#0277bd", "#4fc3f7"],
    "교통": ["#00acc1", "#4dd0e1"],
    "쇼핑": ["#ff5722", "#ff8a65"],
    "커피": ["#6d4c41", "#a1887f"],
    "스트리밍": ["#7c4dff", "#b388ff"],
    "DIGITAL": ["#7c4dff", "#b388ff"],
    "항공": ["#0d47a1", "#1976d2"],
    "마일리지": ["#1565c0", "#42a5f5"],
    "PLATINUM": ["#424242", "#757575"],
    "GLOBAL": ["#1e3a5f", "#3d5a80"],
    "BIZ": ["#37474f", "#78909c"],
    "PET": ["#8d6e63", "#bcaaa4"],
    "VITA": ["#ec407a", "#f48fb1"],
}

# 키워드 기반 tagline 매핑
KEYWORD_TAGLINES = {
    "SELECT": "나에게 맞는 혜택 선택",
    "주유": "주유할 때마다 스마트하게",
    "DRIVE": "드라이버를 위한 스마트 혜택",
    "교통": "이동이 즐거워지는 혜택",
    "쇼핑": "쇼핑의 즐거움을 더하다",
    "커피": "커피 한 잔의 여유와 함께",
    "스트리밍": "디지털 라이프의 필수템",
    "DIGITAL": "디지털 라이프를 위한 선택",
    "항공": "하늘을 향한 혜택",
    "마일리지": "마일리지가 모이는 카드",
    "MILEAGE": "마일리지가 모이는 카드",
    "PLATINUM": "프리미엄 라이프를 위한 선택",
    "GLOBAL": "해외에서 빛나는 혜택",
    "BIZ": "비즈니스를 위한 스마트 파트너",
    "PET": "반려동물과 함께하는 혜택",
    "VITA": "건강한 라이프 파트너",
    "ENERGY": "에너지 넘치는 일상",
    "SIMPLE": "심플하게, 알차게",
    "모니모": "모이는 금융, 커지는 혜택",
    "taptap": "스마트한 일상의 시작",
    "신세계": "쇼핑이 즐거워지는 카드",
    "이마트": "장보기의 필수 파트너",
    "롯데": "즐거움이 가득한 카드",
    "에버랜드": "놀이가 즐거워지는 카드",
    "알라딘": "책과 함께하는 라이프",
    "다이소": "알뜰 쇼핑의 필수템",
    "KTX": "빠른 이동, 빠른 혜택",
    "교육": "자녀 교육의 든든한 파트너",
    "국민행복": "국민과 함께하는 행복",
}

def get_card_metadata(card_name, benefits):
    """카드 이름과 혜택을 분석하여 색상과 tagline 반환"""
    
    # 1. 미리 정의된 메타데이터 확인
    if card_name in CARD_METADATA:
        meta = CARD_METADATA[card_name]
        return {
            "primary_color": meta["colors"][0],
            "secondary_color": meta["colors"][1],
            "tagline": meta["tagline"]
        }
    
    # 2. 키워드 기반 색상 결정
    colors = DEFAULT_COLORS.copy()
    for keyword, color_pair in KEYWORD_COLORS.items():
        if keyword.upper() in card_name.upper():
            colors = color_pair
            break
    
    # 3. 키워드 기반 tagline 결정
    tagline = "일상에 혜택을 더하다"  # 기본값
    for keyword, tag in KEYWORD_TAGLINES.items():
        if keyword.upper() in card_name.upper():
            tagline = tag
            break
    
    # 4. 혜택 기반 tagline 개선 (혜택 분석)
    if benefits:
        categories = set()
        for benefit in benefits:
            if benefit.get("category"):
                categories.add(benefit["category"])
        
        if len(categories) >= 4:
            tagline = "다양한 혜택을 한 장에!"
        elif "커피" in categories and "쇼핑" in categories:
            tagline = "카페와 쇼핑의 스마트 혜택"
        elif "주유" in categories:
            tagline = "주유가 즐거워지는 카드"
        elif "항공" in categories:
            tagline = "여행을 위한 마일리지 카드"
    
    return {
        "primary_color": colors[0],
        "secondary_color": colors[1],
        "tagline": tagline
    }

def main():
    # JSON 파일 읽기
    json_path = r"c:\Users\MADUP\Documents\seokmin\website_samsungcard_recommend\data\samsung_cards.json"
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 각 카드에 메타데이터 추가
    for card in data["cards"]:
        card_name = card["name"]
        benefits = card.get("benefits", [])
        
        metadata = get_card_metadata(card_name, benefits)
        
        card["primary_color"] = metadata["primary_color"]
        card["secondary_color"] = metadata["secondary_color"]
        card["tagline"] = metadata["tagline"]
    
    # JSON 파일 저장
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"완료: {len(data['cards'])}개 카드에 메타데이터 추가됨")
    
    # 결과 샘플 출력
    print("\n샘플 결과:")
    for i, card in enumerate(data["cards"][:5]):
        print(f"  {i+1}. {card['name']}")
        print(f"     색상: {card['primary_color']} -> {card['secondary_color']}")
        print(f"     태그라인: {card['tagline']}")

if __name__ == "__main__":
    main()
