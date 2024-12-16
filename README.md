# LinguaLearn

Real-time translation and language support system for South African classrooms using Meta's Seamless Communication models.

## Overview

LinguaLearn bridges language barriers in South African education using AI translation technology. The system leverages Meta's Seamless Communication models (SeamlessM4T v2, SeamlessExpressive, SeamlessStreaming) to provide real-time translation and language support in multilingual classrooms.

## Key Features

- Real-time translation of teacher instruction
- Expression and speaking style preservation
- Offline capabilities for areas with limited internet
- Support for South Africa's 11 official languages plus indigenous languages
- Classroom streaming interface
- Teacher control panel
- Student progress tracking
- Content adaptation system

## Project Structure

```
lingualearn/
├── src/
│   └── lingualearn/
│       ├── __init__.py          # Package initialization
│       ├── translation.py       # Core translation system
│       ├── classroom.py        # Classroom management
│       └── streaming.py        # Real-time streaming
├── tests/                    # Test directory
└── requirements.txt         # Project dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ZubeidHendricks/lingualearn-system.git
cd lingualearn-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Detailed usage instructions coming soon.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.