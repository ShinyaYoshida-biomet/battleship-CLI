#!/bin/bash
# Battleship CLI Installation Script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

print_color $BLUE "🚢 Battleship CLI Installer"
print_color $BLUE "=========================="

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

# Map architecture names
case $ARCH in
    x86_64|amd64)
        ARCH="x64"
        ;;
    aarch64|arm64)
        ARCH="arm64"
        ;;
    *)
        print_color $RED "❌ Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

# Map OS names
case $OS in
    linux)
        BINARY_NAME="battleship-linux-${ARCH}"
        INSTALL_DIR="/usr/local/bin"
        ;;
    darwin)
        BINARY_NAME="battleship-darwin-${ARCH}"
        INSTALL_DIR="/usr/local/bin"
        ;;
    mingw*|cygwin*|msys*)
        BINARY_NAME="battleship-windows-${ARCH}.exe"
        INSTALL_DIR="$HOME/bin"
        mkdir -p "$INSTALL_DIR"
        ;;
    *)
        print_color $RED "❌ Unsupported OS: $OS"
        exit 1
        ;;
esac

print_color $YELLOW "🔍 Detected: $OS-$ARCH"
print_color $YELLOW "📦 Binary: $BINARY_NAME"

# Get latest release info
print_color $BLUE "📡 Fetching latest release..."
LATEST_RELEASE=$(curl -s https://api.github.com/repos/ShinyaYoshida-biomet/battleship-CLI/releases/latest)
DOWNLOAD_URL=$(echo $LATEST_RELEASE | grep -o "https://github.com/ShinyaYoshida-biomet/battleship-CLI/releases/download/[^\"]*/$BINARY_NAME" | head -1)

if [ -z "$DOWNLOAD_URL" ]; then
    print_color $RED "❌ Could not find binary for your platform: $BINARY_NAME"
    print_color $YELLOW "Available binaries:"
    echo $LATEST_RELEASE | grep -o "https://github.com/ShinyaYoshida-biomet/battleship-CLI/releases/download/[^\"]*" | sed 's/.*\//  - /'
    exit 1
fi

print_color $BLUE "⬇️  Downloading from: $DOWNLOAD_URL"

# Download binary
TEMP_FILE="/tmp/battleship-cli"
if command -v wget >/dev/null 2>&1; then
    wget -q --show-progress -O "$TEMP_FILE" "$DOWNLOAD_URL"
elif command -v curl >/dev/null 2>&1; then
    curl -L --progress-bar -o "$TEMP_FILE" "$DOWNLOAD_URL"
else
    print_color $RED "❌ Neither wget nor curl is available"
    exit 1
fi

# Make executable
chmod +x "$TEMP_FILE"

# Install
print_color $BLUE "📦 Installing to $INSTALL_DIR..."

if [ "$OS" = "linux" ] || [ "$OS" = "darwin" ]; then
    # Unix-like systems
    if [ -w "$INSTALL_DIR" ]; then
        mv "$TEMP_FILE" "$INSTALL_DIR/battleship"
    else
        print_color $YELLOW "🔐 Need sudo permissions to install to $INSTALL_DIR"
        sudo mv "$TEMP_FILE" "$INSTALL_DIR/battleship"
    fi
    
    # Check if directory is in PATH
    if ! echo "$PATH" | grep -q "$INSTALL_DIR"; then
        print_color $YELLOW "⚠️  $INSTALL_DIR is not in your PATH"
        print_color $YELLOW "    Add this to your ~/.bashrc or ~/.zshrc:"
        print_color $BLUE "    export PATH=\"\$PATH:$INSTALL_DIR\""
    fi
else
    # Windows
    mv "$TEMP_FILE" "$INSTALL_DIR/battleship.exe"
    print_color $YELLOW "📝 Add $INSTALL_DIR to your PATH environment variable"
fi

# Test installation
print_color $BLUE "🧪 Testing installation..."
if command -v battleship >/dev/null 2>&1; then
    print_color $GREEN "✅ Installation successful!"
    print_color $GREEN "🚀 Run 'battleship' to start playing!"
else
    INSTALLED_PATH="$INSTALL_DIR/battleship"
    if [ "$OS" = "mingw" ] || [ "$OS" = "cygwin" ] || [ "$OS" = "msys" ]; then
        INSTALLED_PATH="$INSTALL_DIR/battleship.exe"
    fi
    
    if [ -f "$INSTALLED_PATH" ]; then
        print_color $YELLOW "✅ Binary installed at $INSTALLED_PATH"
        print_color $YELLOW "🔧 Add $INSTALL_DIR to your PATH to run 'battleship' from anywhere"
        print_color $BLUE "🚀 Or run directly: $INSTALLED_PATH"
    else
        print_color $RED "❌ Installation failed"
        exit 1
    fi
fi

print_color $BLUE ""
print_color $BLUE "🎮 Ready to play Battleship CLI!"
print_color $BLUE "📚 Visit: https://github.com/ShinyaYoshida-biomet/battleship-CLI"