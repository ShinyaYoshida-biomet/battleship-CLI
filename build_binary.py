#!/usr/bin/env python3
"""
Build script for creating standalone binary executables.
"""
import os
import platform
import subprocess
import sys
from pathlib import Path

def build_binary():
    """Build standalone binary using PyInstaller."""
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Get platform info
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    # Map architecture names
    arch_map = {
        'x86_64': 'x64',
        'amd64': 'x64', 
        'arm64': 'arm64',
        'aarch64': 'arm64'
    }
    arch = arch_map.get(arch, arch)
    
    # Binary name
    binary_name = f"battleship-{system}-{arch}"
    if system == "windows":
        binary_name += ".exe"
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--name", binary_name,          # Output name
        "--add-data", "requirements.txt:.",  # Include requirements
        "--hidden-import", "pandas",
        "--hidden-import", "rich",
        "--hidden-import", "typer",
        "--hidden-import", "inquirer3",
        "--console",                    # Console application
        "--clean",                      # Clean cache
        "main.py"                      # Entry point
    ]
    
    print(f"Building binary: {binary_name}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        
        # Check if binary was created
        binary_path = Path("dist") / binary_name
        if binary_path.exists():
            print(f"✅ Binary created successfully: {binary_path}")
            print(f"Size: {binary_path.stat().st_size / (1024*1024):.1f} MB")
            
            # Test the binary
            print("Testing binary...")
            result = subprocess.run([str(binary_path), "--help"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Binary test successful!")
            else:
                print(f"⚠️ Binary test failed: {result.stderr}")
        else:
            print("❌ Binary not found in dist/ directory")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = build_binary()
    sys.exit(0 if success else 1)