import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useLang } from '../contexts/LangContext';
import { AnimatePresence } from 'framer-motion';

import AppHeader from './AppHeader';
import AppFooter from './AppFooter';
import MobileBottomNav from './MobileBottomNav';
import NotificationBanner from './NotificationBanner';

import {
  LazyHome,
  LazyProductsPage,
  LazyProductPage,
  LazyCartPage,
  LazyCheckoutPage,
  LazyOrdersPage,
  LazyOrderConfirmation,
  LazyFavoritesPage,
  LazyAccountPage,
  LazyLoginPage,
  LazyRegisterPage,
  LazyOrderTrackingPage,
  LazyCollectionPage,
  LazyAboutPage,
  LazyContactPage,
  LazyPrivacyPage,
  LazyTermsPage,
  LazyNotFoundPage,
  LazyFlashSalePage,
  LazyVerifyEmailPage,

} from '../utils/lazyLoad';
import LazyRoute from './LazyRoute';
import ProtectedRoute from './ProtectedRoute';

// Scroll to top component
function ScrollToTop() {
  const location = useLocation();
  
  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  }, [location.pathname]);
  
  return null;
}

export default function RoutesWrapper() {
  const { lang } = useLang();
  const safeLang = ["ar", "en"].includes(lang) ? lang : "en";

  return (
    <div 
      dir={safeLang === "ar" ? "rtl" : "ltr"} 
      className={`${safeLang === "ar" ? "font-arabic" : "font-montserrat"} min-h-screen optimize-text`}
      lang={safeLang}
    >
      <Router>
        <ScrollToTop />
        <NotificationBanner location="top" />
        <AppHeader />
        <NotificationBanner location="header" />
        <main 
          role="main" 
          className="pt-20 sm:pt-24 lg:pt-28 min-h-[calc(100vh-60px)] bg-app"
          id="main-content"
        >
          <AnimatePresence mode="wait">
            <Routes>
              <Route path="/" element={<LazyRoute component={LazyHome} />} />
              <Route path="/products" element={<LazyRoute component={LazyProductsPage} />} />
              <Route path="/collections/:id" element={<LazyRoute component={LazyCollectionPage} />} />
              <Route path="/product/:id" element={<LazyRoute component={LazyProductPage} />} />
              <Route path="/flash-sale/:id" element={<LazyRoute component={LazyFlashSalePage} />} />
              <Route path="/verify-email" element={<LazyRoute component={LazyVerifyEmailPage} />} />
              <Route path="/cart" element={<LazyRoute component={LazyCartPage} />} />
              <Route path="/favorites" element={<LazyRoute component={LazyFavoritesPage} />} />
              <Route path="/about" element={<LazyRoute component={LazyAboutPage} />} />
              <Route path="/contact" element={<LazyRoute component={LazyContactPage} />} />
              <Route path="/privacy" element={<LazyRoute component={LazyPrivacyPage} />} />
              <Route path="/terms" element={<LazyRoute component={LazyTermsPage} />} />
              <Route path="/login" element={<LazyRoute component={LazyLoginPage} />} />
              <Route path="/register" element={<LazyRoute component={LazyRegisterPage} />} />
              <Route
                path="/checkout"
                element={
                  <ProtectedRoute>
                    <LazyRoute component={LazyCheckoutPage} />
                  </ProtectedRoute>
                }
              />
              <Route path="/order-confirmation" element={<LazyRoute component={LazyOrderConfirmation} />} />
              <Route path="/account" element={<LazyRoute component={LazyAccountPage} />} />
              <Route path="/orders" element={<LazyRoute component={LazyOrdersPage} />} />
              <Route path="/track-order" element={<LazyRoute component={LazyOrderTrackingPage} />} />
              <Route path="/track-order/:orderNumber" element={<LazyRoute component={LazyOrderTrackingPage} />} />
              <Route path="/order-tracking" element={<LazyRoute component={LazyOrderTrackingPage} />} />
              <Route path="*" element={<LazyRoute component={LazyNotFoundPage} />} />
            </Routes>
          </AnimatePresence>
        </main>
        <MobileBottomNav />
        <AppFooter />
      </Router>
    </div>
  );
}

