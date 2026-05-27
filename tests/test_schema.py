import pytest

from blackbox_tuner import CategoricalParam, FloatParam, IntParam, ParamSchema


class FakeTrial:
    def suggest_categorical(self, name, choices):
        return choices[-1]

    def suggest_float(self, name, low, high, step=None, log=False):
        if step is not None:
            return low + step
        return high if not log else low

    def suggest_int(self, name, low, high, step=1, log=False):
        return low + step


def test_schema_suggests_values():
    schema = ParamSchema([
        CategoricalParam("mode", ["a", "b"]),
        FloatParam("alpha", 0.0, 1.0, step=0.25),
        IntParam("count", 1, 5),
    ])

    assert schema.suggest(FakeTrial()) == {"mode": "b", "alpha": 0.25, "count": 2}


def test_schema_sanitizes_values():
    schema = ParamSchema([
        CategoricalParam("mode", ["a", "b"]),
        FloatParam("alpha", 0.0, 1.0, step=0.25),
        IntParam("count", 1, 5),
    ])

    assert schema.sanitize({"mode": "z", "alpha": 0.62, "count": 9}) == {
        "mode": "a",
        "alpha": 0.5,
        "count": 5,
    }


def test_schema_rejects_invalid_param_names():
    with pytest.raises(ValueError, match="non-empty"):
        ParamSchema([IntParam("", 1, 2)])


def test_float_rejects_step_with_log():
    with pytest.raises(ValueError, match="step and log"):
        FloatParam("alpha", 0.001, 1.0, step=0.001, log=True)


def test_drop_excludes_locked_params():
    schema = ParamSchema([
        CategoricalParam("entry_type", ["donchian", "gap", "orb"]),
        CategoricalParam("bias", ["trend", "mr"]),
        IntParam("entry_window", 5, 60),
        FloatParam("atr_mult", 0.5, 2.0),
    ])
    reduced = schema.drop({"entry_type", "bias"})
    assert [p.name for p in reduced.params] == ["entry_window", "atr_mult"]


def test_drop_empty_exclude_returns_same():
    schema = ParamSchema([
        IntParam("entry_window", 5, 60),
        FloatParam("atr_mult", 0.5, 2.0),
    ])
    assert [p.name for p in schema.drop(set()).params] == ["entry_window", "atr_mult"]


def test_drop_preserves_original():
    schema = ParamSchema([
        CategoricalParam("entry_type", ["donchian", "gap"]),
        IntParam("entry_window", 5, 60),
    ])
    reduced = schema.drop({"entry_type"})
    assert len(schema.params) == 2          # original unchanged
    assert len(reduced.params) == 1
