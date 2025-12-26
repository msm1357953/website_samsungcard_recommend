"""
AI가 직접 분석하여 모든 혜택을 요약
- 각 혜택마다 간결한 요약 생성
- 할인/적립 구분 포함
- UI에서는 최대 4개만 표시
"""
import json
import re

def summarize_benefit(benefit):
    """개별 혜택을 간결하게 요약"""
    
    desc = benefit.get('description', '') or ''
    detail = benefit.get('detail', '') or ''
    title = benefit.get('title', '') or ''
    category = benefit.get('category', '') or ''
    discount = benefit.get('discount', {}) or {}
    is_select = benefit.get('is_select_option', False)
    
    # 유의사항 제외
    if title == '유의사항':
        return None
    
    # 선택형 옵션 설명만 있는 경우 제외 (실제 혜택 아님)
    if '선택 옵션에 따른' in desc and not discount.get('value'):
        return None
    
    # 할인율/금액 추출
    discount_val = ''
    discount_type = '할인'  # 기본값
    
    if discount.get('value'):
        val = discount['value']
        if discount.get('type') == 'percent':
            if val == int(val):
                discount_val = f"{int(val)}%"
            else:
                discount_val = f"{val}%"
        elif discount.get('type') == 'won':
            val = int(val)
            if val >= 10000:
                discount_val = f"{val//10000}만원"
            else:
                discount_val = f"{val:,}원"
    else:
        # description에서 추출
        percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%', desc)
        if percent_match:
            val = float(percent_match.group(1))
            if val == int(val):
                discount_val = f"{int(val)}%"
            else:
                discount_val = f"{val}%"
        else:
            won_match = re.search(r'([\d,]+)\s*원', desc)
            if won_match:
                val = int(won_match.group(1).replace(',', ''))
                if val >= 10000:
                    discount_val = f"{val//10000}만원"
                else:
                    discount_val = f"{val:,}원"
    
    # 할인/적립 구분
    if '적립' in desc or '적립' in detail or '마일리지' in desc:
        discount_type = '적립'
    elif '할인' in desc or '할인' in detail:
        discount_type = '할인'
    elif '무료' in desc:
        discount_type = '무료'
        discount_val = ''
    
    # 대상 추출 (더 구체적으로)
    target = extract_target(desc, detail, category)
    
    # 결과 조합
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

def extract_target(desc, detail, category):
    """설명에서 대상점/서비스 추출"""
    
    text = desc + ' ' + detail
    
    # 커피/카페
    if '스타벅스' in text:
        return '스타벅스'
    if '투썸' in text:
        return '투썸플레이스'
    if '이디야' in text:
        return '이디야'
    if '메가커피' in text or '메가' in text:
        return '메가커피'
    if '커피전문점' in text or '커피 전문점' in text:
        return '커피전문점'
    
    # 교통
    if '대중교통' in text or ('버스' in text and '지하철' in text):
        return '대중교통'
    if 'KTX' in text:
        return 'KTX'
    if '택시' in text:
        return '택시'
    if '고속버스' in text:
        return '고속버스'
    
    # 쇼핑
    if '네이버' in text and ('쇼핑' in text or '스토어' in text):
        return '네이버쇼핑'
    if '쿠팡' in text and '이츠' not in text:
        return '쿠팡'
    if 'SSG' in text:
        return 'SSG.COM'
    if 'G마켓' in text or '옥션' in text:
        return 'G마켓/옥션'
    if '11번가' in text:
        return '11번가'
    if '온라인쇼핑' in text or '온라인 쇼핑' in text:
        return '온라인쇼핑'
    
    # 배달
    if '배달의민족' in text or '배민' in text:
        return '배달의민족'
    if '쿠팡이츠' in text:
        return '쿠팡이츠'
    if '요기요' in text:
        return '요기요'
    if '배달앱' in text:
        return '배달앱'
    
    # 스트리밍
    if '넷플릭스' in text:
        return '넷플릭스'
    if '유튜브' in text:
        return '유튜브'
    if '디즈니' in text:
        return '디즈니+'
    if '티빙' in text:
        return '티빙'
    if '웨이브' in text:
        return '웨이브'
    if 'OTT' in text or '디지털콘텐츠' in text:
        return 'OTT'
    
    # 주유
    if 'SK에너지' in text or 'SK' in text:
        return 'SK주유'
    if 'GS칼텍스' in text or 'GS' in text:
        return 'GS주유'
    if 'S-OIL' in text:
        return 'S-OIL'
    if '주유' in text:
        return '주유'
    
    # 통신
    if 'SKT' in text or 'KT' in text or 'LG U+' in text:
        return '통신비'
    if '통신' in text:
        return '통신비'
    
    # 마트/편의점
    if '이마트' in text:
        return '이마트'
    if '롯데마트' in text:
        return '롯데마트'
    if '편의점' in text:
        return '편의점'
    if 'CU' in text or 'GS25' in text:
        return '편의점'
    
    # 영화
    if 'CGV' in text:
        return 'CGV'
    if '롯데시네마' in text:
        return '롯데시네마'
    if '메가박스' in text:
        return '메가박스'
    
    # 항공/마일리지
    if '스카이패스' in text or '마일리지' in text:
        return '마일리지'
    if '라운지' in text:
        return '공항라운지'
    if '항공' in text:
        return '항공'
    
    # 기타
    if '다이소' in text:
        return '다이소'
    if '알라딘' in text:
        return '알라딘'
    if '교육' in text or '학원' in text:
        return '교육'
    if '병원' in text or '의료' in text:
        return '의료'
    if '관리비' in text:
        return '관리비'
    if '해외' in text:
        return '해외'
    if '멤버십' in text:
        return '멤버십'
    
    # 기본: 카테고리 사용
    return category if category else '혜택'

def process_all_cards():
    """모든 카드의 모든 혜택 요약"""
    
    json_path = r"c:\Users\MADUP\Documents\seokmin\website_samsungcard_recommend\data\samsung_cards.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for card in data['cards']:
        original_benefits = card.get('benefits', [])
        summarized = []
        
        for benefit in original_benefits:
            summary = summarize_benefit(benefit)
            if summary:
                summarized.append(summary)
        
        # 중복 제거 (같은 category + summary)
        seen = set()
        unique_summarized = []
        for s in summarized:
            key = (s['category'], s['summary'])
            if key not in seen:
                seen.add(key)
                unique_summarized.append(s)
        
        card['summarized_benefits'] = unique_summarized
    
    # 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"완료: {len(data['cards'])}개 카드 혜택 요약")
    
    # 샘플 출력
    print("\n샘플 결과:")
    sample_cards = ['삼성카드 taptap O', '삼성 iD SELECT ALL 카드', '모니모카드', 'THE 1 (스카이패스)']
    
    for card in data['cards']:
        if card['name'] in sample_cards:
            print(f"\n[{card['name']}]")
            for b in card.get('summarized_benefits', [])[:6]:
                select_mark = '(선택)' if b.get('is_select_option') else ''
                print(f"  - {b['category']}: {b['summary']} {select_mark}")

if __name__ == "__main__":
    process_all_cards()
