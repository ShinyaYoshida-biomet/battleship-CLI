# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-09-13

### 🎉 Initial Release

#### Added
- **Beautiful Terminal UI** with Rich library integration
- **Two Game Modes**: Player vs Player (PvP) and Player vs Computer (PvC)  
- **Smart AI Opponent** with hunt/target strategy
- **Flexible Ship Placement**: Manual or random automatic placement
- **Real-time Battle Status**: Live fleet status and enemy intel tracking
- **Cross-platform Support**: Windows, macOS, Linux binaries
- **Easy Installation**: One-liner curl install script
- **Interactive Controls**: Intuitive prompts with arrow key navigation
- **Safe Exit**: Ctrl+C graceful termination
- **Customizable Game Settings**: Board size and ship configurations

#### Features
- Side-by-side board display (attack board + your ships)
- Color-coded battle results (🎯 hits, ❌ misses)
- Enemy intel with estimated damage tracking
- Ship status panels with real-time updates
- Strategic AI ship placement
- Adaptive AI firing patterns
- Multiple ship types (Battleship, Destroyer, Patrol boat)
- Command-line argument support
- Configuration file support

#### Technical
- Built with Python 3.11+
- Rich terminal UI library
- Typer CLI framework
- Pandas for game board management
- PyInstaller for binary distribution
- GitHub Actions CI/CD pipeline
- Cross-platform binary builds

### 🚀 Getting Started
```bash
# Easy install (no Python required)
curl -sSL https://raw.githubusercontent.com/ShinyaYoshida-biomet/battleship-CLI/main/install.sh | bash

# Run the game
battleship
```

---

## Planned for Future Releases

### [1.1.0] - Planned
- [ ] Network multiplayer support
- [ ] Tournament mode
- [ ] Advanced AI difficulty levels
- [ ] Ship customization options
- [ ] Game replay system
- [ ] Statistics tracking
- [ ] Theme customization

### [1.2.0] - Planned  
- [ ] Docker container support
- [ ] Package manager distribution (Homebrew, Chocolatey)
- [ ] Mobile terminal support improvements
- [ ] Localization (multiple languages)
- [ ] Plugin system for custom game modes