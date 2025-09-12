import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Exclude test files from being processed
      exclude: /\.test\.(ts|tsx)$/,
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '0.0.0'),
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Core React libs
          vendor: ['react', 'react-dom'],
          // Routing
          router: ['react-router-dom'],
          // Animation library
          motion: ['framer-motion'],
          // Icon libraries
          icons: ['react-icons', 'lucide-react'],
          // Forms and utilities
          forms: ['react-hook-form'],
          // UI utilities
          utils: ['clsx', 'tailwind-merge'],
          // Date utilities if used
          dates: ['date-fns']
        },
        // Optimize chunk size for better caching
        chunkFileNames: (chunkInfo) => {
          if (chunkInfo.name === 'vendor') {
            return 'assets/vendor-[hash].js';
          }
          return 'assets/[name]-[hash].js';
        },
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name?.split('.') || [];
          const ext = info[info.length - 1];
          if (/\.(woff|woff2|ttf|eot)$/.test(assetInfo.name || '')) {
            return 'assets/fonts/[name]-[hash][extname]';
          }
          if (/\.(png|jpe?g|svg|gif|webp|avif)$/.test(assetInfo.name || '')) {
            return 'assets/images/[name]-[hash][extname]';
          }
          if (ext === 'css') {
            return 'assets/styles/[name]-[hash][extname]';
          }
          return 'assets/[name]-[hash][extname]';
        }
      }
    },
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug'],
        passes: 3, // Multiple passes for better compression
      },
      mangle: {
        safari10: true, // Support Safari 10+
      },
      format: {
        comments: false, // Remove all comments
      }
    },
    target: 'es2015',
    cssCodeSplit: true,
    cssMinify: true,
    // Reduce chunk size limit warnings
    chunkSizeWarningLimit: 1000
  },
  optimizeDeps: {
    exclude: ['lucide-react'],
    include: [
      'react', 
      'react-dom', 
      'react-router-dom', 
      'framer-motion',
      'react-icons/fi',
      'react-icons/hi',
      'react-icons/md'
    ],
    // Force optimization of these packages
    force: true
  },
  server: {
    host: true,
    port: 3000,
    open: false,
    cors: true,
    hmr: {
      overlay: false,
      port: 3001,
    },
    watch: {
      usePolling: true,
    },
  },
  preview: {
    host: true,
    port: 4173,
    open: false,
  },
  // Performance optimizations
  esbuild: {
    // Remove unused imports
    treeShaking: true,
    // Minify identifiers
    minifyIdentifiers: true,
    // Minify syntax
    minifySyntax: true,
    // Minify whitespace
    minifyWhitespace: true,
    // Target modern browsers for better performance
    target: 'es2020',
    // Enable source maps only in development
    sourcemap: process.env.NODE_ENV === 'development'
  },
  // CSS optimization
  css: {
    devSourcemap: process.env.NODE_ENV === 'development',
    postcss: {
      plugins: [
        // Add autoprefixer and other PostCSS plugins if needed
      ]
    }
  }
});
