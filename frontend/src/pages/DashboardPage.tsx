/**
 * DashboardPage.tsx
 * Main page users see after logging in.
 */
import { useNavigate } from "react-router-dom";

export default function DashboardPage() {
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        navigate("/");
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Navbar */}
            <nav className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <span className="text-2xl">🏥</span>
                    <span className="text-xl font-bold text-indigo-700">HealthAI</span>
                </div>
                <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-600">
                        Hello, {user.full_name || "User"} 👋
                    </span>
                    <button
                        onClick={handleLogout}
                        className="text-sm text-red-500 hover:underline"
                    >
                        Logout
                    </button>
                </div>
            </nav>

            {/* Main Content */}
            <div className="max-w-6xl mx-auto px-6 py-10">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">
                    Your Health Dashboard
                </h1>
                <p className="text-gray-500 mb-10">
                    What would you like to do today?
                </p>

                {/* Action Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[
                        {
                            icon: "🔬",
                            title: "Check Symptoms",
                            desc: "Enter your symptoms and get an AI-powered disease prediction.",
                            color: "bg-indigo-600",
                            action: () => navigate("/symptoms"),
                        },
                        {
                            icon: "🏥",
                            title: "Find Hospitals",
                            desc: "Locate nearby hospitals and clinics on a live map.",
                            color: "bg-emerald-600",
                            action: () => navigate("/hospitals"),
                        },
                        {
                            icon: "📋",
                            title: "Medical History",
                            desc: "View all your past predictions and download PDF reports.",
                            color: "bg-purple-600",
                            action: () => navigate("/history"),
                        },
                    ].map((card, i) => (
                        <div
                            key={i}
                            onClick={card.action}
                            className="bg-white rounded-xl shadow-sm hover:shadow-md transition cursor-pointer p-6 border border-gray-100"
                        >
                            <div className="text-4xl mb-4">{card.icon}</div>
                            <h3 className="text-lg font-semibold text-gray-800 mb-2">
                                {card.title}
                            </h3>
                            <p className="text-gray-500 text-sm mb-4">{card.desc}</p>
                            <button
                                className={`${card.color} text-white text-sm px-4 py-2 rounded-lg hover:opacity-90 transition`}
                            >
                                Go →
                            </button>
                        </div>
                    ))}
                </div>

                {/* SDG Badge */}
                <div className="mt-12 bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-4">
                    <span className="text-3xl">🌍</span>
                    <div>
                        <p className="font-semibold text-green-800">
                            Supporting SDG 3: Good Health and Well-Being
                        </p>
                        <p className="text-green-600 text-sm">
                            This platform is built to improve healthcare access for everyone.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}