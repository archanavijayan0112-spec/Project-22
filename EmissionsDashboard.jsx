import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import IntensityGauge from "./IntensityGauge";

const PROVIDER_LABELS = { aws: "AWS", azure: "Azure", gcp: "GCP" };

export default function ProviderComparison({ architecture }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .compareProviders(architecture.id)
      .then((res) => !cancelled && setData(res))
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [architecture.id]);

  if (loading) return <div className="panel">Comparing providers…</div>;
  if (error) return <div className="panel banner banner--error">{error}</div>;
  if (!data) return null;

  const maxCo2 = Math.max(...data.comparisons.map((c) => c.estimated_co2_kg), 1);

  return (
    <div className="panel">
      <div className="panel__header">
        <div>
          <h2>Cross-provider comparison</h2>
          <p>Same architecture, deployed to the closest equivalent region on each provider.</p>
        </div>
      </div>

      <div className="provider-grid">
        {data.comparisons.map((c) => {
          const isGreenest = data.greenest_option && c.provider === data.greenest_option.provider;
          return (
            <div className={`provider-card ${isGreenest ? "provider-card--winner" : ""}`} key={c.provider}>
              {isGreenest && <span className="provider-card__ribbon">Greenest option</span>}
              <h3 className="provider-card__name">{PROVIDER_LABELS[c.provider]}</h3>
              <p className="provider-card__region mono">{c.region}</p>
              <div className="provider-card__co2">
                <span className="mono">{c.estimated_co2_kg.toFixed(1)}</span>
                <span> kg CO₂e/mo</span>
              </div>
              <IntensityGauge value={c.grid_intensity_g_per_kwh} label="Grid intensity" />
              <div className="provider-card__bar">
                <div
                  className="provider-card__bar-fill"
                  style={{ width: `${(c.estimated_co2_kg / maxCo2) * 100}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
