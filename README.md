# blackbox-tuner

Black-box hyperparameter tuning with structured checkpoints and reviewable trial history.

```python
from blackbox_tuner import FloatParam, IntParam, ObjectiveResult, ParamSchema, TuningConfig, tune

schema = ParamSchema([
    IntParam("x", low=-10, high=10),
    FloatParam("y", low=-5.0, high=5.0),
])

def objective(params):
    score = -((params["x"] - 3) ** 2) - ((params["y"] + 1.5) ** 2)
    return ObjectiveResult(score=score, metrics={"loss": -score})

result = tune(schema=schema, objective=objective, config=TuningConfig(n_trials=50, seed=7))
print(result.best_params, result.best_score)
```

## Development checks

Before release:

```bash
python -m pytest -v
python -m build
```

The test suite includes a public-boundary scan to keep examples and package files generic.
