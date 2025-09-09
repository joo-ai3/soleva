import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useCart } from '../contexts/CartContext';
import { useToast } from '../contexts/ToastContext';
import { useTranslation } from '../contexts/LangContext';
import SectionTitle from '../components/SectionTitle';
import EmptyCart from './cart/EmptyCart';
import CartItem from './cart/CartItem';
import CartSummary from './cart/CartSummary';
import RemoveConfirmModal from './cart/RemoveConfirmModal';
import LoadingSkeleton from '../components/LoadingSkeleton';
import type { CartItem as CartItemType } from '../types';

export default function CartPage() {
  const { cart, removeFromCart } = useCart();
  const { showToast } = useToast();

  const t = useTranslation();
  const [showConfirm, setShowConfirm] = useState(false);
  const [removeItem, setRemoveItem] = useState<CartItemType | null>(null);
  const [isLoading] = useState(false);

  const askRemove = (item: CartItemType) => {
    setRemoveItem(item);
    setShowConfirm(true);
  };

  const confirmRemove = () => {
    removeFromCart(removeItem.id, removeItem.color, removeItem.size);
    setShowConfirm(false);
    showToast(t("removeSuccess"));
  };

  if (cart.length === 0) return <EmptyCart />;

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7 }}
      className="container mx-auto py-6 sm:py-10 px-4"
    >
      <SectionTitle>{t("cart")}</SectionTitle>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2 space-y-6">
          {isLoading ? (
            <LoadingSkeleton type="cart" count={3} />
          ) : (
            cart.map((item, i) => (
              <CartItem key={i} item={item} index={i} onRemove={askRemove} />
            ))
          )}
        </div>

        {/* Order Summary */}
        <CartSummary />
      </div>

      {/* Remove Confirmation */}
      {showConfirm && (
        <RemoveConfirmModal 
          item={removeItem} 
          onCancel={() => setShowConfirm(false)} 
          onConfirm={confirmRemove} 
        />
      )}
    </motion.div>
  );
}
