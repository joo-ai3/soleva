import { apiService } from './api';

export interface FlashSaleProduct {
  id: string;
  product: string;
  product_name: string;
  product_name_ar: string;
  product_image: string;
  discount_type: 'percentage' | 'fixed_amount';
  discount_value: number;
  original_price: number;
  discounted_price: number;
  discount_amount: number;
  quantity_limit?: number;
  sold_quantity: number;
  remaining_quantity?: number;
  is_featured: boolean;
  display_order: number;
  is_available: boolean;
}

export interface FlashSale {
  id: string;
  name_en: string;
  name_ar: string;
  description_en: string;
  description_ar: string;
  start_time: string;
  end_time: string;
  banner_image?: string;
  banner_color: string;
  text_color: string;
  display_priority: number;
  is_active: boolean;
  show_countdown: boolean;
  max_uses_per_customer?: number;
  total_usage_limit?: number;
  current_usage_count: number;
  is_running: boolean;
  is_upcoming: boolean;
  is_expired: boolean;
  time_remaining: number;
  products?: FlashSaleProduct[];
  products_count?: number;
}

export interface SpecialOffer {
  id: string;
  name_en: string;
  name_ar: string;
  description_en: string;
  description_ar: string;
  offer_type: 'buy_x_get_y_free' | 'buy_x_get_discount' | 'buy_x_free_shipping' | 'bundle_discount';
  buy_quantity: number;
  free_quantity: number;
  discount_type: 'percentage' | 'fixed_amount';
  discount_value: number;
  applicable_products: string[];
  applicable_categories: string[];
  start_time: string;
  end_time?: string;
  max_uses_per_customer?: number;
  total_usage_limit?: number;
  current_usage_count: number;
  minimum_order_amount?: number;
  button_text_en: string;
  button_text_ar: string;
  button_color: string;
  highlight_color: string;
  is_active: boolean;
  show_on_product_page: boolean;
  show_timer: boolean;
  is_running: boolean;
  is_upcoming: boolean;
  is_expired: boolean;
  time_remaining?: number;
}

export interface CartItem {
  product_id: string;
  quantity: number;
  price: number;
}

export interface OfferCalculationRequest {
  cart_items: CartItem[];
  user_id?: string;
}

export interface OfferCalculationResponse {
  flash_sales: Array<{
    id: string;
    name_en: string;
    name_ar: string;
    total_discount: number;
    applicable_items: Array<{
      product_id: string;
      quantity: number;
      discount_per_item: number;
      total_discount: number;
    }>;
    time_remaining: number;
  }>;
  special_offers: Array<{
    id: string;
    name_en: string;
    name_ar: string;
    offer_type: string;
    discount_amount: number;
    free_items: Array<{
      product_id: string;
      quantity: number;
      price: number;
    }>;
    free_shipping: boolean;
    description: string;
    time_remaining?: number;
    button_text_en: string;
    button_text_ar: string;
    button_color: string;
    highlight_color: string;
  }>;
  best_offer?: any;
  total_discount: number;
  free_shipping_available: boolean;
  coupons_blocked: boolean;
}

export interface ProductOfferCheck {
  product_id: string;
  quantity?: number;
  user_id?: string;
}

export interface ProductOfferResponse {
  flash_sale?: FlashSaleProduct;
  special_offers: SpecialOffer[];
  best_discount?: number;
  has_active_offers: boolean;
}

export interface OfferUsageRecord {
  flash_sale_id?: string;
  special_offer_id?: string;
  user_id?: string;
  order_id?: string;
  discount_amount: number;
  free_shipping_applied: boolean;
  free_items: any[];
  order_total: number;
  flash_sale_items?: Array<{
    product_id: string;
    quantity: number;
  }>;
}

class OffersAPI {
  // Flash Sales
  async getFlashSales(): Promise<FlashSale[]> {
    const response = await apiService.get('/offers/flash-sales/');
    return response.data.results || response.data;
  }

  async getFlashSale(id: string): Promise<FlashSale> {
    const response = await apiService.get(`/offers/flash-sales/${id}/`);
    return response.data;
  }

  async getActiveFlashSales(): Promise<FlashSale[]> {
    const response = await apiService.get('/offers/flash-sales/active/');
    return response.data;
  }

  async getUpcomingFlashSales(): Promise<FlashSale[]> {
    const response = await apiService.get('/offers/flash-sales/upcoming/');
    return response.data;
  }

  // Special Offers
  async getSpecialOffers(): Promise<SpecialOffer[]> {
    const response = await apiService.get('/offers/special-offers/');
    return response.data.results || response.data;
  }

  async getSpecialOffer(id: string): Promise<SpecialOffer> {
    const response = await apiService.get(`/offers/special-offers/${id}/`);
    return response.data;
  }

  async getProductOffers(productId: string): Promise<SpecialOffer[]> {
    const response = await apiService.get(`/offers/special-offers/for_product/?product_id=${productId}`);
    return response.data;
  }

  // Offer Calculations
  async calculateOffers(data: OfferCalculationRequest): Promise<OfferCalculationResponse> {
    const response = await apiService.post('/offers/calculate/', data);
    return response.data;
  }

  async checkProductOffers(data: ProductOfferCheck): Promise<ProductOfferResponse> {
    const response = await apiService.post('/offers/check-product/', data);
    return response.data;
  }

  // Offer Usage
  async recordOfferUsage(data: OfferUsageRecord): Promise<void> {
    await apiService.post('/offers/record-usage/', data);
  }

  // Admin Functions (require admin permissions)
  async activateFlashSale(id: string, isActive: boolean): Promise<void> {
    await apiService.post(`/offers/flash-sales/${id}/activate/`, { is_active: isActive });
  }

  async activateSpecialOffer(id: string, isActive: boolean): Promise<void> {
    await apiService.post(`/offers/special-offers/${id}/activate/`, { is_active: isActive });
  }

  async getOfferAnalytics(): Promise<any> {
    const response = await apiService.get('/offers/analytics/');
    return response.data;
  }
}

export const offersAPI = new OffersAPI();
