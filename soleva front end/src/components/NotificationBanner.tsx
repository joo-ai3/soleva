import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiInfo, FiAlertTriangle, FiCheckCircle, FiAlertCircle, FiTag, FiZap, FiMegaphone } from 'react-icons/fi';
import { useLang } from '../contexts/LangContext';
import { NotificationBanner as NotificationBannerType, websiteManagementApi } from '../services/websiteManagementApi';

interface NotificationBannerProps {
  location: string;
}

const bannerIcons = {
  info: FiInfo,
  warning: FiAlertTriangle,
  success: FiCheckCircle,
  error: FiAlertCircle,
  promotion: FiTag,
  flash_sale: FiZap,
  announcement: FiMegaphone,
};

const bannerColors = {
  info: {
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    border: 'border-blue-200 dark:border-blue-800',
    text: 'text-blue-800 dark:text-blue-200',
    icon: 'text-blue-600 dark:text-blue-400',
  },
  warning: {
    bg: 'bg-yellow-50 dark:bg-yellow-900/20',
    border: 'border-yellow-200 dark:border-yellow-800',
    text: 'text-yellow-800 dark:text-yellow-200',
    icon: 'text-yellow-600 dark:text-yellow-400',
  },
  success: {
    bg: 'bg-green-50 dark:bg-green-900/20',
    border: 'border-green-200 dark:border-green-800',
    text: 'text-green-800 dark:text-green-200',
    icon: 'text-green-600 dark:text-green-400',
  },
  error: {
    bg: 'bg-red-50 dark:bg-red-900/20',
    border: 'border-red-200 dark:border-red-800',
    text: 'text-red-800 dark:text-red-200',
    icon: 'text-red-600 dark:text-red-400',
  },
  promotion: {
    bg: 'bg-purple-50 dark:bg-purple-900/20',
    border: 'border-purple-200 dark:border-purple-800',
    text: 'text-purple-800 dark:text-purple-200',
    icon: 'text-purple-600 dark:text-purple-400',
  },
  flash_sale: {
    bg: 'bg-orange-50 dark:bg-orange-900/20',
    border: 'border-orange-200 dark:border-orange-800',
    text: 'text-orange-800 dark:text-orange-200',
    icon: 'text-orange-600 dark:text-orange-400',
  },
  announcement: {
    bg: 'bg-indigo-50 dark:bg-indigo-900/20',
    border: 'border-indigo-200 dark:border-indigo-800',
    text: 'text-indigo-800 dark:text-indigo-200',
    icon: 'text-indigo-600 dark:text-indigo-400',
  },
};

export default function NotificationBanner({ location }: NotificationBannerProps) {
  const { lang } = useLang();
  const [banners, setBanners] = useState<NotificationBannerType[]>([]);
  const [dismissedBanners, setDismissedBanners] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBanners = async () => {
      try {
        const data = await websiteManagementApi.getBanners(location);
        setBanners(data.filter(banner => banner.should_display));
      } catch (error) {
        console.error('Failed to fetch notification banners:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBanners();
  }, [location]);

  useEffect(() => {
    // Load dismissed banners from localStorage
    const dismissed = localStorage.getItem('dismissed_banners');
    if (dismissed) {
      setDismissedBanners(new Set(JSON.parse(dismissed)));
    }
  }, []);

  const dismissBanner = (bannerId: string) => {
    const newDismissed = new Set(dismissedBanners).add(bannerId);
    setDismissedBanners(newDismissed);
    localStorage.setItem('dismissed_banners', JSON.stringify(Array.from(newDismissed)));
  };

  const visibleBanners = banners.filter(banner => !dismissedBanners.has(banner.id));

  if (loading || visibleBanners.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2">
      <AnimatePresence>
        {visibleBanners.map((banner) => (
          <NotificationBannerItem
            key={banner.id}
            banner={banner}
            lang={lang}
            onDismiss={() => dismissBanner(banner.id)}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}

interface NotificationBannerItemProps {
  banner: NotificationBannerType;
  lang: string;
  onDismiss: () => void;
}

function NotificationBannerItem({ banner, lang, onDismiss }: NotificationBannerItemProps) {
  const [isVisible, setIsVisible] = useState(true);
  const [timeLeft, setTimeLeft] = useState<number | null>(null);

  const IconComponent = bannerIcons[banner.banner_type] || FiInfo;
  const colors = bannerColors[banner.banner_type] || bannerColors.info;
  
  const message = lang === 'ar' ? banner.message_ar : banner.message_en;
  const ctaText = lang === 'ar' ? banner.cta_text_ar : banner.cta_text_en;

  useEffect(() => {
    if (banner.auto_hide_after) {
      setTimeLeft(banner.auto_hide_after);
      
      const interval = setInterval(() => {
        setTimeLeft(prev => {
          if (prev === null || prev <= 1) {
            setIsVisible(false);
            setTimeout(onDismiss, 300); // Wait for animation to complete
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [banner.auto_hide_after, onDismiss]);

  if (!isVisible) return null;

  const customStyles = {
    backgroundColor: banner.background_color || undefined,
    color: banner.text_color || undefined,
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -50, scale: 0.95 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`
        relative overflow-hidden rounded-lg border p-4
        ${banner.background_color ? '' : colors.bg}
        ${banner.background_color ? '' : colors.border}
        ${banner.text_color ? '' : colors.text}
      `}
      style={customStyles}
    >
      <div className="flex items-start gap-3">
        <div className={`flex-shrink-0 ${banner.text_color ? '' : colors.icon}`}>
          <IconComponent size={20} />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <p className="text-sm font-medium leading-relaxed">
                {message}
              </p>
              
              {banner.cta_url && ctaText && (
                <div className="mt-3">
                  <a
                    href={banner.cta_url}
                    className={`
                      inline-flex items-center px-3 py-1.5 text-xs font-medium
                      rounded-full transition-colors duration-200
                      ${banner.text_color 
                        ? 'bg-white/20 hover:bg-white/30 text-current' 
                        : `${colors.bg} ${colors.text} hover:opacity-80`
                      }
                    `}
                    target={banner.cta_url.startsWith('http') ? '_blank' : undefined}
                    rel={banner.cta_url.startsWith('http') ? 'noopener noreferrer' : undefined}
                  >
                    {ctaText}
                  </a>
                </div>
              )}
            </div>
            
            <div className="flex items-center gap-2">
              {timeLeft !== null && timeLeft > 0 && (
                <span className="text-xs opacity-75 font-mono">
                  {timeLeft}s
                </span>
              )}
              
              {banner.is_dismissible && (
                <button
                  onClick={onDismiss}
                  className={`
                    flex-shrink-0 p-1 rounded-full transition-colors duration-200
                    ${banner.text_color 
                      ? 'hover:bg-white/20 text-current' 
                      : `hover:bg-gray-200 dark:hover:bg-gray-700 ${colors.text}`
                    }
                  `}
                  aria-label="Dismiss notification"
                >
                  <FiX size={16} />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Progress bar for auto-hide */}
      {banner.auto_hide_after && timeLeft !== null && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/10">
          <motion.div
            className="h-full bg-current opacity-30"
            initial={{ width: '100%' }}
            animate={{ width: '0%' }}
            transition={{ duration: banner.auto_hide_after, ease: 'linear' }}
          />
        </div>
      )}
    </motion.div>
  );
}
