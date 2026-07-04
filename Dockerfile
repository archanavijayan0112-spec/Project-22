import React, { useState } from "react";
import Navbar from "./components/Navbar";
import UploadArchitecture from "./components/UploadArchitecture";
import EmissionsDashboard from "./components/EmissionsDashboard";
import RegionSuggestions from "./components/RegionSuggestions";
import ProviderComparison from "./components/ProviderComparison";
import Recommendations from "./components/Recommendations";

export default function App() {
  const [architecture, setArchitecture] = useState(null);
  const [tab, setTab] = useState("upload");

  function handleUploaded(arch) {
    setArchitecture(arch);
    setTab("dashboard");
  }

  return (
    <div className="app-shell">
      <Navbar active={tab} onChange={setTab} hasArchitecture={Boolean(architecture)} />
      <main className="app-content">
        {tab === "upload" && <UploadArchitecture onUploaded={handleUploaded} />}

        {tab !== "upload" && !architecture && (
          <div className="empty-state">
            <p>Upload an architecture first to see this view.</p>
          </div>
        )}

        {tab === "dashboard" && architecture && <EmissionsDashboard architecture={architecture} />}
        {tab === "regions" && architecture && <RegionSuggestions architecture={architecture} />}
        {tab === "compare" && architecture && <ProviderComparison architecture={architecture} />}
        {tab === "recommendations" && architecture && <Recommendations architecture={architecture} />}
      </main>
    </div>
  );
}
