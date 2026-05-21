class BlackboxTunerError(Exception):
    """Base exception for blackbox-tuner."""


class SerializationError(BlackboxTunerError):
    """Raised when an event payload cannot be encoded as JSON."""


class CheckpointError(BlackboxTunerError):
    """Raised when a checkpoint sink cannot persist an event."""


class TrialPruned(BlackboxTunerError):
    """Raised by an objective to skip an unpromising parameter set."""
