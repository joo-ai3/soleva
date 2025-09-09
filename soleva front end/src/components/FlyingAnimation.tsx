import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiShoppingCart, FiHeart } from 'react-icons/fi';

interface FlyingAnimationProps {
  type: 'cart' | 'favorite';
  isVisible: boolean;
  startPosition: { x: number; y: number };
  onComplete: () => void;
  productImage?: string;
}

export function FlyingAnimation({ 
  type, 
  isVisible, 
  startPosition, 
  onComplete, 
  productImage 
}: FlyingAnimationProps) {
  const Icon = type === 'cart' ? FiShoppingCart : FiHeart;
  const color = type === 'cart' ? '#ef4444' : '#ec4899';

  // Calculate target position (top-right corner for cart/favorites)
  const targetPosition = {
    x: window.innerWidth - 60,
    y: 60
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{
            x: startPosition.x,
            y: startPosition.y,
            scale: 1,
            opacity: 1,
            rotate: 0
          }}
          animate={{
            x: targetPosition.x,
            y: targetPosition.y,
            scale: 0.3,
            opacity: 0.8,
            rotate: 360
          }}
          exit={{
            scale: 0,
            opacity: 0
          }}
          transition={{
            duration: 1.2,
            ease: [0.23, 1, 0.32, 1], // Custom easing for smooth flight
            scale: { delay: 0.8, duration: 0.4 },
            opacity: { delay: 0.8, duration: 0.4 }
          }}
          onAnimationComplete={onComplete}
          className="fixed z-50 pointer-events-none"
          style={{
            left: 0,
            top: 0,
          }}
        >
          <div className="relative">
            {/* Product image if provided */}
            {productImage && (
              <motion.img
                src={productImage}
                alt="Product flying to cart"
                className="w-16 h-16 rounded-lg shadow-lg border-2 border-white"
                initial={{ scale: 1 }}
                animate={{ scale: 0.8 }}
                transition={{ duration: 0.3 }}
              />
            )}
            
            {/* Icon overlay */}
            <motion.div
              className="absolute -top-2 -right-2 rounded-full p-2 shadow-lg"
              style={{ backgroundColor: color }}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, duration: 0.3, type: 'spring' }}
            >
              <Icon size={16} className="text-white" />
            </motion.div>

            {/* Trail effect */}
            <motion.div
              className="absolute inset-0 rounded-lg"
              style={{
                background: `linear-gradient(45deg, ${color}40, transparent)`,
                filter: 'blur(8px)'
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Context to provide animation trigger globally
const FlyingAnimationContext = React.createContext<{
  triggerAnimation: (type: 'cart' | 'favorite', element: HTMLElement, productImage?: string) => void;
} | null>(null);

export function FlyingAnimationProvider({ children }: { children: React.ReactNode }) {
  const [animations, setAnimations] = useState<Array<{
    id: string;
    type: 'cart' | 'favorite';
    startPosition: { x: number; y: number };
    productImage?: string;
  }>>([]);

  const triggerAnimation = useCallback((
    type: 'cart' | 'favorite',
    element: HTMLElement,
    productImage?: string
  ) => {
    const rect = element.getBoundingClientRect();
    const startPosition = {
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2
    };

    const id = `${type}-${Date.now()}-${Math.random()}`;
    
    setAnimations(prev => [...prev, {
      id,
      type,
      startPosition,
      productImage
    }]);

    // Auto-remove after animation completes
    setTimeout(() => {
      setAnimations(prev => prev.filter(anim => anim.id !== id));
    }, 2000);
  }, []);

  const handleAnimationComplete = useCallback((id: string) => {
    setAnimations(prev => prev.filter(anim => anim.id !== id));
  }, []);

  return (
    <FlyingAnimationContext.Provider value={{ triggerAnimation }}>
      {children}
      {/* Render animations */}
      {animations.map((animation) => (
        <FlyingAnimation
          key={animation.id}
          type={animation.type}
          isVisible={true}
          startPosition={animation.startPosition}
          productImage={animation.productImage}
          onComplete={() => handleAnimationComplete(animation.id)}
        />
      ))}
    </FlyingAnimationContext.Provider>
  );
}

export function useFlyingAnimationTrigger() {
  const context = React.useContext(FlyingAnimationContext);
  if (!context) {
    throw new Error('useFlyingAnimationTrigger must be used within FlyingAnimationProvider');
  }
  return context;
}
