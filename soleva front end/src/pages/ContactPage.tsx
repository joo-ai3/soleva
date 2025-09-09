import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FiMail, FiPhone, FiMapPin, FiSend } from 'react-icons/fi';
import { useLang, useTranslation } from '../contexts/LangContext';
import { useToast } from '../contexts/ToastContext';
import GlassCard from '../components/GlassCard';
import GlassButton from '../components/GlassButton';

export default function ContactPage() {
  const { lang } = useLang();
  const t = useTranslation();
  const { showToast } = useToast();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 1000));

    showToast(lang === 'ar' ? 'تم إرسال رسالتك بنجاح!' : 'Message sent successfully!');
    setFormData({ name: '', email: '', subject: '', message: '' });
    setIsSubmitting(false);
  };

  const contactInfo = [
    {
      icon: <FiPhone />,
      title: lang === 'ar' ? 'الهاتف' : 'Phone',
      value: '+20 100 123 4567',
      link: 'tel:+201001234567'
    },
    {
      icon: <FiMail />,
      title: lang === 'ar' ? 'البريد الإلكتروني' : 'Email',
      value: 'info@solevaeg.com',
      link: 'mailto:info@solevaeg.com'
    },
    {
      icon: <FiMapPin />,
      title: lang === 'ar' ? 'العنوان' : 'Address',
      value: lang === 'ar' ? 'القاهرة، مصر' : 'Cairo, Egypt',
      link: null
    }
  ];

  return (
    <div className="container mx-auto py-6 sm:py-10 px-4 max-w-6xl">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center mb-12"
      >
        <h1 className="text-3xl sm:text-4xl font-bold mb-4 text-[#111]">
          {t("contactUs")}
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          {lang === 'ar' 
            ? 'نحن هنا لمساعدتك. تواصل معنا وسنرد عليك في أقرب وقت ممكن.'
            : 'We\'re here to help. Get in touch with us and we\'ll respond as soon as possible.'
          }
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
        {/* Contact Information */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <GlassCard>
            <h2 className="text-2xl font-bold mb-6 text-[#d1b16a]">
              {t("contactInfo")}
            </h2>
            
            <div className="space-y-6">
              {contactInfo.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                  className="flex items-center gap-4 p-4 glass rounded-xl hover:shadow-lg transition-all"
                >
                  <div className="w-12 h-12 bg-[#d1b16a]/20 rounded-full flex items-center justify-center text-[#d1b16a]">
                    {item.icon}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-700">{item.title}</div>
                    {item.link ? (
                      <a 
                        href={item.link}
                        className="text-[#d1b16a] hover:text-[#d1b16a]/80 transition-colors"
                      >
                        {item.value}
                      </a>
                    ) : (
                      <div className="text-gray-600">{item.value}</div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="mt-8 p-6 glass rounded-xl bg-[#d1b16a]/10">
              <h3 className="font-bold text-lg mb-3 text-[#d1b16a]">
                {lang === 'ar' ? 'ساعات العمل' : 'Business Hours'}
              </h3>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>{lang === 'ar' ? 'السبت - الخميس' : 'Saturday - Thursday'}:</span>
                  <span>9:00 AM - 8:00 PM</span>
                </div>
                <div className="flex justify-between">
                  <span>{lang === 'ar' ? 'الجمعة' : 'Friday'}:</span>
                  <span>2:00 PM - 8:00 PM</span>
                </div>
              </div>
            </div>
          </GlassCard>
        </motion.div>

        {/* Contact Form */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <GlassCard>
            <h2 className="text-2xl font-bold mb-6 text-[#d1b16a]">
              {t("sendMessage")}
            </h2>

            <form onSubmit={handleSubmit} className="contact-form space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {t("name")}
                  </label>
                  <input
                    className="w-full glass border border-[#d1b16a]/40 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#d1b16a] transition-all min-w-0"
                    type="text"
                    required
                    value={formData.name}
                    onChange={e => setFormData({...formData, name: e.target.value})}
                    placeholder={lang === 'ar' ? 'اسمك الكامل' : 'Your full name'}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {t("email")}
                  </label>
                  <input
                    className="w-full glass border border-[#d1b16a]/40 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#d1b16a] transition-all min-w-0"
                    type="email"
                    required
                    value={formData.email}
                    onChange={e => setFormData({...formData, email: e.target.value})}
                    placeholder={lang === 'ar' ? 'بريدك الإلكتروني' : 'Your email address'}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {t("subject")}
                </label>
                <input
                  className="w-full glass border border-[#d1b16a]/40 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#d1b16a] transition-all min-w-0"
                  type="text"
                  required
                  value={formData.subject}
                  onChange={e => setFormData({...formData, subject: e.target.value})}
                  placeholder={lang === 'ar' ? 'موضوع الرسالة' : 'Message subject'}
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {t("yourMessage")}
                </label>
                <textarea
                  className="w-full glass border border-[#d1b16a]/40 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#d1b16a] transition-all resize-none min-w-0"
                  rows={6}
                  required
                  value={formData.message}
                  onChange={e => setFormData({...formData, message: e.target.value})}
                  placeholder={lang === 'ar' ? 'اكتب رسالتك هنا...' : 'Write your message here...'}
                />
              </div>

              <GlassButton
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-[#d1b16a] text-black border-none hover:bg-[#d1b16a]/80 text-lg py-4 min-h-[56px] font-bold hover:scale-105 transition-all duration-300"
              >
                {isSubmitting ? (
                  <div className="w-6 h-6 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                ) : (
                  <>
                    <FiSend />
                    {t("sendMessage")}
                  </>
                )}
              </GlassButton>
            </form>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  );
}