import React from 'react';
import { motion } from 'framer-motion';
import { FiShield, FiLock, FiEye, FiUsers } from 'react-icons/fi';
import { useLang } from '../contexts/LangContext';
import GlassCard from '../components/GlassCard';

export default function PrivacyPage() {
  const { lang } = useLang();


  const sections = [
    {
      icon: <FiEye />,
      title: lang === 'ar' ? 'المعلومات التي نجمعها' : 'Information We Collect',
      content: lang === 'ar' 
        ? [
            'البيانات الشخصية (الاسم، البريد الإلكتروني، رقم الهاتف، العنوان)',
            'معلومات الدفع (تتم معالجتها بأمان عبر شركائنا في الدفع)',
            'سلوك التصفح (الصفحات المزارة، المنتجات المعروضة)',
            'البيانات التقنية (عنوان IP، نوع المتصفح، نوع الجهاز)'
          ]
        : [
            'Personal details (name, email, phone number, address)',
            'Payment information (processed securely via our payment partners)',
            'Browsing behavior (pages visited, products viewed)',
            'Technical data (IP address, browser type, device type)'
          ]
    },
    {
      icon: <FiUsers />,
      title: lang === 'ar' ? 'كيف نستخدم معلوماتك' : 'How We Use Your Information',
      content: lang === 'ar'
        ? [
            'معالجة وتنفيذ طلباتك',
            'تحسين موقعنا وتجربة العملاء',
            'التواصل بشأن العروض والتحديثات (إذا اخترت ذلك)',
            'منع المعاملات الاحتيالية وتعزيز الأمان'
          ]
        : [
            'Process and fulfill your orders',
            'Improve our website and customer experience',
            'Communicate promotions, offers, and updates (if you opt-in)',
            'Prevent fraudulent transactions and enhance security'
          ]
    },
    {
      icon: <FiLock />,
      title: lang === 'ar' ? 'كيف نحمي معلوماتك' : 'How We Protect Your Information',
      content: lang === 'ar'
        ? [
            'نطبق التشفير المعياري في الصناعة والخوادم الآمنة لضمان أمان بياناتك',
            'لا يتم تخزين تفاصيل الدفع الخاصة بك على خوادمنا أبداً',
            'نستخدم بروتوكولات أمان متقدمة لحماية معلوماتك الشخصية',
            'يتم مراجعة أنظمة الأمان لدينا بانتظام وتحديثها'
          ]
        : [
            'We implement industry-standard encryption and secure servers to ensure your data is safe',
            'Your payment details are never stored on our servers',
            'We use advanced security protocols to protect your personal information',
            'Our security systems are regularly reviewed and updated'
          ]
    },
    {
      icon: <FiShield />,
      title: lang === 'ar' ? 'حقوقك' : 'Your Rights',
      content: lang === 'ar'
        ? [
            'الوصول إلى البيانات الشخصية التي نحتفظ بها عنك',
            'طلب التصحيحات أو الحذف',
            'إلغاء الاشتراك في رسائل التسويق في أي وقت',
            'نقل بياناتك إلى خدمة أخرى',
            'تقديم شكوى إلى السلطة المختصة'
          ]
        : [
            'Access the personal data we hold about you',
            'Request corrections or deletion',
            'Opt-out of marketing emails at any time',
            'Data portability to another service',
            'Lodge a complaint with the relevant authority'
          ]
    }
  ];

  return (
    <div className="container mx-auto py-6 sm:py-10 px-4 max-w-4xl">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center mb-12"
      >
        <h1 className="text-3xl sm:text-4xl font-bold mb-4 text-[#111]">
          {lang === 'ar' ? 'سياسة الخصوصية' : 'Privacy Policy'}
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          {lang === 'ar'
            ? 'في سوليفا، نقدر خصوصيتك ونلتزم بحماية بياناتك الشخصية. توضح سياسة الخصوصية هذه كيفية جمع واستخدام وحماية معلوماتك.'
            : 'At Soleva, we value your privacy and are committed to protecting your personal data. This Privacy Policy explains how we collect, use, and safeguard your information.'
          }
        </p>
        <div className="text-sm text-gray-500 mt-4">
          {lang === 'ar' ? 'آخر تحديث: ديسمبر 2024' : 'Last updated: December 2024'}
        </div>
      </motion.div>

      <div className="space-y-8">
        {sections.map((section, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <GlassCard>
              <div className="flex items-start gap-4 mb-4">
                <div className="w-12 h-12 bg-[#d1b16a]/20 rounded-full flex items-center justify-center text-[#d1b16a] flex-shrink-0">
                  {section.icon}
                </div>
                <h2 className="text-xl font-bold text-[#111] flex-1">
                  {section.title}
                </h2>
              </div>
              <ul className="space-y-3 text-gray-600 leading-relaxed">
                {section.content.map((item, itemIndex) => (
                  <li key={itemIndex} className="flex items-start gap-3">
                    <span className="w-2 h-2 bg-[#d1b16a] rounded-full mt-2 flex-shrink-0"></span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </GlassCard>
          </motion.div>
        ))}

        {/* Data Sharing Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <GlassCard>
            <h2 className="text-xl font-bold mb-4 text-[#111]">
              {lang === 'ar' ? 'مشاركة معلوماتك' : 'Sharing Your Information'}
            </h2>
            <div className="text-gray-600 leading-relaxed space-y-3">
              <p>
                {lang === 'ar'
                  ? 'نحن لا نبيع بياناتك الشخصية. نشاركها فقط مع الشركاء الموثوقين (معالجات الدفع، شركات التوصيل) لإكمال طلباتك.'
                  : 'We do not sell your personal data. We only share it with trusted partners (payment processors, delivery companies) to complete your orders.'
                }
              </p>
              <p>
                {lang === 'ar'
                  ? 'جميع شركائنا ملزمون بنفس معايير الخصوصية والأمان التي نلتزم بها.'
                  : 'All our partners are bound by the same privacy and security standards that we uphold.'
                }
              </p>
            </div>
          </GlassCard>
        </motion.div>

        {/* Contact Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <GlassCard className="bg-[#d1b16a]/10">
            <h2 className="text-xl font-bold mb-4 text-[#d1b16a]">
              {lang === 'ar' ? 'تواصل معنا' : 'Contact Us'}
            </h2>
            <p className="text-gray-600 leading-relaxed">
              {lang === 'ar'
                ? 'لأي استفسارات متعلقة بالخصوصية، يرجى التواصل معنا على:'
                : 'For any privacy-related inquiries, please contact us at:'
              }
            </p>
            <div className="mt-4 space-y-2">
              <div className="flex items-center gap-2">
                <span className="font-semibold">{lang === 'ar' ? 'البريد الإلكتروني:' : 'Email:'}</span>
                <a href="mailto:info@solevaeg.com" className="text-[#d1b16a] hover:underline">
                  info@solevaeg.com
                </a>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">{lang === 'ar' ? 'الهاتف:' : 'Phone:'}</span>
                <a href="tel:+201001234567" className="text-[#d1b16a] hover:underline">
                  +20 100 123 4567
                </a>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  );
}