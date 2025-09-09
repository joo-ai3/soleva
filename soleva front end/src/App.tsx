
import { LangProvider } from './contexts/LangContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import { CartProvider } from './contexts/CartContext';
import { ToastProvider } from './contexts/ToastContext';
import { FavoritesProvider } from './contexts/FavoritesContext';
import { WebsiteProvider } from './contexts/WebsiteContext';
import { FlyingAnimationProvider } from './components/FlyingAnimation';
import RoutesWrapper from "./components/RoutesWrapper";
import ErrorBoundary from './components/ui/ErrorBoundary';
import OfflineIndicator from './components/ui/OfflineIndicator';


export default function App() {
  return (
    <ErrorBoundary>
      <LangProvider>
        <ThemeProvider>
          <WebsiteProvider>
            <FlyingAnimationProvider>
              <FavoritesProvider>
                <AuthProvider>
                  <CartProvider>
                    <ToastProvider>
                      <OfflineIndicator />
                      <RoutesWrapper />
                    </ToastProvider>
                  </CartProvider>
                </AuthProvider>
              </FavoritesProvider>
            </FlyingAnimationProvider>
          </WebsiteProvider>
        </ThemeProvider>
      </LangProvider>
    </ErrorBoundary>
  );
}
