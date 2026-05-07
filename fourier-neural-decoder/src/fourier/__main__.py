from __future__ import annotations

import logging
import sys

from fourier.shared.config_loader import load_app_config

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def _configure_logging(debug: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format=LOG_FORMAT,
        stream=sys.stderr,
    )


def main() -> None:
    logger = logging.getLogger(__name__)
    try:
        app_config = load_app_config()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        logging.basicConfig(level=logging.ERROR, format=LOG_FORMAT, stream=sys.stderr)
        logger.error("startup error loading app_config: %s", exc)
        raise SystemExit(1) from exc

    _configure_logging(bool(app_config["debug"]))
    logger.info("fourier app starting on %s:%s (debug=%s)",
                app_config["host"], app_config["port"], app_config["debug"])

    try:
        from fourier.ui.app import create_app
        app = create_app()
        app.run(
            host=app_config["host"],
            port=int(app_config["port"]),
            debug=bool(app_config["debug"]),
        )
    except ImportError as exc:
        logger.error("UI not available: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
