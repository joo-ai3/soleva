import React from 'react';
import { FiTrash2 } from 'react-icons/fi';
import { motion } from 'framer-motion';
import { useLang, useTranslation } from '../../contexts/LangContext';
import GlassCard from '../../components/GlassCard';
import GlassButton from '../../components/GlassButton';

export default function EmptyCartConfirmModal({ onCancel, onConfirm }: {
  onCancel: () => void;
  onConfirm: () => void;
}) {
  const { lang } = useLang();
  const t = useTranslation();

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/50 backdrop-blur-lg p-4" style={{
      backdropFilter: 'blur(15px) saturate(180%)',
      WebkitBackdropFilter: 'blur(15px) saturate(180%)'
    }}>
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      >
        <GlassCard className="max-w-md w-full text-center p-8 shadow-2xl">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.1, duration: 0.5, type: "spring", stiffness: 200 }}
          >
            <FiTrash2 size={64} className="mx-auto mb-6 text-red-500" />
          </motion.div>
          <h3 className="text-2xl font-bold mb-4 text-[var(--text-primary)]">
            {lang === 'ar' ? 'هل أنت متأكد من إفراغ السلة؟' : 'Are you sure you want to empty your cart?'}
          </h3>
          <p className="text-[var(--text-secondary)] mb-8 text-lg leading-relaxed">
            {lang === 'ar' 
              ? 'سيتم حذف جميع المنتجات من سلة التسوق'
              : 'All items will be removed from your shopping cart'
            }
          </p>
          <div className="flex gap-4 justify-center">
            <GlassButton 
              className="bg-red-500 text-white border-none hover:bg-red-600 px-8 py-3 text-lg font-semibold hover:scale-105 transition-all duration-300" 
              onClick={onConfirm}
            >
              {lang === 'ar' ? 'نعم، إفراغ السلة' : 'Yes, Empty Cart'}
            </GlassButton>
            <GlassButton 
              onClick={onCancel}
              className="px-8 py-3 text-lg font-semibold hover:scale-105 transition-all duration-300"
            >
              {t("cancel")}
            </GlassButton>
          </div>
        </GlassCard>
      </motion.div>
    </div>
  );
}