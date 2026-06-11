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

## How Optuna Works

```text
User code
  │
  ├─ define ParamSchema
  ├─ define objective(params)
  └─ call tune(...)
        │
        ▼
   blackbox_tuner.tune()
        │
        ├─ create Study
        ├─ emit run_started
        │
        └─ for each Trial
              │
              ├─ Sampler suggests params
              │
              ├─ emit trial_started
              │
              ├─ run objective(params)
              │     ├─ return float
              │     │   └─ normalize to ObjectiveResult
              │     ├─ return ObjectiveResult
              │     ├─ raise TrialPruned
              │     └─ raise Exception
              │
              ├─ emit trial_completed / trial_pruned / trial_failed
              │
              ├─ update best result if improved
              │
              └─ (Pruner support planned; not yet active)
                    │
                    ▼
               run_completed
```

```text
Study
  ├─ owns the whole tuning session
  ├─ stores trial history
  └─ returns best params / best score

Trial
  ├─ one parameter set
  ├─ one objective evaluation
  └─ one result record

Sampler
  ├─ decides the next params
  ├─ learns from past trials
  └─ balances exploration and exploitation

Pruner
  ├─ planned: watch a running trial
  ├─ planned: stop clearly bad runs early
  └─ not yet implemented (trial.report / trial.should_prune not called)
```

## Development checks

Before release:

```bash
python -m pytest -v
python -m build
```

The test suite includes a public-boundary scan to keep examples and package files generic.
