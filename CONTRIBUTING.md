# Contributing to LinguaLearn

## Development Environment Setup

### Prerequisites
1. Node.js (v16+)
2. Python 3.8+
3. Git
4. A code editor (VS Code recommended)

### First Time Setup

1. **Clone and Install Dependencies**
```bash
# Clone the repository
git clone https://github.com/ZubeidHendricks/lingualearn-system.git
cd lingualearn-system

# Install Node dependencies
npm install react-scripts --legacy-peer-deps
npm install @babel/plugin-proposal-private-property-in-object --legacy-peer-deps

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Install ML Models**
- Download SAM model from Meta
- Place in `models/` directory
- Update config if needed

### Running for Development

1. **Start Development Servers**
```bash
# Start React + Electron
npm start

# In another terminal, start Python backend
python src/lingualearn/api/bridge.py
```

2. **Running Tests**
```bash
# Run all tests
npm test

# Run Python tests
python -m pytest tests/
```

## Project Structure

### Frontend (React + Electron)
- `src/components/` - React components
- `src/main/` - Electron main process
- `src/lingualearn/ui/` - UI-specific code

### Backend (Python)
- `src/lingualearn/api/` - API endpoints
- `src/lingualearn/core/` - Core logic
- `src/lingualearn/ml/` - Machine learning code

### Configuration Files
- `electron-builder.yml` - Electron build config
- `package.json` - Node.js dependencies
- `requirements.txt` - Python dependencies

## Common Development Tasks

### Adding New Features
1. Create a new branch
2. Add tests for the feature
3. Implement the feature
4. Update documentation
5. Submit PR

### Debugging Tips
1. Use Chrome DevTools for React (available in dev mode)
2. Use VS Code debugger for Python backend
3. Check Electron logs for main process issues

### Common Issues

#### Dependency Conflicts
```bash
# Clear dependencies and reinstall
rm -rf node_modules
npm install --legacy-peer-deps
```

#### Python Import Errors
```bash
# Ensure you're in the right directory and venv is activated
pip install -e .
```

## Release Process

1. **Version Update**
   - Update version in package.json
   - Update CHANGELOG.md

2. **Testing**
   - Run all tests
   - Test on different platforms

3. **Building**
```bash
# Build for all platforms
npm run build
```

4. **Distribution**
   - Create GitHub release
   - Upload built packages

## Code Style

### JavaScript/React
- Use ESLint configuration
- Follow React Hooks guidelines
- Use TypeScript types

### Python
- Follow PEP 8
- Use type hints
- Document with docstrings

## Getting Help

- Check existing issues
- Join developer discussions
- Review documentation
- Ask in development channel