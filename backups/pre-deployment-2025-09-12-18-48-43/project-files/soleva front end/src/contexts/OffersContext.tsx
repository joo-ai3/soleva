import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useOfferCalculation, useFlashSales } from '../hooks/useOffers';
import { useCart } from './CartContext';
import { useAuth } from './AuthContext';
import { OfferCalculationResponse } from '../services/offersApi';

interface OffersContextType {
  // Offer calculations
  offerCalculation: OfferCalculationResponse | null;
  isCalculatingOffers: boolean;
  offersError: string | null;
  
  // Flash sales
  activeFlashSales: any[];
  isLoadingFlashSales: boolean;
  flashSalesError: string | null;
  
  // Coupon blocking
  areCouponsBlocked: boolean;
  
  // Methods
  calculateCartOffers: () => Promise<void>;
  clearOffers: () => void;
  canApplyCoupon: () => boolean;
}

const OffersContext = createContext<OffersContextType | undefined>(undefined);

export function OffersProvider({ children }: { children: React.ReactNode }) {
  const { cart } = useCart();
  const { user } = useAuth();
  
  const {
    calculation: offerCalculation,
    loading: isCalculatingOffers,
    error: offersError,
    calculateOffers,
    clearCalculation
  } = useOfferCalculation();
  
  const {
    flashSales: activeFlashSales,
    loading: isLoadingFlashSales,
    error: flashSalesError,
    fetchActive: fetchActiveFlashSales
  } = useFlashSales();

  const [areCouponsBlocked, setAreCouponsBlocked] = useState(false);

  // Calculate offers when cart changes
  useEffect(() => {
    if (cart.length > 0) {
      calculateCartOffers();
    } else {
      clearCalculation();
      setAreCouponsBlocked(false);
    }
  }, [cart]);

  // Update coupon blocking when offer calculation changes
  useEffect(() => {
    if (offerCalculation) {
      setAreCouponsBlocked(offerCalculation.coupons_blocked);
    } else {
      setAreCouponsBlocked(false);
    }
  }, [offerCalculation]);

  const calculateCartOffers = useCallback(async () => {
    if (!cart.length) return;

    try {
      // Convert cart items to the format expected by offers API
      const cartItems = cart.map(item => ({
        product_id: item.product_id.toString(),
        quantity: item.quantity,
        price: item.unit_price
      }));

      await calculateOffers(cartItems, user?.id?.toString());
    } catch (error) {
      console.error('Failed to calculate offers:', error);
    }
  }, [cart, user, calculateOffers]);

  const clearOffers = useCallback(() => {
    clearCalculation();
    setAreCouponsBlocked(false);
  }, [clearCalculation]);

  const canApplyCoupon = useCallback(() => {
    return !areCouponsBlocked;
  }, [areCouponsBlocked]);

  // Fetch active flash sales on mount
  useEffect(() => {
    fetchActiveFlashSales();
  }, [fetchActiveFlashSales]);

  const value = {
    offerCalculation,
    isCalculatingOffers,
    offersError,
    activeFlashSales,
    isLoadingFlashSales,
    flashSalesError,
    areCouponsBlocked,
    calculateCartOffers,
    clearOffers,
    canApplyCoupon
  };

  return (
    <OffersContext.Provider value={value}>
      {children}
    </OffersContext.Provider>
  );
}

export function useOffers() {
  const context = useContext(OffersContext);
  if (!context) {
    throw new Error('useOffers must be used within OffersProvider');
  }
  return context;
}
