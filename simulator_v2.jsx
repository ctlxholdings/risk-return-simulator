import React, { useState, useEffect, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, Cell, ComposedChart, Area } from 'recharts';

// Simulation engine
const runSimulation = (params, nRuns = 100, nYears = 5) => {
  const results = {
    immobilier: { wealthTrajectories: [], revenueTrajectories: [], finalWealth: [] },
    betail: { wealthTrajectories: [], revenueTrajectories: [], finalWealth: [] },
    embouche: { wealthTrajectories: [], revenueTrajectories: [], finalWealth: [] }
  };

  const assets = {
    immobilier: {
      nUnits: params.immobilier.nUnits,
      priceUnit: 500000,
      profitUnit: 112100,
      cycles: 1,
      pLoss: params.immobilier.pLoss,
      revVar: params.immobilier.revVar
    },
    betail: {
      nUnits: params.betail.nUnits,
      priceUnit: 250000,
      profitUnit: 210000,
      cycles: 1,
      pLoss: params.betail.pLoss,
      revVar: params.betail.revVar
    },
    embouche: {
      nUnits: params.embouche.nUnits,
      priceUnit: 300000,
      profitUnit: 275000,
      cycles: 3,
      pLoss: params.embouche.pLoss,
      revVar: params.embouche.revVar
    }
  };

  for (const [assetName, asset] of Object.entries(assets)) {
    const initialCapital = asset.nUnits * asset.priceUnit;
    const cap = params.reinvest ? 999999 : asset.nUnits;

    for (let run = 0; run < nRuns; run++) {
      let nUnits = asset.nUnits;
      let cash = 0;
      const wealthTrajectory = [initialCapital];
      const revenueTrajectory = [];

      for (let year = 0; year < nYears; year++) {
        let yearRevenue = 0;

        for (let cycle = 0; cycle < asset.cycles; cycle++) {
          let lossesThisCycle = 0;

          for (let u = 0; u < nUnits; u++) {
            if (Math.random() < asset.pLoss) {
              lossesThisCycle++;
            } else {
              const variation = (Math.random() - 0.5) * 2 * asset.revVar;
              yearRevenue += asset.profitUnit * (1 + variation);
            }
          }

          nUnits -= lossesThisCycle;

          while (nUnits < cap && cash >= asset.priceUnit) {
            nUnits++;
            cash -= asset.priceUnit;
          }
        }

        revenueTrajectory.push(yearRevenue);
        cash += yearRevenue;

        while (nUnits < cap && cash >= asset.priceUnit) {
          nUnits++;
          cash -= asset.priceUnit;
        }

        wealthTrajectory.push(nUnits * asset.priceUnit + cash);
      }

      results[assetName].wealthTrajectories.push(wealthTrajectory);
      results[assetName].revenueTrajectories.push(revenueTrajectory);
      results[assetName].finalWealth.push(wealthTrajectory[nYears]);
    }
  }

  // Compute statistics
  const stats = {};
  for (const [assetName, data] of Object.entries(results)) {
    const finalWealth = data.finalWealth;
    const initialCapital = assets[assetName].nUnits * assets[assetName].priceUnit;
    
    const mean = finalWealth.reduce((a, b) => a + b, 0) / nRuns;
    const returns = finalWealth.map(w => (w - initialCapital) / initialCapital);
    const meanReturn = returns.reduce((a, b) => a + b, 0) / nRuns;
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - meanReturn, 2), 0) / nRuns;
    const volatility = Math.sqrt(variance);

    // Compute mean trajectory
    const meanWealthTrajectory = [];
    for (let y = 0; y <= nYears; y++) {
      const yearValues = data.wealthTrajectories.map(t => t[y]);
      meanWealthTrajectory.push(yearValues.reduce((a, b) => a + b, 0) / nRuns);
    }
    
    // Compute mean revenue trajectory
    const meanRevenueTrajectory = [];
    for (let y = 0; y < nYears; y++) {
      const yearValues = data.revenueTrajectories.map(t => t[y]);
      meanRevenueTrajectory.push(yearValues.reduce((a, b) => a + b, 0) / nRuns);
    }

    stats[assetName] = {
      meanWealth: mean,
      meanReturn: meanReturn * 100,
      volatility: volatility * 100,
      meanWealthTrajectory,
      meanRevenueTrajectory,
      // Keep first 20 trajectories for display
      sampleRevenueTrajectories: data.revenueTrajectories.slice(0, 20),
      initialCapital
    };
  }

  return stats;
};

const COLORS = {
  immobilier: '#27ae60',
  betail: '#3498db',
  embouche: '#e74c3c'
};

const COLORS_LIGHT = {
  immobilier: 'rgba(39, 174, 96, 0.15)',
  betail: 'rgba(52, 152, 219, 0.15)',
  embouche: 'rgba(231, 76, 60, 0.15)'
};

const LABELS = {
  immobilier: 'Immobilier',
  betail: 'Bétail',
  embouche: 'Embouche'
};

export default function InvestmentSimulator() {
  const [params, setParams] = useState({
    immobilier: { nUnits: 2, pLoss: 0.02, revVar: 0.10 },
    betail: { nUnits: 4, pLoss: 0.20, revVar: 0.20 },
    embouche: { nUnits: 2, pLoss: 0.20, revVar: 0.30 },
    reinvest: false
  });

  const [results, setResults] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState('all');

  const runSim = () => {
    setIsRunning(true);
    setTimeout(() => {
      const res = runSimulation(params, 200, 5);
      setResults(res);
      setIsRunning(false);
    }, 50);
  };

  useEffect(() => {
    runSim();
  }, []);

  const updateParam = (asset, key, value) => {
    setParams(prev => ({
      ...prev,
      [asset]: { ...prev[asset], [key]: value }
    }));
  };

  const wealthChartData = useMemo(() => {
    if (!results) return [];
    return [0, 1, 2, 3, 4, 5].map(year => ({
      year,
      immobilier: results.immobilier.meanWealthTrajectory[year] / 1e6,
      betail: results.betail.meanWealthTrajectory[year] / 1e6,
      embouche: results.embouche.meanWealthTrajectory[year] / 1e6
    }));
  }, [results]);

  const scatterData = useMemo(() => {
    if (!results) return [];
    return Object.entries(results).map(([name, data]) => ({
      name: LABELS[name],
      x: data.volatility,
      y: data.meanReturn,
      color: COLORS[name]
    }));
  }, [results]);

  // Build trajectory chart data for selected asset(s)
  const trajectoryChartData = useMemo(() => {
    if (!results) return { data: [], assets: [] };
    
    const assetsToShow = selectedAsset === 'all' 
      ? ['immobilier', 'betail', 'embouche'] 
      : [selectedAsset];
    
    // Build data structure for chart
    const years = [1, 2, 3, 4, 5];
    const data = years.map(year => {
      const point = { year };
      
      assetsToShow.forEach(assetName => {
        // Add each trajectory as a separate key
        results[assetName].sampleRevenueTrajectories.forEach((traj, i) => {
          point[`${assetName}_${i}`] = traj[year - 1] / 1e6;
        });
        // Add mean
        point[`${assetName}_mean`] = results[assetName].meanRevenueTrajectory[year - 1] / 1e6;
      });
      
      return point;
    });
    
    return { data, assets: assetsToShow };
  }, [results, selectedAsset]);

  const Slider = ({ label, value, onChange, min, max, step, unit = '' }) => (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium">{typeof value === 'number' ? (unit === '%' ? (value * 100).toFixed(0) + '%' : value) : value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
      />
    </div>
  );

  const AssetPanel = ({ name, color, params: assetParams, onChange }) => (
    <div className="bg-white rounded-lg p-4 shadow-sm border-l-4" style={{ borderLeftColor: color }}>
      <h3 className="font-bold text-lg mb-3" style={{ color }}>{LABELS[name]}</h3>
      <Slider
        label="Nombre d'unités"
        value={assetParams.nUnits}
        onChange={(v) => onChange('nUnits', v)}
        min={1}
        max={10}
        step={1}
      />
      <Slider
        label="Prob. perte/an"
        value={assetParams.pLoss}
        onChange={(v) => onChange('pLoss', v)}
        min={0}
        max={0.5}
        step={0.01}
        unit="%"
      />
      <Slider
        label="Variabilité revenus"
        value={assetParams.revVar}
        onChange={(v) => onChange('revVar', v)}
        min={0}
        max={0.5}
        step={0.05}
        unit="%"
      />
      {results && (
        <div className="mt-3 pt-3 border-t text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Rendement 5 ans:</span>
            <span className="font-bold" style={{ color }}>{results[name].meanReturn.toFixed(0)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Volatilité:</span>
            <span className="font-medium">{results[name].volatility.toFixed(0)}%</span>
          </div>
        </div>
      )}
    </div>
  );

  // Render trajectory lines for a single asset
  const renderTrajectoryLines = (assetName) => {
    if (!results) return null;
    const lines = [];
    
    // Individual trajectories (light)
    for (let i = 0; i < 20; i++) {
      lines.push(
        <Line
          key={`${assetName}_${i}`}
          type="monotone"
          dataKey={`${assetName}_${i}`}
          stroke={COLORS[assetName]}
          strokeWidth={1}
          strokeOpacity={0.3}
          dot={false}
          name={i === 0 ? `${LABELS[assetName]} (trajectoires)` : undefined}
          legendType={i === 0 ? 'line' : 'none'}
        />
      );
    }
    
    // Mean trajectory (bold)
    lines.push(
      <Line
        key={`${assetName}_mean`}
        type="monotone"
        dataKey={`${assetName}_mean`}
        stroke={COLORS[assetName]}
        strokeWidth={3}
        dot={{ r: 4, fill: COLORS[assetName] }}
        name={`${LABELS[assetName]} (moyenne)`}
      />
    );
    
    return lines;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">🎯 Simulateur Risque-Rendement</h1>
          <p className="text-gray-600 mt-1">Ajuste les paramètres et observe l'impact sur tes investissements</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <AssetPanel
            name="immobilier"
            color={COLORS.immobilier}
            params={params.immobilier}
            onChange={(key, value) => updateParam('immobilier', key, value)}
          />
          <AssetPanel
            name="betail"
            color={COLORS.betail}
            params={params.betail}
            onChange={(key, value) => updateParam('betail', key, value)}
          />
          <AssetPanel
            name="embouche"
            color={COLORS.embouche}
            params={params.embouche}
            onChange={(key, value) => updateParam('embouche', key, value)}
          />
          
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <h3 className="font-bold text-lg mb-3 text-gray-700">⚙️ Options</h3>
            <label className="flex items-center gap-3 mb-4 cursor-pointer">
              <input
                type="checkbox"
                checked={params.reinvest}
                onChange={(e) => setParams(prev => ({ ...prev, reinvest: e.target.checked }))}
                className="w-5 h-5 rounded accent-indigo-600"
              />
              <span className="text-sm">Réinvestir les profits</span>
            </label>
            <button
              onClick={runSim}
              disabled={isRunning}
              className="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:bg-gray-400 transition-colors"
            >
              {isRunning ? '⏳ Calcul...' : '🚀 Simuler (200 scénarios)'}
            </button>
            
            <div className="mt-4 p-3 bg-yellow-50 rounded-lg text-xs text-yellow-800">
              <strong>💡 Conseil:</strong> Plus le rendement est élevé, plus le risque (volatilité) l'est aussi !
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <h3 className="font-bold text-gray-700 mb-2">📈 Évolution de la richesse (5 ans)</h3>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={wealthChartData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis dataKey="year" label={{ value: 'Année', position: 'bottom', offset: -5 }} />
                <YAxis label={{ value: 'M FCFA', angle: -90, position: 'insideLeft' }} />
                <Tooltip formatter={(v) => `${v.toFixed(2)} M FCFA`} />
                <Legend />
                <Line type="monotone" dataKey="immobilier" stroke={COLORS.immobilier} strokeWidth={2} name="Immobilier" dot={{ r: 4 }} />
                <Line type="monotone" dataKey="betail" stroke={COLORS.betail} strokeWidth={2} name="Bétail" dot={{ r: 4 }} />
                <Line type="monotone" dataKey="embouche" stroke={COLORS.embouche} strokeWidth={2} name="Embouche" dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm">
            <h3 className="font-bold text-gray-700 mb-2">⚖️ Risque vs Rendement</h3>
            <ResponsiveContainer width="100%" height={280}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis type="number" dataKey="x" name="Volatilité" unit="%" label={{ value: 'Risque (Volatilité %)', position: 'bottom', offset: -5 }} />
                <YAxis type="number" dataKey="y" name="Rendement" unit="%" label={{ value: 'Rendement %', angle: -90, position: 'insideLeft' }} />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} formatter={(v) => `${v.toFixed(0)}%`} />
                <Scatter data={scatterData} fill="#8884d8">
                  {scatterData.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-4 mt-2 text-sm">
              {Object.entries(LABELS).map(([key, label]) => (
                <div key={key} className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[key] }} />
                  <span>{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* NEW: Revenue Trajectories Chart */}
        <div className="bg-white rounded-lg p-4 shadow-sm mb-4">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-bold text-gray-700">🎲 20 Trajectoires possibles de revenus</h3>
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedAsset('all')}
                className={`px-3 py-1 text-sm rounded-full transition-colors ${selectedAsset === 'all' ? 'bg-gray-800 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
              >
                Tous
              </button>
              {Object.entries(LABELS).map(([key, label]) => (
                <button
                  key={key}
                  onClick={() => setSelectedAsset(key)}
                  className={`px-3 py-1 text-sm rounded-full transition-colors`}
                  style={{
                    backgroundColor: selectedAsset === key ? COLORS[key] : '#e5e7eb',
                    color: selectedAsset === key ? 'white' : '#374151'
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
          <p className="text-xs text-gray-500 mb-3">
            Chaque ligne fine = un futur possible • Ligne épaisse = moyenne • La dispersion montre le risque
          </p>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={trajectoryChartData.data} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis dataKey="year" label={{ value: 'Année', position: 'bottom', offset: -5 }} />
              <YAxis label={{ value: 'Revenus (M FCFA)', angle: -90, position: 'insideLeft' }} />
              <Tooltip 
                formatter={(v, name) => {
                  if (name.includes('mean')) return [`${v.toFixed(2)} M FCFA`, 'Moyenne'];
                  return [`${v.toFixed(2)} M FCFA`, 'Trajectoire'];
                }}
              />
              {trajectoryChartData.assets.map(assetName => renderTrajectoryLines(assetName))}
            </LineChart>
          </ResponsiveContainer>
          <div className="mt-2 p-3 bg-blue-50 rounded-lg text-xs text-blue-800">
            <strong>🔍 Observe:</strong> L'immobilier a des lignes serrées (stable), l'embouche est dispersé (risqué). 
            Certaines trajectoires d'embouche tombent à 0 quand tous les veaux meurent !
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 shadow-sm">
          <h3 className="font-bold text-gray-700 mb-3">📊 Résumé comparatif</h3>
          {results && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Actif</th>
                    <th className="text-right py-2">Capital initial</th>
                    <th className="text-right py-2">Richesse Y5 (moy)</th>
                    <th className="text-right py-2">Rendement 5 ans</th>
                    <th className="text-right py-2">Volatilité</th>
                    <th className="text-right py-2">Ratio Rend/Risque</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(results).map(([name, data]) => (
                    <tr key={name} className="border-b">
                      <td className="py-2 font-medium" style={{ color: COLORS[name] }}>{LABELS[name]}</td>
                      <td className="text-right">{(data.initialCapital / 1e6).toFixed(1)} M</td>
                      <td className="text-right">{(data.meanWealth / 1e6).toFixed(2)} M</td>
                      <td className="text-right font-bold" style={{ color: COLORS[name] }}>{data.meanReturn.toFixed(0)}%</td>
                      <td className="text-right">{data.volatility.toFixed(0)}%</td>
                      <td className="text-right">{data.volatility > 0 ? (data.meanReturn / data.volatility).toFixed(2) : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="mt-4 text-center text-xs text-gray-500">
          Simulation Monte Carlo • 200 scénarios • Capital: ~1M FCFA par actif • Horizon: 5 ans
        </div>
      </div>
    </div>
  );
}
