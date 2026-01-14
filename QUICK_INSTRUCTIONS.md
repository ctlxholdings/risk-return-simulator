# INSTRUCTIONS RAPIDES
## Simulation Monte Carlo — Risque-Rendement

---

## 1. ARCHITECTURE (1 minute)

```
model.json → simulate.py → results.json → charts.py → PNG
     │
     └────→ excel_writer.py → Excel
```

**Règle d'or:** model.json = source unique. Modifier ICI, exécuter les scripts.

---

## 2. FICHIERS

| Fichier | Rôle | Éditable? |
|---------|------|-----------|
| model.json | Paramètres | ✅ OUI |
| simulate.py | Simulation | ❌ Non |
| results.json | Résultats | ❌ Généré |
| charts.py | Graphiques | ❌ Non |
| excel_writer.py | Export Excel | ❌ Non |

---

## 3. EXÉCUTION

```bash
# 1. Modifier model.json si besoin

# 2. Lancer simulation
python3 simulate.py

# 3. Générer graphiques
python3 charts.py

# 4. (Optionnel) Export Excel
python3 excel_writer.py
```

---

## 4. MODIFIER LES PARAMÈTRES

### Changer le nombre d'unités
```json
// Dans model.json → assets → {actif} → config
"n_units": 4  // Changer cette valeur
```

### Changer les risques
```json
// Dans model.json → assets → {actif} → risks
"capital": {
  "p_loss_total": 0.20  // Probabilité de perte (0-1)
}
```

### Changer la simulation
```json
// Dans model.json → simulation
"n_runs": 1000,   // Plus = plus précis, plus lent
"n_years": 5,     // Horizon
"seed": 42        // Changer pour résultats différents
```

---

## 5. OUTPUTS

### 14 Graphiques (charts/)

| Chart | Description |
|-------|-------------|
| A, B, C, D | Sans réinvestissement |
| A-r, B-r, C-r, D-r | Avec réinvestissement |
| E | Comparaison côte-à-côte |
| F | Croissance unités |
| G | 30 trajectoires |
| H | 1 trajectoire |
| E-v, G-v | Versions TikTok (vertical) |

### Excel
- `unit_economics_output.xlsx` — Paramètres injectés, formules Excel calculent

---

## 6. LOGIQUE MÉTIER

### Deux modes de simulation

| Mode | Comportement |
|------|--------------|
| **Sans réinvest** | Remplace pertes si cash, plafonné à n_initial |
| **Avec réinvest** | Achète autant d'unités que possible |

### Risque appliqué par EVENT

```
Events/an = n_units × n_cycles_year

Immobilier: 2 × 1 = 2 events/an
Bétail:     4 × 1 = 4 events/an
Embouche:   2 × 3 = 6 events/an
```

---

## 7. NOMENCLATURE

| Préfixe | Signification |
|---------|---------------|
| n_ | Nombre |
| p_ | Probabilité (0-1) |
| pct_ | Pourcentage |
| cost_ | Coût |
| price_ | Prix |

| Suffixe | Signification |
|---------|---------------|
| _unit | Par unité |
| _cycle | Par cycle |
| _year | Par an |

---

## 8. VALIDATION RAPIDE

### Rendements attendus (sans réinvest, 5 ans)

| Actif | Return | Volatilité |
|-------|--------|------------|
| Immobilier | ~97% | ~35% |
| Bétail | ~232% | ~89% |
| Embouche | ~377% | ~205% |

### Red flags
- ❌ Embouche < Bétail → BUG
- ❌ Return > 10,000% → BUG
- ❌ Revenus qui chutent à 0 → BUG

---

## 9. DÉPANNAGE

| Problème | Solution |
|----------|----------|
| "File not found" | Vérifier que model.json existe |
| Résultats irréalistes | Vérifier p_loss_total (doit être < 0.5) |
| Charts vides | Relancer simulate.py d'abord |
| Excel pas à jour | Relancer excel_writer.py |

---

## 10. STRUCTURE model.json

```json
{
  "meta": { "version": "2.0" },
  "simulation": {
    "n_runs": 1000,
    "n_years": 5,
    "seed": 42
  },
  "assets": {
    "immobilier": {
      "config": { "n_units": 2, "price_unit": 500000, ... },
      "inputs": { "rent_month": 15000, ... },
      "risks": {
        "revenue": { "pct_low": -0.10, "pct_base": 0, "pct_high": 0.10 },
        "capital": { "p_loss_total": 0.02, ... }
      },
      "excel_mapping": { "cells": { "n_units": "C4", ... } }
    },
    "betail": { ... },
    "embouche": { ... }
  }
}
```

---

## COMMANDES COPIER-COLLER

```bash
# Tout régénérer
python3 simulate.py && python3 charts.py

# Avec Excel
python3 simulate.py && python3 charts.py && python3 excel_writer.py

# Vérifier structure results.json
python3 -c "import json; r=json.load(open('results.json')); print(list(r.keys()))"
```

---

**Contact:** Voir TECHNICAL_DOCUMENTATION.md pour détails complets.
