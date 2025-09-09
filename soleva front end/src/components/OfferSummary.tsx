
import { motion } from 'framer-motion';
import { FiGift, FiTruck, FiTag, FiZap, FiInfo } from 'react-icons/fi';
import { useLang } from '../contexts/LangContext';
import { OfferCalculationResponse } from '../services/offersApi';

interface OfferSummaryProps {
  offerCalculation: OfferCalculationResponse | null;
  className?: string;
}

export default function OfferSummary({ offerCalculation, className = '' }: OfferSummaryProps) {
  const { lang } = useLang();

  if (!offerCalculation) return null;

  const {
    flash_sales,
    special_offers,
    total_discount,
    free_shipping_available,
    coupons_blocked
  } = offerCalculation;

  const hasActiveOffers = flash_sales.length > 0 || special_offers.length > 0;

  if (!hasActiveOffers) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass rounded-xl p-4 border border-green-200 bg-green-50/50 ${className}`}
    >
      <div className="flex items-center gap-2 mb-4">
        <FiGift className="text-green-600" size={20} />
        <h3 className="font-bold text-green-800">
          {lang === 'ar' ? 'العروض النشطة' : 'Active Offers'}
        </h3>
      </div>

      {/* Flash Sales */}
      {flash_sales.length > 0 && (
        <div className="mb-4">
          <h4 className="font-semibold text-sm text-gray-700 mb-2 flex items-center gap-2">
            <FiZap className="text-orange-500" size={14} />
            {lang === 'ar' ? 'عروض البرق' : 'Flash Sales'}
          </h4>
          <div className="space-y-2">
            {flash_sales.map((sale) => (
              <div
                key={sale.id}
                className="flex justify-between items-center p-2 bg-white/70 rounded-lg border border-orange-200"
              >
                <div>
                  <div className="font-medium text-sm">
                    {lang === 'ar' ? sale.name_ar : sale.name_en}
                  </div>
                  <div className="text-xs text-gray-600">
                    {sale.applicable_items.length} {lang === 'ar' ? 'منتج' : 'items'}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-orange-600">
                    -{sale.total_discount} {lang === 'ar' ? 'ج.م' : 'EGP'}
                  </div>
                  {sale.time_remaining > 0 && (
                    <div className="text-xs text-gray-500">
                      {Math.floor(sale.time_remaining / 3600)}h {Math.floor((sale.time_remaining % 3600) / 60)}m
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Special Offers */}
      {special_offers.length > 0 && (
        <div className="mb-4">
          <h4 className="font-semibold text-sm text-gray-700 mb-2 flex items-center gap-2">
            <FiTag className="text-purple-500" size={14} />
            {lang === 'ar' ? 'العروض الخاصة' : 'Special Offers'}
          </h4>
          <div className="space-y-2">
            {special_offers.map((offer) => (
              <div
                key={offer.id}
                className="p-2 bg-white/70 rounded-lg border border-purple-200"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="font-medium text-sm">
                      {lang === 'ar' ? offer.name_ar : offer.name_en}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                      {offer.description}
                    </div>
                  </div>
                  <div className="text-right ml-2">
                    {offer.discount_amount > 0 && (
                      <div className="font-bold text-purple-600">
                        -{offer.discount_amount} {lang === 'ar' ? 'ج.م' : 'EGP'}
                      </div>
                    )}
                    {offer.free_shipping && (
                      <div className="flex items-center gap-1 text-blue-600 text-xs">
                        <FiTruck size={12} />
                        {lang === 'ar' ? 'شحن مجاني' : 'Free shipping'}
                      </div>
                    )}
                    {offer.free_items.length > 0 && (
                      <div className="text-xs text-green-600">
                        +{offer.free_items.length} {lang === 'ar' ? 'مجاني' : 'free'}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Total Savings */}
      {total_discount > 0 && (
        <div className="flex justify-between items-center p-3 bg-green-100 rounded-lg border border-green-300">
          <span className="font-semibold text-green-800">
            {lang === 'ar' ? 'إجمالي التوفير:' : 'Total Savings:'}
          </span>
          <span className="font-bold text-green-700 text-lg">
            -{total_discount} {lang === 'ar' ? 'ج.م' : 'EGP'}
          </span>
        </div>
      )}

      {/* Free Shipping Indicator */}
      {free_shipping_available && (
        <div className="flex items-center gap-2 mt-3 p-2 bg-blue-50 rounded-lg border border-blue-200">
          <FiTruck className="text-blue-600" size={16} />
          <span className="text-blue-800 text-sm font-medium">
            {lang === 'ar' ? 'شحن مجاني مفعل' : 'Free shipping included'}
          </span>
        </div>
      )}

      {/* Coupon Blocked Message */}
      {coupons_blocked && (
        <div className="flex items-center gap-2 mt-3 p-2 bg-yellow-50 rounded-lg border border-yellow-200">
          <FiInfo className="text-yellow-600" size={16} />
          <span className="text-yellow-800 text-sm">
            {lang === 'ar' 
              ? 'لا يمكن استخدام كوبونات الخصم مع العروض النشطة'
              : 'Discount coupons cannot be used with active offers'
            }
          </span>
        </div>
      )}
    </motion.div>
  );
}
