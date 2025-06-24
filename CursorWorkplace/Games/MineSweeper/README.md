# 💣 Minesweeper Game

A modern, responsive implementation of the classic Minesweeper game built with HTML5, CSS3, and JavaScript.

## 🎮 Features

- **Three Difficulty Levels:**
  - **Beginner:** 9x9 grid with 10 mines
  - **Intermediate:** 16x16 grid with 40 mines
  - **Expert:** 16x30 grid with 99 mines

- **Game Mechanics:**
  - Left-click to reveal cells
  - Right-click to flag/unflag mines
  - Automatic neighbor cell revelation for empty cells
  - Mine counter and timer
  - First-click guarantee (never hit a mine on first click)

- **Visual Features:**
  - Modern, responsive design
  - Color-coded numbers (1-8)
  - Smooth animations and transitions
  - Emoji indicators (💣 for mines, 🚩 for flags)
  - Game over modal with results

- **Statistics:**
  - Best time tracking per difficulty
  - Total games won counter
  - Local storage persistence

- **Controls:**
  - Mouse: Left-click to reveal, right-click to flag
  - Keyboard: Press 'R' to reset game
  - Reset button with dynamic emoji states

## 🚀 How to Play

1. **Open the Game:** Simply open `index.html` in any modern web browser
2. **Choose Difficulty:** Select from Beginner, Intermediate, or Expert
3. **Start Playing:** Click on any cell to begin
4. **Flag Mines:** Right-click on cells you suspect contain mines
5. **Win Condition:** Reveal all non-mine cells to win
6. **Lose Condition:** Click on a mine to lose

## 🎯 Game Rules

- Numbers indicate how many mines are adjacent to that cell
- Empty cells (no adjacent mines) automatically reveal their neighbors
- Flag all mines and reveal all safe cells to win
- The game tracks your best time for each difficulty level

## 📱 Responsive Design

The game is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🛠️ Technical Details

- **Pure HTML5/CSS3/JavaScript** - No external dependencies
- **ES6 Classes** - Modern JavaScript architecture
- **CSS Grid** - Responsive game board layout
- **Local Storage** - Persistent statistics
- **Event-Driven** - Clean event handling

## 📁 File Structure

```
MineSweeper/
├── index.html      # Main HTML file
├── style.css       # Styles and responsive design
├── script.js       # Game logic and functionality
└── README.md       # This file
```

## 🎨 Customization

The game is easily customizable:
- Modify difficulty settings in the `difficulties` object
- Adjust colors and styling in `style.css`
- Add new features by extending the `Minesweeper` class

## 🌟 Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## 📝 License

This project is open source and available under the MIT License.

---

**Enjoy playing Minesweeper!** 🎉 