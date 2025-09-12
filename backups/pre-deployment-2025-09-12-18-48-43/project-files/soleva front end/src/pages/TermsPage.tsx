import React from 'react';
import { motion } from 'framer-motion';
import { FiFileText, FiCreditCard, FiTruck, FiRotateCcw, FiShield, FiFile } from 'react-icons/fi';
import { useLang } from '../contexts/LangContext';
import GlassCard from '../components/GlassCard';

export default function TermsPage() {
  const { lang } = useLang();


  const sections = [
    {
      icon: <FiFileText />,
      title: lang === 'ar' ? 'عام' : 'General',
      content: lang === 'ar'
        ? [
            'تحكم هذه الشروط جميع المبيعات واستخدام موقعنا الإلكتروني',
            'يمكننا تحديث هذه الشروط في أي وقت دون إشعار مسبق',
            'باستخدام موقعنا، فإنك توافق على الالتزام بهذه الشروط والأحكام',
            'إذا كنت لا توافق على أي من هذه الشروط، يرجى عدم استخدام خدماتنا'
          ]
        : [
            'These terms govern all sales and use of our website',
            'We may update these terms at any time without prior notice',
            'By using our website, you agree to comply with these terms and conditions',
            'If you do not agree to any of these terms, please do not use our services'
          ]
    },
    {
      icon: <FiCreditCard />,
      title: lang === 'ar' ? 'المنتجات والأسعار' : 'Products & Pricing',
      content: lang === 'ar'
        ? [
            'جميع الأسعار معروضة بالجنيه المصري وتشمل الضرائب المطبقة ما لم يُذكر خلاف ذلك',
            'نحتفظ بالحق في تغيير أسعار المنتجات في أي وقت',
            'يتم تأكيد الطلبات فقط بعد استلام الدفع',
            'نحتفظ بالحق في إلغاء الطلبات المشتبه في أنشطة احتيالية'
          ]
        : [
            'All prices are displayed in Egyptian Pounds (EGP) and include applicable taxes unless stated otherwise',
            'We reserve the right to change product prices at any time',
            'Orders are only confirmed once payment is received',
            'We reserve the right to cancel orders suspected of fraudulent activity'
          ]
    },
    {
      icon: <FiTruck />,
      title: lang === 'ar' ? 'الشحن والتوصيل' : 'Shipping & Delivery',
      content: lang === 'ar'
        ? [
            'أوقات التسليم تقديرية وقد تختلف حسب الموقع',
            'نحن غير مسؤولين عن التأخير الناجم عن شركات الشحن أو الظروف غير المتوقعة',
            'الشحن مجاني للطلبات التي تزيد عن 500 جنيه مصري',
            'يتم التوصيل خلال 3-7 أيام عمل داخل القاهرة والجيزة'
          ]
        : [
            'Delivery times are estimates and may vary depending on location',
            'We are not responsible for delays caused by couriers or unforeseen circumstances',
            'Free shipping on orders over 500 EGP',
            'Delivery within 3-7 business days in Cairo and Giza'
          ]
    },
    {
      icon: <FiRotateCcw />,
      title: lang === 'ar' ? 'الإرجاع والاستبدال' : 'Returns & Refunds',
      content: lang === 'ar'
        ? [
            'يمكنك إرجاع المنتجات خلال 14 يوماً إذا كانت غير مستخدمة وفي العبوة الأصلية',
            'سيتم معالجة المبالغ المستردة إلى طريقة الدفع الأصلية',
            'المنتجات المخصصة أو المخفضة غير قابلة للإرجاع',
            'يتحمل العميل تكلفة الإرجاع ما لم يكن المنتج معيباً'
          ]
        : [
            'You may return items within 14 days if they are unused and in original packaging',
            'Refunds will be processed to your original payment method',
            'Customized or clearance items are non-refundable',
            'Customer bears return shipping costs unless the item is defective'
          ]
    },
    {
      icon: <FiShield />,
      title: lang === 'ar' ? 'حدود المسؤولية' : 'Limitation of Liability',
      content: lang === 'ar'
        ? [
            'نحن غير مسؤولين عن أي أضرار غير مباشرة ناشئة عن استخدام منتجاتنا أو موقعنا',
            'مسؤوليتنا محدودة بقيمة المنتج المشترى',
            'لا نضمن أن الموقع سيكون متاحاً دون انقطاع أو خالياً من الأخطاء',
            'استخدامك للموقع على مسؤوليتك الخاصة'
          ]
        : [
            'We are not liable for any indirect damages arising from the use of our products or website',
            'Our liability is limited to the value of the purchased product',
            'We do not guarantee that the website will be available without interruption or error-free',
            'Your use of the website is at your own risk'
          ]
    },
    {
      icon: <FiFile />,
      title: lang === 'ar' ? 'القانون الحاكم' : 'Governing Law',
      content: lang === 'ar'
        ? [
            'تخضع هذه الشروط لقوانين جمهورية مصر العربية',
            'أي نزاع ينشأ عن هذه الشروط يخضع لاختصاص المحاكم المصرية',
            'إذا كان أي جزء من هذه الشروط غير قانوني، فإن باقي الشروط تبقى سارية',
            'هذه الشروط تشكل الاتفاقية الكاملة بيننا وبينك'
          ]
        : [
            'These terms shall be governed by the laws of the Arab Republic of Egypt',
            'Any dispute arising from these terms is subject to the jurisdiction of Egyptian courts',
            'If any part of these terms is deemed unlawful, the remaining terms remain in effect',
            'These terms constitute the entire agreement between us and you'
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
          {lang === 'ar' ? 'الشروط والأحكام' : 'Terms & Conditions'}
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          {lang === 'ar'
            ? 'مرحباً بك في سوليفا. باستخدام موقعنا وخدماتنا، فإنك توافق على الالتزام بالشروط والأحكام التالية.'
            : 'Welcome to Soleva. By using our website and services, you agree to comply with the following terms and conditions.'
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

        {/* Additional Information */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <GlassCard className="bg-[#d1b16a]/10">
            <h2 className="text-xl font-bold mb-4 text-[#d1b16a]">
              {lang === 'ar' ? 'معلومات إضافية' : 'Additional Information'}
            </h2>
            <div className="text-gray-600 leading-relaxed space-y-3">
              <p>
                {lang === 'ar'
                  ? 'لأي استفسارات حول هذه الشروط والأحكام، يرجى التواصل معنا:'
                  : 'For any questions about these terms and conditions, please contact us:'
                }
              </p>
              <div className="space-y-2">
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
                <div className="flex items-center gap-2">
                  <span className="font-semibold">{lang === 'ar' ? 'العنوان:' : 'Address:'}</span>
                  <span>{lang === 'ar' ? 'القاهرة، مصر' : 'Cairo, Egypt'}</span>
                </div>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  );
}