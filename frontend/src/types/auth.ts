export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  user: User;
  profile: Profile | null;
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
}

export interface Profile {
  id: string;
  user_id: string;
  full_name: string | null;
  budget_min: number | null;
  budget_max: number | null;
  preferred_categories: string[];
  preferred_brands: string[];
  feature_priorities: Record<string, number>;
  shopping_preferences: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface AuthState {
  user: User | null;
  profile: Profile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface TokenPayload {
  sub: string;
  email: string;
  type: string;
  iat: number;
  exp: number;
}
