import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiGift, FiClock, FiTruck, FiTag, FiX, FiCheck } from 'react-icons/fi';
import { useLang } from '../contexts/LangContext';
import { useCart } from '../contexts/CartContext';
import GlassButton from './GlassButton';
import GlassCard from './GlassCard';

interface SpecialOffer {
  id: string;
  name_en: string;
  name_ar: string;
  offer_type: 'buy_x_get_y_free' | 'buy_x_get_discount' | 'buy_x_free_shipping' | 'bundle_discount';
  buy_quantity: number;
  free_quantity: number;
  discount_type: 'percentage' | 'fixed_amount';
  discount_value: number;
  button_text_en: string;
  button_text_ar: string;
  button_color: string;
  highlight_color: string;
  time_remaining?: number;
  show_timer: boolean;
  is_running: boolean;
}

interface SpecialOfferButtonProps {
  offers: SpecialOffer[];
  productId: string;
  productPrice: number;
  onOfferActivate: (offer: SpecialOffer) => void;
}

export default function SpecialOfferButton({ 
  offers, 
  productId, 
  onOfferActivate 
}: SpecialOfferButtonProps) {
  const { lang } = useLang();
  const { cart } = useCart();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedOffer, setSelectedOffer] = useState<SpecialOffer | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<{ [key: string]: number }>({});

  const runningOffers = offers.filter(offer => offer.is_running);

  // Initialize time remaining for all offers
  useEffect(() => {
    const initialTimes: { [key: string]: number } = {};
    runningOffers.forEach(offer => {
      if (offer.time_remaining) {
        initialTimes[offer.id] = offer.time_remaining;
      }
    });
    setTimeRemaining(initialTimes);
  }, [runningOffers]);

  // Update countdown timers
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        const updated = { ...prev };
        Object.keys(updated).forEach(offerId => {
          if (updated[offerId] > 0) {
            updated[offerId] -= 1;
          }
        });
        return updated;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds: number) => {
    if (seconds <= 0) return '00:00:00';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getOfferDescription = (offer: SpecialOffer) => {
    const prefix = lang === 'ar' ? offer.name_ar : offer.name_en;
    
    switch (offer.offer_type) {
      case 'buy_x_get_y_free':
        return lang === 'ar' 
          ? `اشتري ${offer.buy_quantity} واحصل على ${offer.free_quantity} مجاناً`
          : `Buy ${offer.buy_quantity} Get ${offer.free_quantity} Free`;
      
      case 'buy_x_get_discount': {
        const discountText = offer.discount_type === 'percentage' 
          ? `${offer.discount_value}%` 
          : `${offer.discount_value} ${lang === 'ar' ? 'ج.م' : 'EGP'}`;
        return lang === 'ar' 
          ? `اشتري ${offer.buy_quantity} واحصل على خصم ${discountText}`
          : `Buy ${offer.buy_quantity} Get ${discountText} Off`;
      }
      
      case 'buy_x_free_shipping':
        return lang === 'ar' 
          ? `اشتري ${offer.buy_quantity} واحصل على شحن مجاني`
          : `Buy ${offer.buy_quantity} Get Free Shipping`;
      
      case 'bundle_discount': {
        const bundleDiscountText = offer.discount_type === 'percentage' 
          ? `${offer.discount_value}%` 
          : `${offer.discount_value} ${lang === 'ar' ? 'ج.م' : 'EGP'}`;
        return lang === 'ar' 
          ? `عرض حزمة: خصم ${bundleDiscountText}`
          : `Bundle Deal: ${bundleDiscountText} Off`;
      }
      
      default:
        return prefix;
    }
  };

  const getOfferIcon = (offerType: string) => {
    switch (offerType) {
      case 'buy_x_get_y_free':
        return <FiGift className="text-green-500" />;
      case 'buy_x_get_discount':
        return <FiTag className="text-red-500" />;
      case 'buy_x_free_shipping':
        return <FiTruck className="text-blue-500" />;
      case 'bundle_discount':
        return <FiTag className="text-purple-500" />;
      default:
        return <FiGift className="text-green-500" />;
    }
  };

  const handleOfferSelect = (offer: SpecialOffer) => {
    setSelectedOffer(offer);
    setIsModalOpen(true);
  };

  const handleActivateOffer = () => {
    if (selectedOffer) {
      onOfferActivate(selectedOffer);
      setIsModalOpen(false);
      setSelectedOffer(null);
    }
  };

  const currentProductQuantity = cart.find(item => item.product_id === Number(productId))?.quantity || 0;

  if (!runningOffers.length) return null;

  // Show the best offer as the main button
  const mainOffer = runningOffers[0];
  const currentTime = timeRemaining[mainOffer.id] || 0;

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-3"
      >
        {/* Main Offer Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => handleOfferSelect(mainOffer)}
          className="w-full p-4 rounded-xl border-2 text-left transition-all"
          style={{ 
            backgroundColor: `${mainOffer.highlight_color}20`,
            borderColor: mainOffer.button_color,
            color: mainOffer.button_color
          }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getOfferIcon(mainOffer.offer_type)}
              <div>
                <div className="font-bold text-sm">
                  {lang === 'ar' ? mainOffer.button_text_ar : mainOffer.button_text_en}
                </div>
                <div className="text-xs opacity-75">
                  {getOfferDescription(mainOffer)}
                </div>
              </div>
            </div>
            
            {mainOffer.show_timer && currentTime > 0 && (
              <div className="text-right">
                <div className="text-xs opacity-75">
                  {lang === 'ar' ? 'ينتهي خلال' : 'Ends in'}
                </div>
                <div className="font-mono text-sm font-bold">
                  {formatTime(currentTime)}
                </div>
              </div>
            )}
          </div>
        </motion.button>

        {/* Multiple Offers Indicator */}
        {runningOffers.length > 1 && (
          <div className="text-center">
            <button
              onClick={() => setIsModalOpen(true)}
              className="text-sm text-[#d1b16a] hover:underline"
            >
              +{runningOffers.length - 1} {lang === 'ar' ? 'عروض أخرى' : 'more offers'}
            </button>
          </div>
        )}
      </motion.div>

      {/* Offers Modal */}
      <AnimatePresence>
        {isModalOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
            onClick={() => setIsModalOpen(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <GlassCard className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold">
                    {lang === 'ar' ? 'العروض الخاصة' : 'Special Offers'}
                  </h3>
                  <button
                    onClick={() => setIsModalOpen(false)}
                    className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                  >
                    <FiX size={20} />
                  </button>
                </div>

                <div className="space-y-4">
                  {runningOffers.map((offer) => {
                    const offerTime = timeRemaining[offer.id] || 0;
                    const isSelected = selectedOffer?.id === offer.id;
                    
                    return (
                      <motion.div
                        key={offer.id}
                        whileHover={{ scale: 1.01 }}
                        className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                          isSelected 
                            ? 'border-[#d1b16a] bg-[#d1b16a]/10' 
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => setSelectedOffer(offer)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3 flex-1">
                            {getOfferIcon(offer.offer_type)}
                            <div className="flex-1">
                              <h4 className="font-bold text-lg mb-1" style={{ color: offer.button_color }}>
                                {lang === 'ar' ? offer.name_ar : offer.name_en}
                              </h4>
                              <p className="text-gray-600 mb-2">
                                {getOfferDescription(offer)}
                              </p>
                              
                              {/* Offer Details */}
                              <div className="space-y-1 text-sm text-gray-500">
                                {offer.offer_type === 'buy_x_get_y_free' && (
                                  <div className="flex items-center gap-2">
                                    <FiGift size={14} />
                                    {lang === 'ar' 
                                      ? `احصل على ${offer.free_quantity} منتج مجاناً عند شراء ${offer.buy_quantity}`
                                      : `Get ${offer.free_quantity} items free when you buy ${offer.buy_quantity}`
                                    }
                                  </div>
                                )}
                                
                                {offer.offer_type === 'buy_x_free_shipping' && (
                                  <div className="flex items-center gap-2">
                                    <FiTruck size={14} />
                                    {lang === 'ar' ? 'شحن مجاني' : 'Free shipping included'}
                                  </div>
                                )}
                                
                                {currentProductQuantity > 0 && (
                                  <div className="flex items-center gap-2 text-green-600">
                                    <FiCheck size={14} />
                                    {lang === 'ar' 
                                      ? `لديك ${currentProductQuantity} في السلة`
                                      : `You have ${currentProductQuantity} in cart`
                                    }
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          {/* Timer */}
                          {offer.show_timer && offerTime > 0 && (
                            <div className="text-right ml-4">
                              <div className="flex items-center gap-1 text-red-500 mb-1">
                                <FiClock size={14} />
                                <span className="text-xs">
                                  {lang === 'ar' ? 'ينتهي خلال' : 'Ends in'}
                                </span>
                              </div>
                              <div className="font-mono text-sm font-bold text-red-600">
                                {formatTime(offerTime)}
                              </div>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-4 mt-6">
                  <button
                    onClick={() => setIsModalOpen(false)}
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    {lang === 'ar' ? 'إلغاء' : 'Cancel'}
                  </button>
                  <GlassButton
                    onClick={handleActivateOffer}
                    disabled={!selectedOffer}
                    className="flex-1 bg-[#d1b16a] text-black border-none hover:bg-[#d1b16a]/80"
                  >
                    {lang === 'ar' ? 'تفعيل العرض' : 'Activate Offer'}
                  </GlassButton>
                </div>
              </GlassCard>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
