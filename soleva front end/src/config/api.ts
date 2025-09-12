// API Configuration for Backend Integration
export const API_CONFIG = {
  // Base URL - can be overridden by environment variable
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'https://solevaeg.com/api',
  
  // API Version
  VERSION: 'v1',
  
  // Timeout settings
  TIMEOUT: 30000,
  
  // Headers
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  
  // Authentication
  AUTH_TOKEN_KEY: 'auth_token',
  REFRESH_TOKEN_KEY: 'refresh_token',
};

// API Endpoints - Updated to match Django backend URLs
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/auth/login/',
    REGISTER: '/auth/register/',
    LOGOUT: '/auth/logout/',
    REFRESH: '/auth/token/refresh/',
    TOKEN: '/auth/token/',
    PROFILE: '/auth/profile/',
    PASSWORD_RESET: '/auth/password/reset/',
    PASSWORD_RESET_CONFIRM: '/auth/password/reset/confirm/',
    PASSWORD_CHANGE: '/auth/password/change/',
    EMAIL_VERIFY: '/auth/verify/email/',
    EMAIL_RESEND: '/auth/verify/resend/',
    SOCIAL_AUTH: '/auth/social/',
    HEALTH: '/auth/health/',
  },
  
  // Products
  PRODUCTS: {
    LIST: '/products/products/',
    DETAIL: (slug: string) => `/products/products/${slug}/`,
    CATEGORIES: '/products/categories/',
    CATEGORY_TREE: '/products/categories/tree/',
    CATEGORY_DETAIL: (slug: string) => `/products/categories/${slug}/`,
    BRANDS: '/products/brands/',
    BRAND_DETAIL: (slug: string) => `/products/brands/${slug}/`,
    FEATURED: '/products/products/featured/',
    ON_SALE: '/products/products/on_sale/',
    NEW_ARRIVALS: '/products/products/new_arrivals/',
    RELATED: (slug: string) => `/products/products/${slug}/related/`,
    SEARCH: '/products/products/search/',
    STATS: '/products/stats/',
    SUGGESTIONS: '/products/search/suggestions/',
    ATTRIBUTES: '/products/attributes/',
  },
  
  // Cart
  CART: {
    LIST: '/cart/',
    ITEMS: '/cart/items/',
    ADD: '/cart/add/',
    SUMMARY: '/cart/summary/',
    APPLY_COUPON: '/cart/coupon/apply/',
    SAVED_LATER: '/cart/saved/',
  },
  
  // Orders
  ORDERS: {
    LIST: '/orders/orders/',
    DETAIL: (id: string) => `/orders/orders/${id}/`,
    CREATE: '/orders/orders/',
    STATS: '/orders/stats/',
    TRACK: '/orders/track/',
    UPLOAD_PAYMENT_PROOF: (id: string) => `/orders/orders/${id}/upload-payment-proof/`,
  },
  
  // Payment Proofs
  PAYMENT_PROOFS: {
    LIST: '/orders/payment-proofs/',
    DETAIL: (id: string) => `/orders/payment-proofs/${id}/`,
    VERIFY: (id: string) => `/orders/payment-proofs/${id}/verify_payment/`,
  },
  
  // User Management
  USER: {
    PROFILE: '/user/profile/',
    DASHBOARD: '/user/dashboard/',
    STATS: '/user/stats/',
    PREFERENCES: '/user/preferences/',
    ACTIVITY: '/user/activity/',
    ADDRESSES: '/user/addresses/',
    ADDRESS_DETAIL: (id: string) => `/user/addresses/${id}/`,
    DELETE_ACCOUNT: '/user/delete/',
    EXPORT_DATA: '/user/export/',
  },
  
  // Shipping
  SHIPPING: {
    METHODS: '/shipping/methods/',
    RATES: '/shipping/rates/',
    LOCATIONS: '/shipping/locations/',
    GOVERNORATES: '/shipping/governorates/',
    CITIES: (governorate: string) => `/shipping/cities/${governorate}/`,
  },
  
  // Payments
  PAYMENTS: {
    METHODS: '/payments/methods/',
    CREATE_INTENT: '/payments/create-intent/',
    CAPTURE: (intentId: string) => `/payments/capture/${intentId}/`,
    STATUS: (intentId: string) => `/payments/status/${intentId}/`,
    REFUND: '/payments/refund/',
    REFUNDS: '/payments/refunds/',
    TRANSACTIONS: '/payments/transactions/',
    TRANSACTION_DETAIL: (id: string) => `/payments/transactions/${id}/`,
    STATS: '/payments/stats/',
  },
  
  // Coupons
  COUPONS: {
    LIST: '/coupons/',
    VALIDATE: '/coupons/validate/',
    APPLY: '/coupons/apply/',
  },
  
  // Tracking
  TRACKING: {
    EVENTS: '/tracking/events/',
    PAGE_VIEW: '/tracking/page-view/',
    PRODUCT_VIEW: '/tracking/product-view/',
    ADD_TO_CART: '/tracking/add-to-cart/',
    PURCHASE: '/tracking/purchase/',
    CONVERSION: '/tracking/conversion/',
  },
  
  // Admin Panel
  ADMIN: {
    DASHBOARD: '/admin/dashboard/',
    USERS: '/admin/users/',
    ORDERS: '/admin/orders/',
    PRODUCTS: '/admin/products/',
    ANALYTICS: '/admin/analytics/',
    REPORTS: '/admin/reports/',
  },
  
  // Website Management
  WEBSITE: {
    // Public endpoints
    SECTIONS: '/website/sections/',
    CONFIG: '/website/config/',
    BANNERS: '/website/banners/',
    
    // User endpoints
    USER_MESSAGES: '/website/user/messages/',
    USER_MESSAGE_DETAIL: (id: string) => `/website/user/messages/${id}/`,
    MARK_MESSAGE_READ: (id: string) => `/website/user/messages/${id}/mark-read/`,
    UNREAD_COUNT: '/website/user/messages/unread-count/',
    
    // Admin endpoints
    ADMIN_SECTIONS: '/website/admin/sections/',
    ADMIN_SECTION_DETAIL: (id: string) => `/website/admin/sections/${id}/`,
    ADMIN_CONFIG: '/website/admin/config/',
    ADMIN_BANNERS: '/website/admin/banners/',
    ADMIN_BANNER_DETAIL: (id: string) => `/website/admin/banners/${id}/`,
    ADMIN_MESSAGES: '/website/admin/messages/',
    ADMIN_MESSAGE_CREATE: '/website/admin/messages/create/',
    ADMIN_MESSAGE_DETAIL: (id: string) => `/website/admin/messages/${id}/`,
    BULK_SEND: '/website/admin/messages/bulk-send/',
  },
};

// Helper function to build full URL
export const buildApiUrl = (endpoint: string): string => {
  const baseUrl = API_CONFIG.BASE_URL.endsWith('/') 
    ? API_CONFIG.BASE_URL.slice(0, -1) 
    : API_CONFIG.BASE_URL;
  
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  return `${baseUrl}${cleanEndpoint}`;
};

// Helper function to get auth headers
export const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem(API_CONFIG.AUTH_TOKEN_KEY);
  
  return token 
    ? { ...API_CONFIG.DEFAULT_HEADERS, Authorization: `Bearer ${token}` }
    : API_CONFIG.DEFAULT_HEADERS;
};