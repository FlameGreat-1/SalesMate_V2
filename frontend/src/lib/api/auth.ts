import apiClient from './client';
import { API_ENDPOINTS } from './config';
import type { 
  LoginRequest, 
  SignupRequest, 
  AuthResponse 
} from '@/types';

export const authAPI = {
  async signup(data: SignupRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH.SIGNUP,
      data
    );
    return response.data;
  },

  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      data
    );
    return response.data;
  },

  async getMe(): Promise<AuthResponse> {
    const response = await apiClient.get<AuthResponse>(
      API_ENDPOINTS.AUTH.ME
    );
    return response.data;
  },
};
