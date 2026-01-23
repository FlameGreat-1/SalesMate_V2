const STORAGE_KEYS = {
  TOKEN: 'salesmate_token',
  USER: 'salesmate_user',
  PROFILE: 'salesmate_profile',
  ONBOARDING_COMPLETE: 'salesmate_onboarding_complete',
} as const;

export const storage = {
  setToken(token: string): void {
    try {
      localStorage.setItem(STORAGE_KEYS.TOKEN, token);
    } catch (error) {
      console.error('Failed to save token:', error);
    }
  },

  getToken(): string | null {
    try {
      return localStorage.getItem(STORAGE_KEYS.TOKEN);
    } catch (error) {
      console.error('Failed to get token:', error);
      return null;
    }
  },

  removeToken(): void {
    try {
      localStorage.removeItem(STORAGE_KEYS.TOKEN);
    } catch (error) {
      console.error('Failed to remove token:', error);
    }
  },

  setUser(user: any): void {
    try {
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
    } catch (error) {
      console.error('Failed to save user:', error);
    }
  },

  getUser<T>(): T | null {
    try {
      const user = localStorage.getItem(STORAGE_KEYS.USER);
      return user ? JSON.parse(user) : null;
    } catch (error) {
      console.error('Failed to get user:', error);
      return null;
    }
  },

  removeUser(): void {
    try {
      localStorage.removeItem(STORAGE_KEYS.USER);
    } catch (error) {
      console.error('Failed to remove user:', error);
    }
  },

  setProfile(profile: any): void {
    try {
      localStorage.setItem(STORAGE_KEYS.PROFILE, JSON.stringify(profile));
    } catch (error) {
      console.error('Failed to save profile:', error);
    }
  },

  getProfile<T>(): T | null {
    try {
      const profile = localStorage.getItem(STORAGE_KEYS.PROFILE);
      return profile ? JSON.parse(profile) : null;
    } catch (error) {
      console.error('Failed to get profile:', error);
      return null;
    }
  },

  removeProfile(): void {
    try {
      localStorage.removeItem(STORAGE_KEYS.PROFILE);
    } catch (error) {
      console.error('Failed to remove profile:', error);
    }
  },

  setOnboardingComplete(complete: boolean): void {
    try {
      localStorage.setItem(STORAGE_KEYS.ONBOARDING_COMPLETE, String(complete));
    } catch (error) {
      console.error('Failed to save onboarding status:', error);
    }
  },

  isOnboardingComplete(): boolean {
    try {
      return localStorage.getItem(STORAGE_KEYS.ONBOARDING_COMPLETE) === 'true';
    } catch (error) {
      console.error('Failed to get onboarding status:', error);
      return false;
    }
  },

  clearAll(): void {
    try {
      Object.values(STORAGE_KEYS).forEach((key) => {
        localStorage.removeItem(key);
      });
    } catch (error) {
      console.error('Failed to clear storage:', error);
    }
  },
};
