import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { authApi } from '../services/api';
import { API_CONFIG } from '../config/api';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  language_preference: 'en' | 'ar';
  is_verified: boolean;
  email_notifications: boolean;
  sms_notifications: boolean;
  push_notifications: boolean;
  date_joined?: string;
  last_login?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: { email: string; password: string }) => Promise<{ success: boolean; error?: string }>;
  register: (userData: {
    username: string;
    email: string;
    password: string;
    password_confirm: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
    language_preference?: 'en' | 'ar';
  }) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  updateUser: (userData: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated
  const isAuthenticated = !!user && !!localStorage.getItem(API_CONFIG.AUTH_TOKEN_KEY);

  // Load user from localStorage on mount
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem(API_CONFIG.AUTH_TOKEN_KEY);
      const savedUser = localStorage.getItem('user');
      
      if (token && savedUser) {
        try {
          const parsedUser = JSON.parse(savedUser);
          setUser(parsedUser);
          
          // Verify token is still valid by fetching profile
          try {
            const response = await authApi.getProfile();
            if (response.success && response.data) {
              setUser(response.data as User);
              localStorage.setItem('user', JSON.stringify(response.data));
            }
          } catch (error: any) {
            console.warn('Failed to verify token with backend:', error);
            // Don't clear data if backend is unreachable, just log the error
            // This prevents the app from crashing when backend is down
            if (error?.response?.status === 401) {
              // Only clear data if token is actually invalid
              localStorage.removeItem(API_CONFIG.AUTH_TOKEN_KEY);
              localStorage.removeItem(API_CONFIG.REFRESH_TOKEN_KEY);
              localStorage.removeItem('user');
              setUser(null);
            } else if (error?.code === 'NETWORK_ERROR' || error?.message?.includes('Network Error') || !error?.response) {
              // Network error - keep user data and show offline indicator
              console.info('Backend appears to be offline. App will continue in offline mode.');
            }
            // If it's a network error or server error, keep the user data
          }
        } catch (error) {
          console.error('Error loading user:', error);
          // Clear invalid data
          localStorage.removeItem(API_CONFIG.AUTH_TOKEN_KEY);
          localStorage.removeItem(API_CONFIG.REFRESH_TOKEN_KEY);
          localStorage.removeItem('user');
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    loadUser();
  }, []);

  // Auto-refresh token before expiration
  useEffect(() => {
    if (!isAuthenticated) return;

    const refreshInterval = setInterval(async () => {
      await refreshToken();
    }, 50 * 60 * 1000); // Refresh every 50 minutes (tokens expire in 60 minutes)

    return () => clearInterval(refreshInterval);
  }, [isAuthenticated]);

  const login = async (credentials: { email: string; password: string }) => {
    try {
      setIsLoading(true);
      const response = await authApi.login(credentials);
      
      if (response.success && response.data) {
        const loginData = response.data as {
          access: string;
          refresh: string;
          user: User;
        };
        
        // Store tokens
        localStorage.setItem(API_CONFIG.AUTH_TOKEN_KEY, loginData.access);
        localStorage.setItem(API_CONFIG.REFRESH_TOKEN_KEY, loginData.refresh);
        localStorage.setItem('user', JSON.stringify(loginData.user));
        
        setUser(loginData.user);
        return { success: true };
      } else {
        return { success: false, error: response.message || 'Login failed' };
      }
    } catch (error: any) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.message || 'An error occurred during login' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: {
    username: string;
    email: string;
    password: string;
    password_confirm: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
    language_preference?: 'en' | 'ar';
  }) => {
    try {
      setIsLoading(true);
      const response = await authApi.register(userData);
      
      if (response.success) {
        return { success: true };
      } else {
        return { 
          success: false, 
          error: response.message || 'Registration failed' 
        };
      }
    } catch (error: any) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.message || 'An error occurred during registration' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem(API_CONFIG.REFRESH_TOKEN_KEY);
      if (refreshToken) {
        await authApi.logout(refreshToken);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear all auth data
      localStorage.removeItem(API_CONFIG.AUTH_TOKEN_KEY);
      localStorage.removeItem(API_CONFIG.REFRESH_TOKEN_KEY);
      localStorage.removeItem('user');
      setUser(null);
    }
  };

  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const refreshTokenValue = localStorage.getItem(API_CONFIG.REFRESH_TOKEN_KEY);
      if (!refreshTokenValue) return false;

      const response = await authApi.refreshToken(refreshTokenValue);
      
      if (response.success && response.data) {
        const tokenData = response.data as {
          access: string;
          refresh?: string;
        };
        
        localStorage.setItem(API_CONFIG.AUTH_TOKEN_KEY, tokenData.access);
        if (tokenData.refresh) {
          localStorage.setItem(API_CONFIG.REFRESH_TOKEN_KEY, tokenData.refresh);
        }
        return true;
      } else {
        // Refresh failed, logout user
        await logout();
        return false;
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      await logout();
      return false;
    }
  }, []);

  const updateUser = useCallback((userData: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
  }, [user]);

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    refreshToken,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}