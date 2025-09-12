/**
 * Advanced image optimization utilities for Soleva platform
 */
import React from 'react';

interface ImageOptimizationOptions {
  width?: number;
  height?: number;
  quality?: number;
  format?: 'webp' | 'jpeg' | 'png' | 'auto';
  lazy?: boolean;
  placeholder?: boolean;
  responsive?: boolean;
}

interface ResponsiveImageSet {
  src: string;
  srcSet: string;
  sizes: string;
}

class ImageOptimizer {
  private static CDN_BASE_URL = import.meta.env.VITE_CDN_URL || '';
  private static PLACEHOLDER_BASE64 = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik04IDhMMTYgMTZNMTYgOEw4IDE2IiBzdHJva2U9IiM5Q0EzQUYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+Cjwvc3ZnPgo=';

  /**
   * Generate optimized image URL with transformations
   */
  static optimizeImage(
    originalUrl: string, 
    options: ImageOptimizationOptions = {}
  ): string {
    if (!originalUrl) return this.PLACEHOLDER_BASE64;

    // If it's already a data URL or external URL, return as is
    if (originalUrl.startsWith('data:') || originalUrl.startsWith('http')) {
      return originalUrl;
    }

    const {
      width,
      height,
      quality = 85,
      format = 'auto'
    } = options;

    // Build transformation parameters
    const params = new URLSearchParams();
    
    if (width) params.append('w', width.toString());
    if (height) params.append('h', height.toString());
    if (quality) params.append('q', quality.toString());
    if (format !== 'auto') params.append('f', format);

    // Auto format detection
    if (format === 'auto') {
      if (this.supportsWebP()) {
        params.append('f', 'webp');
      } else {
        params.append('f', 'jpeg');
      }
    }

    const transformedUrl = this.CDN_BASE_URL 
      ? `${this.CDN_BASE_URL}/${originalUrl}?${params.toString()}`
      : `${originalUrl}?${params.toString()}`;

    return transformedUrl;
  }

  /**
   * Generate responsive image set with multiple sizes
   */
  static generateResponsiveSet(
    originalUrl: string,
    options: ImageOptimizationOptions = {}
  ): ResponsiveImageSet {
    const breakpoints = [320, 480, 768, 1024, 1200, 1920];
    const { quality = 85, format = 'auto' } = options;

    const srcSet = breakpoints
      .map(width => {
        const optimizedUrl = this.optimizeImage(originalUrl, {
          width,
          quality,
          format
        });
        return `${optimizedUrl} ${width}w`;
      })
      .join(', ');

    const sizes = [
      '(max-width: 320px) 320px',
      '(max-width: 480px) 480px',
      '(max-width: 768px) 768px',
      '(max-width: 1024px) 1024px',
      '(max-width: 1200px) 1200px',
      '1920px'
    ].join(', ');

    return {
      src: this.optimizeImage(originalUrl, { width: 800, quality, format }),
      srcSet,
      sizes
    };
  }

  /**
   * Check if browser supports WebP format
   */
  private static supportsWebP(): boolean {
    try {
      return document.createElement('canvas')
        .toDataURL('image/webp')
        .startsWith('data:image/webp');
    } catch {
      return false;
    }
  }

  /**
   * Generate placeholder image based on dimensions
   */
  static generatePlaceholder(width: number, height: number, text?: string): string {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return this.PLACEHOLDER_BASE64;

    // Draw placeholder background
    ctx.fillStyle = '#f3f4f6';
    ctx.fillRect(0, 0, width, height);

    // Draw placeholder text
    if (text) {
      ctx.fillStyle = '#9ca3af';
      ctx.font = `${Math.min(width, height) / 8}px sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, width / 2, height / 2);
    }

    return canvas.toDataURL('image/png', 0.1);
  }

  /**
   * Preload critical images
   */
  static preloadImage(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve();
      img.onerror = reject;
      img.src = url;
    });
  }



  /**
   * Compress image file before upload
   */
  static async compressImage(
    file: File, 
    maxWidth: number = 1920, 
    maxHeight: number = 1080, 
    quality: number = 0.8
  ): Promise<File> {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();

      img.onload = () => {
        // Calculate new dimensions
        let { width, height } = img;
        
        if (width > height) {
          if (width > maxWidth) {
            height = (height * maxWidth) / width;
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width = (width * maxHeight) / height;
            height = maxHeight;
          }
        }

        canvas.width = width;
        canvas.height = height;

        // Draw and compress
        ctx?.drawImage(img, 0, 0, width, height);
        
        canvas.toBlob(
          (blob) => {
            if (blob) {
              const compressedFile = new File([blob], file.name, {
                type: 'image/jpeg',
                lastModified: Date.now()
              });
              resolve(compressedFile);
            } else {
              resolve(file);
            }
          },
          'image/jpeg',
          quality
        );
      };

      img.src = URL.createObjectURL(file);
    });
  }

  /**
   * Calculate image aspect ratio
   */
  static getAspectRatio(width: number, height: number): number {
    return width / height;
  }

  /**
   * Generate common e-commerce image variants
   */
  static getProductImageVariants(originalUrl: string) {
    return {
      thumbnail: this.optimizeImage(originalUrl, { width: 150, height: 150, quality: 80 }),
      small: this.optimizeImage(originalUrl, { width: 300, height: 300, quality: 85 }),
      medium: this.optimizeImage(originalUrl, { width: 600, height: 600, quality: 85 }),
      large: this.optimizeImage(originalUrl, { width: 1200, height: 1200, quality: 90 }),
      hero: this.optimizeImage(originalUrl, { width: 1920, height: 1080, quality: 95 })
    };
  }

  /**
   * Initialize lazy loading for images
   */
  static initLazyLoading(): void {
    if (typeof window === 'undefined') return;
    
    // Create intersection observer for lazy loading
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement;
          const src = img.dataset.src;
          if (src) {
            img.src = src;
            img.removeAttribute('data-src');
            observer.unobserve(img);
          }
        }
      });
    }, {
      rootMargin: '50px'
    });

    // Observe all images with data-src attribute
    document.querySelectorAll('img[data-src]').forEach(img => {
      observer.observe(img);
    });
  }
}

/**
 * React hook for responsive images
 */
export const useResponsiveImage = (url: string, options: ImageOptimizationOptions = {}) => {
  const { responsive = true } = options;

  if (responsive) {
    return ImageOptimizer.generateResponsiveSet(url, options);
  } else {
    return {
      src: ImageOptimizer.optimizeImage(url, options),
      srcSet: '',
      sizes: ''
    };
  }
};

/**
 * Optimized Image component props
 */
export interface OptimizedImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  quality?: number;
  format?: 'webp' | 'jpeg' | 'png' | 'auto';
  lazy?: boolean;
  responsive?: boolean;
  placeholder?: boolean;
  fallback?: string;
}

export default ImageOptimizer;

// Initialize lazy loading when the module is imported
if (typeof window !== 'undefined') {
  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ImageOptimizer.initLazyLoading);
  } else {
    ImageOptimizer.initLazyLoading();
  }
}