import os
from pathlib import Path
from app.ui import CodeMentorApp


def load_env() -> None:
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


def main() -> None:
    load_env()  # Load .env file first
    app = CodeMentorApp()
    app.run()


if __name__ == "__main__":
    main()