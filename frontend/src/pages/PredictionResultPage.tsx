/**
 * PredictionResultPage.tsx
 * Shows the disease prediction result, confidence score,
 * SHAP explanation, severity, and prevention tips.
 */
import { useNavigate } from "react-router-dom";
import api from "../lib/api";
import { useState } from "react";

export default function PredictionResultPage() {
    const navigate = useNavigate();
    const prediction = JSON.parse(
        localStorage.getItem("prediction") || "null"
    );
    const [downloading, setDownloading] = useState(false);

    const handleDownloadPDF = async () => {
        setDownloading(true);
        try {
            const response = await api.get(
                `/api/v1/reports/generate/${prediction.prediction_id}`,
                { responseType: "blob" }
            );
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement("a");
            link.href = url;
            link.setAttribute(
                "download",
                `HealthAI_Report_${prediction.prediction_id.slice(0, 8)}.pdf`
            );
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            alert("Could not generate PDF. Try again.");
        } finally {
            setDownloading(false);
        }
    };
    if (!prediction) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <p className="text-gray-500 mb-4">No prediction found.</p>
                    <button
                        onClick={() => navigate("/symptoms")}
                        className="bg-indigo-600 text-white px-6 py-2 rounded-lg"
                    >
                        Check Symptoms
                    </button>
                </div>
            </div>
        );
    }

    const severityColors: Record<string, string> = {
        low: "bg-green-100 text-green-700 border-green-300",
        moderate: "bg-yellow-100 text-yellow-700 border-yellow-300",
        high: "bg-orange-100 text-orange-700 border-orange-300",
        critical: "bg-red-100 text-red-700 border-red-300",
    };
    const severityColor =
        severityColors[prediction.severity_level] ||
        "bg-gray-100 text-gray-700";
    return (
        <div className="min-h-screen bg-gray-50">
            {/* Navbar */}
            <nav className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <span className="text-2xl">🏥</span>
                    <span className="text-xl font-bold text-indigo-700">HealthAI</span>
                </div>
                <button
                    onClick={() => navigate("/dashboard")}
                    className="text-sm text-indigo-600 hover:underline"
                >
                    ← Back to Dashboard
                </button>
            </nav>

            <div className="max-w-4xl mx-auto px-6 py-10 space-y-6">
                <h1 className="text-3xl font-bold text-gray-800">
                    Prediction Result
                </h1>

                {/* Main Result Card */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                    <div className="flex items-start justify-between flex-wrap gap-4">
                        <div>
                            <p className="text-sm text-gray-500 mb-1">Predicted Disease</p>
                            <h2 className="text-3xl font-bold text-indigo-700">
                                {prediction.predicted_disease}
                            </h2>
                            <p className="text-sm text-gray-500 mt-1">
                                Recommended Specialist:{" "}
                                <span className="font-medium text-gray-700">
                                    {prediction.specialist_type}
                                </span>
                            </p>
                        </div>
                        <div className="text-right">
                            <p className="text-sm text-gray-500 mb-1">Confidence Score</p>
                            <p className="text-4xl font-bold text-indigo-600">
                                {(prediction.confidence_score * 100).toFixed(1)}%
                            </p>
                        </div>
                    </div>

                    {/* Confidence Bar */}
                    <div className="mt-4">
                        <div className="w-full bg-gray-100 rounded-full h-3">
                            <div
                                className="bg-indigo-600 h-3 rounded-full transition-all"
                                style={{
                                    width: `${prediction.confidence_score * 100}%`,
                                }}
                            />
                        </div>
                    </div>

                    {/* Severity Badge */}
                    <div className="mt-4">
                        <span
                            className={`inline-block px-4 py-1 rounded-full text-sm font-medium border ${severityColor}`}
                        >
                            Severity: {prediction.severity_level.toUpperCase()}
                        </span>
                    </div>
                </div>

                {/* Top Predictions */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">
                        🎯 Top Predictions
                    </h3>
                    <div className="space-y-3">
                        {prediction.top_predictions.map((p: any, i: number) => (
                            <div key={i}>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-gray-700 font-medium">
                                        {i + 1}. {p.disease}
                                    </span>
                                    <span className="text-indigo-600 font-semibold">
                                        {(p.probability * 100).toFixed(1)}%
                                    </span>
                                </div>
                                <div className="w-full bg-gray-100 rounded-full h-2">
                                    <div
                                        className="bg-indigo-400 h-2 rounded-full"
                                        style={{ width: `${p.probability * 100}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* SHAP Explanation */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-1">
                        🧠 Why This Prediction?
                    </h3>
                    <p className="text-sm text-gray-500 mb-4">
                        These symptoms most influenced the AI's decision (SHAP Explainable AI):
                    </p>
                    <div className="space-y-3">
                        {prediction.shap_explanation.map((s: any, i: number) => (
                            <div key={i}>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-gray-700">
                                        {s.symptom.replace(/_/g, " ")}
                                    </span>
                                    <span
                                        className={
                                            s.shap_value >= 0
                                                ? "text-green-600 font-medium"
                                                : "text-red-500 font-medium"
                                        }
                                    >
                                        {s.shap_value >= 0 ? "+" : ""}
                                        {s.shap_value.toFixed(4)}
                                    </span>
                                </div>
                                <div className="w-full bg-gray-100 rounded-full h-2">
                                    <div
                                        className={`h-2 rounded-full ${s.shap_value >= 0 ? "bg-green-500" : "bg-red-400"
                                            }`}
                                        style={{
                                            width: `${Math.min(
                                                Math.abs(s.shap_value) * 200,
                                                100
                                            )}%`,
                                        }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                    <p className="text-xs text-gray-400 mt-3">
                        Green = pushed toward this disease · Red = pushed away
                    </p>
                </div>

                {/* Prevention Tips */}
                {prediction.prevention_tips &&
                    prediction.prevention_tips.length > 0 && (
                        <div className="bg-green-50 rounded-2xl border border-green-200 p-6">
                            <h3 className="text-lg font-semibold text-green-800 mb-3">
                                🛡️ Prevention Tips
                            </h3>
                            <ul className="space-y-2">
                                {prediction.prevention_tips.map(
                                    (tip: string, i: number) => (
                                        <li key={i} className="flex items-start gap-2 text-sm text-green-700">
                                            <span>✅</span>
                                            <span>{tip}</span>
                                        </li>
                                    )
                                )}
                            </ul>
                        </div>
                    )}

                {/* Action Buttons */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button
                        onClick={() => navigate("/hospitals")}
                        className="bg-emerald-600 text-white py-3 rounded-xl font-semibold hover:bg-emerald-700 transition"
                    >
                        🏥 Find Nearby Hospitals
                    </button>
                    <button
                        onClick={() => navigate("/symptoms")}
                        className="bg-indigo-600 text-white py-3 rounded-xl font-semibold hover:bg-indigo-700 transition"
                    >
                        🔬 Check Again
                    </button>
                    <button
                        onClick={handleDownloadPDF}
                        disabled={downloading}
                        className="bg-purple-600 text-white py-3 rounded-xl font-semibold hover:bg-purple-700 transition disabled:opacity-50"
                    >
                        {downloading ? "Generating..." : "📄 Download PDF"}
                    </button>
                </div>
                {/* Disclaimer */}
                <p className="text-center text-xs text-gray-400 pb-6">
                    ⚠️ This is not a medical diagnosis. Always consult a qualified doctor.
                </p>
            </div>
        </div>
    );
}