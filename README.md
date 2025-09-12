# 🚢 Battleship CLI

<img width="454" alt="Battleship CLI Game" src="https://github.com/ShinyaYoshida-biomet/battleship-CLI/assets/33049408/8b26714d-93f3-4f64-a6e7-fc24f80c1010">

## 💖 Welcome to Battleship CLI!

Welcome to the world of naval warfare! This is a beautiful, beginner-friendly terminal-based Battleship game that anyone can enjoy. 🎮

## ✨ Key Features

- **🎯 Two Game Modes**: Play against friends (PvP) or challenge the computer (PvC)
- **🤖 Smart AI Opponent**: Intelligent computer player with strategic thinking
- **🎨 Beautiful UI**: Colorful and easy-to-read terminal interface
- **🎲 Easy Ship Placement**: Choose between manual placement or automatic random placement
- **📊 Real-time Battle Status**: Live tracking of enemy fleet destruction progress
- **⌨️ Smooth Controls**: Intuitive operation with safe Ctrl+C exit anytime

## 🎯 What is Battleship?

Battleship is a classic strategy game where players place ships on a grid and take turns guessing locations to sink their opponent's fleet. The first player to sink all enemy ships wins!

## 🚀 Let's Get Started!

### Step 1: Installation

First, download the game and install the required libraries:

```bash
# Clone the repository (download)
git clone https://github.com/ShinyaYoshida-biomet/battleship-CLI.git
cd battleship-CLI

# Install required libraries
pip install -r requirements.txt
```

💡 **Need help?**: If Python isn't installed, download it from the [official Python website](https://www.python.org/downloads/).

### Step 2: Starting the Game

**For beginners** (easiest way):

```bash
# Super simple! Follow the prompts to set up your game
python main.py
```

**For experienced players** (direct setup):

```bash
# Play against computer (enter your name)
python main.py --mode pvc --player1 YourName

# Play against a friend
python main.py --mode pvp --player1 Player1 --player2 Player2
```

### Step 3: Game Flow

1. **Choose Ship Placement Method**
   - 🎯 Manual: Place each ship one by one
   - 🎲 Random: Automatically place all ships

2. **Place Your Ships**
   - Specify coordinates and orientation (horizontal/vertical)
   - Example: `h 0 0` (horizontal, starting at row 0, column 0)

3. **Battle Begins!**
   - Guess enemy ship locations and attack
   - Example: `3 7` (attack row 3, column 7)
   - 🎯 = Hit, ❌ = Miss

4. **Victory Condition**
   - Sink all enemy ships to win!

## 🎮 Game Modes & Commands

### Basic Commands

```bash
# Play against computer (recommended for beginners)
python main.py --mode pvc --player1 Alice

# Play against a friend
python main.py --mode pvp --player1 Alice --player2 Bob

# Custom board and ship settings
python main.py --mode pvc --board-size 8 8 --ships B:4 D:3 P:2

# See all available options
python main.py --help
```

### Default Ships (Optimized for Quick Games)

- **B** - Battleship (4 cells)
- **D** - Destroyer (3 cells)  
- **P** - Patrol boat (2 cells)

### Advanced Configuration

```bash
# Large board with classic ship setup
python main.py --ships C:5 B:4 D:3 S:3 P:2 --board-size 12 12

# Use traditional config file
python main.py --config config_files/battleship_config.txt
```

## 🆘 Troubleshooting & Tips

### Common Issues & Solutions

1. **"pip install gives errors"**
   ```bash
   # Try using python3
   python3 -m pip install -r requirements.txt
   
   # Or create a virtual environment
   python -m venv battleship-env
   source battleship-env/bin/activate  # Windows: battleship-env\Scripts\activate
   pip install -r requirements.txt
   ```

2. **"Game freezes or stops"**
   - Press Ctrl+C to safely exit anytime
   - Try making your terminal window larger

3. **"I don't understand coordinates"**
   - Enter row (vertical), then column (horizontal)
   - Coordinates start from 0 (0,1,2,3...)
   - Example: Top-right corner is `0 6` (for 7x7 board)

### Gameplay Tips 💡

- **Ship Placement**: `h 2 3` = place horizontally starting at row 2, column 3
- **Ship Placement**: `v 1 0` = place vertically starting at row 1, column 0  
- **Attacking**: `4 5` = attack row 4, column 5
- **Exit**: Press Ctrl+C anytime to safely quit

## 🎨 Beautiful UI Features

### Battle Status Display
```
╭──────── 📊 Fleet Status ────────╮    ╭──────── 📊 Enemy Intel ─────────╮
│ 🚢 Your Fleet:                  │    │ 🎯 Enemy Fleet:                 │
│   ✅ Battleship: INTACT (4/4)   │    │   ⚠️  Battleship: HIT/DAMAGED   │
│   💥 Destroyer: DESTROYED       │    │   💥 Destroyer: DESTROYED       │
│   ⚠️  Patrol boat: DAMAGED (1/2) │    │   ❓ Patrol boat: UNKNOWN       │
╰─────────────────────────────────╯    ╰───────────────────────────────── ╯
```

### Key Features
- **Side-by-side Board Display**: View your attack board and ship positions simultaneously
- **Color-coded Results**: 🎯 Hit=Green, ❌ Miss=Red, 🚢 Ships=Blue
- **Real-time Updates**: Enemy fleet destruction status updates instantly
- **Beautiful Tables**: Clean formatting enhances gameplay experience

## 🤖 AI Features (Computer Battles)

- **Strategic Ship Placement**: AI uses unpredictable patterns to place ships
- **Hunt/Target Strategy**: Intelligent firing patterns to locate and sink ships
- **Adaptive Learning**: AI systematically destroys ships after scoring hits

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

## 🎉 Ready to Battle?

This Battleship CLI is designed for everyone from beginners to experienced players. If you need help:

- Run `python main.py --help` for all available options
- Press Ctrl+C to safely exit anytime
- Report bugs or request features via [Issues](https://github.com/ShinyaYoshida-biomet/battleship-CLI/issues)

**Have an amazing battleship experience!** ⚓️

---

## 🛠️ Technical Details

### Dependencies

- **Python 3.10+**
- **Rich** - Beautiful terminal UI library
- **Typer** - Modern CLI framework  
- **Pandas** - Data manipulation for game boards
- **inquirer3** - Interactive prompts with arrow key navigation

### Installation

```bash
pip install rich typer pandas inquirer3
```

## 🤝 Contributing

Contributions are welcome! This project uses:

- Object-oriented design with clear separation of concerns
- Type hints throughout the codebase
- Google-style docstrings
- Rich library for modern terminal UI
- MVC architecture for clean code structure

## 📜 License

This project is open source. Feel free to use, modify, and distribute as needed.

---

**🚢 Happy Battleshipping!** Made with ❤️ for terminal game lovers.
