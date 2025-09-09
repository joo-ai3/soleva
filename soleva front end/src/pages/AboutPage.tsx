import React from 'react';
import { motion } from 'framer-motion';
import { FiTarget, FiHeart, FiTrendingUp, FiUsers } from 'react-icons/fi';
import { useLang, useTranslation } from '../contexts/LangContext';
import GlassCard from '../components/GlassCard';
import Logo from '../components/Logo';

export default function AboutPage() {
  const { lang } = useLang();
  const t = useTranslation();

  const values = [
    {
      icon: <FiTarget />,
      title: lang === 'ar' ? 'الجودة' : 'Quality',
      desc: lang === 'ar' 
        ? 'نلتزم بأعلى معايير الجودة في كل منتج نقدمه'
        : 'We commit to the highest quality standards in every product we offer'
    },
    {
      icon: <FiHeart />,
      title: lang === 'ar' ? 'الراحة' : 'Comfort',
      desc: lang === 'ar'
        ? 'راحة قدميك هي أولويتنا في كل تصميم'
        : 'Your foot comfort is our priority in every design'
    },
    {
      icon: <FiTrendingUp />,
      title: lang === 'ar' ? 'الابتكار' : 'Innovation',
      desc: lang === 'ar'
        ? 'نبتكر باستمرار لنقدم أحدث التقنيات والتصاميم'
        : 'We continuously innovate to bring the latest technologies and designs'
    },
    {
      icon: <FiUsers />,
      title: lang === 'ar' ? 'العملاء' : 'Customers',
      desc: lang === 'ar'
        ? 'رضا عملائنا هو مقياس نجاحنا'
        : 'Customer satisfaction is our measure of success'
    }
  ];

  const stats = [
    {
      number: '10K+',
      label: lang === 'ar' ? 'عميل سعيد' : 'Happy Customers'
    },
    {
      number: '500+',
      label: lang === 'ar' ? 'منتج متنوع' : 'Product Varieties'
    },
    {
      number: '5',
      label: lang === 'ar' ? 'سنوات خبرة' : 'Years Experience'
    },
    {
      number: '99%',
      label: lang === 'ar' ? 'رضا العملاء' : 'Customer Satisfaction'
    }
  ];

  return (
    <div className="container mx-auto py-6 sm:py-10 px-4 max-w-6xl">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center mb-16"
      >
        <div className="mb-8">
          <Logo size="large" className="justify-center" />
        </div>
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-6 text-[#111]">
          {t("aboutUs")}
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto leading-relaxed">
          {lang === 'ar'
            ? 'في سوليفا، نؤمن بأن كل خطوة تحكي قصة. نحن نصنع أحذية تجمع بين الأناقة المصرية الأصيلة والراحة العصرية، لتكون رفيقك في كل رحلة.'
            : 'At Soleva, we believe every step tells a story. We craft shoes that blend authentic Egyptian elegance with modern comfort, to be your companion on every journey.'
          }
        </p>
      </motion.div>

      {/* Story Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="mb-16"
      >
        <GlassCard>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
            <div>
              <h2 className="text-2xl sm:text-3xl font-bold mb-6 text-[#d1b16a]">
                {t("ourStory")}
              </h2>
              <div className="space-y-4 text-gray-600 leading-relaxed">
                <p>
                  {lang === 'ar'
                    ? 'بدأت رحلة سوليفا من حلم بسيط: صنع أحذية تعكس جمال وأصالة التراث المصري مع توفير أقصى درجات الراحة والجودة.'
                    : 'Soleva\'s journey began with a simple dream: to create shoes that reflect the beauty and authenticity of Egyptian heritage while providing maximum comfort and quality.'
                  }
                </p>
                <p>
                  {lang === 'ar'
                    ? 'اليوم، نفخر بكوننا علامة تجارية مصرية تقدم مجموعة متنوعة من الأحذية للرجال والنساء، بالإضافة إلى خط "سوليفا بيسكس" الاقتصادي.'
                    : 'Today, we\'re proud to be an Egyptian brand offering a diverse range of shoes for men and women, plus our budget-friendly "Soleva Basics" line.'
                  }
                </p>
                <div className="glass p-8 rounded-2xl">
                  <img
                    src="/logo.png"
                    alt="Soleva Logo"
                    className="w-full max-w-sm mx-auto rounded-xl shadow-lg"
                  />
                </div>
              </div>
            </div>
            <div className="relative">
              <img
                src="/logo.png"
                alt="Soleva Logo"
                className="w-full rounded-2xl shadow-lg"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#d1b16a]/20 to-transparent rounded-2xl"></div>
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* Values Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="mb-16"
      >
        <h2 className="text-2xl sm:text-3xl font-bold text-center mb-12 text-[#111]">
          {lang === 'ar' ? 'قيمنا' : 'Our Values'}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {values.map((value, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              whileHover={{ y: -4 }}
            >
              <GlassCard className="text-center h-full">
                <div className="w-16 h-16 bg-[#d1b16a]/20 rounded-full flex items-center justify-center mx-auto mb-4 text-[#d1b16a] text-2xl">
                  {value.icon}
                </div>
                <h3 className="font-bold text-lg mb-3 text-[#111]">{value.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{value.desc}</p>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Stats Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
      >
        <GlassCard className="bg-[#d1b16a]/10">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.7 + index * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl sm:text-4xl font-bold text-[#d1b16a] mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-600 font-medium">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </GlassCard>
      </motion.div>
    </div>
  );
}