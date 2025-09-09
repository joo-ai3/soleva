import { Link } from 'react-router-dom';
import { FiFacebook, FiInstagram, FiMail, FiPhone, FiMapPin, FiTwitter, FiYoutube } from 'react-icons/fi';
import { useLang, useTranslation } from '../contexts/LangContext';
import { useWebsite } from '../contexts/WebsiteContext';
import Logo from './Logo';


export default function AppFooter() {
  const { lang } = useLang();
  const t = useTranslation();
  const { siteConfig } = useWebsite();
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    company: [
      { label: t('aboutUs'), to: '/about' },
      { label: t('contactUs'), to: '/contact' },
      { label: lang === 'ar' ? 'سياسة الخصوصية' : 'Privacy Policy', to: '/privacy' },
      { label: lang === 'ar' ? 'الشروط والأحكام' : 'Terms & Conditions', to: '/terms' }
    ],
    shop: [
      { label: t('products'), to: '/products' },
      { label: t('favorites'), to: '/favorites' },
      { label: t('cart'), to: '/cart' },
      { label: t('orders'), to: '/orders' }
    ],
    support: [
      { label: lang === 'ar' ? 'تتبع الطلب' : 'Track Order', to: '/track-order' },
      { label: lang === 'ar' ? 'مركز المساعدة' : 'Help Center', to: '/help' },
      { label: lang === 'ar' ? 'الشحن والتوصيل' : 'Shipping & Delivery', to: '/shipping' },
      { label: lang === 'ar' ? 'الإرجاع والاستبدال' : 'Returns & Exchanges', to: '/returns' },
      { label: lang === 'ar' ? 'دليل المقاسات' : 'Size Guide', to: '/size-guide' }
    ]
  };

  const contactInfo = [
    {
      icon: <FiPhone size={16} />,
      text: siteConfig?.phone_number || '+20 100 123 4567',
      href: `tel:${siteConfig?.phone_number || '+201001234567'}`
    },
    {
      icon: <FiMail size={16} />,
      text: siteConfig?.primary_email || 'info@solevaeg.com',
      href: `mailto:${siteConfig?.primary_email || 'info@solevaeg.com'}`
    },
    {
      icon: <FiMapPin size={16} />,
      text: lang === 'ar' ? (siteConfig?.address_ar || 'القاهرة، مصر') : (siteConfig?.address_en || 'Cairo, Egypt'),
      href: null
    }
  ];

  const socialLinks = [
    siteConfig?.facebook_url && {
      icon: <FiFacebook size={20} />,
      href: siteConfig.facebook_url,
      label: 'Facebook'
    },
    siteConfig?.instagram_url && {
      icon: <FiInstagram size={20} />,
      href: siteConfig.instagram_url,
      label: 'Instagram'
    },
    siteConfig?.twitter_url && {
      icon: <FiTwitter size={20} />,
      href: siteConfig.twitter_url,
      label: 'Twitter'
    },
    siteConfig?.youtube_url && {
      icon: <FiYoutube size={20} />,
      href: siteConfig.youtube_url,
      label: 'YouTube'
    }
  ].filter((link): link is { icon: JSX.Element; href: string; label: string } => Boolean(link));

  return (
    <footer className="section bg-bg-secondary border-t border-border-primary" role="contentinfo">
      <div className="container">
        <div className="modern-glass-card p-8 lg:p-12 rounded-2xl">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
            {/* Brand Section */}
            <div className="lg:col-span-1">
              <Logo size="medium" className="mb-6" />
              <p className="text-text-secondary mb-6 leading-relaxed">
                {lang === 'ar'
                  ? (siteConfig?.site_description_ar || 'سوليفا - علامة تجارية مصرية رائدة في صناعة الأحذية الفاخرة. نقدم لك أفضل المنتجات بجودة عالية وتصميم عصري.')
                  : (siteConfig?.site_description_en || 'Soleva - A leading Egyptian brand in premium footwear manufacturing. We offer you the best products with high quality and modern design.')
                }
              </p>
              
              {/* Social Links */}
              <div className="flex gap-3">
                {socialLinks.map((social, index) => (
                  <a
                    key={index}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-10 h-10 modern-glass-button hover:bg-primary hover:text-black rounded-full flex items-center justify-center transition-all duration-300"
                    aria-label={social.label}
                  >
                    {social.icon}
                  </a>
                ))}
              </div>
            </div>

            {/* Company Links */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-text-primary">
                {lang === 'ar' ? 'الشركة' : 'Company'}
              </h3>
              <ul className="space-y-3">
                {footerLinks.company.map((link, index) => (
                  <li key={index}>
                    <Link
                      to={link.to}
                      className="text-text-secondary hover:text-primary transition-colors duration-200"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Shop Links */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-text-primary">
                {lang === 'ar' ? 'التسوق' : 'Shop'}
              </h3>
              <ul className="space-y-3">
                {footerLinks.shop.map((link, index) => (
                  <li key={index}>
                    <Link
                      to={link.to}
                      className="text-text-secondary hover:text-primary transition-colors duration-200"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Contact Info */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-text-primary">
                {lang === 'ar' ? 'تواصل معنا' : 'Contact Us'}
              </h3>
              <ul className="space-y-3">
                {contactInfo.map((contact, index) => (
                  <li key={index} className="flex items-center gap-3">
                    <span className="text-primary">{contact.icon}</span>
                    {contact.href ? (
                      <a
                        href={contact.href}
                        className="text-text-secondary hover:text-primary transition-colors duration-200"
                      >
                        {contact.text}
                      </a>
                    ) : (
                      <span className="text-text-secondary">{contact.text}</span>
                    )}
                  </li>
                ))}
              </ul>

              {/* Business Hours */}
              <div className="mt-6">
                <h4 className="font-semibold mb-2 text-text-primary">
                  {lang === 'ar' ? 'ساعات العمل' : 'Business Hours'}
                </h4>
                <div className="text-sm text-text-secondary space-y-1">
                  <div className="flex justify-between">
                    <span>{lang === 'ar' ? 'السبت - الخميس' : 'Sat - Thu'}:</span>
                    <span>9:00 AM - 8:00 PM</span>
                  </div>
                  <div className="flex justify-between">
                    <span>{lang === 'ar' ? 'الجمعة' : 'Friday'}:</span>
                    <span>2:00 PM - 8:00 PM</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Section */}
          <div className="pt-8 border-t border-border-secondary">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <p className="text-text-secondary text-sm text-center md:text-left">
                {lang === 'ar'
                  ? `© ${currentYear} جميع الحقوق محفوظة لـ ${siteConfig?.site_name_ar || 'سوليفا'}. مقر الشركة: ${siteConfig?.address_ar || 'القاهرة، مصر'}.`
                  : `© ${currentYear} All rights reserved for ${siteConfig?.site_name_en || 'Soleva'}. Headquarters: ${siteConfig?.address_en || 'Cairo, Egypt'}.`
                }
              </p>
              
              <div className="flex items-center gap-4 text-sm text-text-secondary">
                <span>{lang === 'ar' ? 'صُنع بـ' : 'Made with'}</span>
                <span className="text-red-500">♥</span>
                <span>{lang === 'ar' ? 'في مصر' : 'in Egypt'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}