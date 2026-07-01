/**
 * LandingPage.tsx
 * The first page users see when they visit the website.
 */
import { useNavigate } from "react-router-dom";

export default function LandingPage() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
            {/* Navbar */}
            <nav className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <span className="text-2xl">🏥</span>
                    <span className="text-xl font-bold text-indigo-700">
                        HealthAI
                    </span>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={() => navigate("/login")}
                        className="px-4 py-2 text-indigo-600 border border-indigo-600 rounded-lg hover:bg-indigo-50 transition"
                    >
                        Login
                    </button>
                    <button
                        onClick={() => navigate("/register")}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                    >
                        Get Started
                    </button>
                </div>
            </nav>

            {/* Hero Section */}
            <div className="max-w-6xl mx-auto px-6 py-20 text-center">
                <h1 className="text-5xl font-bold text-gray-800 mb-6">
                    AI-Powered Disease Prediction
                </h1>
                <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
                    Enter your symptoms and get instant AI predictions,
                    explanations, and nearby hospital recommendations.
                    Supporting SDG 3 — Good Health and Well-Being.
                </p>
                <button
                    onClick={() => navigate("/register")}
                    className="px-8 py-4 bg-indigo-600 text-white text-lg rounded-xl hover:bg-indigo-700 transition shadow-lg"
                >
                    Check Your Symptoms Now →
                </button>
            </div>

            {/* Features Section */}
            <div className="max-w-6xl mx-auto px-6 py-16">
                <h2 className="text-3xl font-bold text-center text-gray-800 mb-12">
                    What HealthAI Does
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {[
                        {
                            icon: "🔬",
                            title: "Disease Prediction",
                            desc: "ML model trained on 132 symptoms predicts 41 diseases with 97.6% accuracy."
                        },
                        {
                            icon: "🧠",
                            title: "Explainable AI",
                            desc: "SHAP explanations show exactly which symptoms influenced the prediction."
                        },
                        {
                            icon: "🏥",
                            title: "Hospital Finder",
                            desc: "Finds nearby hospitals on a live map using your real location."
                        },
                        {
                            icon: "📋",
                            title: "Medical History",
                            desc: "All your predictions saved securely for future reference."
                        },
                        {
                            icon: "📄",
                            title: "PDF Reports",
                            desc: "Download a clinical-style report to share with your doctor."
                        },
                        {
                            icon: "🌍",
                            title: "SDG 3 Aligned",
                            desc: "Built to improve healthcare access for everyone, everywhere."
                        }
                    ].map((feature, i) => (
                        <div
                            key={i}
                            className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition"
                        >
                            <div className="text-4xl mb-4">{feature.icon}</div>
                            <h3 className="text-lg font-semibold text-gray-800 mb-2">
                                {feature.title}
                            </h3>
                            <p className="text-gray-600 text-sm">{feature.desc}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Footer */}
            <footer className="text-center py-8 text-gray-500 text-sm">
                HealthAI — Final Year B.Tech AI/ML Project · SDG 3: Good Health and Well-Being
            </footer>
        </div>
    );
}