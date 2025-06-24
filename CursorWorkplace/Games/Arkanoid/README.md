# Arkanoid Game

A classic Arkanoid/Breakout game built with HTML5 Canvas and JavaScript.

## How to Play

1. **Start the Game**: Open `index.html` in your web browser
2. **Launch the Ball**: Click or press SPACE to start the game and launch the ball
3. **Control the Paddle**: 
   - Use left/right arrow keys or A/D keys
   - Move your mouse over the canvas
4. **Objective**: Break all the bricks without letting the ball fall below the paddle
5. **Scoring**: Each brick destroyed gives you 10 points
6. **Lives**: You start with 3 lives. Lose a life when the ball falls below the paddle
7. **Levels**: Complete a level by destroying all bricks. Each new level increases ball speed

## Controls

- **Arrow Keys** or **A/D**: Move paddle left/right
- **Mouse**: Move paddle by moving mouse over the canvas
- **SPACE**: Launch ball (when not already launched)
- **P**: Pause/Resume game
- **Click**: Start game from menu

## Features

- **Smooth Gameplay**: 60 FPS animation using requestAnimationFrame
- **Multiple Control Schemes**: Keyboard and mouse support
- **Visual Effects**: Glowing ball, 3D brick effects, starry background
- **Progressive Difficulty**: Ball speed increases with each level
- **Responsive Design**: Modern UI with gradient background
- **Game States**: Menu, playing, paused, and game over states
- **Score Tracking**: Real-time score, lives, and level display

## Game Mechanics

- **Ball Physics**: Ball bounces off walls, paddle, and bricks
- **Paddle Bounce**: Ball direction changes based on where it hits the paddle
- **Collision Detection**: Precise collision detection for all game objects
- **Level Progression**: Automatic level advancement when all bricks are destroyed

## Files

- `index.html` - Main HTML file with game canvas and styling
- `game.js` - Complete game logic and mechanics
- `README.md` - This file with game instructions

## Browser Compatibility

This game works in all modern browsers that support HTML5 Canvas:
- Chrome
- Firefox
- Safari
- Edge

## Running the Game

Simply open `index.html` in any modern web browser. No additional setup or dependencies required!

Enjoy playing Arkanoid! 🎮 