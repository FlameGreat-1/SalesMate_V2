export interface UpdateProfileRequest {
  full_name?: string;
}

export interface UpdateBudgetRequest {
  budget_min?: number;
  budget_max?: number;
}

export interface UpdatePreferencesRequest {
  preferred_categories?: string[];
  preferred_brands?: string[];
  feature_priorities?: Record<string, number>;
}

export interface UserProfileResponse {
  user: User;
  profile: Profile;
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

export interface OnboardingData {
  budget_min: number;
  budget_max: number;
  preferred_categories: string[];
  preferred_brands: string[];
}

export interface ProfileUpdatePayload {
  full_name?: string;
  budget_min?: number;
  budget_max?: number;
  preferred_categories?: string[];
  preferred_brands?: string[];
  feature_priorities?: Record<string, number>;
}
