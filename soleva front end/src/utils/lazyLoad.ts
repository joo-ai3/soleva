import { lazy } from 'react';

// Lazy loading helper with retry mechanism
export const retryLazy = (componentImport: () => Promise<any>, name: string) => {
  return lazy(async () => {
    let retryCount = 0;
    const maxRetries = 3;

    while (retryCount < maxRetries) {
      try {
        const component = await componentImport();
        return component;
      } catch (error) {
        retryCount++;
        console.warn(`Failed to load component ${name}, attempt ${retryCount}/${maxRetries}`, error);
        
        if (retryCount >= maxRetries) {
          throw error;
        }
        
        // Wait before retrying (exponential backoff)
        await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, retryCount - 1)));
      }
    }
    
    throw new Error(`Failed to load component ${name} after ${maxRetries} attempts`);
  });
};

// Preload helper for critical routes
export const preloadRoute = (componentImport: () => Promise<any>) => {
  // Only preload if user is likely to navigate (e.g., on hover)
  const preload = () => {
    componentImport().catch(error => {
      console.warn('Failed to preload component:', error);
    });
  };

  return preload;
};

// Lazy loaded pages with retry
export const LazyHome = retryLazy(() => import('../pages/Home'), 'Home');
export const LazyProductsPage = retryLazy(() => import('../pages/ProductsPage'), 'ProductsPage');
export const LazyProductPage = retryLazy(() => import('../pages/ProductPage'), 'ProductPage');
export const LazyCartPage = retryLazy(() => import('../pages/CartPage'), 'CartPage');
export const LazyCheckoutPage = retryLazy(() => import('../pages/CheckoutPage'), 'CheckoutPage');
export const LazyOrdersPage = retryLazy(() => import('../pages/OrdersPage'), 'OrdersPage');
export const LazyOrderConfirmation = retryLazy(() => import('../pages/OrderConfirmation'), 'OrderConfirmation');
export const LazyFavoritesPage = retryLazy(() => import('../pages/FavoritesPage'), 'FavoritesPage');
export const LazyAccountPage = retryLazy(() => import('../pages/AccountPage'), 'AccountPage');
export const LazyLoginPage = retryLazy(() => import('../pages/LoginPage'), 'LoginPage');
export const LazyRegisterPage = retryLazy(() => import('../pages/RegisterPage'), 'RegisterPage');
export const LazyOrderTrackingPage = retryLazy(() => import('../pages/OrderTrackingPage'), 'OrderTrackingPage');
export const LazyCollectionPage = retryLazy(() => import('../pages/CollectionPage'), 'CollectionPage');
export const LazyAboutPage = retryLazy(() => import('../pages/AboutPage'), 'AboutPage');
export const LazyContactPage = retryLazy(() => import('../pages/ContactPage'), 'ContactPage');
export const LazyPrivacyPage = retryLazy(() => import('../pages/PrivacyPage'), 'PrivacyPage');
export const LazyTermsPage = retryLazy(() => import('../pages/TermsPage'), 'TermsPage');
export const LazyNotFoundPage = retryLazy(() => import('../pages/NotFoundPage'), 'NotFoundPage');
export const LazyFlashSalePage = retryLazy(() => import('../pages/FlashSalePage'), 'FlashSalePage');
export const LazyVerifyEmailPage = retryLazy(() => import('../pages/VerifyEmailPage'), 'VerifyEmailPage');

// Preload functions for critical routes
export const preloadHome = preloadRoute(() => import('../pages/Home'));
export const preloadProducts = preloadRoute(() => import('../pages/ProductsPage'));
export const preloadCart = preloadRoute(() => import('../pages/CartPage'));
export const preloadCheckout = preloadRoute(() => import('../pages/CheckoutPage'));
export const preloadFlashSale = preloadRoute(() => import('../pages/FlashSalePage'));
