"""
카테고리별 최고 혜택만 추출 (v2)
- 할인/적립 정확히 구분
- 마일리지 적립은 "마일리지 적립"으로 표시
- 이동통신 = 통신 카테고리
"""
import json
import re

def parse_discount_value(desc, detail, discount_obj):
    """할인 값을 숫자로 파싱 (비교용)"""
    if discount_obj and discount_obj.get('value'):
        return float(discount_obj['value'])
    
    text = desc + ' ' + (detail or '')
    percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
    if percent_match:
        return float(percent_match.group(1))
    
    won_match = re.search(r'([\d,]+)\s*원', text)
    if won_match:
        return int(won_match.group(1).replace(',', ''))
    
    # 마일리지
    mile_match = re.search(r'([\d,]+)\s*마일', text)
    if mile_match:
        return int(mile_match.group(1).replace(',', ''))
    
    return 0

def detect_category(desc, detail):
    """description에서 올바른 카테고리 추출"""
    text = (desc + ' ' + (detail or '')).lower()
    
    # 커피/카페 (먼저 체크)
    if any(k in text for k in ['스타벅스', '투썸', '이디야', '메가커피', '커피', '카페']):
        return '커피'
    
    # 스트리밍/OTT
    if any(k in text for k in ['넷플릭스', '유튜브', '디즈니', '티빙', '웨이브', 'ott', '디지털콘텐츠']):
        return '스트리밍'
    
    # 영화
    if any(k in text for k in ['cgv', '롯데시네마', '메가박스', '영화']):
        return '영화'
    
    # 배달
    if any(k in text for k in ['배달의민족', '배민', '쿠팡이츠', '요기요', '배달앱']):
        return '배달'
    
    # 통신 (이동통신 포함!)
    if any(k in text for k in ['통신', 'skt', 'kt', 'lg u+', '이동통신', '휴대폰', '인터넷요금']):
        return '통신'
    
    # 쇼핑
    if any(k in text for k in ['쿠팡', '네이버', 'ssg', 'g마켓', '옥션', '11번가', '온라인쇼핑', '쇼핑몰', '마트', '이마트', '롯데마트', '편의점']):
        return '쇼핑'
    
    # 주유
    if any(k in text for k in ['주유', 'sk에너지', 'gs칼텍스', 's-oil', '오일뱅크']):
        return '주유'
    
    # 교통
    if any(k in text for k in ['대중교통', '버스', '지하철', '택시', 'ktx', '고속버스', '철도']):
        return '교통'
    
    # 항공/마일리지
    if any(k in text for k in ['마일리지', '스카이패스', '항공', '라운지', '아시아나', '대한항공', '마일']):
        return '항공'
    
    # 해외
    if any(k in text for k in ['해외']):
        return '해외'
    
    return None

def get_best_target(desc, detail, category):
    """가장 구체적인 대상 추출"""
    text = (desc + ' ' + (detail or '')).lower()
    
    # 구체적인 브랜드/서비스 우선
    brands = [
        ('스타벅스', '스타벅스'), ('투썸', '투썸'), ('이디야', '이디야'), ('메가커피', '메가커피'),
        ('넷플릭스', '넷플릭스'), ('유튜브', '유튜브 프리미엄'), ('디즈니', '디즈니+'), ('티빙', '티빙'),
        ('cgv', 'CGV'), ('롯데시네마', '롯데시네마'), ('메가박스', '메가박스'),
        ('배달의민족', '배달의민족'), ('배민', '배달의민족'), ('쿠팡이츠', '쿠팡이츠'), ('요기요', '요기요'),
        ('쿠팡', '쿠팡'), ('네이버', '네이버쇼핑'), ('ssg', 'SSG.COM'), ('11번가', '11번가'),
        ('sk에너지', 'SK주유'), ('gs칼텍스', 'GS주유'), ('s-oil', 'S-OIL'),
        ('스카이패스', '스카이패스'),
    ]
    
    for keyword, brand in brands:
        if keyword in text:
            return brand
    
    # 카테고리별 기본 target 반환 (카테고리가 확실하면 해당 target 사용)
    if category == '통신':
        return '통신비'
    if category == '주유':
        return '주유'
    if category == '해외':
        return '해외'
    
    # 일반적인 대상 (description에서 추출)
    if '대중교통' in text or ('버스' in text and '지하철' in text):
        return '대중교통'
    if '택시' in text:
        return '택시'
    if '온라인쇼핑' in text or '온라인' in text:
        return '온라인쇼핑'
    if '편의점' in text:
        return '편의점'
    if '마일리지' in text or '마일' in text:
        return '마일리지'
    if '라운지' in text:
        return '공항라운지'
    
    # 카테고리 기반 기본값
    defaults = {
        '커피': '커피전문점',
        '교통': '대중교통',
        '쇼핑': '온라인쇼핑',
        '통신': '통신비',
        '주유': '주유',
        '영화': '영화관',
        '항공': '마일리지',
    }
    return defaults.get(category, category)

def format_discount(discount_obj, desc, detail, target, category):
    """할인 값을 문자열로 포맷"""
    text = desc + ' ' + (detail or '')
    
    # 항공/마일리지 카드 처리 (항공 카테고리이면서 스카이패스/마일리지 키워드가 있을 때만)
    is_mileage_card = (category == '항공') and ('스카이패스' in target or '마일리지' in text.lower())
    if is_mileage_card:
        # description에서 마일리지 숫자 추출
        mile_patterns = [
            r'(\d+)\s*마일',
            r'최대\s*(\d+)\s*마일',
            rf'{re.escape(target)}.*?(\d+)\s*마일',
        ]
        for pattern in mile_patterns:
            mile_match = re.search(pattern, text, re.IGNORECASE)
            if mile_match:
                return f"{mile_match.group(1)}마일 적립"
        # 숫자 없으면 기본값
        return "마일리지 적립"
    
    # 적립 vs 할인 판단
    if '적립' in text and '할인' not in text:
        discount_type = '적립'
    else:
        discount_type = '할인'
    
    # 타겟 브랜드와 연관된 할인율 우선 추출
    if target and '스카이패스' not in target:
        brand_pattern = rf'{re.escape(target)}[^0-9]*(\d+(?:\.\d+)?)\s*%'
        brand_match = re.search(brand_pattern, text, re.IGNORECASE)
        if brand_match:
            val = float(brand_match.group(1))
            if val == int(val):
                return f"{int(val)}% {discount_type}"
            return f"{val}% {discount_type}"
    
    # discount 객체에서 추출 (마일리지 카드가 아닌 경우만)
    if discount_obj and discount_obj.get('value') and discount_obj.get('value') > 1:
        val = discount_obj['value']
        if discount_obj.get('type') == 'percent':
            if val == int(val):
                return f"{int(val)}% {discount_type}"
            return f"{val}% {discount_type}"
        elif discount_obj.get('type') == 'won':
            val = int(val)
            if val >= 10000:
                return f"{val//10000}만원 {discount_type}"
            return f"{val:,}원 {discount_type}"
    
    # description + detail에서 추출
    percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
    if percent_match:
        val = float(percent_match.group(1))
        if val == int(val):
            return f"{int(val)}% {discount_type}"
        return f"{val}% {discount_type}"
    
    won_match = re.search(r'([\d,]+)\s*원', text)
    if won_match:
        val = int(won_match.group(1).replace(',', ''))
        if val >= 10000:
            return f"{val//10000}만원 {discount_type}"
        if val > 1:  # 1원 같은 잘못된 값 제외
            return f"{val:,}원 {discount_type}"
    
    if '무료' in text:
        return '무료 제공'
    
    if '할인' in text or '적립' in text:
        return '혜택'
    
    return None

def process_card(card):
    """카드의 혜택을 카테고리별로 합치고 최고 혜택만 추출"""
    benefits = card.get('benefits', [])
    category_best = {}
    
    for benefit in benefits:
        desc = benefit.get('description', '') or ''
        detail = benefit.get('detail', '') or ''
        title = benefit.get('title', '') or ''
        discount_obj = benefit.get('discount', {}) or {}
        
        # 유의사항 제외
        if title == '유의사항' or '유의사항' in desc:
            continue
        if '선택 옵션에 따른' in desc and not discount_obj.get('value'):
            continue
        
        # 카테고리 추출
        category = detect_category(desc, detail)
        if not category:
            continue
        
        # 대상 추출
        target = get_best_target(desc, detail, category)
        if not target:
            continue
        
        # 할인 값 추출
        discount_str = format_discount(discount_obj, desc, detail, target, category)
        if not discount_str:
            continue
        
        # 할인 값 비교용
        value = parse_discount_value(desc, detail, discount_obj)
        
        # 기존 것과 비교해서 더 좋으면 교체
        if category not in category_best or value > category_best[category]['value']:
            category_best[category] = {
                'target': target,
                'discount_str': discount_str,
                'value': value
            }
    
    # 최종 display_benefits 생성
    display_benefits = []
    for category, data in category_best.items():
        summary = f"{data['target']} {data['discount_str']}"
        display_benefits.append({
            'category': category,
            'summary': summary
        })
    
    return display_benefits

def main():
    json_path = r"c:\Users\MADUP\Documents\seokmin\website_samsungcard_recommend\data\samsung_cards.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for card in data['cards']:
        card['display_benefits'] = process_card(card)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"완료: {len(data['cards'])}개 카드")
    
    # 샘플 확인
    samples = ['삼성카드 taptap O', '삼성 iD SELECT ALL 카드', '모니모카드', 'THE 1 (스카이패스)']
    for card in data['cards']:
        if card['name'] in samples:
            print(f"\n=== {card['name']} ===")
            for b in card.get('display_benefits', []):
                print(f"  [{b['category']}] {b['summary']}")

if __name__ == "__main__":
    main()
