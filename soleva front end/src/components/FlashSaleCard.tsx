import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiClock, FiZap, FiEye } from 'react-icons/fi';
import { Link } from 'react-router-dom';
import { useLang } from '../contexts/LangContext';
import OptimizedImage from './OptimizedImage';

interface FlashSaleProduct {
  id: string;
  product: string;
  product_name: string;
  product_name_ar: string;
  product_image: string;
  discount_type: 'percentage' | 'fixed_amount';
  discount_value: number;
  original_price: number;
  discounted_price: number;
  discount_amount: number;
  quantity_limit?: number;
  sold_quantity: number;
  remaining_quantity?: number;
  is_featured: boolean;
  is_available: boolean;
}

interface FlashSale {
  id: string;
  name_en: string;
  name_ar: string;
  description_en: string;
  description_ar: string;
  start_time: string;
  end_time: string;
  banner_image?: string;
  banner_color: string;
  text_color: string;
  display_priority: number;
  show_countdown: boolean;
  is_running: boolean;
  is_upcoming: boolean;
  is_expired: boolean;
  time_remaining: number;
  products: FlashSaleProduct[];
}

interface FlashSaleCardProps {
  flashSale: FlashSale;
  compact?: boolean;
}

export default function FlashSaleCard({ flashSale, compact = false }: FlashSaleCardProps) {
  const { lang } = useLang();
  const [timeRemaining, setTimeRemaining] = useState(flashSale.time_remaining);

  useEffect(() => {
    if (!flashSale.show_countdown || timeRemaining <= 0) return;

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
  }, [flashSale.show_countdown, timeRemaining]);

  const formatTime = (seconds: number) => {
    if (seconds <= 0) return '00:00:00';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusInfo = () => {
    if (flashSale.is_expired || timeRemaining <= 0) {
      return {
        status: lang === 'ar' ? 'انتهى العرض' : 'Sale Ended',
        color: 'text-red-500',
        bgColor: 'bg-red-100'
      };
    }
    
    if (flashSale.is_upcoming) {
      return {
        status: lang === 'ar' ? 'قريباً' : 'Coming Soon',
        color: 'text-orange-500',
        bgColor: 'bg-orange-100'
      };
    }
    
    if (flashSale.is_running) {
      return {
        status: lang === 'ar' ? 'نشط الآن' : 'Live Now',
        color: 'text-green-500',
        bgColor: 'bg-green-100'
      };
    }

    return {
      status: lang === 'ar' ? 'غير نشط' : 'Inactive',
      color: 'text-gray-500',
      bgColor: 'bg-gray-100'
    };
  };

  const statusInfo = getStatusInfo();
  const saleTitle = lang === 'ar' ? flashSale.name_ar : flashSale.name_en;
  const saleDescription = lang === 'ar' ? flashSale.description_ar : flashSale.description_en;
  const featuredProducts = flashSale.products.filter(p => p.is_featured).slice(0, 3);
  const totalProducts = flashSale.products.length;

  if (compact) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ y: -2 }}
        className="glass rounded-xl overflow-hidden border border-[#d1b16a]/20"
        style={{ 
          backgroundColor: `${flashSale.banner_color}15`,
          borderColor: `${flashSale.banner_color}40`
        }}
      >
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <FiZap className="text-orange-500" size={16} />
              <span className="font-bold text-sm" style={{ color: flashSale.text_color }}>
                {saleTitle}
              </span>
            </div>
            <span 
              className={`px-2 py-1 rounded-full text-xs font-medium ${statusInfo.bgColor} ${statusInfo.color}`}
            >
              {statusInfo.status}
            </span>
          </div>

          {flashSale.show_countdown && flashSale.is_running && timeRemaining > 0 && (
            <div className="flex items-center justify-center mb-3 p-2 bg-black/10 rounded-lg">
              <FiClock className="mr-2" size={14} />
              <span className="font-mono text-sm font-bold">
                {formatTime(timeRemaining)}
              </span>
            </div>
          )}

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">
              {totalProducts} {lang === 'ar' ? 'منتج' : 'products'}
            </span>
            <Link
              to={`/flash-sale/${flashSale.id}`}
              className="text-sm font-medium text-[#d1b16a] hover:underline"
            >
              {lang === 'ar' ? 'عرض الكل' : 'View All'}
            </Link>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      className="glass rounded-xl overflow-hidden border border-[#d1b16a]/20 shadow-lg"
      style={{ 
        backgroundColor: `${flashSale.banner_color}10`,
        borderColor: `${flashSale.banner_color}30`
      }}
    >
      {/* Header */}
      <div 
        className="relative p-6 text-white"
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
        
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <FiZap className="text-yellow-300" size={24} />
              <h3 className="text-xl font-bold" style={{ color: flashSale.text_color }}>
                {saleTitle}
              </h3>
            </div>
            <span 
              className={`px-3 py-1 rounded-full text-sm font-medium ${statusInfo.bgColor} ${statusInfo.color}`}
            >
              {statusInfo.status}
            </span>
          </div>

          {saleDescription && (
            <p className="text-sm opacity-90 mb-4" style={{ color: flashSale.text_color }}>
              {saleDescription}
            </p>
          )}

          {/* Countdown Timer */}
          {flashSale.show_countdown && flashSale.is_running && timeRemaining > 0 && (
            <div className="flex items-center justify-center p-3 bg-black/20 rounded-lg">
              <FiClock className="mr-2" />
              <span className="font-mono text-lg font-bold">
                {formatTime(timeRemaining)}
              </span>
              <span className="ml-2 text-sm opacity-75">
                {lang === 'ar' ? 'متبقي' : 'remaining'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Featured Products */}
      {featuredProducts.length > 0 && (
        <div className="p-6">
          <h4 className="font-semibold mb-4 text-gray-800">
            {lang === 'ar' ? 'منتجات مميزة' : 'Featured Products'}
          </h4>
          
          <div className="grid grid-cols-3 gap-4 mb-4">
            {featuredProducts.map((product) => (
              <Link
                key={product.id}
                to={`/product/${product.product}`}
                className="group"
              >
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  className="bg-white rounded-lg overflow-hidden border border-gray-200 group-hover:border-[#d1b16a] transition-colors"
                >
                  <div className="aspect-square relative">
                    <OptimizedImage
                      src={product.product_image}
                      alt={lang === 'ar' ? product.product_name_ar : product.product_name}
                      className="w-full h-full object-cover"
                    />
                    
                    {/* Discount Badge */}
                    <div className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold">
                      -{product.discount_type === 'percentage' 
                        ? `${product.discount_value}%` 
                        : `${product.discount_value} ${lang === 'ar' ? 'ج.م' : 'EGP'}`
                      }
                    </div>

                    {/* Stock Progress */}
                    {product.quantity_limit && (
                      <div className="absolute bottom-2 left-2 right-2">
                        <div className="bg-black/50 rounded-full px-2 py-1">
                          <div className="text-white text-xs text-center mb-1">
                            {product.remaining_quantity} {lang === 'ar' ? 'متبقي' : 'left'}
                          </div>
                          <div className="w-full bg-gray-300 rounded-full h-1">
                            <div 
                              className="bg-red-500 h-1 rounded-full"
                              style={{ 
                                width: `${((product.quantity_limit - (product.remaining_quantity || 0)) / product.quantity_limit) * 100}%` 
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="p-3">
                    <h5 className="font-medium text-sm line-clamp-2 mb-2">
                      {lang === 'ar' ? product.product_name_ar : product.product_name}
                    </h5>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-lg font-bold text-[#d1b16a]">
                          {product.discounted_price} {lang === 'ar' ? 'ج.م' : 'EGP'}
                        </span>
                        <span className="text-sm text-gray-500 line-through ml-2">
                          {product.original_price}
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </Link>
            ))}
          </div>

          {/* View All Button */}
          <div className="text-center">
            <Link
              to={`/flash-sale/${flashSale.id}`}
              className="inline-flex items-center gap-2 px-6 py-3 bg-[#d1b16a] text-black rounded-lg font-medium hover:bg-[#d1b16a]/80 transition-colors"
            >
              <FiEye size={16} />
              {lang === 'ar' ? `عرض جميع المنتجات (${totalProducts})` : `View All Products (${totalProducts})`}
            </Link>
          </div>
        </div>
      )}
    </motion.div>
  );
}
