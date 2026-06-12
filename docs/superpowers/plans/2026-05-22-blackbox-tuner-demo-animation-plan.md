# blackbox-tuner Demo Animation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a separate public demo repo that animates Optuna-style tuning cases, showing API usage, trial progression, pruning, and convergence as a GitHub Pages-ready static site.

**Architecture:** The demo repo is a thin-build static app with a single HTML entry point, a small JS/TS playback engine, SVG-based charts, and case definitions stored as pure data. The UI renders only from event streams, while the API overlay is static copy aligned with the public `blackbox-tuner` API names.

**Tech Stack:** TypeScript, Vite, vanilla DOM/SVG rendering, Vitest, Playwright, GitHub Pages.

---

## Implementation Workspace

Create a new repository at:

`./`

Do not add frontend runtime code to the `blackbox-tuner` library repo. This demo repo must remain separate and public.

Before implementation starts, install the repo dependencies from the new workspace so the generated `package-lock.json` is committed with the first shell. The plan assumes `npm install` is run in the demo repo root after `package.json` exists, and that Playwright browser binaries are installed before the browser smoke step.

## File Structure

Create:

- `package.json` - scripts, dependencies, and GitHub Pages build commands.
- `index.html` - single-page shell.
- `vite.config.ts` - base path and build output configuration.
- `tsconfig.json` - TypeScript compiler settings.
- `playwright.config.ts` - browser smoke test runner.
- `src/main.ts` - app bootstrap.
- `src/api-copy.ts` - static public API names and explanatory copy.
- `src/cases.ts` - synthetic demo case definitions.
- `src/engine.ts` - event generator and playback state machine.
- `src/render.ts` - DOM/SVG rendering helpers.
- `src/app.ts` - app wiring, controls, and state transitions.
- `src/styles.css` - layout and animation styles.
- `tests/cases.test.ts` - case validity and API-copy alignment tests.
- `tests/engine.test.ts` - event ordering and pruning/convergence tests.
- `tests/playback.test.ts` - playback state and control tests.
- `tests/e2e.spec.ts` - browser smoke test.
- `.github/workflows/deploy.yml` - build and publish to GitHub Pages.
- `README.md` - local preview and deployment instructions.

Do not create a backend, database, or runtime Python integration. The demo must stay synthetic and static.

## Task 1: Bootstrap the Static Demo Shell

**Files:**
- Create: `.//package.json`
- Create: `.//index.html`
- Create: `.//vite.config.ts`
- Create: `.//tsconfig.json`
- Create: `.//src/main.ts`
- Create: `.//src/app.ts`
- Create: `.//src/api-copy.ts`
- Create: `.//src/cases.ts`
- Create: `.//src/styles.css`
- Create: `.//README.md`
- Create: `.//tests/cases.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tests/cases.test.ts`:

```typescript
import { describe, expect, it } from "vitest";
import { PUBLIC_API_NAMES } from "../src/api-copy";
import { getCases } from "../src/cases";

describe("case bootstrap", () => {
  it("exposes the public API names used by the overlay", () => {
    expect(PUBLIC_API_NAMES).toEqual([
      "ParamSchema",
      "objective",
      "tune()",
      "ObjectiveResult",
      "TuningConfig",
      "TrialEvent",
      "TrialPruned",
    ]);
  });

  it("loads at least one synthetic demo case", () => {
    const cases = getCases();
    expect(cases.length).toBeGreaterThan(0);
    expect(cases[0].id).toBe("fast_converge");
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
npm test -- tests/cases.test.ts -v
```

Expected: FAIL because `src/api-copy.ts` and `src/cases.ts` do not exist yet.

- [ ] **Step 3: Write the minimal implementation**

Create `src/api-copy.ts`:

```typescript
export const PUBLIC_API_NAMES = [
  "ParamSchema",
  "objective",
  "tune()",
  "ObjectiveResult",
  "TuningConfig",
  "TrialEvent",
  "TrialPruned",
] as const;

export const API_OVERLAY_COPY = [
  "ParamSchema defines the search space.",
  "objective receives params and returns a score.",
  "tune() runs the session and emits events.",
] as const;
```

Create `src/cases.ts`:

```typescript
export type DemoCase = {
  id: string;
  title: string;
  summary: string;
  tags: string[];
  searchSpace: string[];
  objectiveProfile: "fast" | "noisy" | "multimodal" | "plateau";
  pruneProfile: "light" | "heavy" | "late";
  convergenceProfile: "quick" | "slow" | "oscillating";
  notes: string;
};

const CASES: DemoCase[] = [
  {
    id: "fast_converge",
    title: "Fast Convergence",
    summary: "A smooth landscape that locks onto the optimum early.",
    tags: ["easy", "converges"],
    searchSpace: ["x: int[0,10]", "y: float[0,1]"],
    objectiveProfile: "fast",
    pruneProfile: "light",
    convergenceProfile: "quick",
    notes: "Useful for showing the happy path.",
  },
  {
    id: "prune_heavy",
    title: "Prune Heavy",
    summary: "Most early trials are cut before completion.",
    tags: ["pruning", "short-circuit"],
    searchSpace: ["x: int[0,20]", "y: float[0,1]"],
    objectiveProfile: "noisy",
    pruneProfile: "heavy",
    convergenceProfile: "slow",
    notes: "Shows frequent early exits and best-updated recovery.",
  },
  {
    id: "noisy_landscape",
    title: "Noisy Landscape",
    summary: "Scores wobble before the sampler settles.",
    tags: ["noise", "oscillation"],
    searchSpace: ["x: int[0,30]", "temperature: float[0,2]"],
    objectiveProfile: "noisy",
    pruneProfile: "light",
    convergenceProfile: "oscillating",
    notes: "Keeps the curve moving so the demo can show uncertainty.",
  },
  {
    id: "multi_modal",
    title: "Multi Modal",
    summary: "Several local optima compete before one wins.",
    tags: ["local-minima", "exploration"],
    searchSpace: ["x: int[0,40]", "y: float[0,1]"],
    objectiveProfile: "multimodal",
    pruneProfile: "late",
    convergenceProfile: "slow",
    notes: "Demonstrates exploration before exploitation.",
  },
  {
    id: "plateau_then_drop",
    title: "Plateau Then Drop",
    summary: "The search stalls, then suddenly finds a much better region.",
    tags: ["plateau", "late-breakthrough"],
    searchSpace: ["x: int[0,50]", "cooldown: float[0,1]"],
    objectiveProfile: "plateau",
    pruneProfile: "late",
    convergenceProfile: "slow",
    notes: "Useful for showing why patience matters.",
  },
];

export function getCases(): DemoCase[] {
  return CASES.slice();
}
```

Create `src/main.ts`:

```typescript
import "./styles.css";
import { mountApp } from "./app";

mountApp(document.getElementById("app"));
```

Create `src/app.ts`:

```typescript
export function mountApp(root: HTMLElement | null) {
  if (!root) return;
  root.innerHTML = `
    <main class="shell">
      <section class="panel">blackbox-tuner demo</section>
    </main>
  `;
}
```

Create `src/styles.css` with a minimal full-viewport shell:

```css
:root {
  color-scheme: light;
  font-family: system-ui, sans-serif;
}

html,
body,
#app {
  margin: 0;
  min-height: 100%;
}

body {
  background: #f5f7fb;
  color: #111827;
}

.shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
}

.panel {
  padding: 24px 28px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  background: white;
}
```

Create `package.json`:

```json
{
  "name": "blackbox-tuner-demo",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:e2e": "playwright test"
  },
  "devDependencies": {
    "@playwright/test": "^1.54.0",
    "typescript": "^5.5.4",
    "vite": "^5.4.0",
    "vitest": "^2.0.5"
  }
}
```

Create `index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>blackbox-tuner demo</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

Create `vite.config.ts`:

```typescript
import { defineConfig } from "vite";

export default defineConfig({
  base: "/blackbox-tuner-demo/",
  build: {
    outDir: "dist",
  },
});
```

Create `tsconfig.json`:

```json
{
  "tsconfig": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "jsx": "preserve",
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "types": []
  },
  "include": ["src", "tests", "vite.config.ts", "playwright.config.ts"]
}
```

The app must build from `src/main.ts` and deploy under the `/blackbox-tuner-demo/` GitHub Pages base path.

- [ ] **Step 2: Install dependencies and generate the lockfile**

Run:

```bash
npm install
```

Expected: `node_modules/` is created and `package-lock.json` is written at the repo root.

- [ ] **Step 3: Run the test to verify it fails**

Run:

```bash
npm test -- tests/cases.test.ts -v
```

Expected: FAIL because `src/api-copy.ts` and `src/cases.ts` do not exist yet.

- [ ] **Step 4: Write the minimal implementation**

Create `src/api-copy.ts`:

```typescript
export const PUBLIC_API_NAMES = [
  "ParamSchema",
  "objective",
  "tune()",
  "ObjectiveResult",
  "TuningConfig",
  "TrialEvent",
  "TrialPruned",
] as const;

export const API_OVERLAY_COPY = [
  "ParamSchema defines the search space.",
  "objective receives params and returns a score.",
  "tune() runs the session and emits events.",
] as const;
```

Create `src/cases.ts`:

```typescript
export type DemoCase = {
  id: string;
  title: string;
  summary: string;
  tags: string[];
  searchSpace: string[];
  objectiveProfile: "fast" | "noisy" | "multimodal" | "plateau";
  pruneProfile: "light" | "heavy" | "late";
  convergenceProfile: "quick" | "slow" | "oscillating";
  notes: string;
};

const CASES: DemoCase[] = [
  {
    id: "fast_converge",
    title: "Fast Convergence",
    summary: "A smooth landscape that locks onto the optimum early.",
    tags: ["easy", "converges"],
    searchSpace: ["x: int[0,10]", "y: float[0,1]"],
    objectiveProfile: "fast",
    pruneProfile: "light",
    convergenceProfile: "quick",
    notes: "Useful for showing the happy path.",
  },
  {
    id: "prune_heavy",
    title: "Prune Heavy",
    summary: "Most early trials are cut before completion.",
    tags: ["pruning", "short-circuit"],
    searchSpace: ["x: int[0,20]", "y: float[0,1]"],
    objectiveProfile: "noisy",
    pruneProfile: "heavy",
    convergenceProfile: "slow",
    notes: "Shows frequent early exits and best-updated recovery.",
  },
  {
    id: "noisy_landscape",
    title: "Noisy Landscape",
    summary: "Scores wobble before the sampler settles.",
    tags: ["noise", "oscillation"],
    searchSpace: ["x: int[0,30]", "temperature: float[0,2]"],
    objectiveProfile: "noisy",
    pruneProfile: "light",
    convergenceProfile: "oscillating",
    notes: "Keeps the curve moving so the demo can show uncertainty.",
  },
  {
    id: "multi_modal",
    title: "Multi Modal",
    summary: "Several local optima compete before one wins.",
    tags: ["local-minima", "exploration"],
    searchSpace: ["x: int[0,40]", "y: float[0,1]"],
    objectiveProfile: "multimodal",
    pruneProfile: "late",
    convergenceProfile: "slow",
    notes: "Demonstrates exploration before exploitation.",
  },
  {
    id: "plateau_then_drop",
    title: "Plateau Then Drop",
    summary: "The search stalls, then suddenly finds a much better region.",
    tags: ["plateau", "late-breakthrough"],
    searchSpace: ["x: int[0,50]", "cooldown: float[0,1]"],
    objectiveProfile: "plateau",
    pruneProfile: "late",
    convergenceProfile: "slow",
    notes: "Useful for showing why patience matters.",
  },
];

export function getCases(): DemoCase[] {
  return CASES.slice();
}
```

Create `src/main.ts`:

```typescript
import "./styles.css";
import { mountApp } from "./app";

mountApp(document.getElementById("app"));
```

Create `src/app.ts`:

```typescript
export function mountApp(root: HTMLElement | null) {
  if (!root) return;
  root.innerHTML = `
    <main class="shell">
      <section class="panel">blackbox-tuner demo</section>
    </main>
  `;
}
```

Create `src/styles.css` with a minimal full-viewport shell:

```css
:root {
  color-scheme: light;
  font-family: system-ui, sans-serif;
}

html,
body,
#app {
  margin: 0;
  min-height: 100%;
}

body {
  background: #f5f7fb;
  color: #111827;
}

.shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
}

.panel {
  padding: 24px 28px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  background: white;
}
```

Create `package.json`:

```json
{
  "name": "blackbox-tuner-demo",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:e2e": "playwright test"
  },
  "devDependencies": {
    "@playwright/test": "^1.54.0",
    "typescript": "^5.5.4",
    "vite": "^5.4.0",
    "vitest": "^2.0.5"
  }
}
```

Create `index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>blackbox-tuner demo</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

Create `vite.config.ts`:

```typescript
import { defineConfig } from "vite";

export default defineConfig({
  base: "/blackbox-tuner-demo/",
  build: {
    outDir: "dist",
  },
});
```

Create `tsconfig.json`:

```json
{
  "tsconfig": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "jsx": "preserve",
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "types": []
  },
  "include": ["src", "tests", "vite.config.ts", "playwright.config.ts"]
}
```

The app must build from `src/main.ts` and deploy under the `/blackbox-tuner-demo/` GitHub Pages base path.

- [ ] **Step 5: Run the test to verify it passes**

Run:

```bash
npm test -- tests/cases.test.ts -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add package.json package-lock.json index.html vite.config.ts tsconfig.json src tests README.md
git commit -m "feat: bootstrap blackbox-tuner demo shell"
```

## Task 2: Implement the Synthetic Event Engine

**Files:**
- Modify: `.//src/cases.ts`
- Create: `.//src/engine.ts`
- Create: `.//tests/engine.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tests/engine.test.ts`:

```typescript
import { describe, expect, it } from "vitest";
import { buildEventStream } from "../src/engine";

describe("engine", () => {
  it("emits prune and best-updated events in order for a prune-heavy case", () => {
    const stream = buildEventStream("prune_heavy");
    const types = stream.map((event) => event.type);

    expect(types[0]).toBe("run_started");
    expect(types).toContain("trial_pruned");
    expect(types).toContain("best_updated");
    expect(types.at(-1)).toBe("run_completed");
  });

  it("makes the example cases behave differently enough to teach distinct patterns", () => {
    const noisy = buildEventStream("noisy_landscape");
    const multiModal = buildEventStream("multi_modal");
    const plateau = buildEventStream("plateau_then_drop");

    expect(noisy.filter((event) => event.type === "trial_completed").length).toBeGreaterThan(1);
    expect(multiModal.filter((event) => event.type === "best_updated").length).toBeGreaterThan(1);
    expect(plateau.some((event) => event.type === "trial_pruned")).toBe(true);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
npm test -- tests/engine.test.ts -v
```

Expected: FAIL because `buildEventStream` does not exist yet.

- [ ] **Step 3: Write the minimal implementation**

Create `src/engine.ts`:

```typescript
import { getCases } from "./cases";

export type DemoEvent =
  | { type: "run_started"; caseId: string }
  | { type: "trial_started"; trial: number; params: Record<string, number> }
  | { type: "trial_completed"; trial: number; score: number }
  | { type: "trial_pruned"; trial: number; reason: string }
  | { type: "best_updated"; trial: number; score: number }
  | { type: "run_completed" };

export function buildEventStream(caseId: string): DemoEvent[] {
  const demoCase = getCases().find((item) => item.id === caseId) ?? getCases()[0];

  if (demoCase.id === "fast_converge") {
    return [
      { type: "run_started", caseId: demoCase.id },
      { type: "trial_started", trial: 0, params: { x: 1, y: 0.2 } },
      { type: "trial_completed", trial: 0, score: -3.2 },
      { type: "best_updated", trial: 0, score: -3.2 },
      { type: "trial_started", trial: 1, params: { x: 7, y: 0.8 } },
      { type: "trial_completed", trial: 1, score: -0.4 },
      { type: "best_updated", trial: 1, score: -0.4 },
      { type: "run_completed" },
    ];
  }

  return [
    { type: "run_started", caseId: demoCase.id },
    { type: "trial_started", trial: 0, params: { x: 0, y: 0 } },
    { type: "trial_pruned", trial: 0, reason: "low intermediate score" },
    { type: "trial_started", trial: 1, params: { x: 8, y: 0.6 } },
    { type: "trial_completed", trial: 1, score: -0.9 },
    { type: "best_updated", trial: 1, score: -0.9 },
    { type: "run_completed" },
  ];
}
```

Expand `src/cases.ts` to include at least `prune_heavy`, `noisy_landscape`, and `multi_modal` so `buildEventStream()` can choose behavior by case id.
Make `noisy_landscape` alternate between small score gains and regressions, make `multi_modal` require a few bad local optima before the better basin appears, and make `plateau_then_drop` stay flat for several trials before one sharp improvement.

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
npm test -- tests/engine.test.ts -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add src/cases.ts src/engine.ts tests/engine.test.ts
git commit -m "feat: add synthetic demo engine"
```

## Task 3: Render Playback and API Overlay

**Files:**
- Create: `.//src/render.ts`
- Modify: `.//src/app.ts`
- Modify: `.//src/styles.css`
- Create: `.//tests/playback.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tests/playback.test.ts`:

```typescript
import { describe, expect, it } from "vitest";
import { createPlaybackState, stepPlayback, switchPlaybackCase } from "../src/render";

describe("playback", () => {
  it("advances through trial events and preserves best-so-far", () => {
    const state = createPlaybackState("fast_converge");
    const next = stepPlayback(state);

    expect(next.cursor).toBeGreaterThan(0);
    expect(next.bestScore).toBeDefined();
  });

  it("resets playback state when the case changes", () => {
    const state = createPlaybackState("fast_converge");
    const advanced = stepPlayback(state);
    const switched = switchPlaybackCase(advanced, "prune_heavy");

    expect(switched.caseId).toBe("prune_heavy");
    expect(switched.cursor).toBe(0);
    expect(switched.bestScore).toBeNull();
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
npm test -- tests/playback.test.ts -v
```

Expected: FAIL because `createPlaybackState` and `stepPlayback` do not exist yet.

- [ ] **Step 3: Write the minimal implementation**

Create `src/render.ts`:

```typescript
import { buildEventStream } from "./engine";

export type PlaybackState = {
  caseId: string;
  events: ReturnType<typeof buildEventStream>;
  cursor: number;
  bestScore: number | null;
};

export function createPlaybackState(caseId: string): PlaybackState {
  return {
    caseId,
    events: buildEventStream(caseId),
    cursor: 0,
    bestScore: null,
  };
}

export function stepPlayback(state: PlaybackState): PlaybackState {
  const nextCursor = Math.min(state.cursor + 1, state.events.length);
  const visible = state.events.slice(0, nextCursor);
  const bestScore = visible.reduce<number | null>((best, event) => {
    if (event.type !== "best_updated") return best;
    return best === null ? event.score : Math.max(best, event.score);
  }, null);

  return {
    ...state,
    cursor: nextCursor,
    bestScore,
  };
}

export function switchPlaybackCase(state: PlaybackState, caseId: string): PlaybackState {
  return createPlaybackState(caseId);
}
```

Update `src/app.ts` to mount the full layout:

```typescript
import { createPlaybackState, stepPlayback } from "./render";
import { getCases } from "./cases";
import { API_OVERLAY_COPY } from "./api-copy";

export function mountApp(root: HTMLElement | null) {
  if (!root) return;

  const firstCase = getCases()[0];
  const state = createPlaybackState(firstCase.id);

  root.innerHTML = `
    <main class="shell">
      <aside class="rail">
        <h1>blackbox-tuner demo</h1>
      </aside>
      <section class="canvas">
        <div class="card">${firstCase.title}</div>
      </section>
      <aside class="rail">
        <ul>${API_OVERLAY_COPY.map((line) => `<li>${line}</li>`).join("")}</ul>
      </aside>
    </main>
  `;

  void state;
  void stepPlayback;
}
```

Expand `src/styles.css` to a three-column shell, a bottom control bar, and simple animated state classes for active trials and best markers.

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
npm test -- tests/playback.test.ts -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add src/render.ts src/app.ts src/styles.css tests/playback.test.ts
git commit -m "feat: render demo playback"
```

## Task 4: Add Browser Smoke and GitHub Pages Deployment

**Files:**
- Create: `.//playwright.config.ts`
- Create: `.//tests/e2e.spec.ts`
- Create: `.//.github/workflows/deploy.yml`
- Modify: `.//README.md`

- [ ] **Step 1: Write the failing browser smoke test**

Create `tests/e2e.spec.ts`:

```typescript
import { expect, test } from "@playwright/test";

test("loads the first demo case", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("blackbox-tuner demo")).toBeVisible();
  await expect(page.getByText("Fast Convergence")).toBeVisible();
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
npm run test:e2e
```

Expected: FAIL because Playwright config and dev server wiring are not ready yet.

- [ ] **Step 3: Write the minimal implementation**

Create `playwright.config.ts`:

```typescript
import { defineConfig } from "@playwright/test";

export default defineConfig({
  webServer: {
    command: "npm run dev -- --host 127.0.0.1 --port 4173",
    url: "http://127.0.0.1:4173",
    reuseExistingServer: !process.env.CI,
  },
  projects: [
    {
      name: "chromium",
      use: { browserName: "chromium" },
    },
  ],
  use: {
    baseURL: "http://127.0.0.1:4173",
    headless: true,
  },
  testDir: "./tests",
});
```

Create `.github/workflows/deploy.yml` to:

```yaml
name: deploy
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npm test
      - run: npm run build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist
  deploy:
    needs: build-and-deploy
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

Update `README.md` with:

```markdown
## Demo

Run locally:

```bash
npm install
npm run dev
```

Build for GitHub Pages:

```bash
npm run build
```
```

Add a `package.json` script for `test:e2e` that runs Playwright and a `build` script that emits static assets to `dist/`.

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
npx playwright install --with-deps chromium
npm run test:e2e
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add playwright.config.ts .github/workflows/deploy.yml README.md package.json tests/e2e.spec.ts
git commit -m "feat: add browser smoke and deployment"
```

## Task 5: Final Review and Public Publish

**Files:**
- Modify: `.//README.md`

- [ ] **Step 1: Run final verification**

Run:

```bash
npm test
npm run test:e2e
npm run build
git status --short
```

Expected:

- Unit tests pass.
- Browser smoke passes.
- Build produces a GitHub Pages-ready `dist/`.
- Working tree is clean.

- [ ] **Step 2: Validate public boundary**

Check that the demo repo does not import the Python package at runtime and only refers to the public API names in static copy.

```typescript
const overlay = [
  "ParamSchema",
  "objective",
  "tune()",
  "ObjectiveResult",
  "TuningConfig",
  "TrialEvent",
  "TrialPruned",
];
```

Expected: demo stays synthetic and public-facing.

- [ ] **Step 3: Create and publish the public repository**

Run:

```bash
git branch -M main
gh repo create blackbox-tuner-demo --public --source . --remote origin --push
git push -u origin main
```

Expected: a public `blackbox-tuner-demo` repository exists on GitHub, `main` tracks the published branch, and the GitHub Pages workflow can use the pushed contents.

- [ ] **Step 4: Commit documentation updates**

Run:

```bash
git add README.md
git commit -m "docs: document demo usage and deployment"
```

## Task 6: Code Review and Signoff

**Files:**
- None. This task validates the finished work and records the review outcome.

- [ ] **Step 1: Run the final review checklist**

Run:

```bash
npm test
npm run test:e2e
npm run build
git status --short
git diff --check
```

Expected:

- Unit tests pass.
- Browser smoke passes.
- Build succeeds.
- Working tree is clean.
- No whitespace or patch-format errors remain.

- [ ] **Step 2: Verify the public boundary again**

Check that:

- `src/api-copy.ts` only contains public API names and static overlay copy.
- `src/cases.ts` contains only synthetic demo cases.
- No runtime Python integration exists anywhere in the demo repo.
- `package-lock.json` is committed.
- The Playwright and GitHub Pages steps are present in the plan and workflow.

- [ ] **Step 3: Request review on the public branch or PR**

If the demo repo is being merged through a PR, request review from the maintainer before merge.
If the repo is being published directly on `main`, record the review outcome in the repo history and confirm the final push is the reviewed state.

Expected: the demo is signoff-ready and the published state matches the reviewed state.

## Follow-Up Plan

After the demo repo is working, the next improvement path is:

1. Add more case families and richer transitions.
2. Add video export only if a presentation artifact is needed.
3. Keep the demo repo isolated from the library repo so the public API can evolve independently.

## Self-Review

- Spec coverage: static site, animation model, API overlay, synthetic cases, playback, error handling, testing, and deployment are all covered by tasks.
- Scope: the plan intentionally avoids backend services, Python runtime integration, and private data.
- Placeholder scan: no TBD/TODO placeholders remain.
- Type consistency: `DemoCase`, `DemoEvent`, `PlaybackState`, `buildEventStream`, `createPlaybackState`, and `stepPlayback` are used consistently across tests and implementation steps.
