"""
SIMULATE.PY — Monte Carlo unifié
=================================
Flow: model.json → simulate.py → results.json

Règle unifiée:
- Sans réinvestissement: on remplace les pertes SI cash disponible, cap = n_units_initial
- Avec réinvestissement: on achète autant qu'on peut, cap = ∞

La seule différence = le plafond d'unités.
"""

import json
import numpy as np
from datetime import datetime

print("=" * 80)
print("SIMULATE.PY — Monte Carlo unifié")
print("=" * 80)

# =============================================================================
# 1. LECTURE SOURCE UNIQUE
# =============================================================================

with open('model.json', 'r') as f:
    model = json.load(f)

N_RUNS = model['simulation']['n_runs']
N_YEARS = model['simulation']['n_years']
SEED = model['simulation']['seed']

print(f"\nConfiguration: {N_RUNS} runs × {N_YEARS} years (seed={SEED})")

# =============================================================================
# 2. CALCULS P&L (inline)
# =============================================================================

def calculate_pnl(asset_name, asset_data):
    """Calcule P&L depuis les inputs. Retourne profit PAR UNITÉ PAR CYCLE."""
    
    cfg = asset_data['config']
    inp = asset_data['inputs']
    
    n_units = cfg['n_units']
    price_unit = cfg['price_unit']
    n_cycles = cfg['n_cycles_year']
    
    if asset_name == 'immobilier':
        revenue_unit_year = inp['rent_month'] * inp['n_months_occupied']
        cost_unit_year = inp['cost_maintenance'] + inp['cost_taxes'] + inp['cost_management']
        profit_unit_cycle = revenue_unit_year - cost_unit_year
        capital_total = n_units * price_unit
        
    elif asset_name == 'betail':
        milk_net = inp['milk_liters_day'] * inp['n_days_production'] * (1 - inp['pct_milk_loss'])
        revenue_milk = milk_net * inp['price_milk_liter']
        revenue_calf = inp['pct_birth_rate'] * inp['calf_weight_kg'] * inp['price_calf_kg']
        revenue_unit_year = revenue_milk + revenue_calf
        cost_unit_year = inp['cost_feed'] + inp['cost_vet'] + inp['cost_other']
        profit_unit_cycle = revenue_unit_year - cost_unit_year
        capital_total = n_units * price_unit
        
    elif asset_name == 'embouche':
        weight_sell = inp['weight_buy_kg'] + inp['weight_gain_kg']
        revenue_unit_cycle = weight_sell * inp['price_sell_kg']
        cost_unit_cycle = price_unit + inp['cost_feed_cycle'] + inp['cost_vet_cycle'] + inp['cost_other_cycle']
        profit_unit_cycle = revenue_unit_cycle - cost_unit_cycle
        capital_total = (inp['cost_hangar_year'] + 
                        n_units * (price_unit + inp['cost_feed_cycle'] + 
                                   inp['cost_vet_cycle'] + inp['cost_other_cycle']))
    
    profit_unit_year = profit_unit_cycle * n_cycles
    profit_total_year = profit_unit_year * n_units
    return_year = profit_total_year / capital_total
    
    return {
        'n_units': n_units,
        'price_unit': price_unit,
        'n_cycles_year': n_cycles,
        'profit_unit_cycle': profit_unit_cycle,
        'profit_unit_year': profit_unit_year,
        'profit_total_year': profit_total_year,
        'capital_total': capital_total,
        'return_year': return_year,
        'n_events_year': n_units * n_cycles
    }

# =============================================================================
# 3. SIMULATION UNIFIÉE
# =============================================================================

def simulate_asset(asset_name, asset_data, pnl_data, n_runs, n_years, cap):
    """
    Simulation unifiée.
    
    Args:
        cap: plafond d'unités
             - n_units_initial pour mode "sans réinvest"
             - 999999 pour mode "avec réinvest"
    
    Returns:
        revenues[n_runs, n_years]
        capitals[n_runs, n_years+1]
        units[n_runs, n_years+1]
    """
    
    cfg = asset_data['config']
    risks = asset_data['risks']
    
    n_units_initial = cfg['n_units']
    price_unit = cfg['price_unit']
    n_cycles = cfg['n_cycles_year']
    profit_unit_cycle = pnl_data['profit_unit_cycle']
    initial_capital = pnl_data['capital_total']
    
    # Risques
    rev_low = risks['revenue']['pct_low']
    rev_base = risks['revenue']['pct_base']
    rev_high = risks['revenue']['pct_high']
    p_loss = risks['capital']['p_loss_total']
    
    # Storage
    revenues = np.zeros((n_runs, n_years))
    capitals = np.zeros((n_runs, n_years + 1))
    units = np.zeros((n_runs, n_years + 1))
    
    for run in range(n_runs):
        n_units = n_units_initial
        cash = 0.0
        
        capitals[run, 0] = initial_capital
        units[run, 0] = n_units
        
        for year in range(n_years):
            year_revenue = 0.0
            
            for cycle in range(n_cycles):
                # Compteur de pertes ce cycle
                losses_this_cycle = 0
                
                # Chaque unité vivante peut produire ou mourir
                for u in range(n_units):
                    roll = np.random.random()
                    
                    if roll < p_loss:
                        # Unité perdue ce cycle - pas de revenu
                        losses_this_cycle += 1
                    else:
                        # Unité produit
                        rev_var = np.random.triangular(rev_low, rev_base, rev_high)
                        year_revenue += profit_unit_cycle * (1 + rev_var)
                
                # Fin de cycle: retirer les unités mortes
                n_units -= losses_this_cycle
                
                # Fin de cycle: remplacer les pertes si possible (jusqu'au cap)
                while n_units < cap and cash >= price_unit:
                    n_units += 1
                    cash -= price_unit
            
            # Fin d'année: enregistrer revenus
            revenues[run, year] = year_revenue
            cash += year_revenue
            
            # Fin d'année: acheter encore si possible (jusqu'au cap)
            while n_units < cap and cash >= price_unit:
                n_units += 1
                cash -= price_unit
            
            # Capital = valeur des unités + cash
            capitals[run, year + 1] = n_units * price_unit + cash
            units[run, year + 1] = n_units
    
    return revenues, capitals, units


def generate_trajectories(asset_name, asset_data, pnl_data, n_traj, n_years, cap, seed):
    """
    Génère n_traj trajectoires pour visualisation.
    Même logique que simulate_asset.
    
    Returns:
        revenues[n_traj, n_years]  # Trajectoires brutes (revenus annuels)
    """
    np.random.seed(seed)
    
    cfg = asset_data['config']
    risks = asset_data['risks']
    
    n_units_initial = cfg['n_units']
    price_unit = cfg['price_unit']
    n_cycles = cfg['n_cycles_year']
    profit_unit_cycle = pnl_data['profit_unit_cycle']
    
    rev_low = risks['revenue']['pct_low']
    rev_base = risks['revenue']['pct_base']
    rev_high = risks['revenue']['pct_high']
    p_loss = risks['capital']['p_loss_total']
    
    trajectories = np.zeros((n_traj, n_years))
    
    for run in range(n_traj):
        n_units = n_units_initial
        cash = 0.0
        
        for year in range(n_years):
            year_revenue = 0.0
            
            for cycle in range(n_cycles):
                losses_this_cycle = 0
                
                for u in range(n_units):
                    roll = np.random.random()
                    if roll < p_loss:
                        losses_this_cycle += 1
                    else:
                        rev_var = np.random.triangular(rev_low, rev_base, rev_high)
                        year_revenue += profit_unit_cycle * (1 + rev_var)
                
                n_units -= losses_this_cycle
                
                while n_units < cap and cash >= price_unit:
                    n_units += 1
                    cash -= price_unit
            
            trajectories[run, year] = year_revenue
            cash += year_revenue
            
            while n_units < cap and cash >= price_unit:
                n_units += 1
                cash -= price_unit
    
    return trajectories

# =============================================================================
# 4. CALCUL P&L
# =============================================================================

pnl = {}
print("\nP&L THÉORIQUE (sans risque):")
print("-" * 60)
for asset_name in ['immobilier', 'betail', 'embouche']:
    pnl[asset_name] = calculate_pnl(asset_name, model['assets'][asset_name])
    p = pnl[asset_name]
    print(f"{asset_name:<12} profit/unit/cycle={p['profit_unit_cycle']:>10,.0f}  "
          f"return/year={p['return_year']:>7.1%}  events={p['n_events_year']}")

# =============================================================================
# 5. EXÉCUTION DES SIMULATIONS
# =============================================================================

print("\n" + "=" * 80)
print("SIMULATIONS EN COURS...")
print("=" * 80)

results_without = {}
results_with = {}
trajectories = {}

for asset_name in ['immobilier', 'betail', 'embouche']:
    asset_data = model['assets'][asset_name]
    pnl_data = pnl[asset_name]
    initial_capital = pnl_data['capital_total']
    n_units_initial = pnl_data['n_units']
    
    # --- MODE SANS RÉINVESTISSEMENT (cap = n_units_initial) ---
    np.random.seed(SEED)
    print(f"\n{asset_name} (sans reinvest, cap={n_units_initial})...", end=" ")
    
    rev, cap, units = simulate_asset(
        asset_name, asset_data, pnl_data, N_RUNS, N_YEARS, cap=n_units_initial
    )
    
    results_without[asset_name] = {
        'revenues': {
            'mean': rev.mean(axis=0).tolist(),
            'p10': np.percentile(rev, 10, axis=0).tolist(),
            'p50': np.percentile(rev, 50, axis=0).tolist(),
            'p90': np.percentile(rev, 90, axis=0).tolist(),
        },
        'capitals': {
            'mean': cap.mean(axis=0).tolist(),
            'p10': np.percentile(cap, 10, axis=0).tolist(),
            'p50': np.percentile(cap, 50, axis=0).tolist(),
            'p90': np.percentile(cap, 90, axis=0).tolist(),
        },
        'units': {
            'mean': units.mean(axis=0).tolist(),
            'p10': np.percentile(units, 10, axis=0).tolist(),
            'p90': np.percentile(units, 90, axis=0).tolist(),
        },
        'summary': {
            'return_mean': float((cap[:, -1] / initial_capital - 1).mean()),
            'return_p10': float(np.percentile(cap[:, -1] / initial_capital - 1, 10)),
            'return_p90': float(np.percentile(cap[:, -1] / initial_capital - 1, 90)),
            'volatility': float((cap[:, -1] / initial_capital - 1).std()),
            'units_final_mean': float(units[:, -1].mean()),
        }
    }
    
    s = results_without[asset_name]['summary']
    print(f"return={s['return_mean']:.1%}, vol={s['volatility']:.1%}")
    
    # --- MODE AVEC RÉINVESTISSEMENT (cap = ∞) ---
    np.random.seed(SEED)
    print(f"{asset_name} (avec reinvest, cap=∞)...", end=" ")
    
    rev, cap, units = simulate_asset(
        asset_name, asset_data, pnl_data, N_RUNS, N_YEARS, cap=999999
    )
    
    results_with[asset_name] = {
        'revenues': {
            'mean': rev.mean(axis=0).tolist(),
            'p10': np.percentile(rev, 10, axis=0).tolist(),
            'p50': np.percentile(rev, 50, axis=0).tolist(),
            'p90': np.percentile(rev, 90, axis=0).tolist(),
        },
        'capitals': {
            'mean': cap.mean(axis=0).tolist(),
            'p10': np.percentile(cap, 10, axis=0).tolist(),
            'p50': np.percentile(cap, 50, axis=0).tolist(),
            'p90': np.percentile(cap, 90, axis=0).tolist(),
        },
        'units': {
            'mean': units.mean(axis=0).tolist(),
            'p10': np.percentile(units, 10, axis=0).tolist(),
            'p90': np.percentile(units, 90, axis=0).tolist(),
        },
        'summary': {
            'return_mean': float((cap[:, -1] / initial_capital - 1).mean()),
            'return_p10': float(np.percentile(cap[:, -1] / initial_capital - 1, 10)),
            'return_p90': float(np.percentile(cap[:, -1] / initial_capital - 1, 90)),
            'volatility': float((cap[:, -1] / initial_capital - 1).std()),
            'units_final_mean': float(units[:, -1].mean()),
        }
    }
    
    s = results_with[asset_name]['summary']
    print(f"return={s['return_mean']:.1%}, vol={s['volatility']:.1%}, units={s['units_final_mean']:.1f}")
    
    # --- TRAJECTOIRES POUR CHARTS G/H (mode sans réinvest) ---
    traj = generate_trajectories(
        asset_name, asset_data, pnl_data, 
        n_traj=30, n_years=N_YEARS, cap=n_units_initial, seed=123
    )
    trajectories[asset_name] = traj.tolist()

# =============================================================================
# 6. SAUVEGARDE RÉSULTATS
# =============================================================================

results = {
    'meta': {
        'version': '2.1',
        'timestamp': datetime.now().isoformat(),
        'source': 'model.json',
        'n_runs': N_RUNS,
        'n_years': N_YEARS,
        'seed': SEED
    },
    'pnl': {
        asset_name: {
            'profit_unit_cycle': pnl[asset_name]['profit_unit_cycle'],
            'profit_unit_year': pnl[asset_name]['profit_unit_year'],
            'profit_total_year': pnl[asset_name]['profit_total_year'],
            'capital_total': pnl[asset_name]['capital_total'],
            'return_year': pnl[asset_name]['return_year'],
            'n_events_year': pnl[asset_name]['n_events_year']
        }
        for asset_name in ['immobilier', 'betail', 'embouche']
    },
    'simulation': {
        'without_reinvest': results_without,
        'with_reinvest': results_with
    },
    'trajectories': {
        'meta': {'seed': 123, 'n_runs': 30, 'mode': 'without_reinvest'},
        'data': trajectories
    }
}

with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)

# =============================================================================
# 7. RÉSUMÉ FINAL
# =============================================================================

print("\n" + "=" * 80)
print("RÉSUMÉ")
print("=" * 80)

print("\nSANS RÉINVESTISSEMENT (cap = n_units_initial):")
print("-" * 60)
print(f"{'Actif':<12} {'Return 5Y':<12} {'Volatilité':<12} {'Units Y5':<10}")
print("-" * 60)
for asset_name in ['immobilier', 'betail', 'embouche']:
    s = results_without[asset_name]['summary']
    print(f"{asset_name:<12} {s['return_mean']:>10.1%} {s['volatility']:>10.1%} {s['units_final_mean']:>8.1f}")

print("\nAVEC RÉINVESTISSEMENT (cap = ∞):")
print("-" * 60)
print(f"{'Actif':<12} {'Return 5Y':<12} {'Volatilité':<12} {'Units Y5':<10}")
print("-" * 60)
for asset_name in ['immobilier', 'betail', 'embouche']:
    s = results_with[asset_name]['summary']
    print(f"{asset_name:<12} {s['return_mean']:>10.1%} {s['volatility']:>10.1%} {s['units_final_mean']:>8.1f}")

print("\n" + "=" * 80)
print("✓ results.json créé (2 modes + 30 trajectoires)")
print("=" * 80)
