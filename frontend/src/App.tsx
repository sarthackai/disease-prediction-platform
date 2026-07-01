/**
 * App.tsx
 * Main router — connects all pages together.
 */
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import RegisterPage from "./pages/auth/RegisterPage";
import LoginPage from "./pages/auth/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import SymptomInputPage from "./pages/SymptomInputPage";
import PredictionResultPage from "./pages/PredictionResultPage";
import HospitalFinderPage from "./pages/HospitalFinderPage";
import MedicalHistoryPage from "./pages/MedicalHistoryPage";

// Protects pages that require login
function PrivateRoute({ children }: { children: React.ReactElement }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />

        {/* Protected routes — require login */}
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <DashboardPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/symptoms"
          element={
            <PrivateRoute>
              <SymptomInputPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/result"
          element={
            <PrivateRoute>
              <PredictionResultPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/hospitals"
          element={
            <PrivateRoute>
              <HospitalFinderPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/history"
          element={
            <PrivateRoute>
              <MedicalHistoryPage />
            </PrivateRoute>
          }
        />

        {/* Catch all — redirect unknown URLs to home */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}