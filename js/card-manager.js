/**
 * Samsung Card Recommendation - 카드 동적 렌더링 및 필터 기능
 */

class CardManager {
    constructor() {
        this.cards = [];
        this.filteredCards = [];
        this.currentFilter = '추천';
        this.cardGridElement = document.querySelector('.card-grid');
        this.init();
    }

    async init() {
        await this.loadCards();
        this.renderCards();
        this.setupFilterListeners();
    }

    async loadCards() {
        try {
            const response = await fetch('data/samsung_cards.json');
            const data = await response.json();
            this.cards = data.cards;
            this.filteredCards = [...this.cards];
            console.log(`${this.cards.length}개 카드 로드 완료`);
        } catch (error) {
            console.error('카드 데이터 로드 실패:', error);
        }
    }

    renderCards() {
        if (!this.cardGridElement) return;

        this.cardGridElement.innerHTML = '';

        let cardsToShow;

        if (this.currentFilter === '추천') {
            // 추천 탭: 고정 3개 카드만
            const priorityNames = ['삼성카드 taptap O', '삼성 iD SELECT ALL 카드', '모니모카드'];
            cardsToShow = priorityNames
                .map(name => this.cards.find(c => c.name === name))
                .filter(Boolean);
        } else {
            // 다른 탭: 해당 카테고리 혜택 있는 카드만
            cardsToShow = this.filteredCards.slice(0, 20);
        }

        cardsToShow.forEach((card, index) => {
            const cardElement = this.createCardElement(card, index);
            this.cardGridElement.appendChild(cardElement);
        });

        // 카드 개수 업데이트
        const cardCountElement = document.getElementById('card-count');
        if (cardCountElement) {
            cardCountElement.textContent = cardsToShow.length;
        }

        // 필터 탭이면 해당 카테고리 하이라이트
        if (this.currentFilter !== '추천') {
            this.highlightBenefitsByCategory(this.currentFilter);
        }
    }

    createCardElement(card, index) {
        const article = document.createElement('article');
        article.className = 'card-item';
        article.style.animationDelay = `${index * 0.05}s`;

        // display_benefits 사용 (재분류된 혜택), summary 중복 제거, 최대 4개
        const allBenefits = card.display_benefits || card.summarized_benefits || [];
        const seenSummaries = new Set();
        const benefits = [];

        for (const b of allBenefits) {
            const cat = b.category || '혜택';
            const summary = b.summary || '';
            // 잘못된 요약 제외
            if (summary.includes('혜택 혜택') || summary === '혜택' || summary.trim() === '') continue;
            if (!seenSummaries.has(summary) && benefits.length < 4) {
                seenSummaries.add(summary);
                benefits.push({ ...b, category: cat });
            }
        }

        // 연회비 포맷
        const annualFee = card.annual_fee?.domestic
            ? `${card.annual_fee.domestic.toLocaleString()}원`
            : '무료';

        // 버튼 색상
        const primaryColor = card.primary_color || '#1428a0';
        const secondaryColor = card.secondary_color || '#2d4de0';

        // tagline
        const tagline = card.tagline || '일상에 혜택을 더하다';

        article.innerHTML = `
            <div class="card-content">
                <div class="card-image">
                    <div class="card-tagline">${tagline}</div>
                    <img src="${card.image_url}" alt="${card.name}" loading="lazy">
                </div>
                <div class="card-info">
                    <h3 class="card-name">${card.name}</h3>
                    <div class="card-fee">
                        <span class="fee-label">연회비</span>
                        <span class="fee-value">${annualFee}</span>
                    </div>
                    <div class="card-benefits">
                        ${benefits.map((b, i) => this.createBenefitHTML(b, i === 0)).join('')}
                    </div>
                </div>
            </div>
            <div class="card-apply">
                <button class="apply-btn" style="background: linear-gradient(135deg, ${primaryColor}, ${secondaryColor});" onclick="window.open('${card.detail_url}', '_blank')">
                    발급하기
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
                    </svg>
                </button>
            </div>
        `;

        return article;
    }

    getTopBenefits(benefits, count) {
        if (!benefits || !Array.isArray(benefits)) return [];

        // 유의사항 제외, 선택형 제외, 카테고리 있는 혜택만
        return benefits
            .filter(b => {
                if (b.title === '유의사항') return false;
                if (!b.category) return false;
                if (b.is_select_option) return false; // 선택형 혜택 제외
                if (b.title === '선택형') return false;
                return true;
            })
            .slice(0, count);
    }

    createBenefitHTML(benefit, isHighlight) {
        const category = benefit.category || '혜택';
        const icon = this.getCategoryIcon(category);
        // summarized_benefits는 summary 필드 사용
        const value = benefit.summary || benefit.value || '';

        return `
            <div class="benefit-item${isHighlight ? ' highlight' : ''}">
                <span class="benefit-category">${icon}${category}</span>
                <span class="benefit-value">${value}</span>
            </div>
        `;
    }

    getCategoryIcon(category) {
        const icons = {
            '커피': '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M2 21h18v-2H2v2zm18-10v-1c0-1.1-.9-2-2-2h-1V4H3v8c0 2.21 1.79 4 4 4h6c2.21 0 4-1.79 4-4v-1h1c.55 0 1 .45 1 1v1c0 .55-.45 1-1 1h-1v2h1c1.65 0 3-1.35 3-3z"/></svg>',
            '교통': '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8 2 4 2.5 4 6v9.5c0 1.38 1.12 2.5 2.5 2.5L5 19.5V20h2l1.5-2h7l1.5 2h2v-.5L17.5 18c1.38 0 2.5-1.12 2.5-2.5V6c0-3.5-4-4-8-4zM7.5 17c-.83 0-1.5-.67-1.5-1.5S6.67 14 7.5 14s1.5.67 1.5 1.5S8.33 17 7.5 17zm9 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM18 11H6V6h12v5z"/></svg>',
            '쇼핑': '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z"/></svg>',
            '통신': '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 1h-8C6.12 1 5 2.12 5 3.5v17C5 21.88 6.12 23 7.5 23h8c1.38 0 2.5-1.12 2.5-2.5v-17C18 2.12 16.88 1 15.5 1zm-4 21c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm4.5-4H7V4h9v14z"/></svg>',
            '주유': '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19.77 7.23l.01-.01-3.72-3.72L15 4.56l2.11 2.11c-.94.36-1.61 1.26-1.61 2.33 0 1.38 1.12 2.5 2.5 2.5.36 0 .69-.08 1-.21v7.21c0 .55-.45 1-1 1s-1-.45-1-1V14c0-1.1-.9-2-2-2h-1V5c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v16h10v-7.5h1.5v5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V9c0-.69-.28-1.32-.73-1.77zM12 10H6V5h6v5z"/></svg>',
            '스트리밍': '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14zM9.5 8.5l6.5 4-6.5 4z"/></svg>',
            '항공': '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg>',
            '영화': '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/></svg>',
        };
        return icons[category] || '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>';
    }

    formatBenefitValue(benefit) {
        // discount 정보가 있으면 직접 활용
        const discount = benefit.discount;
        if (discount && discount.value) {
            if (discount.type === 'percent') {
                return `${discount.value}% 할인`;
            } else if (discount.type === 'won') {
                return `${discount.value.toLocaleString()}원 할인`;
            }
        }

        // description에서 할인율/금액 추출
        const desc = benefit.description || '';

        // 패턴 매칭: "50% 할인", "10% 적립", "5,000원 할인" 등
        const percentMatch = desc.match(/(\d+)%/);
        if (percentMatch) {
            return `${percentMatch[1]}% 할인`;
        }

        const wonMatch = desc.match(/([\d,]+)원/);
        if (wonMatch) {
            return `${wonMatch[1]}원 할인`;
        }

        // 마일리지 패턴
        const mileageMatch = desc.match(/([\d,]+)\s*마일리지/);
        if (mileageMatch) {
            return `마일리지 적립`;
        }

        // 기본: 짧게 자르기
        const firstLine = desc.split('\n')[0];
        const cleaned = firstLine.replace(/\[.*?\]/g, '').trim();
        return cleaned.length > 12 ? cleaned.substring(0, 10) + '...' : cleaned;
    }

    filterByCategory(category) {
        this.currentFilter = category;

        if (category === '추천') {
            this.filteredCards = [...this.cards];
        } else {
            // display_benefits에서 해당 카테고리 혜택 있는 카드만 필터
            this.filteredCards = this.cards.filter(card => {
                const benefits = card.display_benefits || card.summarized_benefits || [];
                return benefits.some(b => b.category === category);
            });

            // Priority 카드 우선, 이후 해당 카테고리 혜택 개수로 정렬
            const priorityNames = ['삼성카드 taptap O', '삼성 iD SELECT ALL 카드', '모니모카드'];
            this.filteredCards.sort((a, b) => {
                const aPriority = priorityNames.indexOf(a.name);
                const bPriority = priorityNames.indexOf(b.name);
                // 둘 다 priority 카드인 경우 priority 순서대로
                if (aPriority >= 0 && bPriority >= 0) return aPriority - bPriority;
                // priority 카드가 먼저
                if (aPriority >= 0) return -1;
                if (bPriority >= 0) return 1;
                // 나머지는 혜택 개수로 정렬
                const aCount = (a.display_benefits || []).filter(b => b.category === category).length;
                const bCount = (b.display_benefits || []).filter(b => b.category === category).length;
                return bCount - aCount;
            });
        }

        console.log(`${category} 필터: ${this.filteredCards.length}개 카드`);
        this.renderCards();
        this.highlightBenefitsByCategory(category);
    }

    highlightBenefitsByCategory(category) {
        // 선택된 카테고리의 혜택을 하이라이트
        document.querySelectorAll('.benefit-item').forEach(item => {
            item.classList.remove('highlight');
            const cat = item.querySelector('.benefit-category')?.textContent;
            if (cat && cat.includes(category)) {
                item.classList.add('highlight');
            }
        });

        // 추천 탭이면 첫 번째 혜택 하이라이트
        if (category === '추천') {
            document.querySelectorAll('.card-benefits').forEach(benefits => {
                const first = benefits.querySelector('.benefit-item');
                if (first) first.classList.add('highlight');
            });
        }
    }

    setupFilterListeners() {
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                const category = btn.dataset.category || '추천';
                this.filterByCategory(category);
            });
        });
    }
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.cardManager = new CardManager();
});
