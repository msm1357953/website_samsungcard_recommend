// ===== Card Hero Animation =====
class CardHeroAnimation {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.cards = [];
        this.images = [];
        this.loaded = 0;
        this.animationId = null;

        // Card image URLs
        this.cardUrls = [
            'https://d1c5n4ri2guedi.cloudfront.net/card/51/card_img/37691/51card.png',
            'https://d1c5n4ri2guedi.cloudfront.net/card/2885/card_img/44212/2885card_1.png',
            'https://d1c5n4ri2guedi.cloudfront.net/card/657/card_img/27715/657card.png'
        ];

        this.init();
    }

    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.loadImages();
    }

    resize() {
        const container = this.canvas.parentElement;
        this.canvas.width = container.offsetWidth;
        this.canvas.height = 200;
        this.centerX = this.canvas.width / 2;
        this.centerY = this.canvas.height / 2;
    }

    loadImages() {
        this.cardUrls.forEach((url, i) => {
            const img = new Image();
            img.crossOrigin = 'anonymous';
            img.onload = () => {
                this.images[i] = img;
                this.loaded++;
                if (this.loaded === this.cardUrls.length) {
                    this.setupCards();
                    this.animate();
                }
            };
            img.onerror = () => {
                console.log('Image load error, using fallback');
                this.loaded++;
            };
            img.src = url;
        });
    }

    setupCards() {
        const cardWidth = 90;
        const cardHeight = 140;
        const spacing = 100;

        // Card configurations: x offset, initial phase, float speed
        const configs = [
            { offsetX: -spacing, phase: 0, speed: 0.015, rotation: -15 },
            { offsetX: 0, phase: Math.PI / 3, speed: 0.02, rotation: 0 },
            { offsetX: spacing, phase: Math.PI / 1.5, speed: 0.018, rotation: 15 }
        ];

        configs.forEach((config, i) => {
            this.cards.push({
                x: this.centerX + config.offsetX,
                baseY: this.centerY,
                y: this.centerY,
                width: cardWidth,
                height: cardHeight,
                phase: config.phase,
                speed: config.speed,
                rotation: config.rotation * Math.PI / 180,
                floatAmplitude: 8,
                img: this.images[i],
                time: 0,
                shadow: 15
            });
        });
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Update and draw each card
        this.cards.forEach((card, index) => {
            card.time += card.speed;

            // Floating effect
            const floatY = Math.sin(card.time + card.phase) * card.floatAmplitude;
            card.y = card.baseY + floatY;

            // Subtle rotation oscillation
            const rotationOsc = Math.sin(card.time * 0.5) * 0.02;
            const currentRotation = card.rotation + rotationOsc;

            // Update shadow based on height
            card.shadow = 15 + floatY * 0.5;

            this.drawCard(card, currentRotation, index);
        });

        this.animationId = requestAnimationFrame(() => this.animate());
    }

    drawCard(card, rotation, index) {
        this.ctx.save();

        // Move to card center
        this.ctx.translate(card.x, card.y);
        this.ctx.rotate(rotation);

        // Draw shadow
        this.ctx.shadowColor = 'rgba(0, 0, 0, 0.25)';
        this.ctx.shadowBlur = card.shadow;
        this.ctx.shadowOffsetX = 0;
        this.ctx.shadowOffsetY = card.shadow * 0.5;

        // Draw card background (rounded rect)
        const w = card.width;
        const h = card.height;
        const r = 8;

        this.ctx.beginPath();
        this.ctx.moveTo(-w / 2 + r, -h / 2);
        this.ctx.lineTo(w / 2 - r, -h / 2);
        this.ctx.quadraticCurveTo(w / 2, -h / 2, w / 2, -h / 2 + r);
        this.ctx.lineTo(w / 2, h / 2 - r);
        this.ctx.quadraticCurveTo(w / 2, h / 2, w / 2 - r, h / 2);
        this.ctx.lineTo(-w / 2 + r, h / 2);
        this.ctx.quadraticCurveTo(-w / 2, h / 2, -w / 2, h / 2 - r);
        this.ctx.lineTo(-w / 2, -h / 2 + r);
        this.ctx.quadraticCurveTo(-w / 2, -h / 2, -w / 2 + r, -h / 2);
        this.ctx.closePath();

        this.ctx.fillStyle = '#ffffff';
        this.ctx.fill();

        // Reset shadow for image
        this.ctx.shadowColor = 'transparent';

        // Draw card image
        if (card.img) {
            this.ctx.drawImage(card.img, -w / 2, -h / 2, w, h);
        }

        this.ctx.restore();
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }
}

// ===== Filter Interaction =====
document.addEventListener('DOMContentLoaded', function () {
    // Initialize hero animation
    const heroCanvas = document.getElementById('hero-canvas');
    if (heroCanvas) {
        new CardHeroAnimation('hero-canvas');
    }

    // Filter button interaction
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const category = this.dataset.category;
            console.log('Selected category:', category);
        });
    });
});
