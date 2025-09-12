import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// API Error Types
export interface ApiError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
}

export interface ApiResponse<T = any> {
  data: T;
  success: boolean;
  message?: string;
  error?: ApiError;
}

// Network Status
export interface NetworkStatus {
  isOnline: boolean;
  isServerReachable: boolean;
  lastChecked: Date;
}

class ApiService {
  private axiosInstance: AxiosInstance;
  private networkStatus: NetworkStatus = {
    isOnline: navigator.onLine,
    isServerReachable: true,
    lastChecked: new Date()
  };

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000, // 30 seconds timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.setupNetworkMonitoring();
  }

  private setupInterceptors() {
    // Request interceptor
    this.axiosInstance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // Add auth token if available
        const token = localStorage.getItem('accessToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error: any) => {
        return Promise.reject(this.formatError(error));
      }
    );

    // Response interceptor
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => {
        this.updateNetworkStatus(true);
        return response;
      },
      async (error: AxiosError) => {
        this.updateNetworkStatus(false);
        
        // Handle token refresh for 401 errors
        if (error.response?.status === 401) {
          const refreshed = await this.tryRefreshToken();
          if (refreshed && error.config) {
            return this.axiosInstance.request(error.config);
          }
        }
        
        return Promise.reject(this.formatError(error));
      }
    );
  }

  private setupNetworkMonitoring() {
    // Monitor online/offline status
    window.addEventListener('online', () => {
      this.networkStatus.isOnline = true;
      this.checkServerHealth();
    });

    window.addEventListener('offline', () => {
      this.networkStatus.isOnline = false;
      this.networkStatus.isServerReachable = false;
    });

    // Periodic server health check
    setInterval(() => {
      if (this.networkStatus.isOnline) {
        this.checkServerHealth();
      }
    }, 60000); // Check every minute
  }

  private async checkServerHealth(): Promise<boolean> {
    try {
      await this.axiosInstance.get('/health/', { timeout: 5000 });
      this.updateNetworkStatus(true);
      return true;
    } catch (error) {
      console.warn('Backend health check failed:', error);
      this.updateNetworkStatus(false);
      return false;
    }
  }

  private updateNetworkStatus(isServerReachable: boolean) {
    this.networkStatus = {
      isOnline: navigator.onLine,
      isServerReachable,
      lastChecked: new Date()
    };
  }

  private formatError(error: any): ApiError {
    if (!navigator.onLine) {
      return {
        message: 'No internet connection. Please check your network and try again.',
        code: 'NETWORK_ERROR',
        status: 0
      };
    }

    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      return {
        message: 'Request timeout. The server is taking too long to respond.',
        code: 'TIMEOUT_ERROR',
        status: 408
      };
    }

    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data;

      let message = 'An unexpected error occurred. Please try again.';
      
      switch (status) {
        case 400:
          message = data?.message || 'Invalid request. Please check your input.';
          break;
        case 401:
          message = 'Authentication required. Please log in again.';
          break;
        case 403:
          message = 'Access denied. You don\'t have permission for this action.';
          break;
        case 404:
          message = 'The requested resource was not found.';
          break;
        case 429:
          message = 'Too many requests. Please wait a moment and try again.';
          break;
        case 500:
          message = 'Server error. Please try again later.';
          break;
        case 502:
        case 503:
        case 504:
          message = 'Service temporarily unavailable. Please try again later.';
          break;
        default:
          message = data?.message || `Server error (${status}). Please try again.`;
      }

      return {
        message,
        status,
        code: data?.code || `HTTP_${status}`,
        details: data
      };
    } else if (error.request) {
      // Network error - no response received
      return {
        message: 'Unable to connect to server. Please check your internet connection and try again.',
        code: 'NETWORK_ERROR',
        status: 0
      };
    } else {
      // Something else happened
      return {
        message: error.message || 'An unexpected error occurred. Please try again.',
        code: 'UNKNOWN_ERROR'
      };
    }
  }

  private async tryRefreshToken(): Promise<boolean> {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) return false;

      const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
        refresh: refreshToken
      });

      if (response.data.access) {
        localStorage.setItem('accessToken', response.data.access);
        return true;
      }
    } catch {
      // Refresh failed, clear tokens
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    }
    return false;
  }

  // Public API methods with error handling
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<T> = await this.axiosInstance.get(url, config);
      return {
        data: response.data,
        success: true
      };
    } catch (error) {
      return {
        data: null as T,
        success: false,
        error: error as ApiError
      };
    }
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<T> = await this.axiosInstance.post(url, data, config);
      return {
        data: response.data,
        success: true
      };
    } catch (error) {
      return {
        data: null as T,
        success: false,
        error: error as ApiError
      };
    }
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<T> = await this.axiosInstance.put(url, data, config);
      return {
        data: response.data,
        success: true
      };
    } catch (error) {
      return {
        data: null as T,
        success: false,
        error: error as ApiError
      };
    }
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<T> = await this.axiosInstance.delete(url, config);
      return {
        data: response.data,
        success: true
      };
    } catch (error) {
      return {
        data: null as T,
        success: false,
        error: error as ApiError
      };
    }
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<T> = await this.axiosInstance.patch(url, data, config);
      return {
        data: response.data,
        success: true
      };
    } catch (error) {
      return {
        data: null as T,
        success: false,
        error: error as ApiError
      };
    }
  }

  // Utility methods
  getNetworkStatus(): NetworkStatus {
    return { ...this.networkStatus };
  }

  async retryRequest<T = any>(
    requestFn: () => Promise<ApiResponse<T>>,
    maxRetries: number = 3,
    delay: number = 1000
  ): Promise<ApiResponse<T>> {
    let lastError: ApiError | undefined;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      const result = await requestFn();
      
      if (result.success) {
        return result;
      }

      lastError = result.error;

      // Don't retry for certain error types
      if (lastError?.status && [400, 401, 403, 404, 422].includes(lastError.status)) {
        break;
      }

      // Wait before retrying (exponential backoff)
      if (attempt < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, attempt - 1)));
      }
    }

    return {
      data: null as T,
      success: false,
      error: lastError || { message: 'Request failed after multiple attempts' }
    };
  }
}

// Create singleton instance
export const apiService = new ApiService();

// API Endpoints
export const authApi = {
  login: async (credentials: { email: string; password: string }) => {
    return apiService.post('/auth/login/', credentials);
  },
  
  register: async (userData: {
    username: string;
    email: string;
    password: string;
    password_confirm: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
    language_preference?: 'en' | 'ar';
  }) => {
    return apiService.post('/auth/register/', userData);
  },
  
  logout: async (refreshToken: string) => {
    return apiService.post('/auth/logout/', { refresh: refreshToken });
  },
  
  refreshToken: async (refreshToken: string) => {
    return apiService.post('/auth/token/refresh/', { refresh: refreshToken });
  },
  
  getProfile: async () => {
    return apiService.get('/auth/profile/');
  },
  
  updateProfile: async (userData: any) => {
    return apiService.patch('/auth/profile/', userData);
  },
  
  changePassword: async (passwordData: {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }) => {
    return apiService.post('/auth/change-password/', passwordData);
  },
  
  requestPasswordReset: async (email: string) => {
    return apiService.post('/auth/password-reset/', { email });
  },
  
  confirmPasswordReset: async (data: {
    token: string;
    new_password: string;
    new_password_confirm: string;
  }) => {
    return apiService.post('/auth/password-reset/confirm/', data);
  }
};

export const productsApi = {
  getProducts: async (params?: any) => {
    const queryString = params ? new URLSearchParams(params).toString() : '';
    return apiService.get(`/products/products/${queryString ? `?${queryString}` : ''}`);
  },
  
  getProduct: async (id: string | number) => {
    return apiService.get(`/products/products/${id}/`);
  },
  
  getCategories: async () => {
    return apiService.get('/products/categories/');
  },
  
  getBrands: async () => {
    return apiService.get('/products/brands/');
  },
  
  searchProducts: async (query: string) => {
    return apiService.get(`/products/search/?q=${encodeURIComponent(query)}`);
  }
};

export const cartApi = {
  getCart: async () => {
    return apiService.get('/cart/items/');
  },
  
  addToCart: async (data: {
    product_id: number;
    variant_id?: number;
    quantity: number;
  }) => {
    return apiService.post('/cart/add/', data);
  },
  
  updateCartItem: async (itemId: number, data: { quantity: number }) => {
    return apiService.patch(`/cart/items/${itemId}/`, data);
  },
  
  removeFromCart: async (itemId: number) => {
    return apiService.delete(`/cart/items/${itemId}/`);
  },
  
  clearCart: async () => {
    return apiService.delete('/cart/clear/');
  },
  
  getCartSummary: async () => {
    return apiService.get('/cart/summary/');
  },
  
  applyCoupon: async (couponCode: string) => {
    return apiService.post('/cart/apply-coupon/', { code: couponCode });
  },
  
  removeCoupon: async () => {
    return apiService.post('/cart/remove-coupon/');
  }
};

export const ordersApi = {
  getOrders: async (params?: any) => {
    const queryString = params ? new URLSearchParams(params).toString() : '';
    return apiService.get(`/orders/orders/${queryString ? `?${queryString}` : ''}`);
  },
  
  getOrder: async (id: string | number) => {
    return apiService.get(`/orders/orders/${id}/`);
  },
  
  createOrder: async (orderData: any) => {
    return apiService.post('/orders/orders/', orderData);
  },
  
  cancelOrder: async (id: string | number) => {
    return apiService.post(`/orders/orders/${id}/cancel/`);
  },
  
  trackOrder: async (orderNumber: string) => {
    return apiService.get(`/orders/track/${orderNumber}/`);
  },
  
  uploadPaymentProof: async (orderId: number, formData: FormData) => {
    return apiService.post(`/orders/orders/${orderId}/upload-payment-proof/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }
};

export const paymentProofsApi = {
  getPaymentProofs: async (params?: any) => {
    const queryString = params ? new URLSearchParams(params).toString() : '';
    return apiService.get(`/orders/payment-proofs/${queryString ? `?${queryString}` : ''}`);
  },
  
  getPaymentProof: async (id: string | number) => {
    return apiService.get(`/orders/payment-proofs/${id}/`);
  },
  
  verifyPaymentProof: async (id: string | number, data: {
    verification_status: string;
    verification_notes?: string;
  }) => {
    return apiService.post(`/orders/payment-proofs/${id}/verify_payment/`, data);
  }
};

export const favoritesApi = {
  getFavorites: async () => {
    return apiService.get('/favorites/');
  },
  
  addToFavorites: async (productId: number) => {
    return apiService.post('/favorites/', { product_id: productId });
  },
  
  removeFromFavorites: async (productId: number) => {
    return apiService.delete(`/favorites/${productId}/`);
  }
};

export const addressesApi = {
  getAddresses: async () => {
    return apiService.get('/addresses/');
  },
  
  createAddress: async (addressData: any) => {
    return apiService.post('/addresses/', addressData);
  },
  
  updateAddress: async (id: number, addressData: any) => {
    return apiService.patch(`/addresses/${id}/`, addressData);
  },
  
  deleteAddress: async (id: number) => {
    return apiService.delete(`/addresses/${id}/`);
  },
  
  setDefaultAddress: async (id: number) => {
    return apiService.post(`/addresses/${id}/set_default/`);
  }
};

export const shippingApi = {
  getShippingMethods: async () => {
    return apiService.get('/shipping/methods/');
  },
  
  calculateShipping: async (data: {
    governorate: string;
    city: string;
    weight?: number;
    total_amount?: number;
  }) => {
    return apiService.post('/shipping/calculate/', data);
  },
  
  getGovernorates: async () => {
    return apiService.get('/shipping/governorates/');
  },
  
  getCities: async (governorateId: number) => {
    return apiService.get(`/shipping/governorates/${governorateId}/cities/`);
  }
};

export const couponsApi = {
  validateCoupon: async (code: string, cartTotal?: number) => {
    return apiService.post('/coupons/validate/', { 
      code, 
      cart_total: cartTotal 
    });
  },
  
  getCoupons: async () => {
    return apiService.get('/coupons/');
  }
};

export const trackingApi = {
  trackEvent: async (eventData: {
    event_name: string;
    event_data?: any;
    user_id?: number;
    session_id?: string;
  }) => {
    return apiService.post('/tracking/event/', eventData);
  },
  
  trackPageView: async (pageData: {
    page_url: string;
    page_title?: string;
    referrer?: string;
  }) => {
    return apiService.post('/tracking/page-view/', pageData);
  },
  
  trackAddToCart: async (data: {
    product_id: number;
    variant_id?: number;
    quantity: number;
    price: number;
  }) => {
    return apiService.post('/tracking/add-to-cart/', data);
  },
  
  trackPurchase: async (data: {
    order_id: number;
    total_amount: number;
    currency: string;
    items: any[];
  }) => {
    return apiService.post('/tracking/purchase/', data);
  }
};

export const notificationsApi = {
  getNotifications: async (params?: any) => {
    const queryString = params ? new URLSearchParams(params).toString() : '';
    return apiService.get(`/notifications/${queryString ? `?${queryString}` : ''}`);
  },
  
  markAsRead: async (id: number) => {
    return apiService.patch(`/notifications/${id}/`, { is_read: true });
  },
  
  markAllAsRead: async () => {
    return apiService.post('/notifications/mark_all_read/');
  }
};

// Export default instance
export default apiService;