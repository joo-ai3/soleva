import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { FiShoppingCart, FiArrowLeft, FiCheck } from "react-icons/fi";
import clsx from "clsx";
import { useLang, useTranslation } from "../contexts/LangContext";
import { useCart } from "../contexts/CartContext";
import { useToast } from "../contexts/ToastContext";
import { products } from "../data/products";
import GlassButton from "../components/GlassButton";
import GlassCard from "../components/GlassCard";
import FavoriteButton from "../components/FavoriteButton";

export default function ProductPage() {
  const { id } = useParams();
  const { lang } = useLang();
  const t = useTranslation();
  const { addToCart } = useCart();
  const { showToast } = useToast();

  const product = products.find(p => p.id === parseInt(id || "0"));
  const relatedProducts = products.filter(p => p.id !== product?.id && p.collection === product?.collection).slice(0, 4);

  const [selectedColor, setSelectedColor] = useState(product?.colors[0]?.name[lang] || "");
  const [selectedSize, setSelectedSize] = useState(product?.sizes[0] || 0);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isImageChanging, setIsImageChanging] = useState(false);
  const [isAddingToCart, setIsAddingToCart] = useState(false);

  useEffect(() => {
    if (!product) return;
    const interval = setInterval(() => {
      setIsImageChanging(true);
      setTimeout(() => {
        setCurrentImageIndex((prev) => (prev + 1) % product.colors.length);
        setIsImageChanging(false);
      }, 250);
    }, 5000);
    return () => clearInterval(interval);
  }, [product]);

  useEffect(() => {
    if (!product || !selectedColor) return;
    const colorIndex = product.colors.findIndex(color => color.name[lang] === selectedColor);
    if (colorIndex !== -1 && colorIndex !== currentImageIndex) {
      setIsImageChanging(true);
      setTimeout(() => {
        setCurrentImageIndex(colorIndex);
        setIsImageChanging(false);
      }, 200);
    }
  }, [selectedColor, product, lang, currentImageIndex]);

  if (!product) {
    return (
      <div className="container py-20 text-center">
        <GlassCard className="max-w-md mx-auto">
          <h1 className="text-2xl font-bold mb-4 text-red-500">
            {t("productNotFound")}
          </h1>
          <Link to="/products">
            <GlassButton variant="primary">
              <FiArrowLeft />
              {lang === 'ar' ? 'العودة للمنتجات' : 'Back to Products'}
            </GlassButton>
          </Link>
        </GlassCard>
      </div>
    );
  }

  const handleAddToCart = async () => {
    if (!selectedColor || !selectedSize) {
      showToast(lang === "ar" ? "يرجى اختيار اللون والمقاس" : "Please select color and size");
      return;
    }
    
    setIsAddingToCart(true);
    
    // Simulate loading for better UX
    await new Promise(resolve => setTimeout(resolve, 500));
    
    addToCart(product, selectedColor, selectedSize);
    showToast(t("addSuccess"));
    setIsAddingToCart(false);
  };

  const handleColorSelect = (color: any) => {
    setSelectedColor(color.name[lang]);
  };

  const currentImage = product.image;

  return (
    <div className="min-h-screen">
      {/* SEO Schema Markup */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": product.name[lang],
            "description": product.desc[lang],
            "image": product.image,
            "brand": {
              "@type": "Brand",
              "name": "Soleva"
            },
            "offers": {
              "@type": "Offer",
              "price": product.price,
              "priceCurrency": "EGP",
              "availability": "https://schema.org/InStock",
              "seller": {
                "@type": "Organization",
                "name": "Soleva Store"
              }
            },
            "aggregateRating": {
              "@type": "AggregateRating",
              "ratingValue": "4.8",
              "reviewCount": "127"
            }
          })
        }}
      />
      
      <div className="container py-8">
        {/* Breadcrumb */}
        <motion.nav
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <Link to="/" className="hover:text-primary transition-colors">
              {t('home')}
            </Link>
            <span>/</span>
            <Link to="/products" className="hover:text-primary transition-colors">
              {t('products')}
            </Link>
            <span>/</span>
            <span className="text-text-primary">{product.name[lang]}</span>
          </div>
        </motion.nav>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start mb-16">
          {/* Product Image */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="relative"
          >
            <div className="relative overflow-hidden rounded-2xl bg-bg-secondary">
              <AnimatePresence mode="wait">
                <motion.img
                  key={currentImageIndex}
                  src={currentImage}
                  alt={product.name[lang]}
                  className={clsx(
                    'w-full aspect-square object-cover transition-all duration-500',
                    isImageChanging ? 'opacity-0 scale-95' : 'opacity-100 scale-100'
                  )}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 1.05 }}
                  transition={{ duration: 0.6 }}
                  loading="eager"
                  decoding="async"
                  width="600"
                  height="600"
                  sizes="(max-width: 768px) 100vw, 50vw"
                />
              </AnimatePresence>
              
              {/* Image Indicators */}
              <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2">
                {product.colors.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setIsImageChanging(true);
                      setTimeout(() => {
                        setCurrentImageIndex(index);
                        setIsImageChanging(false);
                      }, 200);
                    }}
                    className={clsx(
                      "w-2 h-2 rounded-full transition-all duration-300",
                      currentImageIndex === index
                        ? "bg-primary w-6 shadow-lg"
                        : "bg-white/50 hover:bg-white/80"
                    )}
                    aria-label={`View image ${index + 1}`}
                  />
                ))}
              </div>
            </div>
          </motion.div>

          {/* Product Details */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="space-y-6"
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h1 className="text-3xl lg:text-4xl font-bold mb-3">
                  {product.name[lang]}
                </h1>
                <p className="text-lg text-text-secondary leading-relaxed">
                  {product.desc[lang]}
                </p>
              </div>
              <FavoriteButton productId={product.id} size={24} />
            </div>

            <div className="text-3xl font-bold text-primary">
              {product.price} {t("egp")}
            </div>

            {/* Color Selection */}
            <div>
              <h3 className="text-lg font-semibold mb-4">
                {t("color")}: <span className="text-primary">{selectedColor}</span>
              </h3>
              <div className="flex gap-3 flex-wrap">
                {product.colors.map((color, index) => (
                  <motion.button
                    key={index}
                    onClick={() => handleColorSelect(color)}
                    whileTap={{ scale: 0.95 }}
                    whileHover={{ scale: 1.1 }}
                    className={clsx(
                      "w-12 h-12 rounded-full border-2 cursor-pointer transition-all duration-200 relative",
                      selectedColor === color.name[lang]
                        ? "border-primary ring-2 ring-primary ring-offset-2"
                        : "border-border-primary hover:border-primary"
                    )}
                    style={{ backgroundColor: color.code }}
                    aria-label={color.name[lang]}
                  >
                    {selectedColor === color.name[lang] && (
                      <FiCheck className="absolute inset-0 m-auto text-white drop-shadow-lg" size={20} />
                    )}
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Size Selection */}
            <div>
              <h3 className="text-lg font-semibold mb-4">
                {t("size")}: <span className="text-primary">{selectedSize}</span>
              </h3>
              <div className="flex gap-3 flex-wrap">
                {product.sizes.map((size) => (
                  <motion.button
                    key={size}
                    whileTap={{ scale: 0.95 }}
                    whileHover={{ scale: 1.05 }}
                    onClick={() => setSelectedSize(size)}
                    className={clsx(
                      "px-4 py-3 rounded-lg border font-medium transition-all duration-200 min-w-[60px]",
                      selectedSize === size
                        ? "bg-primary text-black border-primary shadow-lg"
                        : "bg-bg-secondary text-text-primary border-border-primary hover:border-primary hover:bg-primary hover:bg-opacity-10"
                    )}
                  >
                    {size}
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Specifications */}
            <GlassCard variant="compact">
              <h3 className="text-lg font-semibold mb-4">
                {t("specs")}
              </h3>
              <div className="space-y-3">
                {product.specs[lang].map(([key, value], index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                    className="flex justify-between items-center py-2 border-b border-border-secondary last:border-b-0"
                  >
                    <span className="text-text-secondary font-medium">{key}:</span>
                    <span className="text-text-primary font-semibold">{value}</span>
                  </motion.div>
                ))}
              </div>
            </GlassCard>

            {/* Add to Cart */}
            <div className="space-y-4">
              <GlassButton
                onClick={handleAddToCart}
                variant="primary"
                size="lg"
                className="w-full"
                loading={isAddingToCart}
                disabled={!selectedColor || !selectedSize}
              >
                <FiShoppingCart size={20} />
                {isAddingToCart ? 'Adding...' : t("addToCart")}
              </GlassButton>
              
              {(!selectedColor || !selectedSize) && (
                <p className="text-sm text-text-secondary text-center">
                  {lang === "ar" ? "يرجى اختيار اللون والمقاس" : "Please select color and size"}
                </p>
              )}
            </div>
          </motion.div>
        </div>

        {/* Related Products */}
        {relatedProducts.length > 0 && (
          <motion.section
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.6 }}
          >
            <h2 className="text-2xl font-bold mb-8 text-center">
              {lang === "ar" ? "منتجات مشابهة" : "Related Products"}
            </h2>
            <div className="products-grid">
              {relatedProducts.map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.9 + index * 0.1 }}
                  whileHover={{ y: -6, scale: 1.02 }}
                  className="product-card interactive-hover"
                >
                  <Link to={`/product/${item.id}`}>
                    <div className="product-card-image">
                      <img
                        src={item.image}
                        alt={item.name[lang]}
                        loading="lazy"
                        className="w-full h-full object-cover transition-transform duration-700 hover:scale-115"
                      />
                      <FavoriteButton productId={item.id} />
                    </div>
                    <div className="product-card-content">
                      <h3 className="product-card-title line-clamp-2">
                        {item.name[lang]}
                      </h3>
                      <p className="product-card-price">
                        {item.price} {t("egp")}
                      </p>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          </motion.section>
        )}
      </div>
    </div>
  );
}