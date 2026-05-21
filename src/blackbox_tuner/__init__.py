"""Public API for blackbox-tuner."""

from .checkpoints import CheckpointSink, JsonlCheckpoint
from .config import TuningConfig
from .errors import TrialPruned
from .events import TrialEvent
from .objective import ObjectiveResult, normalize_objective_result
from .runner import TuningResult, tune
from .schema import CategoricalParam, FloatParam, IntParam, ParamSchema

__version__ = "0.1.0"

__all__ = [
    "CategoricalParam",
    "CheckpointSink",
    "FloatParam",
    "IntParam",
    "JsonlCheckpoint",
    "ObjectiveResult",
    "ParamSchema",
    "TrialEvent",
    "TuningConfig",
    "TuningResult",
    "TrialPruned",
    "normalize_objective_result",
    "tune",
]
