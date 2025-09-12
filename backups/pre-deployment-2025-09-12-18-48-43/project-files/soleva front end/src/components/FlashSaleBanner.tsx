import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiZap, FiClock, FiArrowRight, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import { Link } from 'react-router-dom';
import { useLang } from '../contexts/LangContext';
import OptimizedImage from './OptimizedImage';

interface FlashSale {
  id: string;
  name_en: string;
  name_ar: string;
  description_en: string;
  description_ar: string;
  banner_image?: string;
  banner_color: string;
  text_color: string;
  time_remaining: number;
  show_countdown: boolean;
  is_running: boolean;
  products_count: number;
}

interface FlashSaleBannerProps {
  flashSales: FlashSale[];
  autoPlay?: boolean;
  autoPlayInterval?: number;
}

export default function FlashSaleBanner({ 
  flashSales, 
  autoPlay = true, 
  autoPlayInterval = 5000 
}: FlashSaleBannerProps) {
  const { lang } = useLang();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState<{ [key: string]: number }>({});

  // Initialize time remaining for all flash sales
  useEffect(() => {
    const initialTimes: { [key: string]: number } = {};
    flashSales.forEach(sale => {
      initialTimes[sale.id] = sale.time_remaining;
    });
    setTimeRemaining(initialTimes);
  }, [flashSales]);

  // Update countdown timers
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        const updated = { ...prev };
        Object.keys(updated).forEach(saleId => {
          if (updated[saleId] > 0) {
            updated[saleId] -= 1;
          }
        });
        return updated;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Auto-play functionality
  useEffect(() => {
    if (!autoPlay || flashSales.length <= 1) return;

    const timer = setInterval(() => {
      setCurrentIndex(prev => (prev + 1) % flashSales.length);
    }, autoPlayInterval);

    return () => clearInterval(timer);
  }, [autoPlay, autoPlayInterval, flashSales.length]);

  const formatTime = (seconds: number) => {
    if (seconds <= 0) return '00:00:00';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const nextSlide = () => {
    setCurrentIndex(prev => (prev + 1) % flashSales.length);
  };

  const prevSlide = () => {
    setCurrentIndex(prev => (prev - 1 + flashSales.length) % flashSales.length);
  };

  if (!flashSales.length) return null;

  const currentSale = flashSales[currentIndex];
  const saleTitle = lang === 'ar' ? currentSale.name_ar : currentSale.name_en;
  const saleDescription = lang === 'ar' ? currentSale.description_ar : currentSale.description_en;
  const currentTimeRemaining = timeRemaining[currentSale.id] || 0;

  return (
    <div className="relative w-full overflow-hidden rounded-xl shadow-lg">
      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -100 }}
          transition={{ duration: 0.5 }}
          className="relative h-64 md:h-80 lg:h-96"
          style={{ backgroundColor: currentSale.banner_color }}
        >
          {/* Background Image */}
          {currentSale.banner_image && (
            <div className="absolute inset-0">
              <OptimizedImage
                src={currentSale.banner_image}
                alt={saleTitle}
                className="w-full h-full object-cover opacity-30"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-black/50 to-transparent" />
            </div>
          )}

          {/* Content */}
          <div className="relative z-10 h-full flex items-center">
            <div className="container mx-auto px-4 md:px-6 lg:px-8">
              <div className="max-w-2xl">
                {/* Flash Sale Header */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="flex items-center gap-3 mb-4"
                >
                  <div className="flex items-center gap-2 px-3 py-1 bg-yellow-400 text-black rounded-full">
                    <FiZap size={16} />
                    <span className="font-bold text-sm">
                      {lang === 'ar' ? 'عرض برق' : 'FLASH SALE'}
                    </span>
                  </div>
                  
                  {currentSale.is_running && (
                    <div className="flex items-center gap-1 px-2 py-1 bg-green-500 text-white rounded-full">
                      <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                      <span className="text-xs font-medium">
                        {lang === 'ar' ? 'مباشر' : 'LIVE'}
                      </span>
                    </div>
                  )}
                </motion.div>

                {/* Title */}
                <motion.h2
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4"
                  style={{ color: currentSale.text_color }}
                >
                  {saleTitle}
                </motion.h2>

                {/* Description */}
                {saleDescription && (
                  <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="text-lg md:text-xl mb-6 opacity-90"
                    style={{ color: currentSale.text_color }}
                  >
                    {saleDescription}
                  </motion.p>
                )}

                {/* Countdown Timer */}
                {currentSale.show_countdown && currentSale.is_running && currentTimeRemaining > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="flex items-center gap-4 mb-6 p-4 bg-black/20 rounded-lg backdrop-blur-sm"
                  >
                    <FiClock className="text-2xl" style={{ color: currentSale.text_color }} />
                    <div>
                      <div className="text-sm opacity-75" style={{ color: currentSale.text_color }}>
                        {lang === 'ar' ? 'ينتهي خلال' : 'Ends in'}
                      </div>
                      <div className="font-mono text-2xl font-bold" style={{ color: currentSale.text_color }}>
                        {formatTime(currentTimeRemaining)}
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Action Button */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                >
                  <Link
                    to={`/flash-sale/${currentSale.id}`}
                    className="inline-flex items-center gap-3 px-8 py-4 bg-white text-black rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors shadow-lg"
                  >
                    {lang === 'ar' ? 'تسوق الآن' : 'Shop Now'}
                    <FiArrowRight size={20} className={lang === 'ar' ? 'rotate-180' : ''} />
                  </Link>
                </motion.div>

                {/* Products Count */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 }}
                  className="mt-4 text-sm opacity-75"
                  style={{ color: currentSale.text_color }}
                >
                  {currentSale.products_count} {lang === 'ar' ? 'منتج في العرض' : 'products on sale'}
                </motion.div>
              </div>
            </div>
          </div>

          {/* Navigation Arrows */}
          {flashSales.length > 1 && (
            <>
              <button
                onClick={prevSlide}
                className="absolute left-4 top-1/2 -translate-y-1/2 z-20 p-2 bg-black/30 hover:bg-black/50 text-white rounded-full transition-colors"
                aria-label="Previous slide"
              >
                <FiChevronLeft size={24} />
              </button>
              <button
                onClick={nextSlide}
                className="absolute right-4 top-1/2 -translate-y-1/2 z-20 p-2 bg-black/30 hover:bg-black/50 text-white rounded-full transition-colors"
                aria-label="Next slide"
              >
                <FiChevronRight size={24} />
              </button>
            </>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Dots Indicator */}
      {flashSales.length > 1 && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 flex gap-2">
          {flashSales.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`w-3 h-3 rounded-full transition-colors ${
                index === currentIndex 
                  ? 'bg-white' 
                  : 'bg-white/50 hover:bg-white/75'
              }`}
              aria-label={`Go to slide ${index + 1}`}
            />
          ))}
        </div>
      )}
    </div>
  );
}