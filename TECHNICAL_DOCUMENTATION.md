# DOCUMENTATION TECHNIQUE COMPLÈTE
## Simulation Monte Carlo — Risque-Rendement Investissements Afrique

**Version:** 2.1  
**Date:** 2026-01-08  
**Auteur:** Claude (Anthropic)

---

# INDEX

1. [VUE D'ENSEMBLE](#1-vue-densemble)
   - 1.1 Objectif du projet
   - 1.2 Architecture générale
   - 1.3 Flux de données

2. [MODEL.JSON — SOURCE UNIQUE DE VÉRITÉ](#2-modeljson--source-unique-de-vérité)
   - 2.1 Structure complète
   - 2.2 Section meta
   - 2.3 Section simulation
   - 2.4 Section assets
   - 2.5 Nomenclature des variables

3. [SIMULATE.PY — MOTEUR DE SIMULATION](#3-simulatepy--moteur-de-simulation)
   - 3.1 Vue d'ensemble
   - 3.2 Fonction calculate_pnl()
   - 3.3 Fonction simulate_asset()
   - 3.4 Fonction generate_trajectories()
   - 3.5 Règle unifiée sans/avec réinvestissement

4. [RESULTS.JSON — STRUCTURE DES RÉSULTATS](#4-resultsjson--structure-des-résultats)
   - 4.1 Structure complète
   - 4.2 Section pnl
   - 4.3 Section simulation
   - 4.4 Section trajectories

5. [CHARTS.PY — VISUALISATIONS](#5-chartspy--visualisations)
   - 5.1 Liste des 14 charts
   - 5.2 Configuration style
   - 5.3 Dépendances données

6. [EXCEL_WRITER.PY — EXPORT EXCEL](#6-excel_writerpy--export-excel)
   - 6.1 Fonctionnement
   - 6.2 Mapping cellules

7. [LOGIQUE MÉTIER](#7-logique-métier)
   - 7.1 Calcul P&L par actif
   - 7.2 Modèle de risque
   - 7.3 Simulation Monte Carlo

8. [NOMENCLATURE](#8-nomenclature)
   - 8.1 Préfixes
   - 8.2 Suffixes
   - 8.3 Exemples

9. [VALIDATION](#9-validation)
   - 9.1 Valeurs attendues
   - 9.2 Red flags

---

# 1. VUE D'ENSEMBLE

## 1.1 Objectif du projet

Outil pédagogique pour lycéens africains illustrant le compromis risque-rendement à travers 3 investissements en FCFA:

| Actif | Capital | Rendement théorique | Risque |
|-------|---------|---------------------|--------|
| Immobilier | 1M FCFA | 22% | Faible |
| Bétail | 1M FCFA | 84% | Moyen |
| Embouche | 1M FCFA | 165% | Élevé |

## 1.2 Architecture générale

```
model.json (SST)
    │
    ├──▶ simulate.py ──▶ results.json ──▶ charts.py ──▶ 14 PNG
    │
    └──▶ excel_writer.py + template.xlsx ──▶ output.xlsx
```

**Principe SST (Single Source of Truth):** Tous les paramètres sont dans model.json. Les autres fichiers LISENT model.json, ils ne définissent jamais de paramètres.

## 1.3 Flux de données

```
┌─────────────┐
│ model.json  │ ← Paramètres (éditable)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ simulate.py │ ← Calculs P&L + Monte Carlo
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ results.json │ ← Résultats (généré)
└──────┬───────┘
       │
       ▼
┌─────────────┐
│  charts.py  │ ← Visualisation pure
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  14 PNG     │ ← Output final
└─────────────┘
```

---

# 2. MODEL.JSON — SOURCE UNIQUE DE VÉRITÉ

## 2.1 Structure complète

```json
{
  "meta": { ... },
  "simulation": { ... },
  "assets": {
    "immobilier": { ... },
    "betail": { ... },
    "embouche": { ... }
  }
}
```

## 2.2 Section meta

```json
"meta": {
  "version": "2.0",
  "timestamp": "2026-01-07T23:00:00",
  "currency": "FCFA",
  "description": "Single Source of Truth - Risk/Return Model"
}
```

## 2.3 Section simulation

```json
"simulation": {
  "n_runs": 1000,      // Nombre de simulations Monte Carlo
  "n_years": 5,        // Horizon de simulation
  "seed": 42           // Seed pour reproductibilité
}
```

## 2.4 Section assets

Chaque actif contient 4 sous-sections:

### 2.4.1 config
```json
"config": {
  "name": "Immobilier",           // Nom technique
  "label": "2 appartements T2",   // Label affichage
  "n_units": 2,                   // Nombre d'unités
  "price_unit": 500000,           // Prix par unité
  "n_cycles_year": 1              // Cycles par an (1 pour immo/bétail, 3 pour embouche)
}
```

### 2.4.2 inputs
Variables spécifiques au calcul P&L de chaque actif.

**Immobilier:**
```json
"inputs": {
  "rent_month": 15000,            // Loyer mensuel
  "n_months_occupied": 10,        // Mois occupés
  "cost_maintenance": 25000,      // Entretien annuel
  "cost_taxes": 7500,             // Taxes
  "cost_management": 5400         // Gestion
}
```

**Bétail:**
```json
"inputs": {
  "milk_liters_day": 2,           // Litres lait/jour
  "n_days_production": 300,       // Jours production
  "pct_milk_loss": 0.20,          // Perte lait (20%)
  "price_milk_liter": 500,        // Prix lait/litre
  "pct_birth_rate": 0.15,         // Taux natalité
  "calf_weight_kg": 80,           // Poids veau
  "price_calf_kg": 2500,          // Prix veau/kg
  "cost_feed": 30000,             // Fourrage
  "cost_vet": 20000,              // Vétérinaire
  "cost_other": 10000             // Autres
}
```

**Embouche:**
```json
"inputs": {
  "weight_buy_kg": 200,           // Poids achat
  "weight_gain_kg": 90,           // Gain poids
  "price_sell_kg": 2500,          // Prix vente/kg
  "cost_hangar_year": 100000,     // Hangar (fixe annuel)
  "cost_feed_cycle": 120000,      // Alimentation/cycle
  "cost_vet_cycle": 20000,        // Vétérinaire/cycle
  "cost_other_cycle": 10000       // Autres/cycle
}
```

### 2.4.3 risks
```json
"risks": {
  "revenue": {
    "pct_low": -0.10,             // Variation basse (triangulaire)
    "pct_base": 0.00,             // Variation base (mode)
    "pct_high": 0.10              // Variation haute
  },
  "capital": {
    "p_loss_total": 0.02,         // Probabilité perte totale
    "p_depreciation": 0.03,       // Probabilité dépréciation
    "pct_depreciation": -0.10,    // Impact dépréciation
    "p_appreciation": 0.95,       // Probabilité appréciation
    "pct_appreciation": 0.02      // Impact appréciation
  }
}
```

### 2.4.4 excel_mapping
```json
"excel_mapping": {
  "column": "C",
  "cells": {
    "n_units": "C4",
    "price_unit": "C5",
    ...
  }
}
```

## 2.5 Nomenclature des variables

| Préfixe | Signification | Exemple |
|---------|---------------|---------|
| n_ | Nombre/quantité | n_units, n_cycles_year |
| p_ | Probabilité (0-1) | p_loss_total |
| pct_ | Pourcentage/ratio | pct_milk_loss |
| price_ | Prix d'achat | price_unit |
| cost_ | Coût opérationnel | cost_feed |

| Suffixe | Signification | Exemple |
|---------|---------------|---------|
| _unit | Par unité | profit_unit |
| _total | Somme toutes unités | capital_total |
| _year | Par an | profit_year |
| _cycle | Par cycle | cost_feed_cycle |

---

# 3. SIMULATE.PY — MOTEUR DE SIMULATION

## 3.1 Vue d'ensemble

```python
# Flow interne
1. Lire model.json
2. Pour chaque actif:
   a. calculate_pnl() → P&L théorique
   b. simulate_asset(cap=n_initial) → mode sans réinvest
   c. simulate_asset(cap=∞) → mode avec réinvest
   d. generate_trajectories() → 30 trajectoires pour charts
3. Sauvegarder results.json
```

## 3.2 Fonction calculate_pnl()

**Signature:**
```python
def calculate_pnl(asset_name, asset_data) -> dict
```

**Retourne:**
```python
{
    'n_units': int,
    'price_unit': int,
    'n_cycles_year': int,
    'profit_unit_cycle': int,      # Profit par unité par cycle
    'profit_unit_year': int,       # = profit_unit_cycle × n_cycles
    'profit_total_year': int,      # = profit_unit_year × n_units
    'capital_total': int,
    'return_year': float,          # = profit_total_year / capital_total
    'n_events_year': int           # = n_units × n_cycles (pour risque)
}
```

**Calculs par actif:**

### Immobilier
```python
revenue_unit_year = rent_month × n_months_occupied
cost_unit_year = cost_maintenance + cost_taxes + cost_management
profit_unit_cycle = revenue_unit_year - cost_unit_year  # (1 cycle/an)
capital_total = n_units × price_unit
```

### Bétail
```python
milk_net = milk_liters_day × n_days_production × (1 - pct_milk_loss)
revenue_milk = milk_net × price_milk_liter
revenue_calf = pct_birth_rate × calf_weight_kg × price_calf_kg
revenue_unit_year = revenue_milk + revenue_calf
cost_unit_year = cost_feed + cost_vet + cost_other
profit_unit_cycle = revenue_unit_year - cost_unit_year  # (1 cycle/an)
capital_total = n_units × price_unit
```

### Embouche
```python
weight_sell = weight_buy_kg + weight_gain_kg
revenue_unit_cycle = weight_sell × price_sell_kg
cost_unit_cycle = price_unit + cost_feed_cycle + cost_vet_cycle + cost_other_cycle
profit_unit_cycle = revenue_unit_cycle - cost_unit_cycle
capital_total = cost_hangar_year + n_units × (price_unit + cost_feed + cost_vet + cost_other)
```

## 3.3 Fonction simulate_asset()

**Signature:**
```python
def simulate_asset(asset_name, asset_data, pnl_data, n_runs, n_years, cap) -> tuple
```

**Paramètre clé — cap:**
- `cap = n_units_initial` → mode sans réinvestissement
- `cap = 999999 (∞)` → mode avec réinvestissement

**Retourne:**
```python
revenues[n_runs, n_years]      # Revenus annuels
capitals[n_runs, n_years+1]    # Capital (Y0 à Y5)
units[n_runs, n_years+1]       # Nombre d'unités
```

**Algorithme:**
```
POUR chaque run (1 à 1000):
    n_units = n_units_initial
    cash = 0
    
    POUR chaque année (1 à 5):
        year_revenue = 0
        
        POUR chaque cycle (1 à n_cycles_year):
            losses_this_cycle = 0
            
            POUR chaque unité (1 à n_units):
                roll = random()
                SI roll < p_loss_total:
                    losses_this_cycle += 1  # Unité perdue
                SINON:
                    variation = triangular(pct_low, pct_base, pct_high)
                    year_revenue += profit_unit_cycle × (1 + variation)
            
            # Fin cycle: retirer les morts
            n_units -= losses_this_cycle
            
            # Fin cycle: remplacer si possible (jusqu'au cap)
            TANT QUE n_units < cap ET cash >= price_unit:
                n_units += 1
                cash -= price_unit
        
        # Fin année
        cash += year_revenue
        
        # Acheter encore si possible
        TANT QUE n_units < cap ET cash >= price_unit:
            n_units += 1
            cash -= price_unit
        
        capital = n_units × price_unit + cash
```

## 3.4 Fonction generate_trajectories()

**Signature:**
```python
def generate_trajectories(asset_name, asset_data, pnl_data, n_traj, n_years, cap, seed) -> ndarray
```

**Paramètres:**
- n_traj = 30 (pour chart G)
- seed = 123 (différent du seed principal pour variété)
- cap = n_units_initial (mode sans réinvest)

**Retourne:**
```python
trajectories[30, 5]  # 30 runs × 5 années de revenus
```

## 3.5 Règle unifiée sans/avec réinvestissement

| Mode | Comportement | Cap |
|------|--------------|-----|
| **Sans réinvest** | On remplace les pertes SI on a le cash | n_units_initial |
| **Avec réinvest** | On achète autant qu'on peut | ∞ |

**Point clé:** La SEULE différence entre les deux modes est le plafond (cap). L'algorithme est identique.

---

# 4. RESULTS.JSON — STRUCTURE DES RÉSULTATS

## 4.1 Structure complète

```json
{
  "meta": { ... },
  "pnl": { ... },
  "simulation": {
    "without_reinvest": { ... },
    "with_reinvest": { ... }
  },
  "trajectories": { ... }
}
```

## 4.2 Section pnl

P&L théorique (sans risque) par actif:

```json
"pnl": {
  "immobilier": {
    "profit_unit_cycle": 112100,
    "profit_unit_year": 112100,
    "profit_total_year": 224200,
    "capital_total": 1000000,
    "return_year": 0.2242,
    "n_events_year": 2
  },
  ...
}
```

## 4.3 Section simulation

Pour chaque mode (without_reinvest, with_reinvest):

```json
"{asset}": {
  "revenues": {
    "mean": [Y1, Y2, Y3, Y4, Y5],
    "p10": [...],
    "p50": [...],
    "p90": [...]
  },
  "capitals": {
    "mean": [Y0, Y1, Y2, Y3, Y4, Y5],
    "p10": [...],
    "p50": [...],
    "p90": [...]
  },
  "units": {
    "mean": [Y0, Y1, Y2, Y3, Y4, Y5],
    "p10": [...],
    "p90": [...]
  },
  "summary": {
    "return_mean": 0.973,
    "return_p10": 0.45,
    "return_p90": 1.42,
    "volatility": 0.347,
    "units_final_mean": 2.0
  }
}
```

## 4.4 Section trajectories

```json
"trajectories": {
  "meta": {
    "seed": 123,
    "n_runs": 30,
    "mode": "without_reinvest"
  },
  "data": {
    "immobilier": [[Y1,Y2,Y3,Y4,Y5], [...], ...],  // 30 arrays
    "betail": [...],
    "embouche": [...]
  }
}
```

---

# 5. CHARTS.PY — VISUALISATIONS

## 5.1 Liste des 14 charts

### Sans réinvestissement (A-D)
| ID | Fichier | Description |
|----|---------|-------------|
| A | chart_a_revenus.png | Revenus annuels + bandes P10-P90 |
| B | chart_b_wealth.png | Richesse cumulée |
| C | chart_c_bulles.png | Scatter risque-rendement |
| D | chart_d_zones.png | Zones colorées risque |

### Avec réinvestissement (A-r à D-r)
| ID | Fichier | Description |
|----|---------|-------------|
| A-r | chart_a_revenus_reinvest.png | Revenus + reinvest |
| B-r | chart_b_capital_reinvest.png | Capital + reinvest |
| C-r | chart_c_bulles_reinvest.png | Bulles + reinvest |
| D-r | chart_d_zones_reinvest.png | Zones + reinvest |

### Comparaison & Pédagogie (E-H)
| ID | Fichier | Description |
|----|---------|-------------|
| E | chart_e_comparaison.png | Côte-à-côte 3 actifs |
| F | chart_f_units.png | Croissance unités |
| G | chart_g_trajectoires.png | 30 trajectoires |
| H | chart_h_une_trajectoire.png | 1 trajectoire |

### Verticales TikTok (9:16)
| ID | Fichier | Description |
|----|---------|-------------|
| E-v | chart_e_comparaison_vertical.png | E vertical |
| G-v | chart_g_trajectoires_vertical.png | G vertical |

## 5.2 Configuration style

```python
COLORS = {
    'immobilier': '#27ae60',  # Vert
    'betail': '#3498db',       # Bleu
    'embouche': '#e74c3c'      # Rouge
}

LABELS = {
    'immobilier': 'Immobilier',
    'betail': 'Bétail',
    'embouche': 'Embouche'
}
```

## 5.3 Dépendances données

| Chart | Source dans results.json |
|-------|--------------------------|
| A, B, C, D | simulation/without_reinvest |
| A-r, B-r, C-r, D-r | simulation/with_reinvest |
| E | both |
| F | with_reinvest/units |
| G, H | trajectories/data |

**Point clé:** charts.py ne fait AUCUNE simulation. Il lit uniquement results.json.

---

# 6. EXCEL_WRITER.PY — EXPORT EXCEL

## 6.1 Fonctionnement

```
model.json + template.xlsx → excel_writer.py → output.xlsx
```

**Étapes:**
1. Charger model.json
2. Charger template Excel (avec formules)
3. Pour chaque asset, pour chaque cellule mappée: écrire la valeur
4. Sauvegarder

**Ce qu'il fait:**
- Écrit les paramètres dans les cellules d'input

**Ce qu'il ne fait PAS:**
- Calculs (Excel fait ses propres calculs via formules)
- Création de formules
- Simulation Monte Carlo

## 6.2 Mapping cellules

### Immobilier (colonne C)
| Cellule | Variable |
|---------|----------|
| C4 | n_units |
| C5 | price_unit |
| C13 | rent_month |
| C14 | n_months_occupied |
| C26 | cost_maintenance |
| C27 | cost_taxes |
| C28 | cost_management |
| C38 | pct_low |
| C39 | pct_base |
| C40 | pct_high |
| C43-C47 | risques capital |

### Bétail (colonne H)
| Cellule | Variable |
|---------|----------|
| H4 | n_units |
| H5 | price_unit |
| H13-H21 | inputs lait/veau |
| H26-H28 | costs |
| H38-H47 | risks |

### Embouche (colonne M)
| Cellule | Variable |
|---------|----------|
| M4 | n_units |
| M5 | n_cycles_year |
| M6 | price_unit |
| M7 | cost_hangar_year |
| M13-M16 | inputs poids/prix |
| M27-M29 | costs |
| M38-M47 | risks |

---

# 7. LOGIQUE MÉTIER

## 7.1 Calcul P&L par actif

### Immobilier
```
Revenus = loyer × mois_occupés = 15000 × 10 = 150,000
Coûts = entretien + taxes + gestion = 25000 + 7500 + 5400 = 37,900
Profit/unité = 150,000 - 37,900 = 112,100
Capital = 2 × 500,000 = 1,000,000
Rendement = (112,100 × 2) / 1,000,000 = 22.4%
```

### Bétail
```
Lait net = 2L × 300j × 0.8 = 480L
Revenu lait = 480 × 500 = 240,000
Revenu veau = 0.15 × 80kg × 2500 = 30,000
Revenus = 240,000 + 30,000 = 270,000
Coûts = 30,000 + 20,000 + 10,000 = 60,000
Profit/unité = 270,000 - 60,000 = 210,000
Capital = 4 × 250,000 = 1,000,000
Rendement = (210,000 × 4) / 1,000,000 = 84%
```

### Embouche
```
Poids vente = 200 + 90 = 290kg
Revenu/veau/cycle = 290 × 2500 = 725,000
Coût/veau/cycle = 300,000 + 120,000 + 20,000 + 10,000 = 450,000
Profit/veau/cycle = 725,000 - 450,000 = 275,000
Capital = 100,000 + 2 × 450,000 = 1,000,000
Rendement = (275,000 × 2 × 3) / 1,000,000 = 165%
```

## 7.2 Modèle de risque

### Risque revenu
Distribution triangulaire autour du profit théorique:
```
profit_réel = profit_théorique × (1 + variation)
variation ~ Triangular(pct_low, pct_base, pct_high)
```

### Risque capital
À chaque EVENT (unité × cycle), tirage:
```
roll = random()
SI roll < p_loss_total:
    Unité perdue (pas de revenu ce cycle)
SINON:
    Unité produit normalement
```

**Nombre d'events par an:**
| Actif | Calcul | Events/an |
|-------|--------|-----------|
| Immobilier | 2 unités × 1 cycle | 2 |
| Bétail | 4 unités × 1 cycle | 4 |
| Embouche | 2 unités × 3 cycles | 6 |

## 7.3 Simulation Monte Carlo

**Paramètres:**
- N_RUNS = 1000 simulations
- N_YEARS = 5 ans
- SEED = 42 (reproductibilité)

**Output:** Distribution de résultats → percentiles (P10, P50, P90) + moyenne

---

# 8. NOMENCLATURE

## 8.1 Préfixes

| Préfixe | Signification | Type |
|---------|---------------|------|
| n_ | Nombre/quantité | int |
| p_ | Probabilité | float 0-1 |
| pct_ | Pourcentage/ratio | float |
| price_ | Prix d'achat | int |
| cost_ | Coût opérationnel | int |

## 8.2 Suffixes

| Suffixe | Signification |
|---------|---------------|
| _unit | Par unité |
| _total | Somme toutes unités |
| _year | Par an |
| _cycle | Par cycle |
| _day | Par jour |
| _month | Par mois |

## 8.3 Exemples

| Variable | Décomposition | Signification |
|----------|---------------|---------------|
| n_units | n + units | Nombre d'unités |
| profit_unit_cycle | profit + unit + cycle | Profit par unité par cycle |
| cost_feed_cycle | cost + feed + cycle | Coût alimentation par cycle |
| p_loss_total | p + loss + total | Probabilité de perte totale |
| pct_milk_loss | pct + milk + loss | Pourcentage de perte de lait |

---

# 9. VALIDATION

## 9.1 Valeurs attendues

### P&L théorique
| Actif | Return/year |
|-------|-------------|
| Immobilier | 22.4% |
| Bétail | 84.0% |
| Embouche | 165.0% |

### Simulation sans réinvestissement (5 ans)
| Actif | Return 5Y | Volatilité |
|-------|-----------|------------|
| Immobilier | ~97% | ~35% |
| Bétail | ~232% | ~89% |
| Embouche | ~377% | ~205% |

### Simulation avec réinvestissement (5 ans)
| Actif | Return 5Y | Volatilité | Units Y5 |
|-------|-----------|------------|----------|
| Immobilier | ~121% | ~46% | ~3.7 |
| Bétail | ~550% | ~274% | ~25.5 |
| Embouche | ~3347% | ~2344% | ~114 |

## 9.2 Red flags

**BUG si ces valeurs sont dépassées:**
- Immobilier return > 500%
- Bétail return > 5000%
- Embouche return > 50000%

**BUG si ordre incorrect:**
- Doit être: Embouche > Bétail > Immobilier (rendement)
- Doit être: Embouche > Bétail > Immobilier (volatilité)

---

# FIN DE DOCUMENTATION

**Fichiers du projet:**
```
model.json              ← SST (paramètres)
simulate.py             ← Moteur simulation
results.json            ← Résultats (généré)
charts.py               ← Visualisations
excel_writer.py         ← Export Excel
charts/                 ← 14 PNG
```

**Commandes:**
```bash
python3 simulate.py      # Génère results.json
python3 charts.py        # Génère 14 PNG
python3 excel_writer.py  # Génère output.xlsx
```
