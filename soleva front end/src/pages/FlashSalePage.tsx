import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiClock, FiZap, FiGrid, FiList, FiFilter, FiArrowLeft } from 'react-icons/fi';
import { useLang } from '../contexts/LangContext';
import { useFlashSale } from '../hooks/useOffers';
import { useCart } from '../contexts/CartContext';
import { useToast } from '../contexts/ToastContext';
import GlassCard from '../components/GlassCard';
import GlassButton from '../components/GlassButton';
import OptimizedImage from '../components/OptimizedImage';
import LoadingSkeleton from '../components/LoadingSkeleton';

export default function FlashSalePage() {
  const { id } = useParams<{ id: string }>();
  const { lang } = useLang();
  const { addToast } = useToast();
  const { addToCart, isUpdating } = useCart();
  
  const { flashSale, loading, error } = useFlashSale(id || '');
  
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'featured' | 'price_low' | 'price_high' | 'discount'>('featured');
  const [filterBy, setFilterBy] = useState<'all' | 'available' | 'limited'>('all');

  // Update countdown timer
  useEffect(() => {
    if (flashSale?.time_remaining) {
      setTimeRemaining(flashSale.time_remaining);
    }
  }, [flashSale]);

  useEffect(() => {
    if (timeRemaining <= 0 || !flashSale?.show_countdown) return;

    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeRemaining, flashSale?.show_countdown]);

  const formatTime = (seconds: number) => {
    if (seconds <= 0) return '00:00:00';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAddToCart = async (productId: string) => {
    try {
      const result = await addToCart({
        product_id: parseInt(productId),
        quantity: 1
      });

      if (result.success) {
        addToast(
          lang === 'ar' ? 'تم إضافة المنتج للسلة' : 'Product added to cart',
          'success'
        );
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
      addToast(
        lang === 'ar' ? 'خطأ في إضافة المنتج' : 'Error adding product',
        'error'
      );
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto py-10 px-4">
        <LoadingSkeleton />
      </div>
    );
  }

  if (error || !flashSale) {
    return (
      <div className="container mx-auto py-20 px-4 text-center">
        <h1 className="text-2xl font-bold mb-4">
          {lang === 'ar' ? 'عرض غير موجود' : 'Flash Sale Not Found'}
        </h1>
        <p className="text-gray-600 mb-6">
          {lang === 'ar' 
            ? 'هذا العرض غير متاح أو انتهت صلاحيته' 
            : 'This flash sale is not available or has expired'
          }
        </p>
        <Link to="/" className="text-[#d1b16a] hover:underline">
          {lang === 'ar' ? 'العودة للرئيسية' : 'Back to Home'}
        </Link>
      </div>
    );
  }

  const products = flashSale.products || [];
  
  // Filter products
  const filteredProducts = products.filter(product => {
    if (filterBy === 'available') return product.is_available;
    if (filterBy === 'limited') return product.quantity_limit && product.remaining_quantity;
    return true;
  });

  // Sort products
  const sortedProducts = [...filteredProducts].sort((a, b) => {
    switch (sortBy) {
      case 'featured':
        return b.is_featured ? 1 : -1;
      case 'price_low':
        return a.discounted_price - b.discounted_price;
      case 'price_high':
        return b.discounted_price - a.discounted_price;
      case 'discount':
        return b.discount_amount - a.discount_amount;
      default:
        return 0;
    }
  });

  const saleTitle = lang === 'ar' ? flashSale.name_ar : flashSale.name_en;
  const saleDescription = lang === 'ar' ? flashSale.description_ar : flashSale.description_en;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div 
        className="relative py-16 text-white"
        style={{ backgroundColor: flashSale.banner_color }}
      >
        {flashSale.banner_image && (
          <div className="absolute inset-0 opacity-20">
            <OptimizedImage
              src={flashSale.banner_image}
              alt={saleTitle}
              className="w-full h-full object-cover"
            />
          </div>
        )}
        
        <div className="relative z-10 container mx-auto px-4">
          {/* Back Button */}
          <Link
            to="/"
            className="inline-flex items-center gap-2 mb-6 text-white/80 hover:text-white transition-colors"
          >
            <FiArrowLeft className={lang === 'ar' ? 'rotate-180' : ''} />
            {lang === 'ar' ? 'العودة' : 'Back'}
          </Link>

          <div className="max-w-4xl">
            <div className="flex items-center gap-3 mb-4">
              <FiZap className="text-yellow-300" size={32} />
              <h1 
                className="text-4xl md:text-5xl font-bold"
                style={{ color: flashSale.text_color }}
              >
                {saleTitle}
              </h1>
            </div>

            {saleDescription && (
              <p 
                className="text-lg md:text-xl mb-6 opacity-90"
                style={{ color: flashSale.text_color }}
              >
                {saleDescription}
              </p>
            )}

            {/* Sale Status & Timer */}
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-1 px-3 py-1 bg-green-500 text-white rounded-full">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                <span className="text-sm font-medium">
                  {flashSale.is_running 
                    ? (lang === 'ar' ? 'نشط الآن' : 'LIVE NOW')
                    : flashSale.is_upcoming 
                    ? (lang === 'ar' ? 'قريباً' : 'COMING SOON')
                    : (lang === 'ar' ? 'انتهى' : 'ENDED')
                  }
                </span>
              </div>

              {flashSale.show_countdown && flashSale.is_running && timeRemaining > 0 && (
                <div className="flex items-center gap-2 px-4 py-2 bg-black/20 rounded-lg">
                  <FiClock />
                  <span className="font-mono text-lg font-bold">
                    {formatTime(timeRemaining)}
                  </span>
                  <span className="text-sm opacity-75">
                    {lang === 'ar' ? 'متبقي' : 'remaining'}
                  </span>
                </div>
              )}

              <div className="text-sm opacity-75">
                {products.length} {lang === 'ar' ? 'منتج في العرض' : 'products on sale'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="container mx-auto px-4 py-6">
        <GlassCard className="p-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            {/* View Mode */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'grid' 
                    ? 'bg-[#d1b16a] text-white' 
                    : 'hover:bg-gray-100'
                }`}
              >
                <FiGrid size={18} />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'list' 
                    ? 'bg-[#d1b16a] text-white' 
                    : 'hover:bg-gray-100'
                }`}
              >
                <FiList size={18} />
              </button>
            </div>

            {/* Filters & Sort */}
            <div className="flex items-center gap-4">
              {/* Filter */}
              <select
                value={filterBy}
                onChange={(e) => setFilterBy(e.target.value as any)}
                className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#d1b16a]"
              >
                <option value="all">
                  {lang === 'ar' ? 'جميع المنتجات' : 'All Products'}
                </option>
                <option value="available">
                  {lang === 'ar' ? 'متاح فقط' : 'Available Only'}
                </option>
                <option value="limited">
                  {lang === 'ar' ? 'كمية محدودة' : 'Limited Quantity'}
                </option>
              </select>

              {/* Sort */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#d1b16a]"
              >
                <option value="featured">
                  {lang === 'ar' ? 'المميزة أولاً' : 'Featured First'}
                </option>
                <option value="price_low">
                  {lang === 'ar' ? 'السعر: منخفض إلى مرتفع' : 'Price: Low to High'}
                </option>
                <option value="price_high">
                  {lang === 'ar' ? 'السعر: مرتفع إلى منخفض' : 'Price: High to Low'}
                </option>
                <option value="discount">
                  {lang === 'ar' ? 'أكبر خصم' : 'Biggest Discount'}
                </option>
              </select>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Products */}
      <div className="container mx-auto px-4 pb-10">
        {sortedProducts.length === 0 ? (
          <div className="text-center py-20">
            <FiFilter className="mx-auto text-gray-400 mb-4" size={48} />
            <h3 className="text-xl font-semibold mb-2">
              {lang === 'ar' ? 'لا توجد منتجات' : 'No Products Found'}
            </h3>
            <p className="text-gray-600">
              {lang === 'ar' 
                ? 'جرب تغيير المرشح أو العودة لاحقاً'
                : 'Try changing the filter or come back later'
              }
            </p>
          </div>
        ) : (
          <div className={`grid gap-6 ${
            viewMode === 'grid' 
              ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' 
              : 'grid-cols-1'
          }`}>
            {sortedProducts.map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <GlassCard className={`overflow-hidden ${viewMode === 'list' ? 'flex' : ''}`}>
                  {/* Product Image */}
                  <div className={`relative ${viewMode === 'list' ? 'w-48 flex-shrink-0' : 'aspect-square'}`}>
                    <Link to={`/product/${product.product}`}>
                      <OptimizedImage
                        src={product.product_image}
                        alt={lang === 'ar' ? product.product_name_ar : product.product_name}
                        className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                      />
                    </Link>
                    
                    {/* Badges */}
                    <div className="absolute top-3 left-3 flex flex-col gap-2">
                      {product.is_featured && (
                        <span className="px-2 py-1 bg-yellow-500 text-black text-xs font-bold rounded">
                          {lang === 'ar' ? 'مميز' : 'FEATURED'}
                        </span>
                      )}
                      <span className="px-2 py-1 bg-red-500 text-white text-xs font-bold rounded">
                        -{product.discount_type === 'percentage' 
                          ? `${product.discount_value}%` 
                          : `${product.discount_value} ${lang === 'ar' ? 'ج.م' : 'EGP'}`
                        }
                      </span>
                    </div>

                    {/* Stock Progress */}
                    {product.quantity_limit && (
                      <div className="absolute bottom-3 left-3 right-3">
                        <div className="bg-black/70 rounded-lg px-3 py-2">
                          <div className="text-white text-xs text-center mb-1">
                            {product.remaining_quantity} {lang === 'ar' ? 'متبقي' : 'left'}
                          </div>
                          <div className="w-full bg-gray-300 rounded-full h-2">
                            <div 
                              className="bg-red-500 h-2 rounded-full transition-all"
                              style={{ 
                                width: `${Math.max(0, Math.min(100, ((product.quantity_limit - (product.remaining_quantity || 0)) / product.quantity_limit) * 100))}%` 
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Product Info */}
                  <div className="p-4 flex-1">
                    <Link to={`/product/${product.product}`}>
                      <h3 className="font-semibold text-lg mb-2 hover:text-[#d1b16a] transition-colors line-clamp-2">
                        {lang === 'ar' ? product.product_name_ar : product.product_name}
                      </h3>
                    </Link>
                    
                    {/* Prices */}
                    <div className="flex items-center gap-3 mb-4">
                      <span className="text-2xl font-bold text-[#d1b16a]">
                        {product.discounted_price} {lang === 'ar' ? 'ج.م' : 'EGP'}
                      </span>
                      <span className="text-lg text-gray-500 line-through">
                        {product.original_price} {lang === 'ar' ? 'ج.م' : 'EGP'}
                      </span>
                    </div>

                    <div className="text-sm text-green-600 font-medium mb-4">
                      {lang === 'ar' ? 'توفر' : 'You save'} {product.discount_amount} {lang === 'ar' ? 'ج.م' : 'EGP'}
                    </div>

                    {/* Add to Cart */}
                    <GlassButton
                      onClick={() => handleAddToCart(product.product, product.discounted_price)}
                      disabled={!product.is_available || isUpdating}
                      className={`w-full ${
                        product.is_available 
                          ? 'bg-[#d1b16a] text-black hover:bg-[#d1b16a]/80' 
                          : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      }`}
                    >
                      {!product.is_available 
                        ? (lang === 'ar' ? 'غير متاح' : 'Out of Stock')
                        : isUpdating 
                        ? (lang === 'ar' ? 'جاري الإضافة...' : 'Adding...')
                        : (lang === 'ar' ? 'أضف للسلة' : 'Add to Cart')
                      }
                    </GlassButton>
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
