/**
 * Three.js Premium Card Showcase
 * Revolut-inspired cinematic card display
 */

class CardShowcase {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;

        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.cards = [];
        this.mouseX = 0;
        this.mouseY = 0;
        this.reflectionPlane = null;

        this.cardImages = [
            'assets/card1.png',      // taptap O (Pink)
            'assets/card2.png',      // SELECT ALL (White)
            'assets/card3_monimo.png' // Monimo (Blue)
        ];

        this.init();
    }

    init() {
        // Scene with deep black background
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0f);

        // Camera - lower angle for dramatic effect
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(50, aspect, 0.1, 1000);
        this.camera.position.set(0, 1.5, 6);
        this.camera.lookAt(0, 0.5, 0);

        // Renderer with high quality settings
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: false
        });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.2;
        this.container.appendChild(this.renderer.domElement);

        // Cinematic Lighting Setup
        this.setupLighting();

        // Reflective Floor
        this.createReflectiveFloor();

        // Load cards
        this.loadCards();

        // Events
        window.addEventListener('resize', () => this.onResize());
        this.container.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.container.addEventListener('mouseleave', () => this.onMouseLeave());

        // Start animation
        this.animate();
    }

    setupLighting() {
        // Ambient - very subtle
        const ambient = new THREE.AmbientLight(0xffffff, 0.15);
        this.scene.add(ambient);

        // Main Key Light - from top right
        const keyLight = new THREE.SpotLight(0xffffff, 1.5);
        keyLight.position.set(5, 8, 5);
        keyLight.angle = Math.PI / 4;
        keyLight.penumbra = 0.5;
        keyLight.castShadow = true;
        keyLight.shadow.mapSize.width = 1024;
        keyLight.shadow.mapSize.height = 1024;
        this.scene.add(keyLight);

        // Rim Light - Blue accent from back left
        const rimLight1 = new THREE.PointLight(0x4488ff, 0.8);
        rimLight1.position.set(-4, 2, -3);
        this.scene.add(rimLight1);

        // Rim Light - Subtle warm accent from back right
        const rimLight2 = new THREE.PointLight(0xff8844, 0.4);
        rimLight2.position.set(4, 2, -3);
        this.scene.add(rimLight2);

        // Bottom fill light - subtle reflection simulation
        const fillLight = new THREE.PointLight(0x2244aa, 0.3);
        fillLight.position.set(0, -2, 2);
        this.scene.add(fillLight);
    }

    createReflectiveFloor() {
        // Reflective dark floor
        const floorGeometry = new THREE.PlaneGeometry(20, 10);
        const floorMaterial = new THREE.MeshStandardMaterial({
            color: 0x111118,
            metalness: 0.9,
            roughness: 0.3,
            transparent: true,
            opacity: 0.8
        });

        this.reflectionPlane = new THREE.Mesh(floorGeometry, floorMaterial);
        this.reflectionPlane.rotation.x = -Math.PI / 2;
        this.reflectionPlane.position.y = -1.2;
        this.reflectionPlane.receiveShadow = true;
        this.scene.add(this.reflectionPlane);

        // Subtle gradient fog effect
        const fogColor = new THREE.Color(0x0a0a0f);
        this.scene.fog = new THREE.Fog(fogColor, 8, 15);
    }

    loadCards() {
        const textureLoader = new THREE.TextureLoader();

        // Card configurations - dramatic angles like Revolut
        const positions = [
            { x: -2.0, y: 0, z: 0.3, rotY: 0.35, rotZ: 0, scale: 1 },    // Left
            { x: 0, y: 0.2, z: 1.2, rotY: 0, rotZ: 0, scale: 1.15 },     // Center - prominent
            { x: 2.0, y: 0, z: 0.3, rotY: -0.35, rotZ: 0, scale: 1 }     // Right
        ];

        this.cardImages.forEach((imgPath, index) => {
            textureLoader.load(imgPath, (texture) => {
                texture.anisotropy = this.renderer.capabilities.getMaxAnisotropy();

                // Simple card geometry - single plane to avoid Z-fighting
                const cardWidth = 1.4;
                const cardHeight = 2.2;

                const geometry = new THREE.PlaneGeometry(cardWidth, cardHeight);
                const material = new THREE.MeshStandardMaterial({
                    map: texture,
                    side: THREE.DoubleSide,
                    metalness: 0.2,
                    roughness: 0.5,
                    transparent: true
                });

                const card = new THREE.Mesh(geometry, material);
                card.castShadow = true;

                // Apply position and rotation
                const pos = positions[index];
                card.position.set(pos.x, pos.y, pos.z);
                card.rotation.y = pos.rotY;
                card.rotation.z = pos.rotZ;
                card.scale.setScalar(pos.scale);

                // Store animation data
                card.userData = {
                    originalY: pos.y,
                    originalRotY: pos.rotY,
                    floatPhase: index * Math.PI * 0.6,
                    floatSpeed: 0.6
                };

                this.cards.push(card);
                this.scene.add(card);
            });
        });
    }

    onMouseMove(event) {
        const rect = this.container.getBoundingClientRect();
        this.mouseX = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouseY = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    }

    onMouseLeave() {
        this.mouseX = 0;
        this.mouseY = 0;
    }

    onResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const time = Date.now() * 0.001;

        // Animate cards - subtle floating
        this.cards.forEach((card, index) => {
            const floatY = Math.sin(time * card.userData.floatSpeed + card.userData.floatPhase) * 0.05;
            card.position.y = card.userData.originalY + floatY;

            // Subtle rotation wobble
            const wobble = Math.sin(time * 0.3 + index * 0.5) * 0.015;
            card.rotation.y = card.userData.originalRotY + wobble;
        });

        // Scene rotation based on mouse - very subtle
        const targetRotY = this.mouseX * 0.15;
        const targetRotX = this.mouseY * 0.08;
        this.scene.rotation.y += (targetRotY - this.scene.rotation.y) * 0.03;
        this.scene.rotation.x += (targetRotX - this.scene.rotation.x) * 0.03;

        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new CardShowcase('card-showcase');
});
