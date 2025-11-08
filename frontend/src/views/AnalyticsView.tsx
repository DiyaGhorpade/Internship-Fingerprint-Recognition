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

  // 🧠 Insights based on analysis
  const insights: Record<string, string> = {
    probability_distribution: `1.) Arc and Loop: The model is slightly unconfident when predicting these classes. The probability scores are comparatively low.

2.) Whorl: The model's confidence is more varied, showing it can sometimes make high-confidence predictions for this class, unlike the other two.`,

    pattern_distribution: `• Whorl (class2_whorl) is the most common pattern (~3400 records).
- Loop (class3_loop) is the second most common (~3100 records).
- Arch (class1_arc) is the least common (~1400 records).

This aligns with the population trends.`,

    heatmap: `This heatmap shows the raw co-occurrence counts of each fingerprint type within each blood group.

- Whorls dominate in all blood groups (highest values 379–536).
- Loops also have high frequency across most blood types (≈300–440).
- Arches have consistently low frequency (≈110–260).
- AB+ has the highest whorl count (536) and an extremely low arch count (≈162).
- AB− has unusually low whorl count (≈292), compared to others.
- O− has higher arch counts (≈248) compared to most groups.`,

    percent_heatmap: `This heatmap displays the percentage distribution of fingerprint types (Arch, Whorl, Loop) across each blood group.

- Whorl fingerprints are most common overall, typically around 37–53% depending on blood group.
- Loop fingerprints also appear frequently (~30–45%).
- Arch fingerprints are the least common (~11–26%).

Noteworthy patterns:
- AB+: Highest arch % (~26%) & high loop (~44%)
- AB-: Very low whorl (~29%) but high arch (~26%)
- A+ / B+ / O+: Balanced distribution but dominated by whorl/loop
- O-: Arch unusually high (~24.8%), whorl relatively low (~32.8%)`,

    barplot: `The actual count of each fingerprint type within every blood group.

- Loops are strong in some types (e.g., AB-, B-, O-).
- Whorl counts are highest across most blood groups.
- Arches are consistently much lower.`,

    mosaic: `A visual representation of how fingerprint types fill each blood group, weighted by total sample size.

AB- and O- show noticeable deviations (larger arch/loop blocks than expected).`,

    residuals: `Residuals = Observed − Expected
- Positive value → observed > expected (over-represented)
- Negative value → observed < expected (under-represented)

Key Findings:
- class1_arc – AB+ (5.8): More arches than expected
- class1_arc – A+ (−5.2): Fewer arches than expected
- class2_whorl – AB+ (5.3): AB+ favors whorls
- class2_whorl – AB− (−6.5): Very low whorls, strong under-representation
- class3_loop – AB− (2.9): AB− favors loops
- class1_arc – O− (4.8): O− favors arches

Blood groups AB+ and AB- show the strongest deviations:
- AB+ → higher arch & whorl
- AB− → very low whorl, higher arch & loop instead

Other subtle but real trends:
- A+ has fewer arches than expected
- O- has more arches and fewer whorls
- Certain groups like AB+ and AB− show strong deviations from expected pattern`,

    correlation_encoded: `This matrix shows correlations between numerical encodings of:
- BloodGroup
- FingerprintType
- P_arc, P_whorl, P_loop (probability columns)

Key observations:
- BloodGroup vs FingerprintType = −0.016 → Essentially no linear correlation.
- Between probability columns, strong negative relationships exist and encoded correlations cannot capture categorical relationships.
- Correlation is near zero doesn't mean "no relationship" — chi-square and log-odds prove there is an association. This is just encoding artifact.`,

    log_odds: `This shows the log-odds of each fingerprint type given each blood group (multinomial or pairwise logistic modeling).

- More negative log-odds = lower likelihood
- Less negative log-odds = higher likelihood
(0 would be neutral, but all values are negative because of baseline encoding.)

Arches (class1_arc):
- Lowest odds in A+ (−4.25) → A+ rarely has arches
- Highest among arches: AB− (−3.38) → AB− more likely to have arches

Whorls (class2_whorl):
- Lowest odds in AB− (−3.27) → AB− strongly under-represented
- Highest odds in AB+ (−2.63) → AB+ more likely to have whorls

Loops (class3_loop):
- Lowest odds in AB+ (−3.23)
- Highest odds in AB− (−2.83)

What it means:
Log-odds highlight where each fingerprint type is unusually likely or unlikely. This matches residual heatmap and frequency heatmap patterns:
- AB+ → high whorl likelihood
- AB− → high loops & arches, low whorl
- A+ → low arches
- O− → moderate arches`,

    chi_square: `• p < 0.05 → Statistically significant
- We reject the null hypothesis
- Fingerprint type and blood group are NOT independent

There is a statistically meaningful association between fingerprint type and blood group.

However, association is not equal to strong prediction. It means distribution patterns differ, but fingerprints cannot accurately predict blood type for individuals.`,
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
      <div className="w-1/2 bg-[#0B1929] border border-gray-700 rounded-lg p-3 overflow-y-auto max-h-72">
        <h4 className="text-sm font-bold text-yellow-300 mb-1 sticky top-0 bg-[#0B1929] pb-1">Insight</h4>
        <p className="text-gray-300 text-xs leading-relaxed whitespace-pre-line">
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
      <div className="mt-8 bg-[#06121F] border border-gray-700 rounded-lg shadow-lg p-4 flex gap-5">
        
        {/* Chi-Square Stats */}
        <div className="w-1/2 bg-[#0A1A2B] rounded-lg border border-gray-700 p-4">
          <h3 className="text-lg font-bold text-yellow-300 mb-3">Chi-Square Test</h3>
          <p className="text-white mb-1"><b>Chi-Square:</b> {data.tables.chi_square.chi2.toFixed(4)}</p>
          <p className="text-white mb-1"><b>p-value:</b> {data.tables.chi_square.p.toFixed(6)}</p>
          <p className="text-white"><b>Degrees of Freedom:</b> {data.tables.chi_square.dof}</p>
        </div>

        {/* Chi-Square Insight */}
        <div className="w-1/2 bg-[#0B1929] border border-gray-700 rounded-lg p-3 overflow-y-auto max-h-72">
          <h4 className="text-sm font-bold text-yellow-300 mb-1 sticky top-0 bg-[#0B1929] pb-1">Insight</h4>
          <p className="text-gray-300 text-xs leading-relaxed whitespace-pre-line">
            {insights.chi_square}
          </p>
        </div>
      </div>
    </div>
  );
}