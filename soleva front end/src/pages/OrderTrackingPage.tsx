import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FiBox, FiTruck, FiCheckCircle, FiClock, FiPackage, 
  FiMapPin, FiPhone, FiMail, FiCalendar, FiArrowLeft,
  FiAlertCircle, FiEye
} from 'react-icons/fi';
import { useLang, useTranslation } from '../contexts/LangContext';
import { apiService } from '../services/api';
import GlassCard from '../components/GlassCard';
import GlassButton from '../components/GlassButton';
import LoadingSkeleton from '../components/LoadingSkeleton';
import SectionTitle from '../components/SectionTitle';

interface TrackingTimeline {
  status: string;
  status_display: string;
  timestamp: string;
  comment?: string;
}

interface OrderTracking {
  order_number: string;
  status: string;
  status_display: string;
  tracking_number?: string;
  courier_company?: string;
  estimated_delivery_date?: string;
  timeline: TrackingTimeline[];
  current_location?: string;
  last_update: string;
}

export default function OrderTrackingPage() {
  const { orderNumber } = useParams<{ orderNumber: string }>();
  const navigate = useNavigate();
  const { lang } = useLang();
  const t = useTranslation();
  
  const [tracking, setTracking] = useState<OrderTracking | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [orderNum, setOrderNum] = useState(orderNumber || '');

  useEffect(() => {
    if (orderNumber) {
      // If order number is in URL, load tracking immediately
      fetchTracking(orderNumber);
    }
  }, [orderNumber]);

  const fetchTracking = async (orderNumber: string, customerEmail?: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({ order_number: orderNumber });
      if (customerEmail) {
        params.append('email', customerEmail);
      }
      
      const response = await apiService.get<OrderTracking>(`/orders/track/?${params}`);
      
      if (response.success && response.data) {
        setTracking(response.data);
      } else {
        setError(typeof response.error === 'string' ? response.error : response.error?.message || 'Order not found');
      }
    } catch (error) {
      setError('Failed to fetch tracking information');
      console.error('Tracking error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTrackOrder = (e: React.FormEvent) => {
    e.preventDefault();
    if (orderNum.trim() && email.trim()) {
      fetchTracking(orderNum.trim(), email.trim());
      // Update URL
      navigate(`/track-order/${orderNum.trim()}`, { replace: true });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <FiClock className="h-5 w-5 text-yellow-500" />;
      case 'confirmed':
        return <FiCheckCircle className="h-5 w-5 text-blue-500" />;
      case 'processing':
        return <FiPackage className="h-5 w-5 text-purple-500" />;
      case 'shipped':
        return <FiTruck className="h-5 w-5 text-orange-500" />;
      case 'out_for_delivery':
        return <FiTruck className="h-5 w-5 text-green-500" />;
      case 'delivered':
        return <FiCheckCircle className="h-5 w-5 text-green-600" />;
      case 'cancelled':
        return <FiAlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <FiBox className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'confirmed': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'processing': return 'text-purple-600 bg-purple-50 border-purple-200';
      case 'shipped': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'out_for_delivery': return 'text-green-600 bg-green-50 border-green-200';
      case 'delivered': return 'text-green-700 bg-green-100 border-green-300';
      case 'cancelled': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(lang === 'ar' ? 'ar-EG' : 'en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!tracking && !loading && !error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4 max-w-md">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <FiBox size={64} className="mx-auto mb-4 text-[#d1b16a]" />
            <SectionTitle className="mb-2">{t('Track Your Order')}</SectionTitle>
            <p className="text-gray-600">
              {lang === 'ar' 
                ? 'أدخل رقم الطلب والبريد الإلكتروني لتتبع طلبك'
                : 'Enter your order number and email to track your order'
              }
            </p>
          </motion.div>

          <GlassCard>
            <form onSubmit={handleTrackOrder} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {lang === 'ar' ? 'رقم الطلب' : 'Order Number'}
                </label>
                <input
                  type="text"
                  value={orderNum}
                  onChange={(e) => setOrderNum(e.target.value)}
                  placeholder={lang === 'ar' ? 'أدخل رقم الطلب' : 'Enter order number'}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#d1b16a] focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {lang === 'ar' ? 'البريد الإلكتروني' : 'Email Address'}
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={lang === 'ar' ? 'أدخل البريد الإلكتروني' : 'Enter email address'}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#d1b16a] focus:border-transparent"
                  required
                />
              </div>

              <GlassButton
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    {lang === 'ar' ? 'جاري البحث...' : 'Tracking...'}
                  </>
                ) : (
                  <>
                    <FiEye className="h-4 w-4" />
                    {lang === 'ar' ? 'تتبع الطلب' : 'Track Order'}
                  </>
                )}
              </GlassButton>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                  {error}
                </div>
              )}
            </form>
          </GlassCard>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-4 mb-4">
            <GlassButton
              onClick={() => navigate(-1)}
              className="flex items-center gap-2"
            >
              <FiArrowLeft className="h-4 w-4" />
              {lang === 'ar' ? 'رجوع' : 'Back'}
            </GlassButton>
          </div>
          
          <SectionTitle className="mb-2">
            {lang === 'ar' ? 'تتبع الطلب' : 'Order Tracking'}
          </SectionTitle>
          {tracking && (
            <p className="text-gray-600">
              {lang === 'ar' ? `رقم الطلب: ${tracking.order_number}` : `Order #${tracking.order_number}`}
            </p>
          )}
        </motion.div>

        {loading && <LoadingSkeleton />}

        {tracking && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Current Status */}
            <div className="lg:col-span-2">
              <GlassCard className="mb-6">
                <div className="flex items-center gap-4 mb-6">
                  {getStatusIcon(tracking.status)}
                  <div>
                    <h3 className="text-xl font-semibold">{tracking.status_display}</h3>
                    <p className="text-gray-600">
                      {lang === 'ar' ? 'آخر تحديث:' : 'Last updated:'} {formatDate(tracking.last_update)}
                    </p>
                  </div>
                </div>

                {tracking.tracking_number && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">
                        {lang === 'ar' ? 'رقم التتبع' : 'Tracking Number'}
                      </p>
                      <p className="font-medium">{tracking.tracking_number}</p>
                    </div>
                    {tracking.courier_company && (
                      <div>
                        <p className="text-sm text-gray-600 mb-1">
                          {lang === 'ar' ? 'شركة الشحن' : 'Courier Company'}
                        </p>
                        <p className="font-medium">{tracking.courier_company}</p>
                      </div>
                    )}
                  </div>
                )}

                {tracking.estimated_delivery_date && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center gap-2">
                      <FiCalendar className="h-5 w-5 text-blue-600" />
                      <div>
                        <p className="font-medium text-blue-800">
                          {lang === 'ar' ? 'تاريخ التسليم المتوقع' : 'Expected Delivery'}
                        </p>
                        <p className="text-blue-600">
                          {formatDate(tracking.estimated_delivery_date)}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </GlassCard>

              {/* Timeline */}
              <GlassCard>
                <h3 className="text-lg font-semibold mb-6">
                  {lang === 'ar' ? 'تاريخ الطلب' : 'Order Timeline'}
                </h3>
                
                <div className="space-y-6">
                  {tracking.timeline.map((event, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex gap-4"
                    >
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-white border-2 border-[#d1b16a] flex items-center justify-center">
                        {getStatusIcon(event.status)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium">{event.status_display}</h4>
                          <span className={`px-2 py-1 rounded text-xs border ${getStatusColor(event.status)}`}>
                            {event.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-1">
                          {formatDate(event.timestamp)}
                        </p>
                        {event.comment && (
                          <p className="text-sm text-gray-700">{event.comment}</p>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </GlassCard>
            </div>

            {/* Sidebar Info */}
            <div className="space-y-6">
              <GlassCard>
                <h3 className="text-lg font-semibold mb-4">
                  {lang === 'ar' ? 'معلومات الطلب' : 'Order Information'}
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <FiBox className="h-4 w-4 text-gray-500" />
                    <span className="text-sm">
                      {lang === 'ar' ? 'رقم الطلب:' : 'Order:'} {tracking.order_number}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <FiClock className="h-4 w-4 text-gray-500" />
                    <span className="text-sm">
                      {lang === 'ar' ? 'الحالة:' : 'Status:'} {tracking.status_display}
                    </span>
                  </div>
                </div>
              </GlassCard>

              {/* Track Another Order */}
              <GlassCard>
                <h3 className="text-lg font-semibold mb-4">
                  {lang === 'ar' ? 'تتبع طلب آخر' : 'Track Another Order'}
                </h3>
                <GlassButton
                  onClick={() => {
                    setTracking(null);
                    setOrderNum('');
                    setEmail('');
                    navigate('/track-order');
                  }}
                  className="w-full"
                >
                  {lang === 'ar' ? 'طلب جديد' : 'New Tracking'}
                </GlassButton>
              </GlassCard>

              {/* Help */}
              <GlassCard>
                <h3 className="text-lg font-semibold mb-4">
                  {lang === 'ar' ? 'تحتاج مساعدة؟' : 'Need Help?'}
                </h3>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <FiPhone className="h-4 w-4 text-gray-500" />
                    <span className="text-sm">+20 100 123 4567</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <FiMail className="h-4 w-4 text-gray-500" />
                    <span className="text-sm">support@soleva.com</span>
                  </div>
                </div>
              </GlassCard>
            </div>
          </div>
        )}

        {error && !loading && (
          <GlassCard>
            <div className="text-center py-8">
              <FiAlertCircle size={48} className="mx-auto mb-4 text-red-500" />
              <h3 className="text-lg font-semibold text-red-700 mb-2">
                {lang === 'ar' ? 'لم يتم العثور على الطلب' : 'Order Not Found'}
              </h3>
              <p className="text-red-600 mb-4">{error}</p>
              <GlassButton
                onClick={() => {
                  setError(null);
                  setTracking(null);
                  setOrderNum('');
                  setEmail('');
                }}
              >
                {lang === 'ar' ? 'حاول مرة أخرى' : 'Try Again'}
              </GlassButton>
            </div>
          </GlassCard>
        )}
      </div>
    </div>
  );
}