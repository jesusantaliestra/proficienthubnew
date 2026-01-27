import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import * as SecureStore from 'expo-secure-store';
import { api } from '../services/api';

interface User {
  id: string;
  email: string;
  name: string;
  userType: 'student' | 'institution' | 'admin';
  institutionId?: string;
  institutionName?: string;
  credits?: number;
  examType?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  const loadStoredAuth = async () => {
    try {
      const storedToken = await SecureStore.getItemAsync('authToken');
      if (storedToken) {
        setToken(storedToken);
        api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
        await refreshUser();
      }
    } catch (error) {
      console.error('Failed to load auth:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, user: userData } = response.data;
    
    await SecureStore.setItemAsync('authToken', access_token);
    setToken(access_token);
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    
    setUser({
      id: userData.id,
      email: userData.email,
      name: userData.name,
      userType: userData.user_type,
      institutionId: userData.institution_id,
      institutionName: userData.institution_name,
      credits: userData.credits,
      examType: userData.current_exam,
    });
  };

  const logout = async () => {
    await SecureStore.deleteItemAsync('authToken');
    delete api.defaults.headers.common['Authorization'];
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const response = await api.get('/auth/me');
      const userData = response.data;
      setUser({
        id: userData.id,
        email: userData.email,
        name: userData.name,
        userType: userData.user_type,
        institutionId: userData.institution_id,
        institutionName: userData.institution_name,
        credits: userData.credits,
        examType: userData.current_exam,
      });
    } catch (error) {
      await logout();
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};