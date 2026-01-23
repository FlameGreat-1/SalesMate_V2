export interface Product {
  id: string;
  sku: string;
  name: string;
  description: string;
  short_description: string;
  category: string;
  subcategory: string;
  brand: string;
  manufacturer: string;
  price: number;
  original_price: number;
  discount_percentage: number;
  currency: string;
  stock_status: string;
  stock_quantity: number;
  reorder_level: number;
  specifications: Record<string, any>;
  features: string[];
  included_accessories: string[];
  target_audience: string[];
  use_cases: string[];
  price_tier: string;
  tags: string[];
  rating: number;
  review_count: number;
  warranty_months: number;
  return_policy_days: number;
  release_date: string;
  is_active: boolean;
  is_featured: boolean;
  is_new_arrival: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductSearchResponse {
  products: Product[];
  total: number;
  query: string;
  filters: SearchFilters;
}

export interface SearchFilters {
  category: string | null;
  brand: string | null;
  min_price: number | null;
  max_price: number | null;
  limit: number;
}

export interface ProductSearchRequest {
  query: string;
  category?: string;
  brand?: string;
  min_price?: number;
  max_price?: number;
  limit?: number;
}

export interface RecommendationResponse {
  products: Product[];
  reason: string;
  based_on: Record<string, any>;
}

export interface CategoryMetadata {
  categories: string[];
}

export interface BrandMetadata {
  brands: string[];
}
