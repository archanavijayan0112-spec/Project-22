import React, { useState } from "react";
import { api } from "../api/client";

const EMPTY_RESOURCE = {
  name: "",
  resource_type: "compute",
  instance_family: "general_purpose",
  region: "us-east-1",
  vcpus: 4,
  size_gb: 0,
  storage_type: "ssd",
  monthly_network_gb: 0,
  utilization: 0.5,
  quantity: 1,
};

const SAMPLE_ARCHITECTURE = {
  name: "Production Web Platform",
  provider: "aws",
  resources: [
    { ...EMPTY_RESOURCE, name: "web-fleet", resource_type: "compute", instance_family: "general_purpose", region: "us-east-1", vcpus: 4, utilization: 0.55, quantity: 3 },
    { ...EMPTY_RESOURCE, name: "primary-database", resource_type: "database", instance_family: "memory_optimized", region: "us-east-1", vcpus: 8, utilization: 0.65, quantity: 1 },
    { ...EMPTY_RESOURCE, name: "batch-worker", resource_type: "compute", instance_family: "burstable", region: "us-east-1", vcpus: 2, utilization: 0.1, quantity: 2 },
    { ...EMPTY_RESOURCE, name: "asset-storage", resource_type: "storage", region: "us-east-1", size_gb: 1500, storage_type: "ssd", vcpus: 0 },
    { ...EMPTY_RESOURCE, name: "cdn-origin", resource_type: "network", region: "us-east-1", vcpus: 0, monthly_network_gb: 2200 },
  ],
};

export default function UploadArchitecture({ onUploaded }) {
  const [name, setName] = useState("");
  const [provider, setProvider] = useState("aws");
  const [resources, setResources] = useState([{ ...EMPTY_RESOURCE }]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [awsSyncing, setAwsSyncing] = useState(false);

  function updateResource(index, field, value) {
    setResources((prev) =>
      prev.map((r, i) => (i === index ? { ...r, [field]: value } : r))
    );
  }

  function addResource() {
    setResources((prev) => [...prev, { ...EMPTY_RESOURCE, name: "" }]);
  }

  function removeResource(index) {
    setResources((prev) => prev.filter((_, i) => i !== index));
  }

  function loadSample() {
    setName(SAMPLE_ARCHITECTURE.name);
    setProvider(SAMPLE_ARCHITECTURE.provider);
    setResources(SAMPLE_ARCHITECTURE.resources.map((r) => ({ ...r })));
    setError(null);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Give this architecture a name before submitting.");
      return;
    }
    if (resources.length === 0 || resources.some((r) => !r.name.trim())) {
      setError("Every resource needs a name.");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        name,
        provider,
        resources: resources.map((r) => ({
          ...r,
          vcpus: Number(r.vcpus) || 0,
          size_gb: Number(r.size_gb) || 0,
          monthly_network_gb: Number(r.monthly_network_gb) || 0,
          utilization: Number(r.utilization),
          quantity: Number(r.quantity) || 1,
        })),
      };
      const architecture = await api.uploadArchitecture(payload);
      onUploaded(architecture);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleAwsSync() {
    setAwsSyncing(true);
    setError(null);
    try {
      const result = await api.syncFromAws(30);
      const imported = result.results.map((item, i) => ({
        ...EMPTY_RESOURCE,
        name: `${item.service} (${item.region})`.slice(0, 60),
        resource_type: item.service?.toLowerCase().includes("storage") ? "storage" : "compute",
        region: item.region || "us-east-1",
        vcpus: item.quantity_hours ? 2 : 0,
        size_gb: item.quantity_gb || 0,
      }));
      setName(`AWS Sync — ${new Date().toLocaleDateString()}`);
      setResources(imported.length ? imported : resources);
      if (result.source === "mock") {
        setError(
          "No AWS credentials configured — imported illustrative demo usage instead of live Cost Explorer data."
        );
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setAwsSyncing(false);
    }
  }

  return (
    <div className="panel">
      <div className="panel__header">
        <div>
          <h2>Upload your architecture</h2>
          <p>Define resources manually, pull a sample, or sync recent usage from AWS Cost Explorer.</p>
        </div>
        <div className="panel__actions">
          <button type="button" className="btn btn--ghost" onClick={loadSample}>
            Load sample architecture
          </button>
          <button type="button" className="btn btn--ghost" onClick={handleAwsSync} disabled={awsSyncing}>
            {awsSyncing ? "Syncing…" : "Sync from AWS"}
          </button>
        </div>
      </div>

      {error && <div className="banner banner--warning">{error}</div>}

      <form onSubmit={handleSubmit} className="form">
        <div className="form__row">
          <label className="field">
            <span>Architecture name</span>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Production Web Platform" />
          </label>
          <label className="field field--narrow">
            <span>Provider</span>
            <select value={provider} onChange={(e) => setProvider(e.target.value)}>
              <option value="aws">AWS</option>
              <option value="azure">Azure</option>
              <option value="gcp">GCP</option>
            </select>
          </label>
        </div>

        <div className="resource-list">
          {resources.map((resource, index) => (
            <div className="resource-card" key={index}>
              <div className="resource-card__header">
                <span className="mono resource-card__index">{String(index + 1).padStart(2, "0")}</span>
                <input
                  className="resource-card__name"
                  value={resource.name}
                  onChange={(e) => updateResource(index, "name", e.target.value)}
                  placeholder="Resource name (e.g. web-fleet)"
                />
                {resources.length > 1 && (
                  <button type="button" className="icon-btn" onClick={() => removeResource(index)} aria-label="Remove resource">
                    ✕
                  </button>
                )}
              </div>

              <div className="resource-card__grid">
                <label className="field">
                  <span>Type</span>
                  <select value={resource.resource_type} onChange={(e) => updateResource(index, "resource_type", e.target.value)}>
                    <option value="compute">Compute</option>
                    <option value="database">Database</option>
                    <option value="storage">Storage</option>
                    <option value="network">Network</option>
                  </select>
                </label>

                <label className="field">
                  <span>Region</span>
                  <input value={resource.region} onChange={(e) => updateResource(index, "region", e.target.value)} placeholder="us-east-1" />
                </label>

                {(resource.resource_type === "compute" || resource.resource_type === "database") && (
                  <>
                    <label className="field">
                      <span>Instance family</span>
                      <select value={resource.instance_family} onChange={(e) => updateResource(index, "instance_family", e.target.value)}>
                        <option value="general_purpose">General purpose</option>
                        <option value="compute_optimized">Compute optimized</option>
                        <option value="memory_optimized">Memory optimized</option>
                        <option value="storage_optimized">Storage optimized</option>
                        <option value="burstable">Burstable</option>
                        <option value="gpu_accelerated">GPU accelerated</option>
                      </select>
                    </label>
                    <label className="field field--narrow">
                      <span>vCPUs</span>
                      <input type="number" min="0" value={resource.vcpus} onChange={(e) => updateResource(index, "vcpus", e.target.value)} />
                    </label>
                    <label className="field field--narrow">
                      <span>Utilization</span>
                      <input type="number" step="0.05" min="0" max="1" value={resource.utilization} onChange={(e) => updateResource(index, "utilization", e.target.value)} />
                    </label>
                    <label className="field field--narrow">
                      <span>Quantity</span>
                      <input type="number" min="1" value={resource.quantity} onChange={(e) => updateResource(index, "quantity", e.target.value)} />
                    </label>
                  </>
                )}

                {resource.resource_type === "storage" && (
                  <>
                    <label className="field field--narrow">
                      <span>Size (GB)</span>
                      <input type="number" min="0" value={resource.size_gb} onChange={(e) => updateResource(index, "size_gb", e.target.value)} />
                    </label>
                    <label className="field">
                      <span>Storage type</span>
                      <select value={resource.storage_type} onChange={(e) => updateResource(index, "storage_type", e.target.value)}>
                        <option value="ssd">SSD</option>
                        <option value="hdd">HDD</option>
                        <option value="object_storage">Object storage</option>
                      </select>
                    </label>
                  </>
                )}

                {resource.resource_type === "network" && (
                  <label className="field field--narrow">
                    <span>Monthly transfer (GB)</span>
                    <input type="number" min="0" value={resource.monthly_network_gb} onChange={(e) => updateResource(index, "monthly_network_gb", e.target.value)} />
                  </label>
                )}
              </div>
            </div>
          ))}
        </div>

        <button type="button" className="btn btn--ghost btn--full" onClick={addResource}>
          + Add another resource
        </button>

        <button type="submit" className="btn btn--primary btn--full" disabled={loading}>
          {loading ? "Estimating…" : "Analyze footprint"}
        </button>
      </form>
    </div>
  );
}
