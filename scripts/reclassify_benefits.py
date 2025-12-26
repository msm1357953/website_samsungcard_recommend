"""
혜택 데이터 재분류 스크립트
- description에서 올바른 카테고리 추출
- 정확한 요약 생성
- 중복 제거
"""
import json
import re

def detect_category(desc, detail, original_cat):
    """description에서 올바른 카테고리 추출"""
    text = (desc + ' ' + (detail or '')).lower()
    
    # 커피/카페
    if any(k in text for k in ['스타벅스', '투썸', '이디야', '메가커피', '커피', '카페']):
        return '커피'
    
    # 스트리밍/OTT
    if any(k in text for k in ['넷플릭스', '유튜브', '디즈니', '티빙', '웨이브', 'ott', '디지털콘텐츠']):
        return '스트리밍'
    
    # 영화
    if any(k in text for k in ['cgv', '롯데시네마', '메가박스', '영화']):
        return '영화'
    
    # 쇼핑
    if any(k in text for k in ['쿠팡', '네이버', 'ssg', 'g마켓', '옥션', '11번가', '온라인쇼핑', '쇼핑몰', '마트', '이마트', '롯데마트', '편의점']):
        return '쇼핑'
    
    # 배달
    if any(k in text for k in ['배달의민족', '배민', '쿠팡이츠', '요기요', '배달앱']):
        return '배달'
    
    # 주유
    if any(k in text for k in ['주유', 'sk에너지', 'gs칼텍스', 's-oil', '오일뱅크']):
        return '주유'
    
    # 통신
    if any(k in text for k in ['통신', 'skt', 'kt', 'lg u+', '이동통신', '인터넷', '휴대폰']):
        return '통신'
    
    # 교통
    if any(k in text for k in ['대중교통', '버스', '지하철', '택시', 'ktx', '고속버스', '철도']):
        return '교통'
    
    # 항공/마일리지
    if any(k in text for k in ['마일리지', '스카이패스', '항공', '라운지', '아시아나', '대한항공']):
        return '항공'
    
    # 해외
    if any(k in text for k in ['해외']):
        return '해외'
    
    # 교육
    if any(k in text for k in ['학원', '교육', '인터넷강의', '학습']):
        return '교육'
    
    # 의료
    if any(k in text for k in ['병원', '의료', '약국', '동물병원']):
        return '의료'
    
    # 관리비
    if any(k in text for k in ['관리비', '아파트']):
        return '생활'
    
    # 기본: 원본 사용하거나 '혜택'
    return original_cat if original_cat else '혜택'

def extract_target(desc, category):
    """description에서 대상 추출"""
    text = desc.lower()
    
    if category == '커피':
        if '스타벅스' in text: return '스타벅스'
        if '투썸' in text: return '투썸'
        if '이디야' in text: return '이디야'
        if '메가커피' in text: return '메가커피'
        return '커피전문점'
    
    if category == '스트리밍':
        if '넷플릭스' in text: return '넷플릭스'
        if '유튜브' in text: return '유튜브'
        if '디즈니' in text: return '디즈니+'
        if '티빙' in text: return '티빙'
        return 'OTT'
    
    if category == '영화':
        if 'cgv' in text: return 'CGV'
        if '롯데시네마' in text: return '롯데시네마'
        if '메가박스' in text: return '메가박스'
        return '영화관'
    
    if category == '쇼핑':
        if '쿠팡' in text and '이츠' not in text: return '쿠팡'
        if '네이버' in text: return '네이버쇼핑'
        if 'ssg' in text: return 'SSG.COM'
        if '11번가' in text: return '11번가'
        if '이마트' in text: return '이마트'
        if '편의점' in text: return '편의점'
        return '온라인쇼핑'
    
    if category == '배달':
        if '배달의민족' in text or '배민' in text: return '배달의민족'
        if '쿠팡이츠' in text: return '쿠팡이츠'
        if '요기요' in text: return '요기요'
        return '배달앱'
    
    if category == '주유':
        return '주유'
    
    if category == '통신':
        return '통신비'
    
    if category == '교통':
        if '택시' in text: return '택시'
        if 'ktx' in text: return 'KTX'
        return '대중교통'
    
    if category == '항공':
        if '라운지' in text: return '공항라운지'
        if '마일리지' in text: return '마일리지'
        return '항공'
    
    if category == '해외':
        return '해외결제'
    
    return category

def extract_discount(desc, discount_obj):
    """할인율/금액 추출"""
    discount_type = '할인'
    
    # discount 객체에서 추출
    if discount_obj and discount_obj.get('value'):
        val = discount_obj['value']
        dtype = discount_obj.get('type')
        
        if dtype == 'percent':
            if val == int(val):
                val_str = f"{int(val)}%"
            else:
                val_str = f"{val}%"
        elif dtype == 'won':
            val = int(val)
            if val >= 10000:
                val_str = f"{val//10000}만원"
            else:
                val_str = f"{val:,}원"
        else:
            val_str = None
        
        if val_str:
            # 적립인지 할인인지
            if '적립' in desc:
                discount_type = '적립'
            return val_str, discount_type
    
    # description에서 추출
    percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%', desc)
    if percent_match:
        val = float(percent_match.group(1))
        if val == int(val):
            val_str = f"{int(val)}%"
        else:
            val_str = f"{val}%"
        if '적립' in desc:
            discount_type = '적립'
        return val_str, discount_type
    
    won_match = re.search(r'([\d,]+)\s*원', desc)
    if won_match:
        val = int(won_match.group(1).replace(',', ''))
        if val >= 10000:
            val_str = f"{val//10000}만원"
        else:
            val_str = f"{val:,}원"
        if '적립' in desc:
            discount_type = '적립'
        return val_str, discount_type
    
    # 무료
    if '무료' in desc:
        return None, '무료'
    
    return None, '혜택'

def process_benefit(benefit):
    """개별 혜택 처리"""
    desc = benefit.get('description', '') or ''
    detail = benefit.get('detail', '') or ''
    title = benefit.get('title', '') or ''
    original_cat = benefit.get('category', '') or ''
    discount_obj = benefit.get('discount', {}) or {}
    is_select = benefit.get('is_select_option', False)
    
    # 유의사항 제외
    if title == '유의사항' or '유의사항' in desc:
        return None
    
    # 선택형 옵션 설명만 있는 경우 제외
    if '선택 옵션에 따른' in desc and not discount_obj.get('value'):
        return None
    
    # 올바른 카테고리 추출
    category = detect_category(desc, detail, original_cat)
    
    # 대상 추출
    target = extract_target(desc, category)
    
    # 할인율/금액 추출
    discount_val, discount_type = extract_discount(desc, discount_obj)
    
    # 요약 생성
    if discount_val:
        summary = f"{target} {discount_val} {discount_type}"
    elif discount_type == '무료':
        summary = f"{target} 무료"
    else:
        summary = f"{target} 혜택"
    
    return {
        'category': category,
        'summary': summary.strip(),
        'is_select_option': is_select
    }

def process_all_cards():
    """모든 카드 처리"""
    json_path = r"c:\Users\MADUP\Documents\seokmin\website_samsungcard_recommend\data\samsung_cards.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for card in data['cards']:
        benefits = card.get('benefits', [])
        processed = []
        
        for benefit in benefits:
            result = process_benefit(benefit)
            if result:
                processed.append(result)
        
        # 중복 제거 (같은 summary)
        seen = set()
        unique = []
        for p in processed:
            if p['summary'] not in seen:
                seen.add(p['summary'])
                unique.append(p)
        
        card['display_benefits'] = unique
    
    # 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"완료: {len(data['cards'])}개 카드 혜택 재분류")
    
    # 샘플 확인
    samples = ['삼성카드 taptap O', '삼성 iD SELECT ALL 카드', '모니모카드']
    for card in data['cards']:
        if card['name'] in samples:
            print(f"\n=== {card['name']} ===")
            for b in card.get('display_benefits', [])[:6]:
                print(f"  [{b['category']}] {b['summary']}")

if __name__ == "__main__":
    process_all_cards()
