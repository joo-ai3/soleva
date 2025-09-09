
import { Link, useLocation, useNavigate } from 'react-router-dom';

import { FiShoppingCart, FiUser, FiMoon, FiSun, FiHeart } from 'react-icons/fi';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';
import { useFavorites } from '../contexts/FavoritesContext';
import { useTheme } from '../contexts/ThemeContext';
import { useLang, useTranslation } from '../contexts/LangContext';
import Logo from './Logo';
import MobileMenu from './MobileMenu';
import clsx from 'clsx';


export default function AppHeader() {
  const { lang, setLang } = useLang();
  const { theme, setTheme } = useTheme();
  const { user } = useAuth();
  const { cart } = useCart();
  const { favorites } = useFavorites();
  const t = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();


  const toggleTheme = () => setTheme(theme === "dark" ? "light" : "dark");
  const toggleLang = () => setLang(lang === "ar" ? "en" : "ar");

  const handleCollectionClick = (collection: string) => {
    const currentPath = location.pathname;
    const newPath = `/products?collection=${collection}`;
    
    if (currentPath !== '/products' || !location.search.includes(`collection=${collection}`)) {
      navigate(newPath);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  const navLinks = [
    { to: '/', label: t('home') },
    { 
      to: null, 
      label: t('collections'), 
      isDropdown: true,
      subItems: [
        { collection: 'mens', label: lang === 'ar' ? 'رجالي' : 'Men' },
        { collection: 'womens', label: lang === 'ar' ? 'نسائي' : 'Women' },
        { collection: 'youth', label: lang === 'ar' ? 'شبابي' : 'Youth' },
        { collection: 'kids', label: lang === 'ar' ? 'أطفالي' : 'Kids' },
        { collection: 'basics', label: lang === 'ar' ? 'أساسي' : 'Essentials' },
        { collection: 'all', label: lang === 'ar' ? 'الكل' : 'All' },
      ]
    },
    { to: '/about', label: t('aboutUs') },
    { to: '/contact', label: t('contactUs') }
  ];

  const isActiveLink = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <header className="nav" role="banner" aria-label="Main navigation">
      <div className="nav-container">
        {/* Logo */}
        <Logo size="medium" />

        {/* Desktop Navigation */}
        <nav className="nav-links hidden md:flex" role="navigation">
          {navLinks.map((link) => (
            <div key={link.to || link.label} className="relative group">
              {link.isDropdown ? (
                <>
                  <button
                    className="nav-link flex items-center gap-1"
                    aria-expanded="false"
                  >
                    {link.label}
                    <svg className="w-4 h-4 transition-transform group-hover:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {/* Dropdown Menu */}
                  <div className="absolute top-full left-0 mt-2 w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 z-50">
                    <div className="modern-glass-card rounded-xl shadow-xl border border-border-primary overflow-hidden">
                      {link.subItems?.map((subItem) => (
                        <button
                          key={subItem.collection}
                          onClick={() => handleCollectionClick(subItem.collection)}
                          className={clsx(
                            'block w-full text-left px-4 py-3 text-sm font-medium transition-colors hover:bg-primary hover:text-black',
                            location.search.includes(`collection=${subItem.collection}`) ? 'bg-primary text-black' : 'text-text-primary'
                          )}
                        >
                          {subItem.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </>
              ) : (
                <Link
                  to={link.to!}
                  onClick={() => window.scrollTo({ top: 0, behavior: 'instant' })}
                  className={clsx(
                    'nav-link',
                    isActiveLink(link.to!) && 'text-primary bg-primary-50'
                  )}
                  aria-current={isActiveLink(link.to!) ? 'page' : undefined}
                >
                  {link.label}
                </Link>
              )}
            </div>
          ))}
        </nav>

        {/* Actions */}
        <div className="nav-actions">
          {/* Favorites - Desktop */}
          <Link 
            to="/favorites" 
            className="hidden md:flex nav-link relative"
            aria-label={`${t("favorites")} ${favorites.length > 0 ? `(${favorites.length} items)` : ''}`}
          >
            <FiHeart size={20} />
            {favorites.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-5 h-5 text-xs font-bold flex items-center justify-center" aria-hidden="true">
                {favorites.length}
              </span>
            )}
          </Link>

          {/* Cart - Desktop */}
          <Link 
            to="/cart" 
            className="hidden md:flex nav-link relative"
            aria-label={`${t("cart")} ${cart.length > 0 ? `(${cart.length} items)` : ''}`}
          >
            <FiShoppingCart size={20} />
            {cart.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-primary text-black rounded-full w-5 h-5 text-xs font-bold flex items-center justify-center" aria-hidden="true">
                {cart.length}
              </span>
            )}
          </Link>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="btn btn-ghost p-3 interactive-hover min-h-[44px] min-w-[44px]"
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
          >
            {theme === "dark" ? <FiSun size={20} /> : <FiMoon size={20} />}
          </button>

          {/* Language Toggle */}
          <button
            onClick={toggleLang}
            className="btn btn-ghost px-4 py-3 text-base font-bold interactive-hover min-h-[44px]"
            aria-label={`Switch to ${lang === "ar" ? "English" : "Arabic"} language`}
          >
            {lang === "ar" ? "EN" : "AR"}
          </button>

          {/* Account - Desktop */}
          <Link
            to={user ? "/account" : "/login"}
            className="hidden md:flex btn btn-ghost p-3 interactive-hover min-h-[44px] min-w-[44px]"
            aria-label={user ? t("account") : t("login")}
          >
            <FiUser size={20} />
          </Link>

          {/* Mobile Menu Toggle */}
          <MobileMenu />
        </div>
      </div>

    </header>
  );
}