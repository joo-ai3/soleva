import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FiHeart } from 'react-icons/fi';
import { useFavorites } from '../contexts/FavoritesContext';
import { useToast } from '../contexts/ToastContext';
import { useTheme } from '../contexts/ThemeContext';
import { useTranslation } from '../contexts/LangContext';
import clsx from 'clsx';

interface FavoriteButtonProps {
  productId: number;
  className?: string;
  size?: number;
  showToast?: boolean;
}

export default function FavoriteButton({ 
  productId, 
  className = '', 
  size = 20, 
  showToast: showToastProp = true 
}: FavoriteButtonProps) {
  const { isFavorite, toggleFavorite } = useFavorites();
  const { showToast } = useToast();
  const { theme } = useTheme();
  const t = useTranslation();
  const [isAnimating, setIsAnimating] = useState(false);

  const isCurrentlyFavorite = isFavorite(productId);

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    setIsAnimating(true);
    toggleFavorite(productId);
    
    if (showToastProp) {
      const message = isCurrentlyFavorite ? t("removeFromFavorites") : t("addToFavorites");
      showToast(message);
    }
    
    setTimeout(() => setIsAnimating(false), 400);
  };

  return (
    <motion.button
      onClick={handleClick}
      className={clsx(
        'favorite-btn relative overflow-hidden group',
        {
          'active': isCurrentlyFavorite,
          'animate-heart-beat': isAnimating
        },
        className
      )}
      whileTap={{ scale: 0.85 }}
      whileHover={{ scale: 1.15 }}
      transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
      aria-label={isCurrentlyFavorite ? t("removeFromFavorites") : t("addToFavorites")}
      style={{
        width: size * 2.2,
        height: size * 2.2,
        background: isCurrentlyFavorite 
          ? 'linear-gradient(135deg, #ef4444, #dc2626)' 
          : theme === 'dark' 
            ? 'rgba(10, 10, 10, 0.95)' 
            : 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(25px) saturate(200%)',
        WebkitBackdropFilter: 'blur(25px) saturate(200%)',
        border: isCurrentlyFavorite 
          ? '2px solid #ef4444' 
          : theme === 'dark'
            ? '2px solid rgba(209, 177, 106, 0.5)'
            : '2px solid rgba(209, 177, 106, 0.4)',
        borderRadius: '50%',
        boxShadow: isCurrentlyFavorite
          ? '0 12px 30px rgba(239, 68, 68, 0.5), 0 0 0 1px rgba(239, 68, 68, 0.3)'
          : theme === 'dark'
            ? '0 12px 30px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(209, 177, 106, 0.3)'
            : '0 12px 30px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(209, 177, 106, 0.25)',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
      }}
    >
      {/* Animated Background Gradient */}
      <div 
        className={clsx(
          "absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 transition-all duration-300",
          isCurrentlyFavorite 
            ? "bg-gradient-to-br from-red-400/30 to-red-600/30 animate-pulse-glow" 
            : theme === 'dark'
              ? "bg-gradient-to-br from-[#d1b16a]/30 to-[#d1b16a]/15"
              : "bg-gradient-to-br from-[#d1b16a]/20 to-[#d1b16a]/10"
        )}
      />
      
      {/* Ripple Effect */}
      <div 
        className={clsx(
          "absolute inset-0 rounded-full opacity-0 group-active:opacity-100 transition-all duration-150",
          isCurrentlyFavorite 
            ? "bg-red-500/40" 
            : theme === 'dark'
              ? "bg-[#d1b16a]/40"
              : "bg-[#d1b16a]/30"
        )}
      />

      <motion.div
        animate={{
          scale: isAnimating ? [1, 1.4, 1] : 1,
          rotate: isAnimating ? [0, -15, 15, 0] : 0,
        }}
        transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
        className="relative z-10 flex items-center justify-center w-full h-full"
      >
        <FiHeart 
          size={size} 
          className={clsx(
            'transition-all duration-300 drop-shadow-sm',
            isCurrentlyFavorite 
              ? 'fill-current text-white' 
              : theme === 'dark'
                ? 'text-gray-200 group-hover:text-[#d1b16a]'
                : 'text-gray-600 group-hover:text-[#d1b16a]'
          )}
          style={{
            filter: isCurrentlyFavorite 
              ? 'drop-shadow(0 3px 6px rgba(0, 0, 0, 0.3))' 
              : theme === 'dark'
                ? 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.5))'
                : 'drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1))'
          }}
        />
      </motion.div>

      {/* Pulse Animation for Active State */}
      {isCurrentlyFavorite && (
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-red-400/60"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.6, 0, 0.6],
          }}
          transition={{
            duration: 2.5,
            repeat: Infinity,
            ease: "easeInOut",
            repeatDelay: 0.5
          }}
        />
      )}
    </motion.button>
  );
}