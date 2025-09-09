import React from 'react';
import { motion } from 'framer-motion';
import { FiMinus, FiPlus, FiTrash2 } from 'react-icons/fi';
import { useCart } from '../../contexts/CartContext';
import { useToast } from '../../contexts/ToastContext';
import { useLang, useTranslation } from '../../contexts/LangContext';
import type { CartItem as CartItemType } from '../../types';

export default function CartItem({ item, index, onRemove }: { item: CartItemType, index: number, onRemove: (item: CartItemType) => void }) {
  const { updateQty } = useCart();
  const { showToast } = useToast();
  const { lang } = useLang();
  const t = useTranslation();

  const handleQty = (diff: number) => {
    const newQty = item.qty + diff;
    if (newQty < 1) return;

    const displayElement = document.querySelector(`[data-item-id="${item.id}-${item.color}-${item.size}"] .quantity-display`);
    if (displayElement) {
      displayElement.classList.add('updating');
      setTimeout(() => displayElement.classList.remove('updating'), 300);
    }

    updateQty(item.id, item.color, item.size, newQty);
    showToast(t("updateSuccess"));
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1, duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
      whileHover={{ y: -3, scale: 1.02 }}
      className="cart-item flex flex-col sm:flex-row items-start sm:items-center gap-4 modern-glass-card rounded-xl border border-[var(--border-secondary)] hover:shadow-lg transition-all duration-300 p-4 sm:p-5"
      data-item-id={`${item.id}-${item.color}-${item.size}`}
    >
      <img
        src={item.image}
        alt={item.name[lang]}
        className="w-20 h-20 sm:w-24 sm:h-24 object-cover rounded-lg flex-shrink-0 transition-transform duration-300 hover:scale-105"
        loading="lazy"
        decoding="async"
        width="96"
        height="96"
      />

      <div className="flex-1 min-w-0 w-full">
        <h3 className="font-semibold text-base sm:text-lg text-[var(--text-primary)] line-clamp-2 mb-2">{item.name[lang]}</h3>
        <div className="text-sm text-[var(--text-secondary)] space-y-1">
          <div>{t("color")}: {item.color}</div>
          <div>{t("size")}: {item.size}</div>
        </div>
        <div className="text-[var(--primary)] font-bold text-lg mt-2">
          {item.price * item.qty} {t("egp")}
        </div>
      </div>

      <div className="flex flex-row sm:flex-col items-center justify-between sm:justify-center gap-4 sm:gap-3 w-full sm:w-auto">
        
        {/* Quantity Control Container */}
        <div className="quantity-control flex items-center gap-3 px-4 py-2 bg-[var(--bg-secondary)] rounded-xl border border-[var(--border-secondary)]">
          <button
            onClick={() => handleQty(-1)}
            className="w-10 h-10 flex items-center justify-center rounded-lg bg-[var(--bg-primary)] border border-[var(--border-secondary)] text-[var(--text-primary)] hover:bg-[var(--primary)] hover:text-white transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={item.qty <= 1}
            aria-label="Decrease quantity"
          >
            <FiMinus />
          </button>

          <span className="quantity-display font-semibold text-lg text-[var(--text-primary)]">{item.qty}</span>

          <button
            onClick={() => handleQty(1)}
            className="w-10 h-10 flex items-center justify-center rounded-lg bg-[var(--bg-primary)] border border-[var(--border-secondary)] text-[var(--text-primary)] hover:bg-[var(--primary)] hover:text-white transition-all duration-300"
            aria-label="Increase quantity"
          >
            <FiPlus />
          </button>
        </div>

        {/* Remove Button */}
        <button
          onClick={() => onRemove(item)}
          className="remove-btn w-14 h-14 sm:w-16 sm:h-16 flex items-center justify-center glass border border-red-200/50 rounded-xl bg-red-50/80 text-red-500 hover:bg-red-500 hover:text-white hover:border-red-500 hover:scale-110 hover:shadow-lg transition-all duration-300"
          aria-label="Remove item from cart"
        >
          <FiTrash2 size={22} />
        </button>
      </div>
    </motion.div>
  );
}
