import subprocess
import sys


def main() -> None:
    try:
        subprocess.run([sys.executable, "-m", "ruff", "format", "."], check=False)
    finally:
        sys.stdout.write("{}\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
