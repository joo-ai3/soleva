import React from 'react';
import { FiBox } from 'react-icons/fi';
import { useTranslation } from '../contexts/LangContext';
import GlassCard from '../components/GlassCard';

export default function OrderTrackingPage() {
  const t = useTranslation();
  
  return (
    <div className="container mx-auto py-10 px-4 max-w-2xl">
      <GlassCard>
        <div className="text-center py-12">
          <FiBox size={64} className="mx-auto mb-4 text-[#d1b16a]" />
          <h1 className="text-2xl font-bold mb-4">{t("orderTracking")}</h1>
          <p className="text-gray-600">{t("orderTrackingPlaceholder")}</p>
        </div>
      </GlassCard>
    </div>
  );
}