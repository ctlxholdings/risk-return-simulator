# Risk-Return Simulator

Interactive Monte Carlo simulator for understanding investment risk in Africa.

## Live

https://learn.ctlx.holdings/risk-return/

## Tech Stack

| Tool | Purpose |
|------|---------|
| Vanilla HTML/CSS/JS | Everything in one file |
| Chart.js | Charts |
| PWA | Offline support |
| Vercel | Deployment |

## Why Vanilla (not React)?

This is a **single-page interactive tool**. Vanilla HTML is better because:

- Zero build step — edit `index.html` and deploy
- Smallest bundle (~50KB total)
- Works offline (PWA ready)
- No dependencies to update

Use Next.js/React when you need **multiple pages with shared components**. See [Platform Specs](../LEARN_PLATFORM_SPECS.md) for decision guide.

## Local Development

```bash
# Option 1: Python server
python3 -m http.server 8080
# Open http://localhost:8080

# Option 2: Just open the file
open index.html
```

## Project Structure

```
├── index.html      # Everything: HTML + CSS + JS (~2100 lines)
├── manifest.json   # PWA manifest
├── sw.js           # Service worker for offline
├── icons/          # PWA icons (72px to 512px)
├── model.json      # Simulation parameters (reference)
└── README.md
```

## Features

| Feature | Description |
|---------|-------------|
| **Cours Mode** | 6 slides explaining risk/return concepts |
| **Simulateur Mode** | Interactive Monte Carlo simulation |
| **3 Assets** | Immobilier (🏠), Bétail (🐄), Embouche (🐂) |
| **4 Tabs** | Paramètres, Richesse, Risque, Trajectoires |
| **Reinvest Toggle** | Compare with/without profit reinvestment |
| **Trajectory Types** | Switch between Revenus and Richesse views |
| **PWA** | Installable, works offline |

## Simulation Model

```javascript
// Asset configuration
ASSETS = {
  immobilier: { price: 500000, profit: 112100, cycles: 1 },  // 22% yield
  betail:     { price: 250000, profit: 210000, cycles: 1 },  // 84% yield
  embouche:   { price: 300000, profit: 275000, cycles: 3 }   // 165% yield (3 cycles/year)
};

// Risk parameters (user-adjustable)
params = {
  immobilier: { nUnits: 2, pLoss: 0.02, revVar: 0.10 },
  betail:     { nUnits: 4, pLoss: 0.20, revVar: 0.20 },
  embouche:   { nUnits: 2, pLoss: 0.20, revVar: 0.30 }
};

// Simulation: 500 runs × 5 years
```

## Key Results (default parameters)

| Asset | Mean Return | P10 (worst 10%) | P90 (best 10%) | Volatility |
|-------|-------------|-----------------|----------------|------------|
| Immobilier | +97% | +50% | +114% | 35% |
| Bétail | +232% | +118% | +332% | 89% |
| Embouche | +377% | **-71%** | +595% | 205% |

**Key insight:** Embouche has highest average return, but 10% of scenarios lose 71% of capital.

## UX Patterns

| Pattern | Implementation |
|---------|----------------|
| **Sticky reinvest toggle** | Visible on all chart tabs, not just Paramètres |
| **Auto-rerun on toggle** | Charts update immediately when reinvest changes |
| **Auto-switch to results** | After "Lancer", switches to Richesse tab |
| **Observation texts** | Each chart has contextual explanation |
| **Initial state** | Stays on Paramètres tab on first load |

## Design System

```css
:root {
  --coral: #FF6B4A;          /* Primary accent */
  --coral-light: #FFF0ED;    /* Light backgrounds */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F8F9FA;
  --text-primary: #2D3436;
  --green: #27ae60;          /* Immobilier */
  --blue: #3498db;           /* Bétail */
  --red: #e74c3c;            /* Embouche */
}
```

## PWA Setup

Files required:
- `manifest.json` — App name, icons, theme color
- `sw.js` — Service worker for offline caching
- Meta tags in HTML head

```html
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#FF6B4A">
<meta name="apple-mobile-web-app-capable" content="yes">
```

## Deployment

Automatic on push to `main` branch via Vercel.

```bash
git add -A && git commit -m "Your message" && git push
```

**Note:** This app is served via rewrite from the main app. URL `learn.ctlx.holdings/risk-return/` proxies to `risk-return-simulator.vercel.app`.

## Related

| Resource | Link |
|----------|------|
| Stochastic Course App | [GitHub](https://github.com/ctlxholdings/stochastic-course-app) |
| Platform Specs | `../LEARN_PLATFORM_SPECS.md` |
| Live Site | https://learn.ctlx.holdings/risk-return/ |

## Python Scripts (for chart generation)

The repo also includes Python scripts for generating static charts:

| File | Purpose |
|------|---------|
| `simulate.py` | Monte Carlo simulation |
| `charts.py` | Generate 19 PNG visualizations |
| `excel_writer.py` | Export to Excel |

These are **not used by the web app** — the web app runs simulations in JavaScript.
