# Installation Guide

## Prerequisites

### Hardware Requirements
- CPU: Dual-core processor or better
- RAM: 8GB minimum (16GB recommended)
- Storage: 1GB free space
- Camera: Built-in or external webcam
- Microphone: Built-in or external microphone

### Software Requirements
- Windows 10/11, macOS 10.15+, or Ubuntu 20.04+
- Node.js 16 or higher
- Python 3.8 or higher

## Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/ZubeidHendricks/lingualearn-system.git
cd lingualearn-system
```

### 2. Install Dependencies

#### Node.js Dependencies
```bash
# Install react-scripts (required)
npm install react-scripts --legacy-peer-deps

# Install babel plugin (required)
npm install @babel/plugin-proposal-private-property-in-object --legacy-peer-deps

# Install other dependencies
npm install --legacy-peer-deps
```

#### Python Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/MacOS:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Download Model Files
1. Download SAM model from Meta
2. Place in `models/` directory
3. Update config if needed

## Running the Application

### Development Mode
```bash
# Start application
npm start
```

### Production Build
```bash
# Create production build
npm run build

# Start production version
npm run start:prod
```

## Common Issues

### Dependency Issues

#### React Scripts Not Found
```bash
npm install react-scripts --legacy-peer-deps
```

#### General Dependency Conflicts
```bash
npm install --legacy-peer-deps
```

### Python Issues

#### ImportError: No module named 'torch'
```bash
pip install torch torchvision
```

#### CUDA Not Found
```bash
# Install CUDA toolkit if needed
pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu117
```

## Platform-Specific Notes

### Windows
- Install Visual C++ Build Tools
- Add Python to PATH
- Check Windows SDK version

### macOS
- Install Xcode Command Line Tools
- Use Homebrew for dependencies

### Linux
- Install build-essential package
- Install Python3-dev package
- Configure webcam permissions