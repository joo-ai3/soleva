import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { useToast } from './ToastContext';

interface FavoriteItem {
  id: number;
  product_id: number;
  product_name: string;
  product_slug: string;
  product_image?: string;
  product_price: number;
  created_at: string;
}

interface FavoritesContextType {
  favorites: FavoriteItem[];
  isLoading: boolean;
  isUpdating: boolean;
  addToFavorites: (productId: number, triggerElement?: HTMLElement, productImage?: string) => Promise<{ success: boolean; error?: string }>;
  removeFromFavorites: (productId: number) => Promise<{ success: boolean; error?: string }>;
  toggleFavorite: (productId: number, triggerElement?: HTMLElement, productImage?: string) => Promise<{ success: boolean; error?: string }>;
  isFavorite: (productId: number) => boolean;
  getFavoriteIds: () => number[];
  refreshFavorites: () => Promise<void>;
  clearFavorites: () => void;
}

const FavoritesContext = createContext<FavoritesContextType | undefined>(undefined);

export function FavoritesProvider({ children }: { children: React.ReactNode }) {
  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  
  const { isAuthenticated, user } = useAuth();
  const { addToast } = useToast();

  // Load favorites when user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      refreshFavorites();
    } else {
      // Load from localStorage for guest users
      const savedFavorites = localStorage.getItem('guest_favorites');
      if (savedFavorites) {
        try {
          const parsedFavorites = JSON.parse(savedFavorites);
          setFavorites(parsedFavorites);
        } catch (error) {
          console.error('Error loading guest favorites:', error);
        }
      }
    }
  }, [isAuthenticated]);

  // Save guest favorites to localStorage
  useEffect(() => {
    if (!isAuthenticated && favorites.length >= 0) {
      localStorage.setItem('guest_favorites', JSON.stringify(favorites));
    }
  }, [favorites, isAuthenticated]);

  const refreshFavorites = useCallback(async () => {
    if (!isAuthenticated) return;

    try {
      setIsLoading(true);
      
      // TODO: Replace with actual API call when backend favorites endpoint is ready
      // const response = await favoritesApi.getAll();
      // if (response.success) {
      //   setFavorites(response.data || []);
      // }
      
      // For now, use localStorage
      const savedFavorites = localStorage.getItem(`favorites_${user?.id}`);
      if (savedFavorites) {
        const parsedFavorites = JSON.parse(savedFavorites);
        setFavorites(parsedFavorites);
      }
    } catch (error) {
      console.error('Error refreshing favorites:', error);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, user]);

  const addToFavorites = async (productId: number, _triggerElement?: HTMLElement, _productImage?: string) => {
    try {
      setIsUpdating(true);
      
      if (isAuthenticated) {
        // TODO: Replace with actual API call when backend is ready
        // const response = await favoritesApi.add(productId);
        // if (response.success) {
        //   await refreshFavorites();
        //   addToast('Added to favorites', 'success');
        //   return { success: true };
        // }
        
        // For now, use localStorage
        const newFavorite: FavoriteItem = {
          id: Date.now(),
          product_id: productId,
          product_name: 'Product', // Would be fetched from API
          product_slug: '',
          product_price: 0,
          created_at: new Date().toISOString(),
        };

        setFavorites(prev => {
          const exists = prev.find(item => item.product_id === productId);
          if (exists) return prev;
          const updated = [...prev, newFavorite];
          localStorage.setItem(`favorites_${user?.id}`, JSON.stringify(updated));
          return updated;
        });

        // TODO: Trigger flying animation if element provided
        // Animation will be handled by the FlyingAnimationProvider context

        addToast('Added to favorites', 'success');
        return { success: true };
      } else {
        // Handle guest favorites
        const newFavorite: FavoriteItem = {
          id: Date.now(),
          product_id: productId,
          product_name: 'Product',
          product_slug: '',
          product_price: 0,
          created_at: new Date().toISOString(),
        };

        setFavorites(prev => {
          const exists = prev.find(item => item.product_id === productId);
          if (exists) return prev;
          return [...prev, newFavorite];
        });

        // TODO: Trigger flying animation for guest favorites too
        // Animation will be handled by the FlyingAnimationProvider context

        addToast('Added to favorites', 'success');
        return { success: true };
      }
    } catch (error: any) {
      console.error('Add to favorites error:', error);
      addToast('Failed to add to favorites', 'error');
      return { success: false, error: error.message };
    } finally {
      setIsUpdating(false);
    }
  };

  const removeFromFavorites = async (productId: number) => {
    try {
      setIsUpdating(true);
      
      if (isAuthenticated) {
        // TODO: Replace with actual API call when backend is ready
        // const response = await favoritesApi.remove(productId);
        // if (response.success) {
        //   await refreshFavorites();
        //   addToast('Removed from favorites', 'success');
        //   return { success: true };
        // }
        
        // For now, use localStorage
        setFavorites(prev => {
          const updated = prev.filter(item => item.product_id !== productId);
          localStorage.setItem(`favorites_${user?.id}`, JSON.stringify(updated));
          return updated;
        });

        addToast('Removed from favorites', 'success');
        return { success: true };
      } else {
        // Handle guest favorites
        setFavorites(prev => prev.filter(item => item.product_id !== productId));
        addToast('Removed from favorites', 'success');
        return { success: true };
      }
    } catch (error: any) {
      console.error('Remove from favorites error:', error);
      addToast('Failed to remove from favorites', 'error');
      return { success: false, error: error.message };
    } finally {
      setIsUpdating(false);
    }
  };

  const toggleFavorite = async (productId: number, triggerElement?: HTMLElement, productImage?: string) => {
    const isFav = isFavorite(productId);
    
    if (isFav) {
      return await removeFromFavorites(productId);
    } else {
      return await addToFavorites(productId, triggerElement, productImage);
    }
  };

  const isFavorite = useCallback((productId: number) => {
    return favorites.some(item => item.product_id === productId);
  }, [favorites]);

  const getFavoriteIds = useCallback(() => {
    return favorites.map(item => item.product_id);
  }, [favorites]);

  const clearFavorites = useCallback(() => {
    setFavorites([]);
    if (isAuthenticated && user) {
      localStorage.removeItem(`favorites_${user.id}`);
    } else {
      localStorage.removeItem('guest_favorites');
    }
    addToast('Favorites cleared', 'success');
  }, [isAuthenticated, user, addToast]);

  const value = {
    favorites,
    isLoading,
    isUpdating,
    addToFavorites,
    removeFromFavorites,
    toggleFavorite,
    isFavorite,
    getFavoriteIds,
    refreshFavorites,
    clearFavorites,
  };

  return (
    <FavoritesContext.Provider value={value}>
      {children}
    </FavoritesContext.Provider>
  );
}

export function useFavorites() {
  const context = useContext(FavoritesContext);
  if (!context) {
    throw new Error('useFavorites must be used within FavoritesProvider');
  }
  return context;
}