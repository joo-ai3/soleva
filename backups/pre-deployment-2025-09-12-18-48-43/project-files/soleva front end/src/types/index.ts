// Product Types - Updated to match backend structure
export interface Product {
  id: number;
  name_en: string;
  name_ar: string;
  slug: string;
  sku: string;
  short_description_en: string;
  short_description_ar: string;
  description_en: string;
  description_ar: string;
  price: number;
  compare_price?: number;
  cost_price?: number;
  track_inventory: boolean;
  inventory_quantity: number;
  low_stock_threshold: number;
  weight?: number;
  length?: number;
  width?: number;
  height?: number;
  is_active: boolean;
  is_featured: boolean;
  is_digital: boolean;
  requires_shipping: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
  published_at?: string;
  
  // Relationships
  category: Category;
  brand?: Brand;
  images: ProductImage[];
  variants: ProductVariant[];
  
  // Computed properties
  is_on_sale: boolean;
  discount_percentage: number;
  is_in_stock: boolean;
  is_low_stock: boolean;
}

export interface Category {
  id: number;
  name_en: string;
  name_ar: string;
  slug: string;
  description_en?: string;
  description_ar?: string;
  parent?: number;
  image?: string;
  icon?: string;
  display_order: number;
  is_active: boolean;
  is_featured: boolean;
  level: number;
  children?: Category[];
}

export interface Brand {
  id: number;
  name: string;
  slug: string;
  description?: string;
  logo?: string;
  website?: string;
  is_active: boolean;
  is_featured: boolean;
}

export interface ProductImage {
  id: number;
  image: string;
  alt_text_en?: string;
  alt_text_ar?: string;
  display_order: number;
  is_primary: boolean;
}

export interface ProductAttribute {
  id: number;
  name_en: string;
  name_ar: string;
  slug: string;
  attribute_type: 'text' | 'number' | 'color' | 'select' | 'multiselect';
  is_required: boolean;
  is_filterable: boolean;
  display_order: number;
  values: ProductAttributeValue[];
}

export interface ProductAttributeValue {
  id: number;
  value_en: string;
  value_ar: string;
  color_code?: string;
  display_order: number;
}

export interface ProductVariant {
  id: number;
  sku: string;
  price?: number;
  compare_price?: number;
  cost_price?: number;
  inventory_quantity: number;
  weight?: number;
  image?: string;
  is_active: boolean;
  effective_price: number;
  effective_compare_price?: number;
  is_in_stock: boolean;
  attribute_values: ProductVariantAttribute[];
}

export interface ProductVariantAttribute {
  id: number;
  attribute: ProductAttribute;
  value: ProductAttributeValue;
}

// Cart Item Types - Updated to match backend structure
export interface CartItem {
  id: number;
  product_id: number;
  product_name: string;
  product_slug: string;
  product_image?: string;
  variant_id?: number;
  variant_attributes?: Record<string, any>;
  unit_price: number;
  quantity: number;
  total_price: number;
  created_at?: string;
  updated_at?: string;
  
  // Additional fields from serializer
  product_details?: {
    id: number;
    name_en: string;
    name_ar: string;
    slug: string;
    price: number;
    compare_price?: number;
    is_in_stock: boolean;
    inventory_quantity?: number;
  };
  variant_details?: {
    id: number;
    sku: string;
    price: number;
    is_in_stock: boolean;
    inventory_quantity: number;
  };
  is_available: boolean;
}

export interface CartSummary {
  subtotal: number;
  shipping_cost: number;
  tax_amount: number;
  discount_amount: number;
  total: number;
  items_count: number;
  total_weight?: number;
  coupon_code?: string;
  coupon_discount?: number;
  shipping_method?: string;
  estimated_delivery?: string;
}

// User Types - Updated to match backend structure
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other';
  language_preference: 'en' | 'ar';
  email_notifications: boolean;
  sms_notifications: boolean;
  push_notifications: boolean;
  is_verified: boolean;
  date_joined?: string;
  last_login?: string;
}

export interface Address {
  id: number;
  full_name: string;
  phone_number: string;
  governorate: string;
  city: string;
  area?: string;
  street_address: string;
  building_number?: string;
  apartment_number?: string;
  floor_number?: string;
  landmark?: string;
  postal_code?: string;
  address_type: 'home' | 'work' | 'other';
  is_default: boolean;
  is_active: boolean;
  latitude?: number;
  longitude?: number;
  created_at: string;
  updated_at: string;
  full_address: string;
}

// Form Types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  language_preference?: 'en' | 'ar';
}

export interface ContactForm {
  name: string;
  email: string;
  subject: string;
  message: string;
}

// API Response Types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// Collection Types
export interface Collection {
  id: string;
  name: {
    ar: string;
    en: string;
  };
  desc: {
    ar: string;
    en: string;
  };
  image: string;
}

// Language Types
export type Language = 'ar' | 'en';

// Theme Types
export type Theme = 'light' | 'dark';

// Toast Types
export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

// Coupon Types - Updated to match backend structure
export interface Coupon {
  id: number;
  code: string;
  name_en: string;
  name_ar: string;
  description_en?: string;
  description_ar?: string;
  discount_type: 'percentage' | 'fixed_amount';
  discount_value: number;
  max_discount_amount?: number;
  minimum_order_amount?: number;
  usage_limit?: number;
  usage_limit_per_customer?: number;
  free_shipping: boolean;
  valid_from: string;
  valid_until?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  usage_count?: number;
  is_expired?: boolean;
  days_until_expiry?: number;
}

export interface CouponUsage {
  id: number;
  coupon_code: string;
  coupon_name: string;
  user_email?: string;
  user_full_name?: string;
  order_id?: string;
  order_total: number;
  discount_amount: number;
  created_at: string;
}

// Shipping Types
export interface ShippingMethod {
  id: number;
  name: string;
  description?: string;
  cost: number;
  estimated_days: number;
  is_active: boolean;
}

export interface Governorate {
  id: number;
  name_en: string;
  name_ar: string;
  code: string;
  shipping_cost: number;
  is_active: boolean;
}

export interface City {
  id: number;
  name_en: string;
  name_ar: string;
  governorate: number;
  shipping_cost: number;
  is_active: boolean;
}

// Payment Types
export interface PaymentMethod {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  is_active: boolean;
  config?: Record<string, any>;
}

export interface PaymentIntent {
  id: string;
  amount: number;
  currency: string;
  status: string;
  client_secret?: string;
  payment_method?: string;
}

// Tracking Types
export interface TrackingEvent {
  id: number;
  event_type: string;
  event_data: Record<string, any>;
  user_id?: number;
  session_id?: string;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}

// Favorites Types
export interface FavoriteItem {
  id: number;
  product_id: number;
  product_name: string;
  product_slug: string;
  product_image?: string;
  product_price: number;
  created_at: string;
}

// Order Types - Updated to match backend structure
export interface Order {
  id: number;
  order_number: string;
  user_id: number;
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'out_for_delivery' | 'delivered' | 'cancelled' | 'refunded' | 'returned';
  payment_status: 'pending' | 'pending_review' | 'under_review' | 'payment_approved' | 'payment_rejected' | 'paid' | 'partially_paid' | 'failed' | 'refunded' | 'cancelled';
  fulfillment_status: 'unfulfilled' | 'partial' | 'fulfilled';
  
  // Customer information
  customer_email: string;
  customer_phone: string;
  customer_name: string;
  
  // Shipping address
  shipping_address_line1: string;
  shipping_address_line2?: string;
  shipping_city: string;
  shipping_governorate: string;
  shipping_postal_code?: string;
  shipping_phone: string;
  shipping_name: string;
  
  // Order totals
  subtotal: number;
  shipping_cost: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  
  // Payment information
  payment_method: 'cash_on_delivery' | 'bank_wallet' | 'e_wallet' | 'paymob' | 'stripe';
  payment_reference?: string;
  
  // Shipping information
  shipping_method: string;
  tracking_number?: string;
  courier_company?: string;
  estimated_delivery_date?: string;
  
  // Coupon information
  coupon_code?: string;
  coupon_discount: number;
  
  // Notes
  customer_notes?: string;
  admin_notes?: string;
  
  // Language
  language: 'en' | 'ar';
  
  // Timestamps
  created_at: string;
  updated_at: string;
  confirmed_at?: string;
  shipped_at?: string;
  delivered_at?: string;
  cancelled_at?: string;
  
  // Relationships
  items: OrderItem[];
  payments?: OrderPayment[];
  shipments?: OrderShipment[];
  refunds?: OrderRefund[];
  status_history?: OrderStatusHistory[];
  payment_proofs?: PaymentProof[];
  
  // Computed properties
  full_shipping_address: string;
  is_paid: boolean;
  can_be_cancelled: boolean;
}

export interface OrderItem {
  id: number;
  product_id: number;
  product_name: string;
  product_sku: string;
  product_image?: string;
  variant_id?: number;
  variant_sku?: string;
  variant_attributes?: Record<string, any>;
  unit_price: number;
  quantity: number;
  total_price: number;
  quantity_fulfilled: number;
  created_at: string;
  is_fulfilled: boolean;
  pending_quantity: number;
}

export interface OrderPayment {
  id: number;
  payment_method: string;
  amount: number;
  currency: string;
  gateway_transaction_id?: string;
  gateway_reference?: string;
  gateway_response?: Record<string, any>;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled' | 'refunded';
  created_at: string;
  updated_at: string;
  processed_at?: string;
}

export interface OrderShipment {
  id: number;
  tracking_number: string;
  courier_company: string;
  shipping_cost: number;
  status: 'pending' | 'picked_up' | 'in_transit' | 'out_for_delivery' | 'delivered' | 'failed_delivery' | 'returned';
  tracking_url?: string;
  estimated_delivery?: string;
  created_at: string;
  updated_at: string;
  shipped_at?: string;
  delivered_at?: string;
}

export interface OrderRefund {
  id: number;
  amount: number;
  reason: string;
  status: 'pending' | 'approved' | 'processed' | 'completed' | 'rejected';
  processed_by?: number;
  gateway_refund_id?: string;
  created_at: string;
  updated_at: string;
  processed_at?: string;
}

export interface OrderStatusHistory {
  id: number;
  previous_status?: string;
  new_status: string;
  comment?: string;
  changed_by?: number;
  created_at: string;
}

export interface PaymentProof {
  id: number;
  image: string;
  original_filename: string;
  file_size: number;
  file_size_mb: number;
  verification_status: 'pending' | 'verified' | 'rejected' | 'needs_clarification';
  verification_notes?: string;
  verified_at?: string;
  description?: string;
  created_at: string;
  updated_at: string;
  uploaded_by_name?: string;
  verified_by_name?: string;
  is_verified: boolean;
}

// Address Types
export interface ShippingAddress {
  governorate: string;
  governorateName: {
    ar: string;
    en: string;
  };
  city: string;
  cityName: {
    ar: string;
    en: string;
  };
  detailedAddress: string;
  shippingCost: number;
}

export interface AddressSelectorProps {
  onAddressChange: (address: ShippingAddress | null) => void;
  selectedGovernorate?: string;
  selectedCity?: string;
  detailedAddress?: string;
  className?: string;
  errors?: {
    governorate?: string;
    city?: string;
    detailedAddress?: string;
  };
}

// Hook Types
export interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}