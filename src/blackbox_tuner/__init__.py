"""Public API for blackbox-tuner."""

from .config import TuningConfig
from .errors import TrialPruned
from .events import TrialEvent
from .objective import ObjectiveResult, normalize_objective_result
from .schema import CategoricalParam, FloatParam, IntParam, ParamSchema

__version__ = "0.1.0"

__all__ = [
    "CategoricalParam",
    "FloatParam",
    "IntParam",
    "ObjectiveResult",
    "ParamSchema",
    "TrialEvent",
    "TuningConfig",
    "TrialPruned",
    "normalize_objective_result",
]
