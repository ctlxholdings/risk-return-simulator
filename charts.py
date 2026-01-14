"""
CHARTS.PY — 14 Visualisations (pure lecture)
=============================================
Flow: results.json → charts.py → charts/*.png

AUCUNE simulation ici. Tout vient de results.json.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

print("=" * 80)
print("CHARTS.PY — Génération 14 visualisations")
print("=" * 80)

# =============================================================================
# 1. LECTURE
# =============================================================================

with open('results.json', 'r') as f:
    results = json.load(f)

Path('charts').mkdir(exist_ok=True)

N_YEARS = results['meta']['n_years']

# =============================================================================
# 2. CONFIGURATION STYLE
# =============================================================================

COLORS = {
    'immobilier': '#27ae60',
    'betail': '#3498db', 
    'embouche': '#e74c3c'
}

LABELS = {
    'immobilier': 'Immobilier',
    'betail': 'Bétail',
    'embouche': 'Embouche'
}

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'legend.fontsize': 10,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.grid': True,
    'grid.alpha': 0.3
})

years_1 = list(range(1, N_YEARS + 1))
years_0 = list(range(N_YEARS + 1))

# =============================================================================
# 3. CHARTS SANS RÉINVESTISSEMENT (A, B, C, D)
# =============================================================================

def chart_a_revenus():
    """A — Revenus annuels avec bandes P10-P90 (sans reinvest)"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data = results['simulation']['without_reinvest']
    
    for asset in ['embouche', 'betail', 'immobilier']:
        r = data[asset]['revenues']
        ax.fill_between(years_1, np.array(r['p10'])/1e6, np.array(r['p90'])/1e6,
                        color=COLORS[asset], alpha=0.2)
        ax.plot(years_1, np.array(r['mean'])/1e6, color=COLORS[asset],
                linewidth=2.5, marker='o', label=LABELS[asset])
    
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    ax.set_xlabel('Année')
    ax.set_ylabel('Revenus (M FCFA)')
    ax.set_title('A — Revenus annuels (bandes = P10-P90)', fontweight='bold')
    ax.legend(loc='upper right')
    ax.set_xticks(years_1)
    
    plt.tight_layout()
    plt.savefig('charts/chart_a_revenus.png', dpi=150)
    plt.close()
    print("✓ chart_a_revenus.png")


def chart_b_wealth():
    """B — Richesse cumulée (sans reinvest)"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data = results['simulation']['without_reinvest']
    
    for asset in ['embouche', 'betail', 'immobilier']:
        c = data[asset]['capitals']
        ax.fill_between(years_0, np.array(c['p10'])/1e6, np.array(c['p90'])/1e6,
                        color=COLORS[asset], alpha=0.2)
        ax.plot(years_0, np.array(c['mean'])/1e6, color=COLORS[asset],
                linewidth=2.5, marker='o', label=LABELS[asset])
    
    ax.axhline(y=1, color='gray', linestyle='--', linewidth=1, label='Capital initial')
    ax.set_xlabel('Année')
    ax.set_ylabel('Richesse (M FCFA)')
    ax.set_title('B — Richesse cumulée sur 5 ans', fontweight='bold')
    ax.legend(loc='upper left')
    ax.set_xticks(years_0)
    
    plt.tight_layout()
    plt.savefig('charts/chart_b_wealth.png', dpi=150)
    plt.close()
    print("✓ chart_b_wealth.png")


def chart_c_bulles():
    """C — Scatter risque-rendement (sans reinvest)"""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    data = results['simulation']['without_reinvest']
    
    points = []
    for asset in ['immobilier', 'betail', 'embouche']:
        s = data[asset]['summary']
        vol = s['volatility'] * 100
        ret = s['return_mean'] * 100
        points.append((LABELS[asset], vol, ret, COLORS[asset]))
    
    for name, vol, ret, color in points:
        ax.scatter(vol, ret, s=800, c=color, alpha=0.7, edgecolors='white', linewidth=2)
        ax.annotate(name, (vol, ret), textcoords="offset points", xytext=(12, 0),
                    ha='left', fontsize=12, fontweight='bold')
    
    ax.axhline(y=3.5, color='gray', linestyle='--', linewidth=1, label='BEAC 3.5%')
    ax.set_xlabel('Risque (Volatilité %)')
    ax.set_ylabel('Rendement moyen (%)')
    ax.set_title('C — Risque vs Rendement (sans réinvest)', fontweight='bold')
    ax.legend(loc='lower right')
    ax.set_xlim(0, max(p[1] for p in points) * 1.3)
    ax.set_ylim(0, max(p[2] for p in points) * 1.2)
    
    plt.tight_layout()
    plt.savefig('charts/chart_c_bulles.png', dpi=150)
    plt.close()
    print("✓ chart_c_bulles.png")


def chart_d_zones():
    """D — Zones risque-rendement (sans reinvest)"""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    data = results['simulation']['without_reinvest']
    
    points = []
    for asset in ['immobilier', 'betail', 'embouche']:
        s = data[asset]['summary']
        vol = s['volatility'] * 100
        ret = s['return_mean'] * 100
        points.append((LABELS[asset], vol, ret, COLORS[asset]))
    
    max_vol = max(p[1] for p in points) * 1.4
    max_ret = max(p[2] for p in points) * 1.3
    
    # Zones
    ax.axvspan(0, 50, alpha=0.1, color='green', label='Zone Sûre')
    ax.axvspan(50, 100, alpha=0.1, color='orange', label='Zone Modérée')
    ax.axvspan(100, max_vol, alpha=0.1, color='red', label='Zone Risquée')
    
    for name, vol, ret, color in points:
        ax.scatter(vol, ret, s=500, c=color, edgecolors='black', linewidth=2, zorder=5)
        ax.annotate(name, (vol, ret), textcoords="offset points", xytext=(10, 5),
                    ha='left', fontsize=11, fontweight='bold')
    
    ax.axhline(y=3.5, color='gray', linestyle='--', linewidth=1)
    ax.text(max_vol * 0.95, 3.5, 'BEAC 3.5%', ha='right', va='bottom', fontsize=10, color='gray')
    
    ax.set_xlabel('Risque (Volatilité %)')
    ax.set_ylabel('Rendement moyen (%)')
    ax.set_title('D — Zones Risque-Rendement', fontweight='bold')
    ax.legend(loc='upper left')
    ax.set_xlim(0, max_vol)
    ax.set_ylim(0, max_ret)
    
    plt.tight_layout()
    plt.savefig('charts/chart_d_zones.png', dpi=150)
    plt.close()
    print("✓ chart_d_zones.png")

# =============================================================================
# 4. CHARTS AVEC RÉINVESTISSEMENT (A-r, B-r, C-r, D-r)
# =============================================================================

def chart_a_revenus_reinvest():
    """A-r — Revenus annuels avec réinvestissement"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data = results['simulation']['with_reinvest']
    
    for asset in ['embouche', 'betail', 'immobilier']:
        r = data[asset]['revenues']
        ax.fill_between(years_1, np.array(r['p10'])/1e6, np.array(r['p90'])/1e6,
                        color=COLORS[asset], alpha=0.2)
        ax.plot(years_1, np.array(r['mean'])/1e6, color=COLORS[asset],
                linewidth=2.5, marker='o', label=LABELS[asset])
    
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    ax.set_xlabel('Année')
    ax.set_ylabel('Revenus (M FCFA)')
    ax.set_title('A-r — Revenus annuels avec réinvestissement', fontweight='bold')
    ax.legend(loc='upper left')
    ax.set_xticks(years_1)
    
    plt.tight_layout()
    plt.savefig('charts/chart_a_revenus_reinvest.png', dpi=150)
    plt.close()
    print("✓ chart_a_revenus_reinvest.png")


def chart_b_capital_reinvest():
    """B-r — Capital avec réinvestissement"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data = results['simulation']['with_reinvest']
    
    for asset in ['embouche', 'betail', 'immobilier']:
        c = data[asset]['capitals']
        ax.fill_between(years_0, np.array(c['p10'])/1e6, np.array(c['p90'])/1e6,
                        color=COLORS[asset], alpha=0.2)
        ax.plot(years_0, np.array(c['mean'])/1e6, color=COLORS[asset],
                linewidth=2.5, marker='o', label=LABELS[asset])
    
    ax.axhline(y=1, color='gray', linestyle='--', linewidth=1, label='Capital initial')
    ax.set_xlabel('Année')
    ax.set_ylabel('Capital (M FCFA)')
    ax.set_title('B-r — Capital avec réinvestissement', fontweight='bold')
    ax.legend(loc='upper left')
    ax.set_xticks(years_0)
    
    plt.tight_layout()
    plt.savefig('charts/chart_b_capital_reinvest.png', dpi=150)
    plt.close()
    print("✓ chart_b_capital_reinvest.png")


def chart_c_bulles_reinvest():
    """C-r — Scatter risque-rendement avec réinvestissement"""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    data = results['simulation']['with_reinvest']
    
    points = []
    for asset in ['immobilier', 'betail', 'embouche']:
        s = data[asset]['summary']
        vol = s['volatility'] * 100
        ret = s['return_mean'] * 100
        points.append((LABELS[asset], vol, ret, COLORS[asset]))
    
    for name, vol, ret, color in points:
        ax.scatter(vol, ret, s=800, c=color, alpha=0.7, edgecolors='white', linewidth=2)
        ax.annotate(name, (vol, ret), textcoords="offset points", xytext=(12, 0),
                    ha='left', fontsize=12, fontweight='bold')
    
    ax.axhline(y=3.5, color='gray', linestyle='--', linewidth=1, label='BEAC 3.5%')
    ax.set_xlabel('Risque (Volatilité %)')
    ax.set_ylabel('Rendement moyen (%)')
    ax.set_title('C-r — Risque vs Rendement (avec réinvest)', fontweight='bold')
    ax.legend(loc='lower right')
    ax.set_xlim(0, max(p[1] for p in points) * 1.3)
    ax.set_ylim(0, max(p[2] for p in points) * 1.2)
    
    plt.tight_layout()
    plt.savefig('charts/chart_c_bulles_reinvest.png', dpi=150)
    plt.close()
    print("✓ chart_c_bulles_reinvest.png")


def chart_d_zones_reinvest():
    """D-r — Zones avec réinvestissement"""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    data = results['simulation']['with_reinvest']
    
    points = []
    for asset in ['immobilier', 'betail', 'embouche']:
        s = data[asset]['summary']
        vol = s['volatility'] * 100
        ret = s['return_mean'] * 100
        points.append((LABELS[asset], vol, ret, COLORS[asset]))
    
    max_vol = max(p[1] for p in points) * 1.2
    max_ret = max(p[2] for p in points) * 1.2
    
    # Zones adaptées aux % plus élevés
    ax.axvspan(0, 100, alpha=0.1, color='green', label='Zone Sûre')
    ax.axvspan(100, 500, alpha=0.1, color='orange', label='Zone Modérée')
    ax.axvspan(500, max_vol, alpha=0.1, color='red', label='Zone Risquée')
    
    for name, vol, ret, color in points:
        ax.scatter(vol, ret, s=500, c=color, edgecolors='black', linewidth=2, zorder=5)
        ax.annotate(name, (vol, ret), textcoords="offset points", xytext=(10, 5),
                    ha='left', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('Risque (Volatilité %)')
    ax.set_ylabel('Rendement moyen (%)')
    ax.set_title('D-r — Zones Risque-Rendement (avec réinvest)', fontweight='bold')
    ax.legend(loc='upper left')
    ax.set_xlim(0, max_vol)
    ax.set_ylim(0, max_ret)
    
    plt.tight_layout()
    plt.savefig('charts/chart_d_zones_reinvest.png', dpi=150)
    plt.close()
    print("✓ chart_d_zones_reinvest.png")

# =============================================================================
# 5. CHARTS COMPARAISON & PÉDAGOGIE (E, F, G, H)
# =============================================================================

def chart_e_comparaison():
    """E — Comparaison avec/sans réinvestissement (3 subplots)"""
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    
    data_no = results['simulation']['without_reinvest']
    data_yes = results['simulation']['with_reinvest']
    
    for idx, asset in enumerate(['immobilier', 'betail', 'embouche']):
        ax = axes[idx]
        color = COLORS[asset]
        
        # Sans réinvestissement
        c_no = np.array(data_no[asset]['capitals']['mean']) / 1e6
        ax.plot(years_0, c_no, color=color, linewidth=2, linestyle='--', label='Sans réinv.')
        
        # Avec réinvestissement
        c_yes = data_yes[asset]['capitals']
        c_mean = np.array(c_yes['mean']) / 1e6
        c_p10 = np.array(c_yes['p10']) / 1e6
        c_p90 = np.array(c_yes['p90']) / 1e6
        ax.fill_between(years_0, c_p10, c_p90, color=color, alpha=0.15)
        ax.plot(years_0, c_mean, color=color, linewidth=2.5, marker='o', label='Avec réinv.')
        
        ax.axhline(y=1, color='gray', linestyle=':', linewidth=1)
        ax.set_xlabel('Année')
        ax.set_ylabel('Richesse (M FCFA)' if idx == 0 else '')
        ax.set_title(LABELS[asset], fontsize=12, fontweight='bold')
        ax.legend(loc='upper left', fontsize=9)
        ax.set_xticks(years_0)
    
    plt.suptitle('E — Impact du réinvestissement sur 5 ans', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('charts/chart_e_comparaison.png', dpi=150)
    plt.close()
    print("✓ chart_e_comparaison.png")


def chart_f_units():
    """F — Croissance du nombre d'unités"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data = results['simulation']['with_reinvest']
    
    for asset in ['embouche', 'betail', 'immobilier']:
        u = data[asset]['units']
        ax.fill_between(years_0, u['p10'], u['p90'], color=COLORS[asset], alpha=0.2)
        ax.plot(years_0, u['mean'], color=COLORS[asset], linewidth=2.5, marker='o', label=LABELS[asset])
    
    ax.set_xlabel('Année')
    ax.set_ylabel("Nombre d'unités")
    ax.set_title('F — Croissance des unités (avec réinvestissement)', fontweight='bold')
    ax.legend(loc='upper left')
    ax.set_xticks(years_0)
    
    plt.tight_layout()
    plt.savefig('charts/chart_f_units.png', dpi=150)
    plt.close()
    print("✓ chart_f_units.png")


def chart_g_trajectoires():
    """G — 30 trajectoires par actif (lu depuis results.json)"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    traj_data = results['trajectories']['data']
    
    for idx, asset_name in enumerate(['immobilier', 'betail', 'embouche']):
        ax = axes[idx]
        color = COLORS[asset_name]
        
        # Lire les 30 trajectoires pré-calculées
        trajectories = np.array(traj_data[asset_name])  # 30 × 5
        
        # Plot chaque trajectoire
        for run in range(trajectories.shape[0]):
            ax.plot(years_1, trajectories[run]/1e6, color=color, alpha=0.4, linewidth=1)
        
        # Moyenne
        ax.plot(years_1, trajectories.mean(axis=0)/1e6, color='black', linewidth=2.5, label='Moyenne')
        
        ax.set_xlabel('Année')
        ax.set_ylabel('Revenus (M FCFA)' if idx == 0 else '')
        ax.set_title(LABELS[asset_name], fontsize=13, fontweight='bold')
        ax.set_xticks(years_1)
        ax.legend(loc='upper right')
        ax.set_ylim(bottom=0)
    
    plt.suptitle('G — Volatilité des revenus (30 trajectoires)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('charts/chart_g_trajectoires.png', dpi=150)
    plt.close()
    print("✓ chart_g_trajectoires.png")


def chart_h_une_trajectoire():
    """H — Une seule trajectoire par actif (lu depuis results.json)"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    traj_data = results['trajectories']['data']
    
    for asset_name in ['immobilier', 'betail', 'embouche']:
        # Prendre la première trajectoire
        trajectory = np.array(traj_data[asset_name][0])  # 5 années
        
        marker = {'immobilier': 'o', 'betail': 's', 'embouche': '^'}[asset_name]
        ax.plot(years_1, trajectory/1e6, color=COLORS[asset_name],
                linewidth=2.5, marker=marker, markersize=8, label=LABELS[asset_name])
    
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    ax.set_xlabel('Année')
    ax.set_ylabel('Revenus (M FCFA)')
    ax.set_title('H — Une trajectoire par actif', fontweight='bold')
    ax.legend(loc='upper right')
    ax.set_xticks(years_1)
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig('charts/chart_h_une_trajectoire.png', dpi=150)
    plt.close()
    print("✓ chart_h_une_trajectoire.png")

# =============================================================================
# 6. VERSIONS VERTICALES TIKTOK (E-v, G-v)
# =============================================================================

def chart_e_vertical():
    """E-v — Comparaison vertical (TikTok 9:16)"""
    fig, axes = plt.subplots(3, 1, figsize=(6, 10.67))
    
    data_no = results['simulation']['without_reinvest']
    data_yes = results['simulation']['with_reinvest']
    
    for idx, asset in enumerate(['immobilier', 'betail', 'embouche']):
        ax = axes[idx]
        color = COLORS[asset]
        
        c_no = np.array(data_no[asset]['capitals']['mean']) / 1e6
        ax.plot(years_0, c_no, color=color, linewidth=2, linestyle='--', label='Sans')
        
        c_yes = np.array(data_yes[asset]['capitals']['mean']) / 1e6
        ax.plot(years_0, c_yes, color=color, linewidth=2.5, marker='o', label='Avec')
        
        ax.axhline(y=1, color='gray', linestyle=':', linewidth=1)
        ax.set_ylabel('M FCFA')
        ax.set_title(LABELS[asset], fontweight='bold')
        ax.legend(loc='upper left', fontsize=8)
        ax.set_xticks(years_0)
        if idx == 2:
            ax.set_xlabel('Année')
    
    plt.suptitle('Impact réinvestissement', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig('charts/chart_e_comparaison_vertical.png', dpi=150)
    plt.close()
    print("✓ chart_e_comparaison_vertical.png")


def chart_g_vertical():
    """G-v — Trajectoires vertical (TikTok 9:16)"""
    fig, axes = plt.subplots(3, 1, figsize=(6, 10.67))
    
    traj_data = results['trajectories']['data']
    
    for idx, asset_name in enumerate(['immobilier', 'betail', 'embouche']):
        ax = axes[idx]
        color = COLORS[asset_name]
        
        trajectories = np.array(traj_data[asset_name])
        
        for run in range(trajectories.shape[0]):
            ax.plot(years_1, trajectories[run]/1e6, color=color, alpha=0.4, linewidth=1)
        ax.plot(years_1, trajectories.mean(axis=0)/1e6, color='black', linewidth=2, label='Moy.')
        
        ax.set_ylabel('M FCFA')
        ax.set_title(LABELS[asset_name], fontweight='bold')
        ax.legend(loc='upper right', fontsize=8)
        ax.set_xticks(years_1)
        ax.set_ylim(bottom=0)
        if idx == 2:
            ax.set_xlabel('Année')
    
    plt.suptitle('30 trajectoires possibles', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig('charts/chart_g_trajectoires_vertical.png', dpi=150)
    plt.close()
    print("✓ chart_g_trajectoires_vertical.png")

# =============================================================================
# 7. EXÉCUTION
# =============================================================================

print("\nGénération des charts...")
print("-" * 40)

# Sans réinvestissement
chart_a_revenus()
chart_b_wealth()
chart_c_bulles()
chart_d_zones()

# Avec réinvestissement
chart_a_revenus_reinvest()
chart_b_capital_reinvest()
chart_c_bulles_reinvest()
chart_d_zones_reinvest()

# Comparaison & pédagogie
chart_e_comparaison()
chart_f_units()
chart_g_trajectoires()
chart_h_une_trajectoire()

# Verticales TikTok
chart_e_vertical()
chart_g_vertical()

# =============================================================================
# 8. RÉSUMÉ
# =============================================================================

print("\n" + "=" * 80)
print("RÉSUMÉ — 14 charts générés")
print("=" * 80)

import os
charts_dir = 'charts'
files = sorted(os.listdir(charts_dir))
print(f"\nDossier: {charts_dir}/")
for f in files:
    size = os.path.getsize(f"{charts_dir}/{f}") / 1024
    print(f"  {f:<40} {size:>6.1f} KB")

print("\n" + "=" * 80)
print("✓ Terminé")
print("=" * 80)
