class PaintTool {
    constructor() {
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.isDrawing = false;
        this.currentTool = 'brush';
        this.currentColor = '#000000';
        this.brushSize = 5;
        this.opacity = 1;
        
        // Drawing state
        this.lastX = 0;
        this.lastY = 0;
        this.startX = 0;
        this.startY = 0;
        
        // Canvas size presets
        this.canvasSizes = {
            small: { width: 400, height: 300 },
            medium: { width: 800, height: 600 },
            large: { width: 1200, height: 800 },
            full: { width: window.innerWidth - 100, height: window.innerHeight - 200 }
        };
        
        this.initializeCanvas();
        this.setupEventListeners();
        this.updateStatus();
    }
    
    initializeCanvas() {
        // Set initial canvas size
        this.resizeCanvas('medium');
        
        // Set initial canvas background
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Set initial drawing settings
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.globalCompositeOperation = 'source-over';
    }
    
    setupEventListeners() {
        // Canvas events
        this.canvas.addEventListener('mousedown', this.startDrawing.bind(this));
        this.canvas.addEventListener('mousemove', this.draw.bind(this));
        this.canvas.addEventListener('mouseup', this.stopDrawing.bind(this));
        this.canvas.addEventListener('mouseout', this.stopDrawing.bind(this));
        
        // Touch events for mobile
        this.canvas.addEventListener('touchstart', this.handleTouch.bind(this));
        this.canvas.addEventListener('touchmove', this.handleTouch.bind(this));
        this.canvas.addEventListener('touchend', this.stopDrawing.bind(this));
        
        // Tool buttons
        document.getElementById('brushTool').addEventListener('click', () => this.setTool('brush'));
        document.getElementById('eraserTool').addEventListener('click', () => this.setTool('eraser'));
        document.getElementById('lineTool').addEventListener('click', () => this.setTool('line'));
        document.getElementById('rectangleTool').addEventListener('click', () => this.setTool('rectangle'));
        document.getElementById('circleTool').addEventListener('click', () => this.setTool('circle'));
        document.getElementById('fillTool').addEventListener('click', () => this.setTool('fill'));
        
        // Color palette
        document.querySelectorAll('.color-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setColor(e.target.dataset.color);
                document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
        
        // Custom color picker
        document.getElementById('customColor').addEventListener('change', (e) => {
            this.setColor(e.target.value);
            document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
        });
        
        // Brush size slider
        document.getElementById('brushSize').addEventListener('input', (e) => {
            this.brushSize = parseInt(e.target.value);
            document.getElementById('sizeValue').textContent = this.brushSize + 'px';
            this.updateStatus();
        });
        
        // Opacity slider
        document.getElementById('opacity').addEventListener('input', (e) => {
            this.opacity = parseInt(e.target.value) / 100;
            document.getElementById('opacityValue').textContent = e.target.value + '%';
            this.updateStatus();
        });
        
        // Canvas size buttons
        document.getElementById('smallCanvas').addEventListener('click', () => this.resizeCanvas('small'));
        document.getElementById('mediumCanvas').addEventListener('click', () => this.resizeCanvas('medium'));
        document.getElementById('largeCanvas').addEventListener('click', () => this.resizeCanvas('large'));
        document.getElementById('fullCanvas').addEventListener('click', () => this.resizeCanvas('full'));
        
        // Control buttons
        document.getElementById('clearBtn').addEventListener('click', () => this.clearCanvas());
        document.getElementById('saveBtn').addEventListener('click', () => this.saveImage());
        
        // Mouse coordinates display
        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = Math.round(e.clientX - rect.left);
            const y = Math.round(e.clientY - rect.top);
            document.getElementById('coordinates').textContent = `X: ${x}, Y: ${y}`;
        });
    }
    
    handleTouch(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const rect = this.canvas.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
        if (e.type === 'touchstart') {
            this.startDrawing({ clientX: touch.clientX, clientY: touch.clientY });
        } else if (e.type === 'touchmove') {
            this.draw({ clientX: touch.clientX, clientY: touch.clientY });
        }
    }
    
    startDrawing(e) {
        this.isDrawing = true;
        const rect = this.canvas.getBoundingClientRect();
        this.lastX = e.clientX - rect.left;
        this.lastY = e.clientY - rect.top;
        this.startX = this.lastX;
        this.startY = this.lastY;
        
        if (this.currentTool === 'fill') {
            this.floodFill(this.lastX, this.lastY);
        }
    }
    
    draw(e) {
        if (!this.isDrawing) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;
        
        this.ctx.globalAlpha = this.opacity;
        
        switch (this.currentTool) {
            case 'brush':
                this.drawBrush(currentX, currentY);
                break;
            case 'eraser':
                this.drawEraser(currentX, currentY);
                break;
            case 'line':
                this.previewLine(currentX, currentY);
                break;
            case 'rectangle':
                this.previewRectangle(currentX, currentY);
                break;
            case 'circle':
                this.previewCircle(currentX, currentY);
                break;
        }
        
        this.lastX = currentX;
        this.lastY = currentY;
    }
    
    stopDrawing() {
        if (!this.isDrawing) return;
        
        this.isDrawing = false;
        
        // Finalize shape drawing
        if (['line', 'rectangle', 'circle'].includes(this.currentTool)) {
            this.finalizeShape();
        }
    }
    
    drawBrush(x, y) {
        this.ctx.globalCompositeOperation = 'source-over';
        this.ctx.strokeStyle = this.currentColor;
        this.ctx.lineWidth = this.brushSize;
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.lastX, this.lastY);
        this.ctx.lineTo(x, y);
        this.ctx.stroke();
    }
    
    drawEraser(x, y) {
        this.ctx.globalCompositeOperation = 'destination-out';
        this.ctx.strokeStyle = 'rgba(0,0,0,1)';
        this.ctx.lineWidth = this.brushSize;
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.lastX, this.lastY);
        this.ctx.lineTo(x, y);
        this.ctx.stroke();
    }
    
    previewLine(x, y) {
        // Clear the canvas and redraw everything except the current preview
        this.redrawCanvas();
        
        this.ctx.globalCompositeOperation = 'source-over';
        this.ctx.strokeStyle = this.currentColor;
        this.ctx.lineWidth = this.brushSize;
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.startX, this.startY);
        this.ctx.lineTo(x, y);
        this.ctx.stroke();
    }
    
    previewRectangle(x, y) {
        this.redrawCanvas();
        
        this.ctx.globalCompositeOperation = 'source-over';
        this.ctx.strokeStyle = this.currentColor;
        this.ctx.lineWidth = this.brushSize;
        
        const width = x - this.startX;
        const height = y - this.startY;
        
        this.ctx.strokeRect(this.startX, this.startY, width, height);
    }
    
    previewCircle(x, y) {
        this.redrawCanvas();
        
        this.ctx.globalCompositeOperation = 'source-over';
        this.ctx.strokeStyle = this.currentColor;
        this.ctx.lineWidth = this.brushSize;
        
        const radius = Math.sqrt(Math.pow(x - this.startX, 2) + Math.pow(y - this.startY, 2));
        
        this.ctx.beginPath();
        this.ctx.arc(this.startX, this.startY, radius, 0, 2 * Math.PI);
        this.ctx.stroke();
    }
    
    finalizeShape() {
        // The shape is already drawn in the preview, so we just need to update the status
        this.updateStatus();
    }
    
    floodFill(startX, startY) {
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const pixels = imageData.data;
        
        const startPos = (startY * this.canvas.width + startX) * 4;
        const startR = pixels[startPos];
        const startG = pixels[startPos + 1];
        const startB = pixels[startPos + 2];
        const startA = pixels[startPos + 3];
        
        // Convert current color to RGB
        const targetColor = this.hexToRgb(this.currentColor);
        
        if (startR === targetColor.r && startG === targetColor.g && startB === targetColor.b) {
            return; // Same color, no need to fill
        }
        
        const stack = [[startX, startY]];
        
        while (stack.length > 0) {
            const [x, y] = stack.pop();
            const pos = (y * this.canvas.width + x) * 4;
            
            if (x < 0 || x >= this.canvas.width || y < 0 || y >= this.canvas.height) continue;
            if (pixels[pos] !== startR || pixels[pos + 1] !== startG || 
                pixels[pos + 2] !== startB || pixels[pos + 3] !== startA) continue;
            
            pixels[pos] = targetColor.r;
            pixels[pos + 1] = targetColor.g;
            pixels[pos + 2] = targetColor.b;
            pixels[pos + 3] = Math.round(this.opacity * 255);
            
            stack.push([x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]);
        }
        
        this.ctx.putImageData(imageData, 0, 0);
    }
    
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }
    
    redrawCanvas() {
        // This would need to be implemented with a proper undo/redo system
        // For now, we'll just redraw the current state
        // In a real implementation, you'd want to store the canvas state before drawing
    }
    
    setTool(tool) {
        this.currentTool = tool;
        
        // Update active tool button
        document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(tool + 'Tool').classList.add('active');
        
        this.updateStatus();
    }
    
    setColor(color) {
        this.currentColor = color;
        document.getElementById('customColor').value = color;
        this.updateStatus();
    }
    
    resizeCanvas(size) {
        const dimensions = this.canvasSizes[size];
        
        // Store current canvas content
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        tempCanvas.width = this.canvas.width;
        tempCanvas.height = this.canvas.height;
        tempCtx.drawImage(this.canvas, 0, 0);
        
        // Resize canvas
        this.canvas.width = dimensions.width;
        this.canvas.height = dimensions.height;
        
        // Restore canvas content
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(tempCanvas, 0, 0);
        
        // Update active size button
        document.querySelectorAll('.size-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(size + 'Canvas').classList.add('active');
        
        this.updateStatus();
    }
    
    clearCanvas() {
        if (confirm('Are you sure you want to clear the canvas?')) {
            this.ctx.fillStyle = '#ffffff';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            this.updateStatus();
        }
    }
    
    saveImage() {
        const link = document.createElement('a');
        link.download = 'paint-tool-image.png';
        link.href = this.canvas.toDataURL();
        link.click();
    }
    
    updateStatus() {
        const toolNames = {
            brush: 'Brush Tool',
            eraser: 'Eraser Tool',
            line: 'Line Tool',
            rectangle: 'Rectangle Tool',
            circle: 'Circle Tool',
            fill: 'Fill Tool'
        };
        
        const colorNames = {
            '#000000': 'Black',
            '#ff0000': 'Red',
            '#00ff00': 'Green',
            '#0000ff': 'Blue',
            '#ffff00': 'Yellow',
            '#ff00ff': 'Magenta',
            '#00ffff': 'Cyan',
            '#ffa500': 'Orange',
            '#800080': 'Purple',
            '#008000': 'Dark Green',
            '#ffffff': 'White',
            '#808080': 'Gray'
        };
        
        const toolInfo = `${toolNames[this.currentTool]} | Size: ${this.brushSize}px | Color: ${colorNames[this.currentColor] || this.currentColor}`;
        document.getElementById('toolInfo').textContent = toolInfo;
        
        const status = `Canvas: ${this.canvas.width} × ${this.canvas.height} | Opacity: ${Math.round(this.opacity * 100)}%`;
        document.getElementById('status').textContent = status;
    }
}

// Initialize the paint tool when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new PaintTool();
});

// Handle window resize for full canvas mode
window.addEventListener('resize', () => {
    const fullCanvasBtn = document.getElementById('fullCanvas');
    if (fullCanvasBtn.classList.contains('active')) {
        // Recalculate full canvas size
        const paintTool = window.paintTool;
        if (paintTool) {
            paintTool.canvasSizes.full = {
                width: window.innerWidth - 100,
                height: window.innerHeight - 200
            };
            paintTool.resizeCanvas('full');
        }
    }
}); 