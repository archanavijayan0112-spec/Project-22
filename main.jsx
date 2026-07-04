import React, { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api/client";
import IntensityGauge from "./IntensityGauge";

// Static hex values mirroring the CSS custom properties, used directly since
// recharts renders to SVG fills before the DOM guarantees computed styles.
const TYPE_COLORS = {
  compute: "#e8b23d",
  database: "#d9713c",
  storage: "#5fb8b3",
  network: "#4fc17d",
};

export default function EmissionsDashboard({ architecture }) {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .estimateEmissions(architecture.id)
      .then((data) => !cancelled && setSummary(data))
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [architecture.id]);

  if (loading) return <div className="panel">Calculating emissions…</div>;
  if (error) return <div className="panel banner banner--error">{error}</div>;
  if (!summary) return null;

  const chartData = summary.breakdown.map((r) => ({
    name: r.resource_name,
    co2: r.co2_kg,
    type: r.resource_type,
  }));

  return (
    <div className="panel">
      <div className="panel__header">
        <div>
          <h2>{summary.architecture_name}</h2>
          <p>Monthly footprint estimate for {summary.provider.toUpperCase()}</p>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat-card stat-card--accent">
          <span className="stat-card__label">Total CO₂e / month</span>
          <span className="stat-card__value mono">{summary.total_co2_kg.toFixed(1)} kg</span>
        </div>
        <div className="stat-card">
          <span className="stat-card__label">Energy consumed</span>
          <span className="stat-card__value mono">{summary.total_energy_kwh.toFixed(1)} kWh</span>
        </div>
        <div className="stat-card">
          <span className="stat-card__label">≈ trees needed / year</span>
          <span className="stat-card__value mono">{summary.equivalent_trees_needed.toFixed(1)}</span>
        </div>
        <div className="stat-card">
          <span className="stat-card__label">≈ km driven</span>
          <span className="stat-card__value mono">{summary.equivalent_km_driven.toFixed(0)}</span>
        </div>
      </div>

      <div className="chart-card">
        <h3 className="chart-card__title">Emissions by resource</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid stroke="var(--border-subtle)" vertical={false} />
            <XAxis dataKey="name" stroke="var(--text-tertiary)" tick={{ fontSize: 12 }} />
            <YAxis stroke="var(--text-tertiary)" tick={{ fontSize: 12 }} unit=" kg" />
            <Tooltip
              contentStyle={{ background: "var(--bg-surface-raised)", border: "1px solid var(--border-subtle)", borderRadius: 8, color: "var(--text-primary)" }}
              formatter={(value) => [`${value.toFixed(2)} kg CO₂e`, "Emissions"]}
            />
            <Bar dataKey="co2" radius={[6, 6, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={index} fill={TYPE_COLORS[entry.type] || "#5fb8b3"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="resource-emission-list">
        <h3 className="chart-card__title">Resource breakdown</h3>
        {summary.breakdown
          .sort((a, b) => b.co2_kg - a.co2_kg)
          .map((r) => (
            <div className="resource-emission-row" key={r.resource_id}>
              <div className="resource-emission-row__meta">
                <span className="resource-emission-row__name">{r.resource_name}</span>
                <span className="resource-emission-row__type">{r.resource_type} · {r.region}</span>
              </div>
              <div className="resource-emission-row__gauge">
                <IntensityGauge value={r.co2_kg} min={0} max={Math.max(...summary.breakdown.map((b) => b.co2_kg), 1)} unit="kg CO₂e" />
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}
