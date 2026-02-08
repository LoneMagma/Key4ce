<div align="center">

# Key4ce

**A powerful keystroke visualization and analysis tool**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-pytest-orange.svg)](https://pytest.org)

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Demo](#demo) • [Contributing](#contributing)

</div>

---

## Demo

<!-- Add your demo GIF or video here -->
<!-- You can record terminal sessions with asciinema: https://asciinema.org/ -->
<!-- Or create GIFs with LICEcap: https://www.cockos.com/licecap/ -->

```bash
# Example usage
python -m key4ce --help
```

**📹 Add your demo here:**
- Record your terminal with [asciinema](https://asciinema.org/)
- Convert to GIF with [agg](https://github.com/asciinema/agg)
- Or use [terminalizer](https://terminalizer.com/) for animated terminal recordings

<!-- 
Example GIF embedding:
![Key4ce Demo](assets/demo.gif)
-->

---

## Features

### Core Functionality
- Real-time keystroke capture and analysis
- Cross-platform support (Windows, macOS, Linux)
- Customizable event handling
- Lightweight and performant

### Advanced Capabilities
- Keystroke pattern recognition
- Configurable logging and output
- Extensible architecture
- CLI interface

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from PyPI (when published)
```bash
pip install key4ce
```

### Install from source
```bash
git clone https://github.com/LoneMagma/Key4ce.git
cd Key4ce
pip install -e .
```

---

## Usage

### Quick Start

```python
from key4ce import KeystrokeListener

# Initialize the listener
listener = KeystrokeListener()

# Start capturing keystrokes
listener.start()
```

### CLI Interface

```bash
# Basic usage
key4ce start

# With custom configuration
key4ce start --config config.yaml

# View help
key4ce --help
```

### Configuration

Create a `config.yaml` file:

```yaml
logging:
  level: INFO
  output: keystrokes.log

capture:
  enabled: true
  filter_keys: []
```

---

## Project Structure

```
Key4ce/
├── key4ce/           # Main package
│   ├── __init__.py
│   ├── listener.py   # Core listener implementation
│   └── cli.py        # Command-line interface
├── tests/            # Test suite
├── docs/             # Documentation
├── pyproject.toml    # Project metadata
└── README.md
```

---

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/LoneMagma/Key4ce.git
cd Key4ce

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=key4ce

# Run specific test file
pytest tests/test_listener.py
```

### Code Quality

```bash
# Format code
black key4ce/

# Lint code
flake8 key4ce/

# Type checking
mypy key4ce/
```

---

## Adding Animations and GIFs

### Method 1: Asciinema (Recommended for Terminal)

1. Install asciinema:
   ```bash
   pip install asciinema
   ```

2. Record your session:
   ```bash
   asciinema rec demo.cast
   ```

3. Convert to GIF:
   ```bash
   # Install agg
   cargo install --git https://github.com/asciinema/agg
   
   # Convert
   agg demo.cast demo.gif
   ```

4. Add to README:
   ```markdown
   ![Demo](assets/demo.gif)
   ```

### Method 2: GIF Screen Recording

Use tools like:
- **LICEcap** (Windows/Mac): https://www.cockos.com/licecap/
- **Peek** (Linux): https://github.com/phw/peek
- **ScreenToGif** (Windows): https://www.screentogif.com/

### Method 3: Animated SVG Badges

Add dynamic badges from shields.io:

```markdown
![Build](https://img.shields.io/github/actions/workflow/status/LoneMagma/Key4ce/tests.yml?branch=main)
![Downloads](https://img.shields.io/pypi/dm/key4ce)
![Stars](https://img.shields.io/github/stars/LoneMagma/Key4ce?style=social)
```

### Method 4: GitHub Profile README Tricks

- **Typing SVG**: https://readme-typing-svg.demolab.com/
- **GitHub Stats**: https://github.com/anuraghazra/github-readme-stats
- **Activity Graph**: https://github.com/Ashutosh00710/github-readme-activity-graph

---

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with Python
- Powered by modern development tools
- Community-driven development

---

<div align="center">

**Made with ⚡ by [LoneMagma](https://github.com/LoneMagma)**

[![GitHub followers](https://img.shields.io/github/followers/LoneMagma?style=social)](https://github.com/LoneMagma)
[![GitHub stars](https://img.shields.io/github/stars/LoneMagma/Key4ce?style=social)](https://github.com/LoneMagma/Key4ce)

</div>
