"""Public API for blackbox-tuner."""

from importlib.metadata import PackageNotFoundError, version

from .checkpoints import CheckpointSink, JsonlCheckpoint
from .config import TuningConfig
from .errors import TrialPruned
from .events import TrialEvent
from .objective import ObjectiveResult, normalize_objective_result
from .runner import TuningResult, tune
from .schema import CategoricalParam, FloatParam, IntParam, ParamSchema

try:
    __version__ = version("blackbox-tuner")
except PackageNotFoundError:
    __version__ = "0.2.0"

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
