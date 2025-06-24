// Game canvas and context
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Game state
let gameState = 'menu'; // 'menu', 'playing', 'paused', 'gameOver'
let score = 0;
let lives = 3;
let level = 1;

// Paddle properties
const paddle = {
    width: 100,
    height: 15,
    x: canvas.width / 2 - 50,
    y: canvas.height - 30,
    speed: 8,
    dx: 0
};

// Ball properties
const ball = {
    x: canvas.width / 2,
    y: canvas.height - 50,
    radius: 8,
    speed: 5,
    dx: 0,
    dy: 0,
    isLaunched: false
};

// Brick properties
const brickRowCount = 5;
const brickColumnCount = 10;
const brickWidth = 75;
const brickHeight = 20;
const brickPadding = 5;
const brickOffsetTop = 80;
const brickOffsetLeft = 30;

// Create bricks array
const bricks = [];
for (let c = 0; c < brickColumnCount; c++) {
    bricks[c] = [];
    for (let r = 0; r < brickRowCount; r++) {
        bricks[c][r] = { x: 0, y: 0, status: 1, color: getBrickColor(r) };
    }
}

// Colors for different brick rows
function getBrickColor(row) {
    const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'];
    return colors[row];
}

// Input handling
const keys = {};
let mouseX = 0;

// Event listeners
document.addEventListener('keydown', (e) => {
    keys[e.key] = true;
    
    if (e.key === ' ' && gameState === 'menu') {
        startGame();
    }
    
    if (e.key === 'p' || e.key === 'P') {
        togglePause();
    }
});

document.addEventListener('keyup', (e) => {
    keys[e.key] = false;
});

canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
});

canvas.addEventListener('click', () => {
    if (gameState === 'menu') {
        startGame();
    }
});

// Game functions
function startGame() {
    gameState = 'playing';
    resetBall();
    resetPaddle();
    if (level === 1) {
        resetBricks();
    }
}

function togglePause() {
    if (gameState === 'playing') {
        gameState = 'paused';
    } else if (gameState === 'paused') {
        gameState = 'playing';
    }
}

function resetBall() {
    ball.x = canvas.width / 2;
    ball.y = canvas.height - 50;
    ball.dx = 0;
    ball.dy = 0;
    ball.isLaunched = false;
}

function resetPaddle() {
    paddle.x = canvas.width / 2 - paddle.width / 2;
}

function resetBricks() {
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            bricks[c][r].status = 1;
        }
    }
}

function launchBall() {
    if (!ball.isLaunched) {
        ball.isLaunched = true;
        ball.dx = (Math.random() - 0.5) * 8;
        ball.dy = -ball.speed;
    }
}

function updatePaddle() {
    // Keyboard controls
    if (keys['ArrowLeft'] || keys['a'] || keys['A']) {
        paddle.dx = -paddle.speed;
    } else if (keys['ArrowRight'] || keys['d'] || keys['D']) {
        paddle.dx = paddle.speed;
    } else {
        paddle.dx = 0;
    }
    
    // Mouse controls
    if (mouseX > 0 && mouseX < canvas.width) {
        paddle.x = mouseX - paddle.width / 2;
    }
    
    // Update paddle position
    paddle.x += paddle.dx;
    
    // Keep paddle within canvas bounds
    if (paddle.x < 0) {
        paddle.x = 0;
    }
    if (paddle.x + paddle.width > canvas.width) {
        paddle.x = canvas.width - paddle.width;
    }
}

function updateBall() {
    if (!ball.isLaunched) {
        ball.x = paddle.x + paddle.width / 2;
        ball.y = paddle.y - ball.radius;
        return;
    }
    
    ball.x += ball.dx;
    ball.y += ball.dy;
    
    // Wall collision
    if (ball.x + ball.radius > canvas.width || ball.x - ball.radius < 0) {
        ball.dx = -ball.dx;
    }
    
    if (ball.y - ball.radius < 0) {
        ball.dy = -ball.dy;
    }
    
    // Paddle collision
    if (ball.y + ball.radius > paddle.y && 
        ball.x > paddle.x && 
        ball.x < paddle.x + paddle.width &&
        ball.y - ball.radius < paddle.y + paddle.height) {
        
        // Calculate bounce angle based on where ball hits paddle
        const hitPos = (ball.x - paddle.x) / paddle.width;
        const angle = (hitPos - 0.5) * Math.PI / 3; // -30 to 30 degrees
        
        ball.dx = ball.speed * Math.sin(angle);
        ball.dy = -ball.speed * Math.cos(angle);
    }
    
    // Bottom wall collision (lose life)
    if (ball.y + ball.radius > canvas.height) {
        lives--;
        if (lives <= 0) {
            gameOver();
        } else {
            resetBall();
            resetPaddle();
        }
    }
}

function checkBrickCollision() {
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            const brick = bricks[c][r];
            if (brick.status === 1) {
                if (ball.x > brick.x && 
                    ball.x < brick.x + brickWidth && 
                    ball.y > brick.y && 
                    ball.y < brick.y + brickHeight) {
                    
                    ball.dy = -ball.dy;
                    brick.status = 0;
                    score += 10;
                    
                    // Check if all bricks are destroyed
                    if (checkLevelComplete()) {
                        nextLevel();
                    }
                }
            }
        }
    }
}

function checkLevelComplete() {
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            if (bricks[c][r].status === 1) {
                return false;
            }
        }
    }
    return true;
}

function nextLevel() {
    level++;
    ball.speed += 0.5;
    resetBall();
    resetPaddle();
    resetBricks();
}

function gameOver() {
    gameState = 'gameOver';
}

function drawPaddle() {
    ctx.fillStyle = '#00ff00';
    ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
    
    // Add some visual effects
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    ctx.strokeRect(paddle.x, paddle.y, paddle.width, paddle.height);
}

function drawBall() {
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fillStyle = '#ff0000';
    ctx.fill();
    ctx.closePath();
    
    // Add glow effect
    ctx.shadowColor = '#ff0000';
    ctx.shadowBlur = 10;
    ctx.fill();
    ctx.shadowBlur = 0;
}

function drawBricks() {
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            if (bricks[c][r].status === 1) {
                const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
                const brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
                bricks[c][r].x = brickX;
                bricks[c][r].y = brickY;
                
                ctx.fillStyle = bricks[c][r].color;
                ctx.fillRect(brickX, brickY, brickWidth, brickHeight);
                
                // Add 3D effect
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 1;
                ctx.strokeRect(brickX, brickY, brickWidth, brickHeight);
            }
        }
    }
}

function drawUI() {
    // Update score display
    document.getElementById('score').textContent = score;
    document.getElementById('lives').textContent = lives;
    document.getElementById('level').textContent = level;
}

function drawMenu() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#fff';
    ctx.font = '48px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('ARKANOID', canvas.width / 2, canvas.height / 2 - 50);
    
    ctx.font = '24px Arial';
    ctx.fillText('Click or Press SPACE to Start', canvas.width / 2, canvas.height / 2 + 20);
    ctx.fillText('Use arrow keys or mouse to move', canvas.width / 2, canvas.height / 2 + 50);
    ctx.fillText('Press P to pause', canvas.width / 2, canvas.height / 2 + 80);
}

function drawPause() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#fff';
    ctx.font = '36px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('PAUSED', canvas.width / 2, canvas.height / 2);
    ctx.font = '18px Arial';
    ctx.fillText('Press P to resume', canvas.width / 2, canvas.height / 2 + 40);
}

function drawGameOver() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#ff0000';
    ctx.font = '48px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2 - 50);
    
    ctx.fillStyle = '#fff';
    ctx.font = '24px Arial';
    ctx.fillText(`Final Score: ${score}`, canvas.width / 2, canvas.height / 2);
    ctx.fillText('Refresh page to play again', canvas.width / 2, canvas.height / 2 + 40);
}

function draw() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw stars background
    ctx.fillStyle = '#fff';
    for (let i = 0; i < 50; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        ctx.fillRect(x, y, 1, 1);
    }
    
    if (gameState === 'menu') {
        drawMenu();
    } else if (gameState === 'playing') {
        drawBricks();
        drawPaddle();
        drawBall();
        drawUI();
    } else if (gameState === 'paused') {
        drawBricks();
        drawPaddle();
        drawBall();
        drawUI();
        drawPause();
    } else if (gameState === 'gameOver') {
        drawGameOver();
    }
}

function update() {
    if (gameState === 'playing') {
        updatePaddle();
        updateBall();
        checkBrickCollision();
        
        // Auto-launch ball if not launched
        if (!ball.isLaunched && (keys[' '] || mouseX > 0)) {
            launchBall();
        }
    }
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

// Start the game loop
gameLoop(); 