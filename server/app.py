from __future__ import annotations

# OpenEnv validate expects:
# - `server/app.py` to define a callable `main()`
# - the `server` script entry point to reference `server.app:main`
#
# We return the FastAPI app defined at the project root.
from app import app as _app


def main():
    return _app


if __name__ == "__main__":
    main()

