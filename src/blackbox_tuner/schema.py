from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Sequence


JSONScalar = str | int | float | bool | None


@dataclass(frozen=True)
class CategoricalParam:
    name: str
    choices: Sequence[Any]
    kind: Literal["categorical"] = "categorical"

    def __post_init__(self) -> None:
        _validate_name(self.name)
        if len(self.choices) == 0:
            raise ValueError(f"{self.name}: choices must not be empty")


@dataclass(frozen=True)
class FloatParam:
    name: str
    low: float
    high: float
    step: float | None = None
    log: bool = False
    kind: Literal["float"] = "float"

    def __post_init__(self) -> None:
        _validate_name(self.name)
        if self.low > self.high:
            raise ValueError(f"{self.name}: low must be <= high")
        if self.step is not None and self.step <= 0:
            raise ValueError(f"{self.name}: step must be positive")
        if self.step is not None and self.log:
            raise ValueError(f"{self.name}: step and log cannot be used together")


@dataclass(frozen=True)
class IntParam:
    name: str
    low: int
    high: int
    step: int = 1
    log: bool = False
    kind: Literal["int"] = "int"

    def __post_init__(self) -> None:
        _validate_name(self.name)
        if self.low > self.high:
            raise ValueError(f"{self.name}: low must be <= high")
        if self.step <= 0:
            raise ValueError(f"{self.name}: step must be positive")


Param = CategoricalParam | FloatParam | IntParam


class ParamSchema:
    def __init__(self, params: Sequence[Param]) -> None:
        self.params = list(params)
        names = [param.name for param in self.params]
        if len(names) != len(set(names)):
            raise ValueError("parameter names must be unique")

    def suggest(self, trial: Any) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for param in self.params:
            if param.kind == "categorical":
                values[param.name] = trial.suggest_categorical(param.name, list(param.choices))
            elif param.kind == "float":
                values[param.name] = trial.suggest_float(
                    param.name,
                    param.low,
                    param.high,
                    step=param.step,
                    log=param.log,
                )
            elif param.kind == "int":
                values[param.name] = trial.suggest_int(
                    param.name,
                    param.low,
                    param.high,
                    step=param.step,
                    log=param.log,
                )
        return values

    def sanitize(self, values: dict[str, Any]) -> dict[str, Any]:
        sanitized = dict(values)
        for param in self.params:
            if param.name not in values:
                continue
            raw = values[param.name]
            if param.kind == "categorical":
                sanitized[param.name] = raw if raw in param.choices else list(param.choices)[0]
            elif param.kind == "float":
                sanitized[param.name] = _snap_float(float(raw), param.low, param.high, param.step)
            elif param.kind == "int":
                sanitized[param.name] = _snap_int(int(round(float(raw))), param.low, param.high, param.step)
        return sanitized


def _validate_name(name: str) -> None:
    if not isinstance(name, str) or not name:
        raise ValueError("parameter name must be a non-empty string")


def _snap_float(value: float, low: float, high: float, step: float | None) -> float:
    clipped = min(max(value, low), high)
    if step is None:
        return clipped
    steps = round((clipped - low) / step)
    return min(max(low + steps * step, low), high)


def _snap_int(value: int, low: int, high: int, step: int) -> int:
    clipped = min(max(value, low), high)
    steps = round((clipped - low) / step)
    return min(max(low + steps * step, low), high)
