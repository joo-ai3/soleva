import React from 'react';
import { motion } from 'framer-motion';

interface LoadingSkeletonProps {
  type?: 'product' | 'cart' | 'text' | 'image';
  className?: string;
  count?: number;
}

export default function LoadingSkeleton({ type = 'product', className = '', count = 1 }: LoadingSkeletonProps) {
  const skeletonVariants = {
    loading: {
      opacity: [0.4, 0.8, 0.4],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  const ProductSkeleton = () => (
    <motion.div 
      variants={skeletonVariants}
      animate="loading"
      className={`bg-gray-200 dark:bg-gray-700 rounded-xl overflow-hidden ${className}`}
    >
      <div className="aspect-square bg-gray-300 dark:bg-gray-600 rounded-t-xl"></div>
      <div className="p-4 space-y-3">
        <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
        <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
        <div className="h-5 bg-gray-300 dark:bg-gray-600 rounded w-1/3"></div>
        <div className="h-10 bg-gray-300 dark:bg-gray-600 rounded"></div>
      </div>
    </motion.div>
  );

  const CartSkeleton = () => (
    <motion.div 
      variants={skeletonVariants}
      animate="loading"
      className={`bg-gray-200 dark:bg-gray-700 rounded-xl p-4 flex items-center gap-4 ${className}`}
    >
      <div className="w-20 h-20 bg-gray-300 dark:bg-gray-600 rounded-lg flex-shrink-0"></div>
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
        <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
        <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-1/3"></div>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-lg"></div>
        <div className="w-8 h-4 bg-gray-300 dark:bg-gray-600 rounded"></div>
        <div className="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-lg"></div>
      </div>
    </motion.div>
  );

  const TextSkeleton = () => (
    <motion.div 
      variants={skeletonVariants}
      animate="loading"
      className={`space-y-2 ${className}`}
    >
      <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-full"></div>
      <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-5/6"></div>
      <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-4/6"></div>
    </motion.div>
  );

  const ImageSkeleton = () => (
    <motion.div 
      variants={skeletonVariants}
      animate="loading"
      className={`bg-gray-300 dark:bg-gray-600 rounded-lg ${className}`}
    >
    </motion.div>
  );

  const renderSkeleton = () => {
    switch (type) {
      case 'product':
        return <ProductSkeleton />;
      case 'cart':
        return <CartSkeleton />;
      case 'text':
        return <TextSkeleton />;
      case 'image':
        return <ImageSkeleton />;
      default:
        return <ProductSkeleton />;
    }
  };

  return (
    <>
      {Array.from({ length: count }, (_, index) => (
        <div key={index}>
          {renderSkeleton()}
        </div>
      ))}
    </>
  );
}