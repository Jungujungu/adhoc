// Global variables
let scene, camera, renderer, controls;
let earth, clouds;
let stars = [];

// Initialize the 3D scene
function init() {
    // Create scene
    scene = new THREE.Scene();
    
    // Create camera
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 0, 3);
    
    // Create renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.getElementById('container').appendChild(renderer.domElement);
    
    // Add orbit controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 1.5;
    controls.maxDistance = 10;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.5;
    
    // Create Earth
    createEarth();
    
    // Create starfield
    createStarfield();
    
    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
    scene.add(ambientLight);
    
    // Add directional light (sun)
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 3, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    // Hide loading screen
    document.getElementById('loading').style.display = 'none';
    
    // Start animation loop
    animate();
}

// Create the Earth with realistic textures
function createEarth() {
    const earthGeometry = new THREE.SphereGeometry(1, 64, 64);
    
    // Earth texture loader
    const textureLoader = new THREE.TextureLoader();
    
    // Load Earth textures
    const earthTexture = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_atmos_2048.jpg');
    const bumpMap = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_normal_2048.jpg');
    const specularMap = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_specular_2048.jpg');
    const cloudsTexture = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_clouds_1024.png');
    
    // Create Earth material
    const earthMaterial = new THREE.MeshPhongMaterial({
        map: earthTexture,
        bumpMap: bumpMap,
        bumpScale: 0.05,
        specularMap: specularMap,
        specular: new THREE.Color('grey'),
        shininess: 10
    });
    
    // Create Earth mesh
    earth = new THREE.Mesh(earthGeometry, earthMaterial);
    earth.castShadow = true;
    earth.receiveShadow = true;
    scene.add(earth);
    
    // Create clouds layer
    const cloudsGeometry = new THREE.SphereGeometry(1.01, 64, 64);
    const cloudsMaterial = new THREE.MeshPhongMaterial({
        map: cloudsTexture,
        transparent: true,
        opacity: 0.4
    });
    
    clouds = new THREE.Mesh(cloudsGeometry, cloudsMaterial);
    scene.add(clouds);
}

// Create starfield background
function createStarfield() {
    const starsGeometry = new THREE.BufferGeometry();
    const starsMaterial = new THREE.PointsMaterial({
        color: 0xffffff,
        size: 0.1,
        transparent: true,
        opacity: 0.8
    });
    
    const starsVertices = [];
    for (let i = 0; i < 10000; i++) {
        const x = (Math.random() - 0.5) * 2000;
        const y = (Math.random() - 0.5) * 2000;
        const z = (Math.random() - 0.5) * 2000;
        starsVertices.push(x, y, z);
    }
    
    starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
    const starField = new THREE.Points(starsGeometry, starsMaterial);
    scene.add(starField);
}

// Handle window resize
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    
    // Rotate clouds slightly faster than Earth
    if (clouds) {
        clouds.rotation.y += 0.001;
    }
    
    // Update controls
    controls.update();
    
    // Render scene
    renderer.render(scene, camera);
}

// Add some interactive features
function addInteractivity() {
    // Add click event for Earth
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    
    function onMouseClick(event) {
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObject(earth);
        
        if (intersects.length > 0) {
            // Get the intersection point
            const point = intersects[0].point;
            
            // Convert to spherical coordinates
            const lat = Math.asin(point.y) * (180 / Math.PI);
            const lon = Math.atan2(point.x, point.z) * (180 / Math.PI);
            
            console.log(`Clicked at: Latitude ${lat.toFixed(2)}°, Longitude ${lon.toFixed(2)}°`);
            
            // You could add a marker or show information here
            showLocationInfo(lat, lon);
        }
    }
    
    window.addEventListener('click', onMouseClick);
}

// Show location information (placeholder)
function showLocationInfo(lat, lon) {
    // This could be expanded to show real location data
    const info = document.getElementById('info');
    const locationDiv = document.createElement('div');
    locationDiv.style.marginTop = '10px';
    locationDiv.style.padding = '5px';
    locationDiv.style.borderTop = '1px solid rgba(255,255,255,0.3)';
    locationDiv.innerHTML = `📍 Lat: ${lat.toFixed(2)}°, Lon: ${lon.toFixed(2)}°`;
    
    // Remove previous location info
    const prevLocation = info.querySelector('.location-info');
    if (prevLocation) {
        prevLocation.remove();
    }
    
    locationDiv.className = 'location-info';
    info.appendChild(locationDiv);
}

// Initialize everything when the page loads
window.addEventListener('load', () => {
    init();
    addInteractivity();
});

// Add some additional visual effects
function addAtmosphere() {
    // Create atmospheric glow
    const atmosphereGeometry = new THREE.SphereGeometry(1.1, 64, 64);
    const atmosphereMaterial = new THREE.ShaderMaterial({
        vertexShader: `
            varying vec3 vNormal;
            void main() {
                vNormal = normalize(normalMatrix * normal);
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            varying vec3 vNormal;
            void main() {
                float intensity = pow(0.7 - dot(vNormal, vec3(0, 0, 1.0)), 2.0);
                gl_FragColor = vec4(0.3, 0.6, 1.0, 1.0) * intensity;
            }
        `,
        blending: THREE.AdditiveBlending,
        side: THREE.BackSide
    });
    
    const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    scene.add(atmosphere);
}

// Add atmosphere after Earth is created
setTimeout(addAtmosphere, 1000); 