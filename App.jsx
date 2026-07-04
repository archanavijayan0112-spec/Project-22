import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import IntensityGauge from "./IntensityGauge";

export default function RegionSuggestions({ architecture }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .suggestRegions(architecture.id)
      .then((res) => !cancelled && setData(res))
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [architecture.id]);

  if (loading) return <div className="panel">Scanning regions for a cleaner grid…</div>;
  if (error) return <div className="panel banner banner--error">{error}</div>;
  if (!data) return null;

  const maxIntensity = Math.max(
    ...data.suggestions.map((s) => s.grid_intensity_g_per_kwh),
    700
  );

  return (
    <div className="panel">
      <div className="panel__header">
        <div>
          <h2>Greener region suggestions</h2>
          <p>
            Currently deployed in <span className="mono">{data.current_region}</span> at{" "}
            <strong>{data.current_co2_kg.toFixed(1)} kg CO₂e/month</strong>.
          </p>
        </div>
      </div>

      {data.suggestions.length === 0 ? (
        <div className="banner banner--success">
          You're already in one of the cleanest available regions for this provider.
        </div>
      ) : (
        <div className="region-list">
          {data.suggestions.map((s) => (
            <div className="region-card" key={s.region}>
              <div className="region-card__top">
                <span className="region-card__name mono">{s.region}</span>
                <span className={`badge ${s.co2_reduction_percent > 0 ? "badge--positive" : "badge--neutral"}`}>
                  {s.co2_reduction_percent > 0
                    ? `−${s.co2_reduction_percent.toFixed(1)}% CO₂e`
                    : `+${Math.abs(s.co2_reduction_percent).toFixed(1)}% CO₂e`}
                </span>
              </div>
              <IntensityGauge
                value={s.grid_intensity_g_per_kwh}
                max={maxIntensity}
                label="Grid intensity"
              />
              <div className="region-card__footer">
                <span>Projected footprint</span>
                <span className="mono">{s.estimated_co2_kg.toFixed(1)} kg CO₂e/month</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
