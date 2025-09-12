# 🚢 Battleship CLI

<img width="454" alt="Battleship CLI Game" src="https://github.com/ShinyaYoshida-biomet/battleship-CLI/assets/33049408/8b26714d-93f3-4f64-a6e7-fc24f80c1010">

## ✨ Features

- **🎮 Multiple Game Modes**: Player vs Player or Player vs Computer
- **🤖 Smart AI Opponent**: Intelligent computer player with strategic thinking
- **🎨 Modern Terminal UI**: Beautiful interface with colors, tables, and side-by-side board display
- **⚙️ Flexible Configuration**: CLI arguments or traditional config files
- **📱 Responsive Design**: Works great on different terminal sizes
- **🚀 Fast Setup**: No config files required - just run and play!

## 🎯 What is Battleship?

Battleship is a classic strategy game where players place ships on a grid and take turns guessing locations to sink their opponent's fleet. If you're new to the game, check out the rules on [Wikipedia](https://en.wikipedia.org/wiki/Battleship_(game)).

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ShinyaYoshida-biomet/battleship-CLI.git
cd battleship-CLI

# Install dependencies
pip install -r requirements.txt
```

### Run the Game

```bash
# Quick start - play against computer
python main.py --mode pvc --player1 YourName

# Or just run with prompts
python main.py
```

## 🎮 Game Modes

### Quick Commands

```bash
# Player vs Computer (recommended for quick games)
python main.py --mode pvc --player1 Alice

# Player vs Player
python main.py --mode pvp --player1 Alice --player2 Bob

# Custom board size and ships
python main.py --mode pvc --board-size 8 8 --ships B:4 D:3 P:2

# Get help with all options
python main.py --help
```

### Default Ships (Optimized for Quick Games)

- **B** - Battleship (4 cells)
- **D** - Destroyer (3 cells)  
- **P** - Patrol boat (2 cells)

### Advanced Configuration

```bash
# Large board with classic ships
python main.py --ships C:5 B:4 D:3 S:3 P:2 --board-size 12 12

# Use traditional config file
python main.py --config config_files/battleship_config.txt
```

## 🎨 Modern UI Features

- **Side-by-side Board Display**: See your attack board and ship positions simultaneously
- **Color-coded Results**: Green for hits, red for misses, blue for ships
- **Interactive Prompts**: Clear, guided input with validation
- **Beautiful Tables**: Rich formatting for enhanced gameplay experience
- **Real-time Feedback**: Immediate visual confirmation of actions

## 🤖 AI Features

- **Smart Ship Placement**: AI strategically places ships to avoid predictable patterns
- **Hunt/Target Strategy**: AI uses intelligent firing patterns to locate and sink ships
- **Adaptive Behavior**: AI learns from hits to systematically destroy ships

## 📋 CLI Reference

```bash
usage: main.py [-h] [--mode {pvp,pvc,prompt}] [--board-size ROWS COLS]
               [--ships [NAME:SIZE ...]] [--config PATH] 
               [--player1 PLAYER1] [--player2 PLAYER2]

Options:
  --mode {pvp,pvc,prompt}     Game mode (default: prompt)
  --board-size ROWS COLS      Board dimensions (default: 10 10)
  --ships [NAME:SIZE ...]     Custom ships (default: B:4 D:3 P:2)
  --config PATH               Use config file
  --player1, --player2        Player names
```

## 🛠️ Dependencies

- **Python 3.10+**
- **Rich** - Terminal UI library
- **Typer** - Modern CLI framework
- **Pandas** - Data manipulation for game boards

## 🤝 Contributing

Contributions are welcome! This project uses:

- Object-oriented design with clear separation of concerns
- Type hints throughout the codebase
- Google-style docstrings
- Rich library for modern terminal UI

## 📜 License

This project is open source. Feel free to use, modify, and distribute as needed.
