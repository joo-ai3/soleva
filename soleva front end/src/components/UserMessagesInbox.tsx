import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiMail, FiMailOpen, FiStar, FiExternalLink, FiClock, 
  FiTag, FiZap, FiPackage, FiHeadphones, FiHeart, 
  FiBookOpen, FiMegaphone, FiSettings 
} from 'react-icons/fi';
import { useLang } from '../contexts/LangContext';
import { useAuth } from '../contexts/AuthContext';
import { UserMessage, websiteManagementApi } from '../services/websiteManagementApi';
import { formatDistanceToNow } from 'date-fns';
import { ar, enUS } from 'date-fns/locale';

const messageTypeIcons = {
  promotion: FiTag,
  flash_sale: FiZap,
  order_update: FiPackage,
  support_reply: FiHeadphones,
  welcome: FiHeart,
  newsletter: FiBookOpen,
  announcement: FiMegaphone,
  system: FiSettings,
};

const messageTypeColors = {
  promotion: 'text-purple-600 bg-purple-100 dark:bg-purple-900/30',
  flash_sale: 'text-orange-600 bg-orange-100 dark:bg-orange-900/30',
  order_update: 'text-blue-600 bg-blue-100 dark:bg-blue-900/30',
  support_reply: 'text-green-600 bg-green-100 dark:bg-green-900/30',
  welcome: 'text-pink-600 bg-pink-100 dark:bg-pink-900/30',
  newsletter: 'text-indigo-600 bg-indigo-100 dark:bg-indigo-900/30',
  announcement: 'text-cyan-600 bg-cyan-100 dark:bg-cyan-900/30',
  system: 'text-gray-600 bg-gray-100 dark:bg-gray-900/30',
};

interface UserMessagesInboxProps {
  className?: string;
}

export default function UserMessagesInbox({ className = '' }: UserMessagesInboxProps) {
  const { lang, t } = useLang();
  const { user } = useAuth();
  const [messages, setMessages] = useState<UserMessage[]>([]);
  const [selectedMessage, setSelectedMessage] = useState<UserMessage | null>(null);
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (user) {
      fetchMessages();
      fetchUnreadCount();
    }
  }, [user]);

  const fetchMessages = async () => {
    try {
      const data = await websiteManagementApi.getUserMessages();
      setMessages(data);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUnreadCount = async () => {
    try {
      const { unread_count } = await websiteManagementApi.getUnreadMessagesCount();
      setUnreadCount(unread_count);
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  };

  const handleMessageClick = async (message: UserMessage) => {
    setSelectedMessage(message);
    
    if (!message.is_read) {
      try {
        await websiteManagementApi.markMessageAsRead(message.id);
        // Update local state
        setMessages(prev => prev.map(msg => 
          msg.id === message.id ? { ...msg, is_read: true } : msg
        ));
        setUnreadCount(prev => Math.max(0, prev - 1));
      } catch (error) {
        console.error('Failed to mark message as read:', error);
      }
    }
  };

  const formatMessageDate = (dateString: string) => {
    const date = new Date(dateString);
    const locale = lang === 'ar' ? ar : enUS;
    return formatDistanceToNow(date, { addSuffix: true, locale });
  };

  if (!user) {
    return null;
  }

  if (loading) {
    return (
      <div className={`${className} animate-pulse`}>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-card rounded-lg p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gray-300 rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-300 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={`${className} space-y-6`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FiMail size={24} className="text-primary" />
          <h2 className="text-xl font-bold text-text-primary">
            {lang === 'ar' ? 'الرسائل' : 'Messages'}
          </h2>
          {unreadCount > 0 && (
            <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full min-w-[20px] text-center">
              {unreadCount}
            </span>
          )}
        </div>
      </div>

      {messages.length === 0 ? (
        <div className="text-center py-12 bg-card rounded-lg">
          <FiMail size={48} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-text-primary mb-2">
            {lang === 'ar' ? 'لا توجد رسائل' : 'No Messages'}
          </h3>
          <p className="text-text-secondary">
            {lang === 'ar' 
              ? 'ستظهر رسائلك هنا عندما نرسل لك تحديثات وعروض خاصة' 
              : 'Your messages will appear here when we send you updates and special offers'
            }
          </p>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Messages List */}
          <div className="lg:col-span-1 space-y-3 max-h-[600px] overflow-y-auto">
            <AnimatePresence>
              {messages.map((message) => (
                <MessageItem
                  key={message.id}
                  message={message}
                  isSelected={selectedMessage?.id === message.id}
                  onClick={() => handleMessageClick(message)}
                  lang={lang}
                  formatDate={formatMessageDate}
                />
              ))}
            </AnimatePresence>
          </div>

          {/* Message Detail */}
          <div className="lg:col-span-2">
            {selectedMessage ? (
              <MessageDetail
                message={selectedMessage}
                lang={lang}
                formatDate={formatMessageDate}
              />
            ) : (
              <div className="bg-card rounded-lg p-8 text-center">
                <FiMailOpen size={48} className="mx-auto text-gray-400 mb-4" />
                <p className="text-text-secondary">
                  {lang === 'ar' 
                    ? 'اختر رسالة لعرضها' 
                    : 'Select a message to view'
                  }
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

interface MessageItemProps {
  message: UserMessage;
  isSelected: boolean;
  onClick: () => void;
  lang: string;
  formatDate: (date: string) => string;
}

function MessageItem({ message, isSelected, onClick, lang, formatDate }: MessageItemProps) {
  const IconComponent = messageTypeIcons[message.message_type] || FiMail;
  const colorClass = messageTypeColors[message.message_type] || messageTypeColors.system;
  const subject = lang === 'ar' ? message.subject_ar : message.subject_en;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`
        bg-card rounded-lg p-4 cursor-pointer transition-all duration-200
        ${isSelected ? 'ring-2 ring-primary shadow-lg' : 'hover:shadow-md'}
        ${!message.is_read ? 'border-l-4 border-primary' : ''}
      `}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-full ${colorClass}`}>
          <IconComponent size={16} />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            {message.is_important && (
              <FiStar size={14} className="text-yellow-500 fill-current" />
            )}
            <h3 className={`text-sm font-medium truncate ${!message.is_read ? 'font-bold' : ''}`}>
              {subject}
            </h3>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-xs text-text-secondary">
              {formatDate(message.sent_at)}
            </span>
            
            {!message.is_read && (
              <div className="w-2 h-2 bg-primary rounded-full"></div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

interface MessageDetailProps {
  message: UserMessage;
  lang: string;
  formatDate: (date: string) => string;
}

function MessageDetail({ message, lang, formatDate }: MessageDetailProps) {
  const IconComponent = messageTypeIcons[message.message_type] || FiMail;
  const colorClass = messageTypeColors[message.message_type] || messageTypeColors.system;
  
  const subject = lang === 'ar' ? message.subject_ar : message.subject_en;
  const content = lang === 'ar' ? message.message_ar : message.message_en;
  const actionText = lang === 'ar' ? message.action_text_ar : message.action_text_en;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-card rounded-lg p-6 h-full"
    >
      {/* Header */}
      <div className="flex items-start gap-4 mb-6 pb-4 border-b border-border-primary">
        <div className={`p-3 rounded-full ${colorClass}`}>
          <IconComponent size={20} />
        </div>
        
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            {message.is_important && (
              <FiStar size={16} className="text-yellow-500 fill-current" />
            )}
            <h1 className="text-lg font-bold text-text-primary">{subject}</h1>
          </div>
          
          <div className="flex items-center gap-4 text-sm text-text-secondary">
            <span className="flex items-center gap-1">
              <FiClock size={14} />
              {formatDate(message.sent_at)}
            </span>
            {message.expires_at && (
              <span className="text-orange-600">
                {lang === 'ar' ? 'تنتهي' : 'Expires'}: {formatDate(message.expires_at)}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="prose prose-sm max-w-none dark:prose-invert mb-6">
        <div 
          className="text-text-primary leading-relaxed whitespace-pre-wrap"
          dangerouslySetInnerHTML={{ __html: content.replace(/\n/g, '<br>') }}
        />
      </div>

      {/* Action Button */}
      {message.action_url && actionText && (
        <div className="flex gap-3">
          <a
            href={message.action_url}
            className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
            target={message.action_url.startsWith('http') ? '_blank' : undefined}
            rel={message.action_url.startsWith('http') ? 'noopener noreferrer' : undefined}
          >
            {actionText}
            {message.action_url.startsWith('http') && (
              <FiExternalLink size={14} />
            )}
          </a>
        </div>
      )}

      {/* Attachment */}
      {message.attachment && (
        <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <a
            href={message.attachment}
            className="flex items-center gap-2 text-primary hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            <FiPackage size={16} />
            {lang === 'ar' ? 'مرفق' : 'Attachment'}
            <FiExternalLink size={14} />
          </a>
        </div>
      )}
    </motion.div>
  );
}
