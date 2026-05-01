from __future__ import annotations

import sys

from fourier.shared.config_loader import load_app_config, load_rate_limits


def main() -> None:
    try:
        app_config = load_app_config()
        load_rate_limits()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"[fourier] startup error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    try:
        from fourier.ui.app import create_app

        app = create_app()
        app.run(
            host=app_config["host"],
            port=int(app_config["port"]),
            debug=bool(app_config["debug"]),
        )
    except ImportError as exc:
        print(f"[fourier] UI not available: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
