"""
삼성카드 혜택 데이터 정제 스크립트
- 카테고리별 대표 혜택 4개 추출
- 중복 카테고리 제거
- 간결한 혜택 값 생성
"""
import json
import re
from collections import OrderedDict

def extract_benefit_value(benefit):
    """혜택에서 간결한 값 추출 (예: "스타벅스 50%", "대중교통 10%")"""
    
    desc = benefit.get('description', '')
    title = benefit.get('title', '')
    discount = benefit.get('discount', {})
    category = benefit.get('category', '')
    
    # 할인율/금액 추출
    discount_text = ''
    if discount.get('value'):
        val = discount['value']
        if discount.get('type') == 'percent':
            # 소수점 정리: 10.0 -> 10, 1.5 -> 1.5
            if val == int(val):
                discount_text = f"{int(val)}%"
            else:
                discount_text = f"{val}%"
        elif discount.get('type') == 'won':
            val = int(val)
            if val >= 10000:
                discount_text = f"{val//10000}만원"
            else:
                discount_text = f"{val:,}원"
    
    # description에서 할인율 추출 시도
    if not discount_text:
        percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%', desc)
        if percent_match:
            val = float(percent_match.group(1))
            if val == int(val):
                discount_text = f"{int(val)}%"
            else:
                discount_text = f"{val}%"
        else:
            won_match = re.search(r'([\d,]+)\s*원', desc)
            if won_match:
                val = int(won_match.group(1).replace(',', ''))
                if val >= 10000:
                    discount_text = f"{val//10000}만원"
                else:
                    discount_text = f"{val:,}원"
    
    # 대상점 추출 (스타벅스, CGV 등)
    target = ''
    
    # 커피 관련
    if category == '커피':
        if '스타벅스' in desc:
            target = '스타벅스'
        elif '커피전문점' in desc or '커피 전문점' in desc:
            target = '커피전문점'
        elif '투썸' in desc:
            target = '투썸플레이스'
        elif '메가커피' in desc:
            target = '메가커피'
        elif '이디야' in desc:
            target = '이디야'
        else:
            target = '커피'
    
    # 교통 관련
    elif category == '교통':
        if '대중교통' in desc or '버스' in desc or '지하철' in desc:
            target = '대중교통'
        elif '택시' in desc:
            target = '택시'
        elif 'KTX' in desc or '철도' in desc:
            target = 'KTX'
        elif '고속버스' in desc:
            target = '고속버스'
        else:
            target = '교통'
    
    # 쇼핑 관련
    elif category == '쇼핑':
        if '온라인' in desc or '온라인쇼핑' in desc:
            target = '온라인쇼핑'
        elif '쿠팡' in desc:
            target = '쿠팡'
        elif '네이버' in desc:
            target = '네이버'
        elif '배달' in desc:
            target = '배달앱'
        elif '할인점' in desc or '마트' in desc:
            target = '할인점'
        elif '편의점' in desc:
            target = '편의점'
        else:
            target = '쇼핑'
    
    # 스트리밍 관련
    elif category == '스트리밍':
        if '넷플릭스' in desc:
            target = '넷플릭스'
        elif '유튜브' in desc:
            target = '유튜브'
        elif '디즈니' in desc:
            target = '디즈니+'
        elif '티빙' in desc:
            target = '티빙'
        elif '웨이브' in desc:
            target = '웨이브'
        else:
            target = 'OTT'
    
    # 통신 관련
    elif category == '통신':
        if 'SKT' in desc or 'KT' in desc or 'LG' in desc:
            target = '통신비'
        else:
            target = '통신비'
    
    # 주유 관련
    elif category == '주유':
        target = '주유'
    
    # 항공 관련
    elif category == '항공':
        if '마일리지' in desc or '스카이패스' in desc:
            target = '마일리지'
        elif '라운지' in desc:
            target = '공항라운지'
        else:
            target = '항공'
    
    # 영화 관련
    elif category == '영화':
        if 'CGV' in desc:
            target = 'CGV'
        elif '롯데시네마' in desc:
            target = '롯데시네마'
        elif '메가박스' in desc:
            target = '메가박스'
        else:
            target = '영화'
    
    # 기본
    if not target:
        target = category or title[:6]
    
    # 결과 조합
    if discount_text:
        return f"{target} {discount_text}"
    else:
        # 마일리지, 적립 등
        if '마일리지' in desc:
            return '마일리지 적립'
        elif '적립' in desc:
            return f"{target} 적립"
        elif '무료' in desc:
            return f"{target} 무료"
        else:
            return target[:10] + '...' if len(target) > 10 else target

def get_cleaned_benefits(benefits, max_count=4):
    """중복 카테고리 제거하고, 깔끔한 혜택 4개 추출"""
    if not benefits:
        return []
    
    seen_categories = set()
    cleaned = []
    
    for b in benefits:
        # 제외 조건
        if b.get('title') == '유의사항':
            continue
        if b.get('is_select_option'):
            continue
        if b.get('title') == '선택형':
            continue
        if not b.get('category'):
            continue
        
        category = b['category']
        
        # 중복 카테고리 제거
        if category in seen_categories:
            continue
        seen_categories.add(category)
        
        # 간결한 값 추출
        value = extract_benefit_value(b)
        
        cleaned.append({
            'category': category,
            'value': value
        })
        
        if len(cleaned) >= max_count:
            break
    
    return cleaned

def process_cards():
    """모든 카드의 혜택 정제"""
    
    json_path = r"c:\Users\MADUP\Documents\seokmin\website_samsungcard_recommend\data\samsung_cards.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for card in data['cards']:
        original_benefits = card.get('benefits', [])
        cleaned_benefits = get_cleaned_benefits(original_benefits)
        
        # cleaned_benefits 추가
        card['cleaned_benefits'] = cleaned_benefits
    
    # 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"완료: {len(data['cards'])}개 카드 혜택 정제")
    
    # 샘플 출력
    print("\n샘플 결과:")
    sample_cards = ['삼성카드 taptap O', '삼성 iD SELECT ALL 카드', '모니모카드', '삼성카드 & MILEAGE PLATINUM (스카이패스)']
    
    for card in data['cards']:
        if card['name'] in sample_cards:
            print(f"\n[{card['name']}]")
            for b in card.get('cleaned_benefits', []):
                print(f"  - {b['category']}: {b['value']}")

if __name__ == "__main__":
    process_cards()
