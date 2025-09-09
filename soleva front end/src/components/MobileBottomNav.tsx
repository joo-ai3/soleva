import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FiHome, 
  FiGrid, 
  FiHeart, 
  FiShoppingBag, 
  FiUser 
} from 'react-icons/fi';
import { useCart } from '../contexts/CartContext';
import { useFavorites } from '../contexts/FavoritesContext';
import { useAuth } from '../contexts/AuthContext';
import { useLang } from '../contexts/LangContext';
import clsx from 'clsx';

interface NavItem {
  id: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  label: string;
  labelAr: string;
  path: string;
  badge?: number;
  activeColor?: string;
}

export default function MobileBottomNav() {
  const location = useLocation();
  const { getCartItemsCount } = useCart();
  const { favorites } = useFavorites();
  const { user } = useAuth();
  const { lang } = useLang();

  const cartCount = getCartItemsCount();
  const favoritesCount = favorites.length;

  const navItems: NavItem[] = [
    {
      id: 'home',
      icon: FiHome,
      label: 'Home',
      labelAr: 'الرئيسية',
      path: '/',
      activeColor: '#3b82f6'
    },
    {
      id: 'products',
      icon: FiGrid,
      label: 'Products',
      labelAr: 'المنتجات',
      path: '/products',
      activeColor: '#8b5cf6'
    },
    {
      id: 'favorites',
      icon: FiHeart,
      label: 'Favorites',
      labelAr: 'المفضلة',
      path: '/favorites',
      badge: favoritesCount,
      activeColor: '#ec4899'
    },
    {
      id: 'cart',
      icon: FiShoppingBag,
      label: 'Cart',
      labelAr: 'السلة',
      path: '/cart',
      badge: cartCount,
      activeColor: '#10b981'
    },
    {
      id: 'account',
      icon: FiUser,
      label: user ? 'Account' : 'Login',
      labelAr: user ? 'الحساب' : 'تسجيل الدخول',
      path: user ? '/account' : '/login',
      activeColor: '#f59e0b'
    }
  ];

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <>
      {/* Bottom Navigation */}
      <motion.nav
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        className="fixed bottom-0 left-0 right-0 z-40 md:hidden safe-area-bottom"
      >
        <div className="mobile-glass border-t border-border-primary px-2 py-1">
          <div className="flex items-center justify-around">
            {navItems.map((item) => {
              const active = isActive(item.path);
              const Icon = item.icon;
              const label = lang === 'ar' ? item.labelAr : item.label;

              return (
                <Link
                  key={item.id}
                  to={item.path}
                  className="relative flex flex-col items-center justify-center py-2 px-3 min-w-[60px] touch-target"
                >
                  {/* Active indicator */}
                  {active && (
                                      <motion.div
                    layoutId="activeTab"
                    className="absolute -top-1 left-1/2 w-8 h-1 rounded-full"
                    initial={false}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    style={{
                      x: '-50%',
                      backgroundColor: item.activeColor
                    }}
                  />
                  )}

                  {/* Icon with badge */}
                  <div className="relative mb-1">
                    <Icon 
                      size={20} 
                      className={clsx(
                        'transition-colors duration-200',
                        active 
                          ? 'text-primary' 
                          : 'text-gray-500 dark:text-gray-400'
                      )}
                    />
                    
                    {/* Badge */}
                    {item.badge && item.badge > 0 && (
                      <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center cart-badge"
                      >
                        {item.badge > 99 ? '99+' : item.badge}
                      </motion.span>
                    )}
                  </div>

                  {/* Label */}
                  <span 
                    className={clsx(
                      'text-xs font-medium transition-colors duration-200',
                      active 
                        ? 'text-primary' 
                        : 'text-gray-500 dark:text-gray-400'
                    )}
                  >
                    {label}
                  </span>

                  {/* Touch feedback */}
                  <motion.div
                    className="absolute inset-0 rounded-lg"
                    whileTap={{ 
                      backgroundColor: 'rgba(59, 130, 246, 0.1)',
                      scale: 0.95 
                    }}
                    transition={{ duration: 0.1 }}
                  />
                </Link>
              );
            })}
          </div>
        </div>
      </motion.nav>

      {/* Spacer for bottom navigation */}
      <div className="h-20 md:hidden" />
    </>
  );
}
