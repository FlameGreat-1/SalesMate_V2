export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: Number(process.env.NEXT_PUBLIC_API_TIMEOUT) || 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
} as const;

export const API_ENDPOINTS = {
  AUTH: {
    SIGNUP: '/auth/signup',
    LOGIN: '/auth/login',
    ME: '/auth/me',
  },
  USERS: {
    ME: '/users/me',
    PROFILE: '/users/profile',
    BUDGET: '/users/budget',
    PREFERENCES: '/users/preferences',
  },
  PRODUCTS: {
    SEARCH: '/products/search',
    DETAIL: (id: string) => `/products/${id}`,
    RECOMMENDATIONS: '/products/recommendations/personalized',
    CATEGORIES: '/products/meta/categories',
    BRANDS: '/products/meta/brands',
  },
  CHAT: {
    START: '/chat/start',
    MESSAGE: '/chat/message',
    STREAM: '/chat/message/stream',
  },
  HISTORY: {
    CONVERSATIONS: '/history/conversations',
    ACTIVE: '/history/active',
    DETAIL: (id: string) => `/history/conversations/${id}`,
  },
} as const;
