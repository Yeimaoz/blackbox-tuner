# blackbox-tuner Demo Animation Design

> 版本: 1.0
> 最後審查: 2026-05-22
> 擁有者: codex
> 狀態: draft, user-reviewed pending

## 0. Purpose

Create a separate public demo repo for `blackbox-tuner` that presents Optuna-style tuning as a dynamic, browser-based animation. The demo should explain three things clearly:

1. How to use the public API.
2. How the tuning loop progresses.
3. How example cases change search, pruning, and convergence behavior.

This is a presentation layer only. The demo repo must stay independent from the library repo structure and must not introduce private platform terms or private data. The demo should not import the Python package at runtime; it should present a curated explanation of the public API names and flow.

## 1. Repo Boundary

The demo lives in a new repository, tentatively named `blackbox-tuner-demo`.

In scope:

- Browser-based single-page demo.
- Static deployment to GitHub Pages.
- Case selector with multiple synthetic example cases.
- Animated trial playback.
- Visual explanation of API wiring and tuning state.

Out of scope:

- Backend service.
- Python runtime in the browser.
- Real data integration.
- Authenticated user workflows.
- Database persistence.

## 2. User Experience

The first screen should be the actual demo, not a landing page.

Layout:

- Left rail: case selector and summary chips.
- Center: animated trial timeline and score curve.
- Right rail: API flow and live state labels.
- Bottom bar: playback controls.

Controls:

- `Play`
- `Pause`
- `Step`
- `Reset`
- `Speed`

The reader should be able to:

- Switch between cases.
- Watch trials appear one by one.
- See prune events stop poor trials early.
- See best-so-far updates.
- Understand how `objective`, `schema`, and `tune()` connect.

## 3. Case Model

Each example case is pure data. Cases describe how the synthetic tuning session should behave.

Required case fields:

- `id`
- `title`
- `summary`
- `tags`
- `search_space`
- `objective_profile`
- `prune_profile`
- `convergence_profile`
- `notes`

Example case families:

- `fast_converge`
- `noisy_landscape`
- `prune_heavy`
- `multi_modal`
- `plateau_then_drop`

Cases should generate an event stream with these event types:

- `run_started`
- `trial_started`
- `trial_completed`
- `trial_pruned`
- `best_updated`
- `run_completed`

## 4. Animation Model

The demo should not depend on live Optuna execution. Instead, it should replay a synthetic event stream that behaves like Optuna.

Animation layers:

- Trial stream: each trial enters, resolves, or gets pruned.
- Score curve: objective values accumulate over time.
- Best-so-far track: highlights the strongest trial.
- API wiring overlay: shows `ParamSchema -> objective -> tune() -> events`.

Playback is driven by a single event timeline. The renderer consumes that timeline and updates the view incrementally.

## 5. Architecture

The demo repo should stay simple and static.

Recommended stack:

- Static HTML entry point.
- CSS for layout and motion primitives.
- SVG for charts and timeline markers.
- Small vanilla JS controller for state and playback.
- Thin build step for bundling static assets into a GitHub Pages-ready site.

Modules:

- `case-data/`: JSON case definitions.
- `engine/`: synthetic event generator and playback state machine.
- `ui/`: layout, selectors, chips, charts, and overlays.
- `deploy/`: GitHub Pages configuration.

Dependency direction:

```text
case-data -> engine -> ui -> deployment
```

The UI should render from events only. No view should need to read case internals directly.
The API overlay should be static copy that stays aligned with the public `blackbox-tuner` API names, not a runtime-generated import from the Python package.

## 6. Error Handling

The demo should fail gracefully.

Behavior:

- Invalid case data should render an explicit invalid-case state.
- Missing case data should fall back to a minimal toy case.
- Playback errors should stop the animation at the current frame and display a short message.
- Unsupported animation features should degrade to a static view rather than blank output.

The demo must never show a blank screen as the default failure mode.

## 7. Testing

Testing should focus on case validity, event ordering, and browser smoke.

Required checks:

- Each case can generate a valid event stream.
- Pruned trials and completed trials appear in the expected order.
- Best-so-far updates only when a better score appears.
- Case switching resets playback state.
- Static deployment loads in a browser and renders the first case.
- Local preview can run from the same build output used for GitHub Pages.

## 8. Deployment

Primary deployment target:

- GitHub Pages from the demo repo.

The demo should be shareable as a public URL and usable without a backend.

## 9. Review Gates

Before implementation:

- Confirm the demo repo boundary is separate from `blackbox-tuner`.
- Confirm the content is presentation only.
- Confirm case definitions remain synthetic.
- Confirm GitHub Pages is the deployment target.

Before release:

- Run browser smoke tests.
- Verify the first case loads.
- Verify case switching and playback still work.
- Verify the public URL is accessible.
