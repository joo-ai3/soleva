import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Trash2, Plus, Minus, ShoppingBag, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLang, useTranslation } from '../contexts/LangContext';
import { useApiQuery, useApiMutation } from '../hooks/useApi';
import { apiService } from '../services/api';

import GlassCard from '../components/GlassCard';
import GlassButton from '../components/GlassButton';
import SectionTitle from '../components/SectionTitle';
import ErrorMessage from '../components/ui/ErrorMessage';
import { LoadingSpinner, InlineLoadingSpinner, ButtonLoadingSpinner } from '../components/ui/LoadingSpinner';
import { Cart, CartItem } from '../types';

// API Functions
const fetchCart = () => apiService.get<Cart>('/cart/');
const updateCartItem = (data: { item_id: number; quantity: number }) => 
  apiService.patch<CartItem>(`/cart/items/${data.item_id}/`, { quantity: data.quantity });
const removeCartItem = (itemId: number) => 
  apiService.delete(`/cart/items/${itemId}/`);
const clearCart = () => 
  apiService.delete('/cart/clear/');

export const CartPageWithApi: React.FC = () => {
  const { lang } = useLang();
  const t = useTranslation();
  const [updatingItems, setUpdatingItems] = useState<Set<number>>(new Set());
  const [removingItems, setRemovingItems] = useState<Set<number>>(new Set());

  // Fetch cart data
  const {
    data: cart,
    loading: cartLoading,
    error: cartError,
    retry: retryCart
  } = useApiQuery(fetchCart, {
    retries: 2,
    onError: (error) => {
      console.error('Failed to fetch cart:', error);
    }
  });

  // Update cart item quantity
  const {
    loading: updateLoading,
    error: updateError,
    execute: executeUpdate
  } = useApiMutation(updateCartItem, {
    onSuccess: () => {
      retryCart(); // Refresh cart after update
    },
    onError: (error) => {
      console.error('Failed to update cart item:', error);
    }
  });

  // Remove cart item
  const {
    loading: removeLoading,
    error: removeError,
    execute: executeRemove
  } = useApiMutation(removeCartItem, {
    onSuccess: () => {
      retryCart(); // Refresh cart after removal
    },
    onError: (error) => {
      console.error('Failed to remove cart item:', error);
    }
  });

  // Clear entire cart
  const {
    loading: clearLoading,
    error: clearError,
    execute: executeClear
  } = useApiMutation(clearCart, {
    onSuccess: () => {
      retryCart(); // Refresh cart after clearing
    },
    onError: (error) => {
      console.error('Failed to clear cart:', error);
    }
  });

  const handleQuantityUpdate = async (itemId: number, newQuantity: number) => {
    if (newQuantity < 1) return;
    
    setUpdatingItems(prev => new Set(prev).add(itemId));
    
    try {
      await executeUpdate({ item_id: itemId, quantity: newQuantity });
    } finally {
      setUpdatingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(itemId);
        return newSet;
      });
    }
  };

  const handleRemoveItem = async (itemId: number) => {
    setRemovingItems(prev => new Set(prev).add(itemId));
    
    try {
      await executeRemove(itemId);
    } finally {
      setRemovingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(itemId);
        return newSet;
      });
    }
  };

  const handleClearCart = async () => {
    if (window.confirm(lang === 'ar' ? 'هل أنت متأكد من حذف جميع المنتجات؟' : 'Are you sure you want to clear all items?')) {
      await executeClear();
    }
  };

  // Show loading state for initial cart fetch
  if (cartLoading && !cart) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <SectionTitle className="mb-8">{t('Shopping Cart')}</SectionTitle>
          <InlineLoadingSpinner text={t('Loading your cart...')} />
        </div>
      </div>
    );
  }

  // Show error state with retry option
  if (cartError && !cart) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <SectionTitle className="mb-8">{t('Shopping Cart')}</SectionTitle>
          <ErrorMessage
            error={cartError}
            onRetry={retryCart}
            className="max-w-md mx-auto"
          />
        </div>
      </div>
    );
  }

  const isEmpty = !cart || !cart.items || cart.items.length === 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <SectionTitle className="mb-4">{t('Shopping Cart')}</SectionTitle>
          {!isEmpty && (
            <p className="text-lg text-gray-600">
              {cart.items.length} {lang === 'ar' ? 'منتج في السلة' : 'items in your cart'}
            </p>
          )}
        </motion.div>

        {/* Error Messages */}
        {updateError && (
          <ErrorMessage
            error={updateError}
            inline
            className="mb-6"
            onRetry={() => {
              // Error will be cleared on retry
            }}
          />
        )}

        {removeError && (
          <ErrorMessage
            error={removeError}
            inline
            className="mb-6"
            onRetry={() => {
              // Error will be cleared on retry
            }}
          />
        )}

        {clearError && (
          <ErrorMessage
            error={clearError}
            inline
            className="mb-6"
            onRetry={handleClearCart}
          />
        )}

        {isEmpty ? (
          /* Empty Cart */
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-16"
          >
            <GlassCard className="max-w-md mx-auto">
              <div className="text-6xl mb-4">🛒</div>
              <h3 className="text-xl font-semibold mb-2">
                {lang === 'ar' ? 'السلة فارغة' : 'Your Cart is Empty'}
              </h3>
              <p className="text-gray-600 mb-6">
                {lang === 'ar' 
                  ? 'ابدأ بإضافة منتجات إلى سلة التسوق'
                  : 'Start adding some products to your cart'
                }
              </p>
              <GlassButton as={Link} to="/products" variant="primary">
                {t('Start Shopping')}
              </GlassButton>
            </GlassCard>
          </motion.div>
        ) : (
          /* Cart with Items */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Cart Items */}
            <div className="lg:col-span-2 space-y-4">
              {/* Cart Controls */}
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-900">
                  {t('Cart Items')}
                </h2>
                <GlassButton
                  onClick={handleClearCart}
                  disabled={clearLoading}
                  variant="ghost"
                  className="text-red-600 hover:text-red-700"
                >
                  {clearLoading ? <ButtonLoadingSpinner /> : <Trash2 className="h-4 w-4 mr-2" />}
                  {t('Clear Cart')}
                </GlassButton>
              </div>

              {/* Items List */}
              {cart.items.map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <GlassCard className="overflow-hidden">
                    <div className="p-6">
                      <div className="flex items-center gap-4">
                        {/* Product Image */}
                        <div className="w-20 h-20 rounded-lg overflow-hidden flex-shrink-0">
                          <img
                            src={item.product_image || '/placeholder-product.jpg'}
                            alt={item.product_name}
                            className="w-full h-full object-cover"
                          />
                        </div>

                        {/* Product Info */}
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-gray-900 truncate">
                            {item.product_name}
                          </h3>
                          <p className="text-sm text-gray-600">
                            {item.product_price} {t('egp')} {lang === 'ar' ? 'للقطعة' : 'each'}
                          </p>
                          {item.variant_attributes && Object.keys(item.variant_attributes).length > 0 && (
                            <div className="flex flex-wrap gap-2 mt-1">
                              {Object.entries(item.variant_attributes).map(([key, value]) => (
                                <span
                                  key={key}
                                  className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                                >
                                  {key}: {value}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>

                        {/* Quantity Controls */}
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleQuantityUpdate(item.id, item.quantity - 1)}
                            disabled={item.quantity <= 1 || updatingItems.has(item.id)}
                            className="w-8 h-8 rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
                          >
                            <Minus className="h-4 w-4" />
                          </button>
                          
                          <div className="w-12 text-center font-medium">
                            {updatingItems.has(item.id) ? (
                              <LoadingSpinner size="sm" />
                            ) : (
                              item.quantity
                            )}
                          </div>
                          
                          <button
                            onClick={() => handleQuantityUpdate(item.id, item.quantity + 1)}
                            disabled={updatingItems.has(item.id)}
                            className="w-8 h-8 rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
                          >
                            <Plus className="h-4 w-4" />
                          </button>
                        </div>

                        {/* Item Total */}
                        <div className="text-right min-w-0">
                          <div className="font-semibold text-gray-900">
                            {(item.product_price * item.quantity).toFixed(2)} {t('egp')}
                          </div>
                          <button
                            onClick={() => handleRemoveItem(item.id)}
                            disabled={removingItems.has(item.id)}
                            className="text-red-600 hover:text-red-700 text-sm disabled:opacity-50 disabled:cursor-not-allowed mt-1"
                          >
                            {removingItems.has(item.id) ? (
                              <LoadingSpinner size="sm" />
                            ) : (
                              t('Remove')
                            )}
                          </button>
                        </div>
                      </div>
                    </div>
                  </GlassCard>
                </motion.div>
              ))}
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <GlassCard className="sticky top-24">
                  <div className="p-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-6">
                      {t('Order Summary')}
                    </h2>

                    <div className="space-y-3 mb-6">
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t('Subtotal')}</span>
                        <span className="font-medium">{cart.subtotal} {t('egp')}</span>
                      </div>
                      
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t('Items')}</span>
                        <span className="text-sm">{cart.total_items}</span>
                      </div>

                      <div className="border-t pt-3">
                        <div className="flex justify-between text-lg font-semibold">
                          <span>{t('Total')}</span>
                          <span>{cart.subtotal} {t('egp')}</span>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <GlassButton
                        as={Link}
                        to="/checkout"
                        variant="primary"
                        className="w-full"
                        disabled={cartLoading || updateLoading || removeLoading}
                      >
                        <ShoppingBag className="h-5 w-5 mr-2" />
                        {t('Proceed to Checkout')}
                      </GlassButton>
                      
                      <GlassButton
                        as={Link}
                        to="/products"
                        variant="ghost"
                        className="w-full"
                      >
                        {t('Continue Shopping')}
                      </GlassButton>
                    </div>

                    {/* Network Status Warning */}
                    {(updateError || removeError || clearError) && (
                      <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <div className="flex items-start gap-2">
                          <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                          <p className="text-xs text-yellow-800">
                            {lang === 'ar' 
                              ? 'تحقق من اتصالك بالإنترنت إذا استمرت المشاكل'
                              : 'Check your internet connection if issues persist'
                            }
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </GlassCard>
              </motion.div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
