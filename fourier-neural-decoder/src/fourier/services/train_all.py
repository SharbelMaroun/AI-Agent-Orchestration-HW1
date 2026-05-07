"""Terminal entry point — train RNN, LSTM, and FC regressors back-to-back.

Usage:
    uv run python -m fourier.services.train_all                  # all three, with noise
    uv run python -m fourier.services.train_all rnn              # one model, with noise
    uv run python -m fourier.services.train_all rnn fc           # subset, with noise
    uv run python -m fourier.services.train_all --clean          # all three, NO noise
    uv run python -m fourier.services.train_all --clean rnn      # one model, NO noise

In `--clean` mode, alpha_train_max and beta_train_max are forced to 0 and
weights are saved to weights/{model}_regressor_clean.pt so the noisy weights
on disk are not overwritten.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from fourier.services.train_fc import train_fc
from fourier.services.train_lstm import train_lstm
from fourier.services.train_rnn import train_rnn
from fourier.shared.config_loader import load_training_config

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

_TRAINERS = {"rnn": train_rnn, "lstm": train_lstm, "fc": train_fc}


def _clean_suffix(weights_path: str) -> Path:
    """weights/rnn_regressor.pt -> weights/rnn_regressor_clean.pt"""
    p = Path(weights_path)
    return p.with_name(f"{p.stem}_clean{p.suffix}")


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, stream=sys.stderr)
    logger = logging.getLogger(__name__)

    args = list(argv if argv is not None else sys.argv[1:])
    clean = "--clean" in args
    args = [a for a in args if a != "--clean"]

    selected = args or list(_TRAINERS.keys())
    invalid = [a for a in selected if a not in _TRAINERS]
    if invalid:
        logger.error("unknown model(s): %s — choose from %s", invalid, list(_TRAINERS.keys()))
        return 2

    cfg = load_training_config()
    data_cfg = dict(cfg["data"])
    if clean:
        data_cfg["alpha_train_max"] = 0.0
        data_cfg["beta_train_max"] = 0.0
        logger.info("CLEAN MODE — α=β=0 during training, weights saved to *_clean.pt")

    for name in selected:
        sub_cfg = cfg[name]
        out_path = _clean_suffix(sub_cfg["weights_path"]) if clean else Path(sub_cfg["weights_path"])
        logger.info("=== training %s%s → %s ===", name, " (clean)" if clean else "", out_path)
        metrics = _TRAINERS[name](sub_cfg, data_cfg, out_path)
        logger.info("[%s] final %s", name, metrics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
