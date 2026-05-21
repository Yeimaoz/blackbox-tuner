from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class TuningConfig:
    direction: Literal["maximize", "minimize"] = "maximize"
    n_trials: int = 100
    seed: int | None = None
    run_id: str | None = None

    def __post_init__(self) -> None:
        if self.n_trials <= 0:
            raise ValueError("n_trials must be positive")
