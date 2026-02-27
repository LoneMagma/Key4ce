# Key4ce

A minimalist, cross-platform terminal typing game with rich analytics and configurable aesthetics.

## Features

- **Clean, Minimal UI** - Focus on what matters: your typing
- **Real-time Analytics** - WPM, accuracy, consistency tracking
- **Configurable Everything** - Themes, animations, all via YAML
- **Multiple Text Sources** - Custom files, Project Gutenberg, GitHub code
- **Ghost Racer** - Compete against your best performance
- **Comprehensive Reports** - Detailed post-session analysis

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd Key4ce

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

## Usage

```bash
# Run the game
key4ce

# Or run as module
python -m key4ce
```

## Configuration

Configuration files are stored in platform-appropriate locations:
- **Windows**: `%APPDATA%/Key4ce/`
- **macOS**: `~/Library/Application Support/Key4ce/`
- **Linux**: `~/.config/key4ce/`

### Files
- `settings.yaml` - Main application settings
- `themes.yaml` - Color theme definitions
- `animations.yaml` - Animation configurations

## Controls

| Key | Action |
|-----|--------|
| Arrow Keys | Navigate menus |
| Enter | Select option |
| Escape | Back / Quit |
| ? | Help |

## License

MIT License
