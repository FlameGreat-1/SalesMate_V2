'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '@/lib/api/auth';
import { storage } from '@/lib/utils/storage';
import type { User, Profile, AuthState } from '@/types';

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  updateProfile: (profile: Profile) => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    profile: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  useEffect(() => {
    const initAuth = async () => {
      const token = storage.getToken();
      const user = storage.getUser<User>();
      const profile = storage.getProfile<Profile>();

      if (token && user) {
        setState({
          user,
          profile,
          token,
          isAuthenticated: true,
          isLoading: false,
        });

        try {
          await refreshUser();
        } catch (error) {
          logout();
        }
      } else {
        setState((prev) => ({ ...prev, isLoading: false }));
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setState((prev) => ({ ...prev, isLoading: true }));

    try {
      const response = await authAPI.login({ email, password });

      storage.setToken(response.access_token);
      storage.setUser(response.user);
      if (response.profile) {
        storage.setProfile(response.profile);
      }

      setState({
        user: response.user,
        profile: response.profile,
        token: response.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      setState((prev) => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const signup = async (email: string, password: string, fullName?: string) => {
    setState((prev) => ({ ...prev, isLoading: true }));

    try {
      const response = await authAPI.signup({ email, password, full_name: fullName });

      storage.setToken(response.access_token);
      storage.setUser(response.user);
      if (response.profile) {
        storage.setProfile(response.profile);
      }

      setState({
        user: response.user,
        profile: response.profile,
        token: response.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      setState((prev) => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const logout = () => {
    storage.clearAll();
    setState({
      user: null,
      profile: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  };

  const updateProfile = (profile: Profile) => {
    storage.setProfile(profile);
    setState((prev) => ({ ...prev, profile }));
  };

  const refreshUser = async () => {
    try {
      const response = await authAPI.getMe();
      
      storage.setUser(response.user);
      if (response.profile) {
        storage.setProfile(response.profile);
      }

      setState((prev) => ({
        ...prev,
        user: response.user,
        profile: response.profile,
      }));
    } catch (error) {
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        signup,
        logout,
        updateProfile,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
