import React, { useEffect, useState } from "react";
import axios from "axios";

export default function AnalyticsView() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    axios.get("http://localhost:8000/analytics")
      .then((res) => setData(res.data))
      .catch((err) => console.error("Analytics API error:", err));
  }, []);

  if (!data) return (
    <p className="text-white text-center mt-6 text-lg animate-pulse">
      Loading analytics...
    </p>
  );

  // 🧠 Insight placeholders — fill later
  const insights: Record<string, string> = {
    probability_distribution: "1.)Arc and Loop: The model is very unconfident when predicting these classes. The probability scores are almost always low.\n2.Whorl:The model's confidence is more varied, showing it can sometimes make high-confidence predictions for this class, unlike the other two.",
    pattern_distribution: "Frequency of each fingerprint type in the dataset.",
    heatmap: "Raw counts showing how fingerprint types map to blood groups.",
    percent_heatmap: "Percent distribution — helps compare across blood groups.",
    barplot: "Bar chart showing fingerprint count across each blood group.",
    mosaic: "Visual proportion of fingerprint types vs blood groups.",
    residuals: "Standardized residuals — deviation from expected counts under independence assumption.",
    correlation_encoded: "Correlation between encoded labels — directional but weak signal expected.",
    log_odds: "Log-Odds values from statistical model — indicates strength/direction of association.",
  };

  const plotCard = (title: string, filename: string | null, insightKey: string) => (
    <div className="bg-[#06121F] border border-gray-700 rounded-lg shadow-lg p-4 flex gap-5">
      
      {/* Chart */}
      <div className="w-1/2">
        <h3 className="font-semibold mb-2 text-white text-sm">{title}</h3>
        {filename ? (
          <img
            src={`http://localhost:8000/${filename.replace(/\\/g, "/")}`}
            alt={title}
            className="rounded border border-gray-600 w-full max-h-72 object-contain"
          />
        ) : (
          <p className="text-gray-400 text-sm">Not generated</p>
        )}
      </div>

      {/* Insight Box */}
      <div className="w-1/2 bg-[#0B1929] border border-gray-700 rounded-lg p-3">
        <h4 className="text-sm font-bold text-yellow-300 mb-1">Insight</h4>
        <p className="text-gray-300 text-xs leading-relaxed italic">
          {insights[insightKey]}
        </p>
      </div>
    </div>
  );

  return (
    <div className="p-6 text-white">
      <h2 className="text-2xl font-bold mb-6 text-center">Fingerprint ↔ Blood Group Analytics</h2>

      {/* All Plots */}
      <div className="grid grid-cols-1 gap-6">

        {plotCard("Probability Distribution", data.plots.probability_distribution, "probability_distribution")}
        {plotCard("Fingerprint Pattern Distribution", data.plots.pattern_distribution, "pattern_distribution")}
        {plotCard("Heatmap", data.plots.heatmap, "heatmap")}
        {plotCard("% Heatmap", data.plots.percent_heatmap, "percent_heatmap")}
        {plotCard("Bar Chart", data.plots.barplot, "barplot")}
        {plotCard("Mosaic Plot", data.plots.mosaic, "mosaic")}
        {plotCard("Residual Heatmap", data.plots.residuals, "residuals")}
        {plotCard("Correlation (Encoded Labels)", data.plots.correlation_encoded, "correlation_encoded")}
        {plotCard("Log-Odds Ratio", data.plots.log_odds, "log_odds")}

      </div>

      {/* Chi-Square Summary */}
      <div className="mt-8 p-4 bg-[#0A1A2B] rounded-lg border border-gray-700">
        <h3 className="text-lg font-bold text-yellow-300 mb-2">Chi-Square Test</h3>
        <p><b>Chi-Square:</b> {data.tables.chi_square.chi2.toFixed(4)}</p>
        <p><b>p-value:</b> {data.tables.chi_square.p.toFixed(6)}</p>
        <p><b>Degrees of Freedom:</b> {data.tables.chi_square.dof}</p>
      </div>
    </div>
  );
}
