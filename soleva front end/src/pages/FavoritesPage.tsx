import React, { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiHeart, FiShoppingBag } from 'react-icons/fi';
import { useLang, useTranslation } from '../contexts/LangContext';
import { useFavorites } from '../contexts/FavoritesContext';
import { products } from '../data/products';
import GlassButton from '../components/GlassButton';
import GlassCard from '../components/GlassCard';
import SectionTitle from '../components/SectionTitle';
import FavoriteButton from '../components/FavoriteButton';

const FavoritesPage: React.FC = () => {
  const { lang } = useLang();
  const t = useTranslation();
  const { favorites } = useFavorites();

  const favoriteProducts = useMemo(() => 
    products.filter(product => favorites.includes(product.id)), 
    [favorites]
  );


  return (
    <div className="min-h-screen bg-app visual-hierarchy">
      <div className="container mx-auto px-4 py-6 sm:py-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-6 sm:mb-8"
        >
          <SectionTitle className="mb-3 sm:mb-4">
            {t('favorites')}
          </SectionTitle>
          {favoriteProducts.length > 0 && (
            <p className="text-base sm:text-lg text-gray-600 max-w-2xl mx-auto">
              {lang === 'ar' 
                ? `لديك ${favoriteProducts.length} منتج في المفضلة`
                : `You have ${favoriteProducts.length} item${favoriteProducts.length !== 1 ? 's' : ''} in your favorites`
              }
            </p>
          )}
        </motion.div>

        {favoriteProducts.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="text-center py-12 sm:py-16"
          >
            <GlassCard className="max-w-md mx-auto p-6 sm:p-8">
              <FiHeart className="w-16 h-16 mx-auto mb-4 text-[#d1b16a]" />
              <h3 className="text-lg sm:text-xl font-semibold mb-2 text-[#111]">
                {t('noFavoritesYet')}
              </h3>
              <p className="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6">
                {t('startAddingFavorites')}
              </p>
              <Link to="/products">
                <GlassButton className="bg-[#d1b16a] text-black border-none hover:bg-[#d1b16a]/80 text-sm sm:text-base">
                  <FiShoppingBag className="mr-2" />
                  {t('browseProducts')}
                </GlassButton>
              </Link>
            </GlassCard>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
           className="products-grid"
          >
            {favoriteProducts.map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -8, scale: 1.03 }}
               className="product-card group interactive-hover h-full"
              >
                <Link to={`/product/${product.id}`} className="block h-full">
                 <div className="product-card-image relative overflow-hidden">
                    <img
                      src={product.image}
                      alt={product.name[lang]}
                      className="w-full aspect-square object-cover transition-transform duration-700 group-hover:scale-115"
                      loading={index < 6 ? "eager" : "lazy"}
                      decoding="async"
                      width="300"
                      height="300"
                    />
                    <FavoriteButton productId={product.id} size={20} />
                  </div>
                  
                 <div className="product-card-content flex-1 flex flex-col">
                   <h3 className="product-card-title">
                      {product.name[lang]}
                    </h3>
                   <p className="product-card-description text-sm text-[var(--text-secondary)] mb-3 line-clamp-2 flex-1">
                      {product.desc[lang]}
                    </p>
                    <div className="flex items-center justify-between sm:flex-col sm:items-start sm:gap-3">
                     <span className="product-card-price">
                        {product.price} {t('egp')}
                      </span>
                     <div className="w-full">
                        <GlassButton 
                          variant="primary"
                          className="w-full text-[#000000]"
                        >
                          {t('viewDetails')}
                        </GlassButton>
                      </div>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default FavoritesPage;