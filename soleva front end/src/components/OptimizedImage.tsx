import React, { useState, useRef, useEffect } from 'react';
import ImageOptimizer, { OptimizedImageProps } from '../utils/imageOptimization';

interface OptimizedImageComponentProps extends Omit<OptimizedImageProps, 'placeholder'> {
  onLoad?: () => void;
  onError?: () => void;
  placeholder?: React.ReactNode;
  className?: string;
  highResolution?: boolean; // New prop for high-res mobile images
  lazyLoad?: boolean; // Enhanced lazy loading
}

// Helper function to get optimized image props
const getOptimizedImageProps = (props: any) => {
  return {
    src: ImageOptimizer.optimizeImage(props.src, props),
    alt: props.alt,
    style: props.style,
  };
};

export default function OptimizedImage({
  onLoad,
  onError,
  placeholder,
  className = '',
  highResolution = false,
  lazyLoad = true,
  ...props
}: OptimizedImageComponentProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isInView, setIsInView] = useState(!lazyLoad);
  const imgRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Enhanced optimization for high-resolution mobile
  const enhancedProps = {
    ...props,
    quality: highResolution ? 95 : (props.quality || 80),
    // Use 2x resolution for mobile high-DPI screens
    ...(highResolution && typeof window !== 'undefined' && window.devicePixelRatio > 1 && {
      width: typeof props.width === 'number' ? props.width * 2 : props.width,
      height: typeof props.height === 'number' ? props.height * 2 : props.height,
    })
  };

  const optimizedProps = getOptimizedImageProps(enhancedProps);

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (!lazyLoad || isInView) return;

    const container = containerRef.current;
    if (!container) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      {
        rootMargin: '50px' // Start loading 50px before it comes into view
      }
    );

    observer.observe(container);

    return () => observer.disconnect();
  }, [lazyLoad, isInView]);

  useEffect(() => {
    const img = imgRef.current;
    if (!img || !isInView) return;

    const handleLoad = () => {
      setIsLoaded(true);
      onLoad?.();
    };

    const handleError = () => {
      setHasError(true);
      onError?.();
    };

    img.addEventListener('load', handleLoad);
    img.addEventListener('error', handleError);

    return () => {
      img.removeEventListener('load', handleLoad);
      img.removeEventListener('error', handleError);
    };
  }, [onLoad, onError, isInView]);

  if (hasError) {
    return (
      <div 
        className={`flex items-center justify-center bg-gray-100 dark:bg-gray-800 ${className}`}
        style={{ width: props.width, height: props.height }}
      >
        <div className="text-gray-400 text-center">
          <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span className="text-sm">Image not found</span>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className={`relative overflow-hidden ${className}`}>
      {!isLoaded && placeholder && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-gray-800">
          {placeholder}
        </div>
      )}
      
      {!isLoaded && !placeholder && (
        <div className="absolute inset-0 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-pulse" />
      )}
      
      {isInView && (
        <img
          ref={imgRef}
          {...optimizedProps}
          className={`transition-opacity duration-300 ${
            isLoaded ? 'opacity-100' : 'opacity-0'
          } ${className}`}
          style={{
            ...optimizedProps.style,
            width: props.width || '100%',
            height: props.height || '100%',
            // Enhanced display quality for high-res screens
            imageRendering: highResolution ? 'crisp-edges' : 'auto',
          }}
          // Add WebP support with fallback
          onError={({ currentTarget }) => {
            if (currentTarget.src.includes('.webp')) {
              // Fallback to original format if WebP fails
              const originalSrc = optimizedProps.src?.replace('.webp', '.jpg') || optimizedProps.src;
              if (originalSrc) currentTarget.src = originalSrc;
            } else {
              setHasError(true);
              onError?.();
            }
          }}
        />
      )}
    </div>
  );
}