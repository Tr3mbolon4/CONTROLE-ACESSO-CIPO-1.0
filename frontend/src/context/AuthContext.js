import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

function formatApiErrorDetail(detail) {
  if (detail == null) return "Algo deu errado. Tente novamente.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail.map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e))).filter(Boolean).join(" ");
  if (detail && typeof detail.msg === "string") return detail.msg;
  return String(detail);
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // null = checking, false = not authenticated
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    try {
      const { data } = await axios.get(`${API}/api/auth/me`, { withCredentials: true });
      setUser(data);
    } catch (error) {
      setUser(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (email, password) => {
    try {
      const { data } = await axios.post(
        `${API}/api/auth/login`,
        { email, password },
        { withCredentials: true }
      );
      setUser(data);
      return { success: true };
    } catch (e) {
      return { success: false, error: formatApiErrorDetail(e.response?.data?.detail) || e.message };
    }
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/api/auth/logout`, {}, { withCredentials: true });
    } catch (e) {
      console.error('Logout error:', e);
    }
    setUser(false);
  };

  const refreshToken = async () => {
    try {
      await axios.post(`${API}/api/auth/refresh`, {}, { withCredentials: true });
      return true;
    } catch (e) {
      setUser(false);
      return false;
    }
  };

  const value = {
    user,
    loading,
    login,
    logout,
    refreshToken,
    checkAuth,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    isPortaria: user?.role === 'portaria' || user?.role === 'admin',
    isGestor: user?.role === 'gestor' || user?.role === 'admin',
    isDiretoria: user?.role === 'diretoria' || user?.role === 'admin',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
