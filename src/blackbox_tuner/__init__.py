"""Public API for blackbox-tuner."""

from importlib.metadata import PackageNotFoundError, version

from .checkpoints import CheckpointSink, JsonlCheckpoint
from .config import TuningConfig
from .errors import BlackboxTunerError, CheckpointError, SerializationError, TrialPruned
from .events import TrialEvent
from .objective import ObjectiveResult, normalize_objective_result
from .runner import ObjectiveFn, TuningResult, tune
from .schema import CategoricalParam, FloatParam, IntParam, ParamSchema

try:
    __version__ = version("blackbox-tuner")
except PackageNotFoundError:
    __version__ = "0.2.0"

__all__ = [
    "BlackboxTunerError",
    "CategoricalParam",
    "CheckpointError",
    "CheckpointSink",
    "FloatParam",
    "IntParam",
    "JsonlCheckpoint",
    "ObjectiveFn",
    "ObjectiveResult",
    "ParamSchema",
    "SerializationError",
    "TrialEvent",
    "TuningConfig",
    "TuningResult",
    "TrialPruned",
    "normalize_objective_result",
    "tune",
]
