import React from 'react';
import { FiShoppingCart } from 'react-icons/fi';
import { Link } from 'react-router-dom';
import { useLang, useTranslation } from '../../contexts/LangContext';
import GlassButton from '../../components/GlassButton';
import { motion } from 'framer-motion';

export default function EmptyCart() {
  const { lang } = useLang();
  const t = useTranslation();

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        className="text-center max-w-md mx-auto px-4"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, duration: 0.6, type: "spring", stiffness: 180 }}
          className="mb-8"
        >
          <FiShoppingCart size={80} className="mx-auto text-[#d1b16a] drop-shadow-lg animate-liquid-float" />
        </motion.div>
        
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="text-3xl font-bold mb-4 text-[#111]"
        >
          {t("empty")}
        </motion.h1>
        
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
          className="text-gray-600 mb-8 leading-relaxed"
        >
          {lang === "ar" ? "ابدأ التسوق الآن واكتشف مجموعتنا الرائعة" : "Start shopping now and discover our amazing collection"}
        </motion.p>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          <Link to="/products">
            <GlassButton className="bg-[#d1b16a] text-black border-none hover:bg-[#d1b16a]/80 px-8 py-3 text-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300">
              <FiShoppingCart className="mr-2" />
              {t("shopNow")}
            </GlassButton>
          </Link>
        </motion.div>
      </motion.div>
    </div>
  );
}
