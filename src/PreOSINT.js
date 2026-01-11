import React, { useState } from "react";
import { ShieldAlert } from "lucide-react";

export default function PreOSINT({ BACKEND_URL }) {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const scanRisk = async () => {
    if (!text.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const res = await fetch(`${BACKEND_URL}/api/preosint/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Pre-OSINT scan failed", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-black/50 border border-red-500/30 rounded-xl p-6">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <ShieldAlert className="w-5 h-5 text-red-400" />
        Pre-OSINT Exposure Scanner
      </h2>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste text you plan to post publicly..."
        className="w-full bg-black/60 text-white border border-red-500/30 rounded-lg p-3 h-32 mb-4"
      />

      <button
        onClick={scanRisk}
        disabled={loading}
        className="px-5 py-2 bg-red-600 hover:bg-red-700 rounded-lg font-medium"
      >
        {loading ? "Scanning..." : "Scan Exposure Risk"}
      </button>

      {result && (
        <div className="mt-6 border border-red-500/30 rounded-lg p-4 bg-black/40">
          <p className="text-sm mb-2">
            <strong>Risk Score:</strong> {result.risk_score}
          </p>
          <p className="text-sm mb-3">
            <strong>Overall Risk:</strong>{" "}
            <span className="text-red-400 font-bold">
              {result.overall_risk}
            </span>
          </p>

          <ul className="list-disc list-inside text-sm text-gray-300 space-y-1">
            {result.identified_risks.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
