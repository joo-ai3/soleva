import React, { memo } from 'react';
import { motion } from 'framer-motion';
import { FiHeart, FiShoppingBag, FiEye } from 'react-icons/fi';
import { useCart } from '../contexts/CartContext';
import { useFavorites } from '../contexts/FavoritesContext';
import { useFlyingAnimationTrigger } from './FlyingAnimation';
import { useLang } from '../contexts/LangContext';
import OptimizedImage from './OptimizedImage';
import clsx from 'clsx';

interface Product {
  id: number;
  name: string;
  name_ar?: string;
  price: number;
  originalPrice?: number;
  image: string;
  slug: string;
  rating?: number;
  reviewCount?: number;
  inStock?: boolean;
  isNew?: boolean;
  discount?: number;
}

interface MobileProductGridProps {
  products: Product[];
  isLoading?: boolean;
  className?: string;
  onProductClick?: (product: Product) => void;
}

const ProductCardSkeleton = memo(() => (
  <div className="mobile-glass rounded-2xl p-4 animate-pulse">
    <div className="aspect-square bg-gray-200 dark:bg-gray-700 rounded-xl mb-3" />
    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2" />
    <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-2/3 mb-3" />
    <div className="flex justify-between items-center">
      <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
      <div className="h-8 w-8 bg-gray-200 dark:bg-gray-700 rounded-full" />
    </div>
  </div>
));

const ProductCard = memo(({ product, onProductClick }: { 
  product: Product; 
  onProductClick?: (product: Product) => void;
}) => {
  const { addToCart, isUpdating } = useCart();
  const { toggleFavorite, isFavorite, isUpdating: favoritesUpdating } = useFavorites();
  const { triggerAnimation } = useFlyingAnimationTrigger();
  const { lang } = useLang();

  const productName = lang === 'ar' && product.name_ar ? product.name_ar : product.name;
  const isProductFavorite = isFavorite(product.id);
  const discountPercent = product.originalPrice 
    ? Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)
    : product.discount;

  const handleAddToCart = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    const button = e.currentTarget;
    
    const result = await addToCart({
      product_id: product.id,
      quantity: 1,
      triggerElement: button,
      productImage: product.image
    });

    if (result.success) {
      triggerAnimation('cart', button, product.image);
    }
  };

  const handleToggleFavorite = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    const button = e.currentTarget;
    
    const result = await toggleFavorite(product.id, button, product.image);
    
    if (result.success && !isProductFavorite) {
      triggerAnimation('favorite', button, product.image);
    }
  };

  const handleProductClick = () => {
    onProductClick?.(product);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
      className="mobile-glass rounded-2xl p-4 cursor-pointer relative group"
      onClick={handleProductClick}
    >
      {/* Product Image */}
      <div className="relative aspect-square mb-3 overflow-hidden rounded-xl">
        <OptimizedImage
          src={product.image}
          alt={productName}
          className="w-full h-full object-cover mobile-product-image"
          highResolution={true}
          lazyLoad={true}
        />
        
        {/* Badges */}
        <div className="absolute top-2 left-2 flex flex-col gap-1">
          {product.isNew && (
            <span className="bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-full">
              {lang === 'ar' ? 'جديد' : 'New'}
            </span>
          )}
          {discountPercent && discountPercent > 0 && (
            <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
              -{discountPercent}%
            </span>
          )}
        </div>

        {/* Actions Overlay */}
        <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center gap-2">
          <button
            onClick={handleToggleFavorite}
            disabled={favoritesUpdating}
            className={clsx(
              'p-2 rounded-full backdrop-blur-sm transition-all duration-200',
              isProductFavorite 
                ? 'bg-pink-500 text-white' 
                : 'bg-white/90 text-gray-700 hover:bg-pink-500 hover:text-white'
            )}
          >
            <FiHeart size={16} fill={isProductFavorite ? 'currentColor' : 'none'} />
          </button>
          
          <button
            onClick={(e) => e.stopPropagation()}
            className="p-2 rounded-full bg-white/90 text-gray-700 hover:bg-blue-500 hover:text-white backdrop-blur-sm transition-all duration-200"
          >
            <FiEye size={16} />
          </button>
        </div>
      </div>

      {/* Product Info */}
      <div className="space-y-2">
        {/* Product Name */}
        <h3 className="mobile-product-title text-text-primary font-semibold leading-tight line-clamp-2">
          {productName}
        </h3>

        {/* Rating */}
        {product.rating && (
          <div className="flex items-center gap-1">
            <div className="flex">
              {[...Array(5)].map((_, i) => (
                <span 
                  key={i} 
                  className={clsx(
                    'text-xs',
                    i < Math.floor(product.rating!) ? 'text-yellow-400' : 'text-gray-300'
                  )}
                >
                  ★
                </span>
              ))}
            </div>
            {product.reviewCount && (
              <span className="text-xs text-gray-500">({product.reviewCount})</span>
            )}
          </div>
        )}

        {/* Price and Add to Cart */}
        <div className="flex items-center justify-between">
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="mobile-product-price font-bold text-primary">
                {product.price} {lang === 'ar' ? 'ج.م' : 'EGP'}
              </span>
              {product.originalPrice && (
                <span className="text-sm text-gray-500 line-through">
                  {product.originalPrice}
                </span>
              )}
            </div>
            {!product.inStock && (
              <span className="text-xs text-red-500 font-medium">
                {lang === 'ar' ? 'غير متوفر' : 'Out of Stock'}
              </span>
            )}
          </div>

          <button
            onClick={handleAddToCart}
            disabled={isUpdating || !product.inStock}
            className={clsx(
              'p-2 rounded-full transition-all duration-200 touch-target',
              product.inStock
                ? 'bg-primary hover:bg-primary-dark text-black hover:scale-110'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            )}
          >
            <FiShoppingBag size={16} />
          </button>
        </div>
      </div>
    </motion.div>
  );
});

export default function MobileProductGrid({ 
  products, 
  isLoading = false, 
  className = '',
  onProductClick 
}: MobileProductGridProps) {
  if (isLoading) {
    return (
      <div className={clsx('grid grid-cols-2 gap-4 p-4', className)}>
        {[...Array(6)].map((_, index) => (
          <ProductCardSkeleton key={index} />
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4">
        <div className="w-24 h-24 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center mb-4">
          <FiShoppingBag size={32} className="text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-text-primary mb-2">
          No Products Found
        </h3>
        <p className="text-text-secondary text-center">
          We couldn't find any products matching your criteria.
        </p>
      </div>
    );
  }

  return (
    <div className={clsx('grid grid-cols-2 gap-4 p-4', className)}>
      {products.map((product, index) => (
        <motion.div
          key={product.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1, duration: 0.3 }}
        >
          <ProductCard 
            product={product} 
            onProductClick={onProductClick}
          />
        </motion.div>
      ))}
    </div>
  );
}

ProductCard.displayName = 'ProductCard';
ProductCardSkeleton.displayName = 'ProductCardSkeleton';
