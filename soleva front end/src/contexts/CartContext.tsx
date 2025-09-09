import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { cartApi, trackingApi } from '../services/api';
import { useAuth } from './AuthContext';
import { useToast } from './ToastContext';

interface CartItem {
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
}

interface CartSummary {
  items_count: number;
  subtotal: number;
  shipping_cost: number;
  tax_amount: number;
  discount_amount: number;
  total: number;
  coupon_code?: string;
  coupon_discount?: number;
}

interface CartContextType {
  cart: CartItem[];
  cartSummary: CartSummary | null;
  isLoading: boolean;
  isUpdating: boolean;
  addToCart: (data: {
    product_id: number;
    variant_id?: number;
    quantity?: number;
    attributes?: Record<string, any>;
    triggerElement?: HTMLElement;
    productImage?: string;
  }) => Promise<{ success: boolean; error?: string }>;
  updateCartItem: (itemId: number, quantity: number) => Promise<{ success: boolean; error?: string }>;
  removeFromCart: (itemId: number) => Promise<{ success: boolean; error?: string }>;
  clearCart: () => Promise<{ success: boolean; error?: string }>;
  applyCoupon: (code: string) => Promise<{ success: boolean; error?: string }>;
  refreshCart: () => Promise<void>;
  getCartTotal: () => number;
  getCartItemsCount: () => number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [cartSummary, setCartSummary] = useState<CartSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  
  const { isAuthenticated } = useAuth();
  const { addToast } = useToast();

  // Load cart data when user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      refreshCart();
    } else {
      // Load from localStorage for guest users
      const savedCart = localStorage.getItem('guest_cart');
      if (savedCart) {
        try {
          const parsedCart = JSON.parse(savedCart);
          setCart(parsedCart);
        } catch (error) {
          console.error('Error loading guest cart:', error);
        }
      }
    }
  }, [isAuthenticated]);

  // Save guest cart to localStorage
  useEffect(() => {
    if (!isAuthenticated && cart.length > 0) {
      localStorage.setItem('guest_cart', JSON.stringify(cart));
    }
  }, [cart, isAuthenticated]);

  const refreshCart = useCallback(async () => {
    if (!isAuthenticated) return;

    try {
      setIsLoading(true);
      
      // Fetch cart items and summary in parallel
      const [itemsResponse, summaryResponse] = await Promise.all([
        cartApi.getCart(),
        cartApi.getCartSummary()
      ]);

      if (itemsResponse.success) {
        setCart(itemsResponse.data || []);
      }

      if (summaryResponse.success) {
        setCartSummary(summaryResponse.data);
      }
    } catch (error) {
      console.error('Error refreshing cart:', error);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  const addToCart = async (data: {
    product_id: number;
    variant_id?: number;
    quantity?: number;
    attributes?: Record<string, any>;
    triggerElement?: HTMLElement;
    productImage?: string;
  }) => {
    try {
      setIsUpdating(true);
      
      if (isAuthenticated) {
        const response = await cartApi.addToCart({
          product_id: data.product_id,
          variant_id: data.variant_id,
          quantity: data.quantity || 1
        });
        
        if (response.success) {
          await refreshCart();
          
          // Track add to cart event
          trackingApi.trackAddToCart({
            product_id: data.product_id,
            quantity: data.quantity || 1,
            price: 0 // Price will be filled by backend
          });
          
          // TODO: Trigger flying animation if element provided
          // Animation will be handled by the FlyingAnimationProvider context
          
          addToast('Product added to cart', 'success');
          return { success: true };
        } else {
          addToast(response.message || 'Failed to add product to cart', 'error');
          return { success: false, error: response.message };
        }
      } else {
        // Handle guest cart (localStorage)
        const newItem: CartItem = {
          id: Date.now(), // Temporary ID for guest cart
          product_id: data.product_id,
          product_name: 'Product', // This would need to be fetched
          product_slug: '',
          variant_id: data.variant_id,
          variant_attributes: data.attributes,
          unit_price: 0, // This would need to be fetched
          quantity: data.quantity || 1,
          total_price: 0,
        };

        setCart(prev => {
          const existingIndex = prev.findIndex(item => 
            item.product_id === data.product_id && 
            item.variant_id === data.variant_id
          );

          if (existingIndex > -1) {
            const updated = [...prev];
            updated[existingIndex].quantity += data.quantity || 1;
            updated[existingIndex].total_price = updated[existingIndex].unit_price * updated[existingIndex].quantity;
            return updated;
          }

          return [...prev, newItem];
        });

        // TODO: Trigger flying animation for guest cart too
        // Animation will be handled by the FlyingAnimationProvider context

        addToast('Product added to cart', 'success');
        return { success: true };
      }
    } catch (error: any) {
      console.error('Add to cart error:', error);
      addToast('Failed to add product to cart', 'error');
      return { success: false, error: error.message };
    } finally {
      setIsUpdating(false);
    }
  };

  const updateCartItem = async (itemId: number, quantity: number) => {
    try {
      setIsUpdating(true);
      
      if (isAuthenticated) {
        const response = await cartApi.updateCartItem(itemId, { quantity });
        
        if (response.success) {
          await refreshCart();
          return { success: true };
        } else {
          addToast(response.message || 'Failed to update cart item', 'error');
          return { success: false, error: response.message };
        }
      } else {
        // Handle guest cart
        setCart(prev => prev.map(item => 
          item.id === itemId 
            ? { ...item, quantity, total_price: item.unit_price * quantity }
            : item
        ));
        return { success: true };
      }
    } catch (error: any) {
      console.error('Update cart item error:', error);
      addToast('Failed to update cart item', 'error');
      return { success: false, error: error.message };
    } finally {
      setIsUpdating(false);
    }
  };

  const removeFromCart = async (itemId: number) => {
    try {
      setIsUpdating(true);
      
      if (isAuthenticated) {
        const response = await cartApi.removeFromCart(itemId);
        
        if (response.success) {
          await refreshCart();
          addToast('Item removed from cart', 'success');
          return { success: true };
        } else {
          addToast(response.message || 'Failed to remove item', 'error');
          return { success: false, error: response.message };
        }
      } else {
        // Handle guest cart
        setCart(prev => prev.filter(item => item.id !== itemId));
        addToast('Item removed from cart', 'success');
        return { success: true };
      }
    } catch (error: any) {
      console.error('Remove from cart error:', error);
      addToast('Failed to remove item', 'error');
      return { success: false, error: error.message };
    } finally {
      setIsUpdating(false);
    }
  };

  const clearCart = async () => {
    try {
      setIsUpdating(true);
      
      if (isAuthenticated) {
        const response = await cartApi.clearCart();
        
        if (response.success) {
          setCart([]);
          setCartSummary(null);
          addToast('Cart cleared', 'success');
          return { success: true };
        } else {
          addToast(response.message || 'Failed to clear cart', 'error');
          return { success: false, error: response.message };
        }
      } else {
        // Handle guest cart
        setCart([]);
        localStorage.removeItem('guest_cart');
        addToast('Cart cleared', 'success');
        return { success: true };
      }
    } catch (error: any) {
      console.error('Clear cart error:', error);
      addToast('Failed to clear cart', 'error');
      return { success: false, error: error.message };
    } finally {
      setIsUpdating(false);
    }
  };

  const applyCoupon = async (code: string) => {
    try {
      setIsUpdating(true);
      
      if (!isAuthenticated) {
        addToast('Please login to apply coupon', 'error');
        return { success: false, error: 'Authentication required' };
      }

      const response = await cartApi.applyCoupon(code);
      
      if (response.success) {
        await refreshCart();
        addToast('Coupon applied successfully', 'success');
        return { success: true };
      } else {
        addToast(response.message || 'Invalid coupon code', 'error');
        return { success: false, error: response.message };
      }
    } catch (error: any) {
      console.error('Apply coupon error:', error);
      addToast('Failed to apply coupon', 'error');
      return { success: false, error: error.message };
    } finally {
      setIsUpdating(false);
    }
  };

  const getCartTotal = useCallback(() => {
    if (cartSummary) {
      return cartSummary.total;
    }
    return cart.reduce((total, item) => total + item.total_price, 0);
  }, [cart, cartSummary]);

  const getCartItemsCount = useCallback(() => {
    if (cartSummary) {
      return cartSummary.items_count;
    }
    return cart.reduce((count, item) => count + item.quantity, 0);
  }, [cart, cartSummary]);

  const value = {
    cart,
    cartSummary,
    isLoading,
    isUpdating,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
    applyCoupon,
    refreshCart,
    getCartTotal,
    getCartItemsCount,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
}