import json

with open('data/samsung_cards.json', encoding='utf-8') as f:
    data = json.load(f)

# K-패스 삼성체크카드 확인
for card in data['cards']:
    if 'K-패스' in card['name']:
        print(f"=== {card['name']} ===")
        print(f"display_benefits: {card.get('display_benefits')}")
        break
