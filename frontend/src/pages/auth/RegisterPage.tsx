/**
 * RegisterPage.tsx
 * New user registration form.
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../../lib/api";

export default function RegisterPage() {
    const navigate = useNavigate();
    const [form, setForm] = useState({
        full_name: "",
        email: "",
        password: "",
        phone: "",
        age: "",
        gender: "",
    });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        try {
            const res = await registerUser({
                full_name: form.full_name,
                email: form.email,
                password: form.password,
                phone: form.phone || undefined,
                age: form.age ? parseInt(form.age) : undefined,
                gender: form.gender || undefined,
            });
            localStorage.setItem("token", res.data.access_token);
            localStorage.setItem("user", JSON.stringify(res.data));
            navigate("/dashboard");
        } catch (err: any) {
            setError(
                err.response?.data?.detail || "Registration failed. Try again."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
            <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
                {/* Header */}
                <div className="text-center mb-6">
                    <span className="text-4xl">🏥</span>
                    <h1 className="text-2xl font-bold text-gray-800 mt-2">
                        Create Account
                    </h1>
                    <p className="text-gray-500 text-sm mt-1">
                        Join HealthAI to get started
                    </p>
                </div>

                {/* Error */}
                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-3 text-sm mb-4">
                        {error}
                    </div>
                )}

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Full Name *
                        </label>
                        <input
                            name="full_name"
                            type="text"
                            required
                            value={form.full_name}
                            onChange={handleChange}
                            placeholder="John Doe"
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Email *
                        </label>
                        <input
                            name="email"
                            type="email"
                            required
                            value={form.email}
                            onChange={handleChange}
                            placeholder="john@example.com"
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Password *
                        </label>
                        <input
                            name="password"
                            type="password"
                            required
                            value={form.password}
                            onChange={handleChange}
                            placeholder="Minimum 6 characters"
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Phone
                            </label>
                            <input
                                name="phone"
                                type="tel"
                                value={form.phone}
                                onChange={handleChange}
                                placeholder="+91 9999999999"
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Age
                            </label>
                            <input
                                name="age"
                                type="number"
                                value={form.age}
                                onChange={handleChange}
                                placeholder="25"
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Gender
                        </label>
                        <select
                            name="gender"
                            value={form.gender}
                            onChange={handleChange}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                        >
                            <option value="">Select gender</option>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                            <option value="other">Other</option>
                        </select>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-indigo-600 text-white py-2 rounded-lg font-medium hover:bg-indigo-700 transition disabled:opacity-50"
                    >
                        {loading ? "Creating account..." : "Create Account"}
                    </button>
                </form>

                {/* Login link */}
                <p className="text-center text-sm text-gray-500 mt-4">
                    Already have an account?{" "}
                    <button
                        onClick={() => navigate("/login")}
                        className="text-indigo-600 font-medium hover:underline"
                    >
                        Login here
                    </button>
                </p>
            </div>
        </div>
    );
}