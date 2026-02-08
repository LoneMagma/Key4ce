"""Entry point for Key4ce application."""

import sys


def main() -> int:
    """Main entry point for the application."""
    from key4ce.app import Key4ceApp
    
    app = Key4ceApp()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
