import React from "react";

/**
 * The app's signature visual element: a horizontal gradient bar spanning the
 * clean -> severe carbon intensity scale, with a marker showing where a given
 * value falls. Reused across the dashboard, region suggestions, and provider
 * comparison so the same visual language means the same thing everywhere.
 */
export default function IntensityGauge({ value, min = 0, max = 700, label, unit = "gCO₂/kWh" }) {
  const clamped = Math.max(min, Math.min(max, value));
  const pct = ((clamped - min) / (max - min)) * 100;

  return (
    <div className="intensity-gauge">
      {label && (
        <div className="intensity-gauge__label">
          <span>{label}</span>
          <span className="mono intensity-gauge__value">
            {value.toFixed(1)} {unit}
          </span>
        </div>
      )}
      <div className="intensity-gauge__track">
        <div className="intensity-gauge__marker" style={{ left: `${pct}%` }} />
      </div>
    </div>
  );
}
