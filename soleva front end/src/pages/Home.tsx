import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiShoppingBag, FiTruck, FiShield, FiHeadphones, FiArrowRight } from 'react-icons/fi';
import { useLang, useTranslation } from '../contexts/LangContext';
import { products } from '../data/products';
import GlassCard from '../components/GlassCard';
import GlassButton from '../components/GlassButton';
import Logo from '../components/Logo';
import FavoriteButton from '../components/FavoriteButton';
import OptimizedImage from '../components/OptimizedImage';

export default function Home() {
  const { lang } = useLang();
  const t = useTranslation();

  const featuredProducts = products.slice(0, 6);

  const features = [
    {
      icon: <FiTruck className="w-8 h-8" />,
      title: t("freeShipping"),
      description: lang === 'ar' ? "شحن مجاني للطلبات فوق 500 جنيه" : "Free shipping on orders over 500 EGP"
    },
    {
      icon: <FiShield className="w-8 h-8" />,
      title: t("securePayment"),
      description: lang === 'ar' ? "دفع آمن 100%" : "100% secure payment processing"
    },
    {
      icon: <FiHeadphones className="w-8 h-8" />,
      title: t("customerSupport"),
      description: lang === 'ar' ? "دعم العملاء على مدار الساعة" : "Round the clock customer support"
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="section-lg">
        <div className="container">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
            {/* Hero Content */}
            <div className="text-center lg:text-left">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8 }}
                className="mb-8 lg:hidden"
              >
                <Logo size="large" className="justify-center mb-8" />
              </motion.div>
              
              <motion.h1
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                className="mb-6 text-4xl lg:text-5xl xl:text-6xl font-bold"
              >
                {lang === 'ar' ? 'مرحباً بك في سوليفا' : 'Welcome to Soleva'}
              </motion.h1>
              
              <motion.p
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="text-xl lg:text-2xl mb-8 max-w-2xl mx-auto lg:mx-0"
              >
                {lang === 'ar' 
                  ? 'اكتشف مجموعة أحذية فاخرة بتصميم عصري وجودة لا مثيل لها'
                  : 'Discover premium footwear with modern design and unmatched quality'
                }
              </motion.p>
              
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.6 }}
                className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start items-center"
              >
                <Link to="/products">
                  <GlassButton 
                    variant="primary"
                    size="lg"
                    className="w-full sm:w-auto min-w-[200px] text-lg font-semibold"
                  >
                    <FiShoppingBag />
                    {t("shopNow")}
                  </GlassButton>
                </Link>
                <Link to="/about">
                  <GlassButton 
                    variant="secondary"
                    size="lg"
                    className="w-full sm:w-auto min-w-[200px] text-lg"
                  >
                    {lang === 'ar' ? 'عن سوليفا' : 'About Soleva'}
                    <FiArrowRight />
                  </GlassButton>
                </Link>
              </motion.div>
            </div>

            {/* Hero Image */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="relative"
            >
              <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                <OptimizedImage
                  src={featuredProducts[0]?.image || "https://images.pexels.com/photos/1598508/pexels-photo-1598508.jpeg?auto=compress&cs=tinysrgb&w=800"}
                  alt="Premium Soleva footwear collection showcase - Modern Egyptian shoes with exceptional quality"
                  className="w-full h-[400px] lg:h-[500px] object-cover transition-transform duration-700 hover:scale-105"
                  loading="eager"
                  priority={true}
                  type="hero"
                  width={600}
                  height={500}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
                <div className="absolute top-4 right-4 hidden lg:block">
                  <Logo size="medium" />
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="section" aria-labelledby="features-title">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 id="features-title" className="mb-4">
              {lang === 'ar' ? 'لماذا تختار سوليفا؟' : 'Why Choose Soleva?'}
            </h2>
            <p className="text-xl max-w-2xl mx-auto">
              {lang === 'ar' 
                ? 'نقدم لك أفضل تجربة تسوق مع ضمان الجودة والخدمة المتميزة'
                : 'We provide the best shopping experience with quality assurance and exceptional service'
              }
            </p>
          </motion.div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ y: -5, scale: 1.02 }}
                className="feature-card"
              >
                <GlassCard className="text-center h-full">
                  <div className="text-primary mb-6 flex justify-center">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-semibold mb-4">
                    {feature.title}
                  </h3>
                  <p className="text-text-secondary leading-relaxed">
                    {feature.description}
                  </p>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="section" aria-labelledby="featured-title">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 id="featured-title" className="mb-4">
              {t("featuredProducts")}
            </h2>
            <p className="text-xl max-w-2xl mx-auto">
              {lang === 'ar' 
                ? 'منتجات مختارة بعناية خصيصاً لك'
                : 'Handpicked items just for you'
              }
            </p>
          </motion.div>
          
          <div className="mobile-products-grid sm:grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
            {featuredProducts.map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 50, scale: 0.9 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ 
                  duration: 0.7, 
                  delay: index * 0.15,
                  type: "spring",
                  stiffness: 100,
                  damping: 15
                }}
                whileHover={{ 
                  y: -15, 
                  scale: 1.05,
                  rotateY: 2,
                  transition: { duration: 0.3, type: "spring", stiffness: 300 }
                }}
                whileTap={{ scale: 0.98 }}
               className="product-card group interactive-hover"
              >
                <Link to={`/product/${product.id}`} className="block h-full">
                 <div className="product-card-image">
                    <OptimizedImage
                      src={product.image}
                      alt={`${product.name[lang as 'ar' | 'en']} - Premium footwear from Soleva collection`}
                      loading={index < 3 ? "eager" : "lazy"}
                      className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-115"
                      type="product"
                      width={400}
                      height={400}
                      priority={index < 3}
                    />
                    <FavoriteButton productId={product.id} />
                  </div>
                  
                 <div className="product-card-content">
                   <h3 className="product-card-title">
                      {product.name[lang as 'ar' | 'en']}
                    </h3>
                   <p className="product-card-description">
                      {product.desc[lang as 'ar' | 'en']}
                    </p>
                   <div className="product-card-price">
                      {product.price} {t("egp")}
                    </div>
                   <div className="product-card-actions">
                      <GlassButton 
                        variant="primary"
                        className="w-full text-[#000000]"
                      >
                        {t("viewDetails")}
                      </GlassButton>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
          
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="text-center mt-12"
          >
            <Link to="/products">
              <GlassButton 
                variant="secondary"
                size="lg"
              >
                {lang === 'ar' ? 'عرض جميع المنتجات' : 'View All Products'}
                <FiArrowRight />
              </GlassButton>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
          >
            <GlassCard className="text-center max-w-4xl mx-auto">
              <h2 className="mb-6">
                {lang === 'ar' 
                  ? 'مستعد لتجربة الجودة الفائقة؟'
                  : 'Ready to Experience Premium Quality?'
                }
              </h2>
              <p className="text-xl mb-8 leading-relaxed">
                {lang === 'ar'
                  ? 'انضم إلى آلاف العملاء الراضين الذين يثقون في سوليفا'
                  : 'Join thousands of satisfied customers who trust Soleva for their premium needs'
                }
              </p>
              <Link to="/products">
                <GlassButton 
                  variant="primary"
                  size="lg"
                >
                  <FiShoppingBag />
                  {t("shopNow")}
                </GlassButton>
              </Link>
            </GlassCard>
          </motion.div>
        </div>
      </section>
    </div>
  );
}