import { apiService } from './api';

export interface WebsiteSection {
  id: string;
  name: string;
  section_type: string;
  title_en: string;
  title_ar: string;
  subtitle_en: string;
  subtitle_ar: string;
  content_en: string;
  content_ar: string;
  image?: string;
  background_image?: string;
  video_url?: string;
  cta_text_en: string;
  cta_text_ar: string;
  cta_url: string;
  is_active: boolean;
  display_order: number;
  background_color: string;
  text_color: string;
  custom_css: string;
  created_at: string;
  updated_at: string;
}

export interface SiteConfiguration {
  site_name_en: string;
  site_name_ar: string;
  site_description_en: string;
  site_description_ar: string;
  primary_email: string;
  support_email: string;
  sales_email: string;
  business_email: string;
  phone_number: string;
  whatsapp_number: string;
  address_en: string;
  address_ar: string;
  facebook_url: string;
  instagram_url: string;
  twitter_url: string;
  youtube_url: string;
  tiktok_url: string;
  business_hours: string;
  shipping_info_en: string;
  shipping_info_ar: string;
  return_policy_en: string;
  return_policy_ar: string;
  created_at: string;
  updated_at: string;
}

export interface NotificationBanner {
  id: string;
  title: string;
  message_en: string;
  message_ar: string;
  banner_type: 'info' | 'warning' | 'success' | 'error' | 'promotion' | 'flash_sale' | 'announcement';
  display_location: 'top' | 'header' | 'footer' | 'sidebar' | 'popup' | 'all_pages' | 'homepage' | 'product_pages' | 'checkout';
  is_active: boolean;
  is_dismissible: boolean;
  auto_hide_after?: number;
  background_color: string;
  text_color: string;
  icon: string;
  cta_text_en: string;
  cta_text_ar: string;
  cta_url: string;
  priority: number;
  should_display: boolean;
  is_scheduled_active: boolean;
}

export interface UserMessage {
  id: string;
  user: string;
  user_email: string;
  user_name: string;
  subject_en: string;
  subject_ar: string;
  message_en: string;
  message_ar: string;
  message_type: 'promotion' | 'flash_sale' | 'order_update' | 'support_reply' | 'welcome' | 'newsletter' | 'announcement' | 'system';
  is_read: boolean;
  is_important: boolean;
  attachment?: string;
  action_url: string;
  action_text_en: string;
  action_text_ar: string;
  related_order?: string;
  related_product?: string;
  sent_at: string;
  read_at?: string;
  expires_at?: string;
}

export const websiteManagementApi = {
  // Website Sections
  getSections: async (sectionType?: string): Promise<WebsiteSection[]> => {
    const params = sectionType ? { section_type: sectionType } : {};
    const response = await apiService.get('/website/sections/', { params });
    return response.data;
  },

  // Site Configuration
  getSiteConfig: async (): Promise<SiteConfiguration> => {
    const response = await apiService.get('/website/config/');
    return response.data;
  },

  // Notification Banners
  getBanners: async (location?: string): Promise<NotificationBanner[]> => {
    const params = location ? { location } : {};
    const response = await apiService.get('/website/banners/', { params });
    return response.data;
  },

  // User Messages
  getUserMessages: async (): Promise<UserMessage[]> => {
    const response = await apiService.get('/website/user/messages/');
    return response.data;
  },

  getUserMessage: async (messageId: string): Promise<UserMessage> => {
    const response = await apiService.get(`/website/user/messages/${messageId}/`);
    return response.data;
  },

  markMessageAsRead: async (messageId: string): Promise<void> => {
    await apiService.post(`/website/user/messages/${messageId}/mark-read/`);
  },

  getUnreadMessagesCount: async (): Promise<{ unread_count: number }> => {
    const response = await apiService.get('/website/user/messages/unread-count/');
    return response.data;
  },
};

// Cache for site configuration
let siteConfigCache: SiteConfiguration | null = null;
let siteConfigCacheTime = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export const getCachedSiteConfig = async (): Promise<SiteConfiguration> => {
  const now = Date.now();
  
  if (siteConfigCache && (now - siteConfigCacheTime) < CACHE_DURATION) {
    return siteConfigCache;
  }
  
  try {
    siteConfigCache = await websiteManagementApi.getSiteConfig();
    siteConfigCacheTime = now;
    return siteConfigCache;
  } catch {
    // Return default configuration if API fails
    return {
      site_name_en: 'Soleva',
      site_name_ar: 'سوليفا',
      site_description_en: 'Premium Fashion & Lifestyle',
      site_description_ar: 'أزياء وأسلوب حياة مميز',
      primary_email: 'info@solevaeg.com',
      support_email: 'support@solevaeg.com',
      sales_email: 'sales@solevaeg.com',
      business_email: 'business@solevaeg.com',
      phone_number: '+20 100 123 4567',
      whatsapp_number: '+20 100 123 4567',
      address_en: 'Cairo, Egypt',
      address_ar: 'القاهرة، مصر',
      facebook_url: 'https://www.facebook.com/share/1BNS1QbzkP/',
      instagram_url: 'https://www.instagram.com/soleva.eg',
      twitter_url: '',
      youtube_url: '',
      tiktok_url: '',
      business_hours: '9 AM - 6 PM',
      shipping_info_en: 'Free shipping on orders over 500 EGP',
      shipping_info_ar: 'شحن مجاني للطلبات أكثر من 500 جنيه',
      return_policy_en: '30-day return policy',
      return_policy_ar: 'سياسة الإرجاع خلال 30 يوم',
      created_at: '',
      updated_at: ''
    };
  }
};
