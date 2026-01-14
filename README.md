# Package v2.2 — Simulation Monte Carlo avec Storytelling Charts

**Date:** 9 janvier 2026  
**Version:** 2.2

---

## Contenu

### Fichiers Core
| Fichier | Rôle |
|---------|------|
| `model.json` | Source unique des paramètres (SST) |
| `simulate.py` | Simulation Monte Carlo (v2.1 - correct) |
| `results.json` | Résultats pré-calculés |
| `charts.py` | Génération des 19 visualisations |
| `excel_writer.py` | Export vers Excel |

### Documentation
- `QUICK_INSTRUCTIONS.md` — Guide rapide
- `TECHNICAL_DOCUMENTATION.md` — Documentation complète

---

## Charts Générés (19 total)

### Standard (14 charts)

| ID | Fichier | Description |
|----|---------|-------------|
| A | chart_a_revenus.png | Revenus annuels + bandes P10-P90 |
| B | chart_b_wealth.png | Richesse cumulée 5 ans |
| C | chart_c_bulles.png | Scatter risque-rendement |
| D | chart_d_zones.png | Zones colorées (sûre/modérée/risquée) |
| A-r | chart_a_revenus_reinvest.png | Revenus avec réinvestissement |
| B-r | chart_b_capital_reinvest.png | Capital avec réinvestissement |
| C-r | chart_c_bulles_reinvest.png | Bulles avec réinvestissement |
| D-r | chart_d_zones_reinvest.png | Zones avec réinvestissement |
| E | chart_e_comparaison.png | Comparaison avec/sans réinvest |
| F | chart_f_units.png | Croissance nombre d'unités |
| G | chart_g_trajectoires.png | 30 trajectoires par actif |
| H | chart_h_une_trajectoire.png | 1 trajectoire par actif |
| E-v | chart_e_comparaison_vertical.png | Version TikTok (9:16) |
| G-v | chart_g_trajectoires_vertical.png | Version TikTok (9:16) |

### Storytelling (5 nouveaux charts)

| ID | Fichier | Description | Message pédagogique |
|----|---------|-------------|---------------------|
| S1 | chart_s1_promesse.png | **LA PROMESSE** — Rendements théoriques | "Voici ce qu'on te promet" |
| S2 | chart_s2_mais_icons.png | **MAIS...** — Risque visualisé avec icônes | "Mais X sur 10 risquent une perte" |
| S3 | chart_s3_malchanceux.png | **SI TU ES MALCHANCEUX** — P10 wealth | "Les 10% les plus malchanceux perdent..." |
| S4 | chart_s4_ecart.png | **L'ÉCART** — Dumbbell P10-P90 | "L'écart entre chanceux et malchanceux" |
| S5 | chart_s5_chute.png | **LA CHUTE** — Slope chart promise→reality | "De 825% promis à -71% réel pour embouche" |

---

## Utilisation

```bash
# Régénérer les résultats (optionnel - results.json déjà inclus)
python3 simulate.py

# Générer tous les charts
python3 charts.py

# Export Excel (optionnel)
python3 excel_writer.py
```

---

## Résultats Clés (v2.1 correct)

### Sans réinvestissement — 5 ans

| Actif | Return moyen | P10 (malchanceux) | P90 (chanceux) | Volatilité |
|-------|--------------|-------------------|----------------|------------|
| Immobilier | +97% | +50% | +114% | 35% |
| Bétail | +232% | +118% | +332% | 89% |
| Embouche | +377% | **-71%** | +595% | 205% |

**Point clé:** L'embouche a le meilleur rendement moyen mais les 10% les plus malchanceux **perdent 71% de leur capital**.

---

## Validation

Ce package utilise la logique v2.1 **correcte**:
- Quand un veau meurt → `n_units--` (capital perdu)
- Remplacement uniquement si cash disponible

Le bug v3.1 (où n_units restait constant) a été corrigé.
