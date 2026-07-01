/**
 * api.ts
 * Central API client — all backend calls go through here.
 * Automatically attaches JWT token to every request.
 */
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Automatically attach JWT token to every request if it exists
api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Auth
export const registerUser = (data: {
    full_name: string;
    email: string;
    password: string;
    phone?: string;
    age?: number;
    gender?: string;
}) => api.post("/api/v1/auth/register", data);

export const loginUser = (data: {
    email: string;
    password: string;
}) => api.post("/api/v1/auth/login", data);

// Predictions
export const predictDisease = (data: {
    symptoms: string[];
    input_method?: string;
}) => api.post("/api/v1/predictions/predict", data);

export const getSymptoms = () =>
    api.get("/api/v1/predictions/symptoms");

// Hospitals
export const getNearbyHospitals = (
    lat: number,
    lon: number,
    radius?: number
) => api.get("/api/v1/hospitals/nearby", {
    params: { lat, lon, radius: radius || 5000 }
});

export default api;