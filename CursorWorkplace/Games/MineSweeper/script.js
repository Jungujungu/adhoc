class Minesweeper {
    constructor() {
        this.difficulties = {
            beginner: { rows: 9, cols: 9, mines: 10 },
            intermediate: { rows: 16, cols: 16, mines: 40 },
            expert: { rows: 16, cols: 30, mines: 99 }
        };
        
        this.currentDifficulty = 'beginner';
        this.gameBoard = [];
        this.mineLocations = new Set();
        this.revealedCells = new Set();
        this.flaggedCells = new Set();
        this.gameStarted = false;
        this.gameOver = false;
        this.gameWon = false;
        this.timer = 0;
        this.timerInterval = null;
        this.firstClick = true;
        
        this.initializeGame();
        this.setupEventListeners();
        this.loadStats();
    }
    
    initializeGame() {
        const config = this.difficulties[this.currentDifficulty];
        this.rows = config.rows;
        this.cols = config.cols;
        this.totalMines = config.mines;
        this.remainingMines = this.totalMines;
        
        this.createBoard();
        this.updateDisplay();
    }
    
    createBoard() {
        const gameBoard = document.getElementById('game-board');
        gameBoard.innerHTML = '';
        gameBoard.style.gridTemplateColumns = `repeat(${this.cols}, 1fr)`;
        
        this.gameBoard = [];
        this.mineLocations.clear();
        this.revealedCells.clear();
        this.flaggedCells.clear();
        
        // Create empty board
        for (let row = 0; row < this.rows; row++) {
            this.gameBoard[row] = [];
            for (let col = 0; col < this.cols; col++) {
                this.gameBoard[row][col] = {
                    isMine: false,
                    neighborMines: 0,
                    revealed: false,
                    flagged: false
                };
                
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                
                cell.addEventListener('click', (e) => this.handleLeftClick(row, col));
                cell.addEventListener('contextmenu', (e) => {
                    e.preventDefault();
                    this.handleRightClick(row, col);
                });
                
                gameBoard.appendChild(cell);
            }
        }
    }
    
    placeMines(firstRow, firstCol) {
        const config = this.difficulties[this.currentDifficulty];
        let minesPlaced = 0;
        
        while (minesPlaced < config.mines) {
            const row = Math.floor(Math.random() * this.rows);
            const col = Math.floor(Math.random() * this.cols);
            
            // Don't place mine on first click or if already a mine
            if ((row === firstRow && col === firstCol) || this.gameBoard[row][col].isMine) {
                continue;
            }
            
            this.gameBoard[row][col].isMine = true;
            this.mineLocations.add(`${row},${col}`);
            minesPlaced++;
        }
        
        // Calculate neighbor mines for all cells
        for (let row = 0; row < this.rows; row++) {
            for (let col = 0; col < this.cols; col++) {
                if (!this.gameBoard[row][col].isMine) {
                    this.gameBoard[row][col].neighborMines = this.countNeighborMines(row, col);
                }
            }
        }
    }
    
    countNeighborMines(row, col) {
        let count = 0;
        for (let dr = -1; dr <= 1; dr++) {
            for (let dc = -1; dc <= 1; dc++) {
                const newRow = row + dr;
                const newCol = col + dc;
                if (this.isValidCell(newRow, newCol) && this.gameBoard[newRow][newCol].isMine) {
                    count++;
                }
            }
        }
        return count;
    }
    
    isValidCell(row, col) {
        return row >= 0 && row < this.rows && col >= 0 && col < this.cols;
    }
    
    handleLeftClick(row, col) {
        if (this.gameOver || this.gameWon || this.flaggedCells.has(`${row},${col}`)) {
            return;
        }
        
        if (this.firstClick) {
            this.startGame();
            this.placeMines(row, col);
            this.firstClick = false;
        }
        
        if (this.gameBoard[row][col].isMine) {
            this.gameOver = true;
            this.revealAllMines();
            this.endGame(false);
            return;
        }
        
        this.revealCell(row, col);
        
        if (this.checkWin()) {
            this.gameWon = true;
            this.endGame(true);
        }
    }
    
    handleRightClick(row, col) {
        if (this.gameOver || this.gameWon || this.revealedCells.has(`${row},${col}`)) {
            return;
        }
        
        const cellKey = `${row},${col}`;
        const cell = this.gameBoard[row][col];
        
        if (cell.flagged) {
            cell.flagged = false;
            this.flaggedCells.delete(cellKey);
            this.remainingMines++;
        } else {
            cell.flagged = true;
            this.flaggedCells.add(cellKey);
            this.remainingMines--;
        }
        
        this.updateCellDisplay(row, col);
        this.updateMineCounter();
    }
    
    revealCell(row, col) {
        if (!this.isValidCell(row, col) || 
            this.revealedCells.has(`${row},${col}`) || 
            this.flaggedCells.has(`${row},${col}`)) {
            return;
        }
        
        const cellKey = `${row},${col}`;
        this.revealedCells.add(cellKey);
        this.gameBoard[row][col].revealed = true;
        
        this.updateCellDisplay(row, col);
        
        // If cell has no neighbor mines, reveal neighbors
        if (this.gameBoard[row][col].neighborMines === 0) {
            for (let dr = -1; dr <= 1; dr++) {
                for (let dc = -1; dc <= 1; dc++) {
                    this.revealCell(row + dr, col + dc);
                }
            }
        }
    }
    
    updateCellDisplay(row, col) {
        const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
        const gameCell = this.gameBoard[row][col];
        
        cell.className = 'cell';
        
        if (gameCell.flagged) {
            cell.textContent = '🚩';
            cell.classList.add('flagged');
        } else if (gameCell.revealed) {
            cell.classList.add('revealed');
            if (gameCell.isMine) {
                cell.textContent = '💣';
                cell.classList.add('mine');
            } else if (gameCell.neighborMines > 0) {
                cell.textContent = gameCell.neighborMines;
                cell.dataset.number = gameCell.neighborMines;
            } else {
                cell.textContent = '';
            }
        } else {
            cell.textContent = '';
        }
    }
    
    revealAllMines() {
        this.mineLocations.forEach(location => {
            const [row, col] = location.split(',').map(Number);
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            cell.textContent = '💣';
            cell.classList.add('mine');
            
            // Add explosion animation to the clicked mine
            if (this.revealedCells.has(location)) {
                cell.classList.add('mine-exploded');
            }
        });
    }
    
    checkWin() {
        return this.revealedCells.size === (this.rows * this.cols - this.totalMines);
    }
    
    startGame() {
        this.gameStarted = true;
        this.startTimer();
    }
    
    startTimer() {
        this.timer = 0;
        this.timerInterval = setInterval(() => {
            this.timer++;
            this.updateTimer();
        }, 1000);
    }
    
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
    
    endGame(won) {
        this.stopTimer();
        this.gameOver = true;
        
        const resetBtn = document.getElementById('reset-btn');
        if (won) {
            resetBtn.textContent = '😎';
            resetBtn.classList.add('game-won');
            this.updateStats(true);
        } else {
            resetBtn.textContent = '😵';
            resetBtn.classList.add('game-over');
        }
        
        this.showGameOverModal(won);
    }
    
    showGameOverModal(won) {
        const modal = document.getElementById('game-over-modal');
        const title = document.getElementById('modal-title');
        const message = document.getElementById('modal-message');
        
        if (won) {
            title.textContent = '🎉 Congratulations!';
            message.textContent = `You won in ${this.timer} seconds!`;
        } else {
            title.textContent = '💥 Game Over!';
            message.textContent = 'Better luck next time!';
        }
        
        modal.style.display = 'block';
    }
    
    resetGame() {
        this.gameOver = false;
        this.gameWon = false;
        this.gameStarted = false;
        this.firstClick = true;
        this.stopTimer();
        
        const resetBtn = document.getElementById('reset-btn');
        resetBtn.textContent = '😊';
        resetBtn.classList.remove('game-over', 'game-won');
        
        this.initializeGame();
    }
    
    updateDisplay() {
        this.updateMineCounter();
        this.updateTimer();
    }
    
    updateMineCounter() {
        document.getElementById('mine-count').textContent = this.remainingMines.toString().padStart(2, '0');
    }
    
    updateTimer() {
        document.getElementById('timer').textContent = this.timer.toString().padStart(3, '0');
    }
    
    updateStats(won) {
        if (won) {
            const gamesWon = parseInt(localStorage.getItem('minesweeper_games_won') || '0') + 1;
            localStorage.setItem('minesweeper_games_won', gamesWon.toString());
            
            const currentBest = localStorage.getItem(`minesweeper_best_time_${this.currentDifficulty}`);
            if (!currentBest || this.timer < parseInt(currentBest)) {
                localStorage.setItem(`minesweeper_best_time_${this.currentDifficulty}`, this.timer.toString());
            }
            
            this.loadStats();
        }
    }
    
    loadStats() {
        const gamesWon = localStorage.getItem('minesweeper_games_won') || '0';
        const bestTime = localStorage.getItem(`minesweeper_best_time_${this.currentDifficulty}`) || '--';
        
        document.getElementById('games-won').textContent = gamesWon;
        document.getElementById('best-time').textContent = bestTime === '--' ? '--' : `${bestTime}s`;
    }
    
    changeDifficulty(difficulty) {
        if (this.currentDifficulty !== difficulty) {
            this.currentDifficulty = difficulty;
            this.resetGame();
            
            // Update active button
            document.querySelectorAll('.difficulty-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`[data-difficulty="${difficulty}"]`).classList.add('active');
        }
    }
    
    setupEventListeners() {
        // Reset button
        document.getElementById('reset-btn').addEventListener('click', () => {
            this.resetGame();
        });
        
        // Difficulty buttons
        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.changeDifficulty(btn.dataset.difficulty);
            });
        });
        
        // Modal buttons
        document.getElementById('play-again-btn').addEventListener('click', () => {
            document.getElementById('game-over-modal').style.display = 'none';
            this.resetGame();
        });
        
        document.getElementById('close-modal-btn').addEventListener('click', () => {
            document.getElementById('game-over-modal').style.display = 'none';
        });
        
        // Close modal when clicking outside
        document.getElementById('game-over-modal').addEventListener('click', (e) => {
            if (e.target.id === 'game-over-modal') {
                e.target.style.display = 'none';
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'r' || e.key === 'R') {
                this.resetGame();
            }
        });
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new Minesweeper();
}); 