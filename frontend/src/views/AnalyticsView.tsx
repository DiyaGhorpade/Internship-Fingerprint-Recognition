import React, { useEffect, useState } from "react";
import axios from "axios";

export default function AnalyticsView() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    axios.get("http://localhost:8000/analytics")
      .then((res) => setData(res.data))
      .catch((err) => console.error("Analytics API error:", err));
  }, []);

  if (!data) return <p className="text-white text-center mt-6">Loading analytics...</p>;

  const plotCard = (title: string, filename: string | null) => (
    <div className="p-3 bg-[#06121F] border border-gray-700 rounded-lg shadow-md">
      <h3 className="font-semibold mb-2 text-white">{title}</h3>
      {filename ? (
        <img
          src={`http://localhost:8000/${filename.replace(/\\/g, "/")}`}
          alt={title}
          className="rounded border border-gray-600 max-w-full"
        />
      ) : (
        <p className="text-gray-400 text-sm">Not generated</p>
      )}
    </div>
  );

  return (
    <div className="p-6 text-white">
      <h2 className="text-2xl font-bold mb-6">Fingerprint ↔ Blood Group Analytics</h2>

      {/* Frequency Table */}
      <h3 className="text-xl font-semibold mb-3 text-cyan-300">Frequency Table</h3>
      <pre className="bg-gray-900 p-4 rounded-lg text-sm overflow-x-auto border border-gray-700">
        {JSON.stringify(data.tables.frequency, null, 2)}
      </pre>

      {/* Plot Grid */}
      <div className="grid grid-cols-2 gap-6 mt-6">

        {plotCard("Heatmap", data.plots.heatmap)}
        {plotCard("% Heatmap", data.plots.percent_heatmap)}

        {plotCard("Bar Chart", data.plots.barplot)}
        {plotCard("Mosaic Plot", data.plots.mosaic)}

        {plotCard("Residual Heatmap", data.plots.residuals)}

        {plotCard("Correlation (Encoded Labels)", data.plots.correlation_encoded)}
        {plotCard("Fingerprint Distribution", data.plots.pattern_distribution)}


      </div>

      {/* Chi Square */}
      <div className="mt-8 p-4 bg-[#0A1A2B] rounded-lg border border-gray-700">
        <h3 className="text-lg font-bold text-yellow-300 mb-2">Chi-Square Test</h3>
        <p><b>Chi-Square:</b> {data.tables.chi_square.chi2.toFixed(4)}</p>
        <p><b>p-value:</b> {data.tables.chi_square.p.toFixed(6)}</p>
        <p><b>Degrees of Freedom:</b> {data.tables.chi_square.dof}</p>
      </div>
    </div>
  );
}
