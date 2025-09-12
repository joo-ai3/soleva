import { useState, useEffect, useCallback } from 'react';
import { offersAPI, FlashSale, SpecialOffer, OfferCalculationResponse, ProductOfferResponse } from '../services/offersApi';

export function useFlashSales() {
  const [flashSales, setFlashSales] = useState<FlashSale[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFlashSales = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await offersAPI.getFlashSales();
      setFlashSales(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch flash sales');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchActiveFlashSales = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await offersAPI.getActiveFlashSales();
      setFlashSales(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch active flash sales');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFlashSales();
  }, [fetchFlashSales]);

  return {
    flashSales,
    loading,
    error,
    refetch: fetchFlashSales,
    fetchActive: fetchActiveFlashSales
  };
}

export function useSpecialOffers() {
  const [offers, setOffers] = useState<SpecialOffer[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOffers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await offersAPI.getSpecialOffers();
      setOffers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch special offers');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOffers();
  }, [fetchOffers]);

  return {
    offers,
    loading,
    error,
    refetch: fetchOffers
  };
}

export function useProductOffers(productId: string) {
  const [offers, setOffers] = useState<SpecialOffer[]>([]);
  const [productOfferData, setProductOfferData] = useState<ProductOfferResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProductOffers = useCallback(async (id: string) => {
    if (!id) return;
    
    setLoading(true);
    setError(null);
    try {
      const [offersData, productData] = await Promise.all([
        offersAPI.getProductOffers(id),
        offersAPI.checkProductOffers({ product_id: id, quantity: 1 })
      ]);
      
      setOffers(offersData);
      setProductOfferData(productData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch product offers');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (productId) {
      fetchProductOffers(productId);
    }
  }, [productId, fetchProductOffers]);

  return {
    offers,
    productOfferData,
    loading,
    error,
    refetch: () => fetchProductOffers(productId)
  };
}

export function useOfferCalculation() {
  const [calculation, setCalculation] = useState<OfferCalculationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const calculateOffers = useCallback(async (cartItems: any[], userId?: string) => {
    if (!cartItems.length) {
      setCalculation(null);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const formattedItems = cartItems.map(item => ({
        product_id: item.id || item.product_id,
        quantity: item.qty || item.quantity,
        price: item.price
      }));

      const data = await offersAPI.calculateOffers({
        cart_items: formattedItems,
        user_id: userId
      });
      
      setCalculation(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to calculate offers');
      setCalculation(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const recordOfferUsage = useCallback(async (usageData: any) => {
    try {
      await offersAPI.recordOfferUsage(usageData);
    } catch (err) {
      console.error('Failed to record offer usage:', err);
    }
  }, []);

  return {
    calculation,
    loading,
    error,
    calculateOffers,
    recordOfferUsage,
    clearCalculation: () => setCalculation(null)
  };
}

export function useFlashSale(id: string) {
  const [flashSale, setFlashSale] = useState<FlashSale | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFlashSale = useCallback(async (saleId: string) => {
    if (!saleId) return;
    
    setLoading(true);
    setError(null);
    try {
      const data = await offersAPI.getFlashSale(saleId);
      setFlashSale(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch flash sale');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (id) {
      fetchFlashSale(id);
    }
  }, [id, fetchFlashSale]);

  return {
    flashSale,
    loading,
    error,
    refetch: () => fetchFlashSale(id)
  };
}
