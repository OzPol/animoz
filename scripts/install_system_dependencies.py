"""Install the shared native prerequisites on Debian or Ubuntu."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Bootstrap from the checkout: this script must work before a venv exists.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from animoz.runtime import load_runtime  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print-packages", action="store_true")
    args = parser.parse_args()
    packages = load_runtime().system_packages
    if args.print_packages:
        print(" ".join(packages))
        return
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        parser.error(
            "Run with sudo on Debian/Ubuntu, or use the development container."
        )
    subprocess.run(["apt-get", "update"], check=True)
    subprocess.run(
        ["apt-get", "install", "-y", "--no-install-recommends", "--", *packages],
        check=True,
    )


if __name__ == "__main__":
    main()
