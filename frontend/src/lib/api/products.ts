import apiClient from './client';
import { API_ENDPOINTS } from './config';
import type {
  Product,
  ProductSearchRequest,
  ProductSearchResponse,
  RecommendationResponse,
} from '@/types';

export const productsAPI = {
  async search(params: ProductSearchRequest): Promise<ProductSearchResponse> {
    const response = await apiClient.get<ProductSearchResponse>(
      API_ENDPOINTS.PRODUCTS.SEARCH,
      { params }
    );
    return response.data;
  },

  async getById(id: string): Promise<Product> {
    const response = await apiClient.get<Product>(
      API_ENDPOINTS.PRODUCTS.DETAIL(id)
    );
    return response.data;
  },

  async getRecommendations(): Promise<RecommendationResponse> {
    const response = await apiClient.get<RecommendationResponse>(
      API_ENDPOINTS.PRODUCTS.RECOMMENDATIONS
    );
    return response.data;
  },

  async getCategories(): Promise<string[]> {
    const response = await apiClient.get<string[]>(
      API_ENDPOINTS.PRODUCTS.CATEGORIES
    );
    return response.data;
  },

  async getBrands(): Promise<string[]> {
    const response = await apiClient.get<string[]>(
      API_ENDPOINTS.PRODUCTS.BRANDS
    );
    return response.data;
  },
};
