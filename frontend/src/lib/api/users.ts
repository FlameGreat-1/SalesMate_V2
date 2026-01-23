import apiClient from './client';
import { API_ENDPOINTS } from './config';
import type {
  UserProfileResponse,
  UpdateProfileRequest,
  UpdateBudgetRequest,
  UpdatePreferencesRequest,
  Profile,
} from '@/types';

export const usersAPI = {
  async getMe(): Promise<UserProfileResponse> {
    const response = await apiClient.get<UserProfileResponse>(
      API_ENDPOINTS.USERS.ME
    );
    return response.data;
  },

  async getProfile(): Promise<UserProfileResponse> {
    const response = await apiClient.get<UserProfileResponse>(
      API_ENDPOINTS.USERS.PROFILE
    );
    return response.data;
  },

  async updateProfile(data: UpdateProfileRequest): Promise<Profile> {
    const response = await apiClient.put<Profile>(
      API_ENDPOINTS.USERS.PROFILE,
      data
    );
    return response.data;
  },

  async updateBudget(data: UpdateBudgetRequest): Promise<Profile> {
    const response = await apiClient.patch<Profile>(
      API_ENDPOINTS.USERS.BUDGET,
      data
    );
    return response.data;
  },

  async updatePreferences(data: UpdatePreferencesRequest): Promise<Profile> {
    const response = await apiClient.patch<Profile>(
      API_ENDPOINTS.USERS.PREFERENCES,
      data
    );
    return response.data;
  },
};
