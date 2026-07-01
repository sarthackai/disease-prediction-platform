/**
 * SymptomInputPage.tsx
 * User selects symptoms from a searchable checklist.
 * Sends them to the backend for prediction.
 */
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getSymptoms, predictDisease } from "../lib/api";

export default function SymptomInputPage() {
    const navigate = useNavigate();
    const [allSymptoms, setAllSymptoms] = useState<string[]>([]);
    const [search, setSearch] = useState("");
    const [selected, setSelected] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        // Load all 132 symptoms from backend
        getSymptoms().then((res) => {
            setAllSymptoms(res.data.symptoms);
        });
    }, []);

    const filtered = allSymptoms.filter((s) =>
        s.toLowerCase().replace(/_/g, " ").includes(search.toLowerCase())
    );

    const toggleSymptom = (symptom: string) => {
        setSelected((prev) =>
            prev.includes(symptom)
                ? prev.filter((s) => s !== symptom)
                : [...prev, symptom]
        );
    };

    const handlePredict = async () => {
        if (selected.length < 1) {
            setError("Please select at least 1 symptom.");
            return;
        }
        setLoading(true);
        setError("");
        try {
            const res = await predictDisease({ symptoms: selected });
            // Save result to localStorage so result page can read it
            localStorage.setItem("prediction", JSON.stringify(res.data));
            navigate("/result");
        } catch (err: any) {
            setError(
                err.response?.data?.detail || "Prediction failed. Try again."
            );
        } finally {
            setLoading(false);
        }
    };

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

            <div className="max-w-4xl mx-auto px-6 py-10">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">
                    Select Your Symptoms
                </h1>
                <p className="text-gray-500 mb-6">
                    Search and select all symptoms you are experiencing.
                </p>

                {/* Search Box */}
                <input
                    type="text"
                    placeholder="Search symptoms..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 mb-4 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />

                {/* Selected Count */}
                {selected.length > 0 && (
                    <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3 mb-4 text-sm text-indigo-700">
                        ✅ {selected.length} symptom(s) selected:{" "}
                        {selected
                            .map((s) => s.replace(/_/g, " "))
                            .join(", ")}
                    </div>
                )}

                {/* Error */}
                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-3 text-sm mb-4">
                        {error}
                    </div>
                )}

                {/* Symptom Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mb-8 max-h-96 overflow-y-auto pr-1">
                    {filtered.map((symptom) => (
                        <button
                            key={symptom}
                            onClick={() => toggleSymptom(symptom)}
                            className={`text-left px-3 py-2 rounded-lg text-sm border transition ${selected.includes(symptom)
                                    ? "bg-indigo-600 text-white border-indigo-600"
                                    : "bg-white text-gray-700 border-gray-200 hover:border-indigo-400"
                                }`}
                        >
                            {symptom.replace(/_/g, " ")}
                        </button>
                    ))}
                </div>

                {/* Predict Button */}
                <button
                    onClick={handlePredict}
                    disabled={loading || selected.length === 0}
                    className="w-full bg-indigo-600 text-white py-3 rounded-xl font-semibold text-lg hover:bg-indigo-700 transition disabled:opacity-50"
                >
                    {loading ? "Analyzing symptoms..." : "🔬 Predict Disease"}
                </button>

                {/* Disclaimer */}
                <p className="text-center text-xs text-gray-400 mt-4">
                    ⚠️ This is not a medical diagnosis. Always consult a qualified doctor.
                </p>
            </div>
        </div>
    );
}