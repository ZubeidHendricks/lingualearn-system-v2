# LinguaLearn System

A desktop application for capturing and preserving indigenous language terms using AI-powered object recognition.

## Features
- Real-time object detection using Meta's Segment Anything Model (SAM)
- Voice recording for local term capture
- Support for South African languages
- Offline capability for areas with limited connectivity
- Visual dictionary of terms with object recognition

## Prerequisites
- Node.js v16 or higher
- Python 3.8 or higher
- Webcam for object detection
- Microphone for voice recording

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ZubeidHendricks/lingualearn-system.git
cd lingualearn-system
```

### 2. Install Dependencies
There are known dependency conflicts that need to be resolved during installation. Follow these steps in order:

```bash
# Install react-scripts with legacy peer deps
npm install react-scripts --legacy-peer-deps

# Install required babel plugin
npm install @babel/plugin-proposal-private-property-in-object --legacy-peer-deps

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Install Model Files
Download the required model files:
- Download the SAM model file from Meta
- Place it in the `models` directory
- Update the model path in config if necessary

## Running the Application

```bash
# Start the application (this will start both React and Electron)
npm start
```

### Common Issues and Solutions

#### React Scripts Not Found
If you encounter the error "'react-scripts' is not recognized", run:
```bash
npm install react-scripts --legacy-peer-deps
```

#### Dependency Conflicts
If you see dependency conflict errors, use the `--legacy-peer-deps` flag:
```bash
npm install --legacy-peer-deps
```

## Development Setup

### Environment Setup
1. Camera access is required for object detection
2. Microphone access is required for voice recording
3. Ensure Python environment has all ML dependencies installed

### Directory Structure
```
lingualearn-system/
├── src/
│   ├── lingualearn/      # Python backend code
│   ├── main/            # Electron main process
│   └── components/      # React components
├── models/             # AI model files
├── tests/             # Test files
└── docs/              # Documentation
```

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
- Meta's Segment Anything Model (SAM)
- OpenAI's Whisper for voice recognition
- The indigenous language communities of South Africa