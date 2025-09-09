import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  FiFileText, FiEye, FiPackage, FiTruck, FiClock, 
  FiCheckCircle, FiXCircle, FiAlertCircle, FiDollarSign 
} from 'react-icons/fi';
import { useLang } from '../contexts/LangContext';
import { useAuth } from '../contexts/AuthContext';
import { ordersApi } from '../services/api';
import { Order } from '../types';
import GlassCard from '../components/GlassCard';
import LoadingSkeleton from '../components/LoadingSkeleton';
import PaymentProofSection from '../components/PaymentProofSection';

const OrdersPage: React.FC = () => {
  const { t, lang } = useLang();
  const { user } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await ordersApi.getAll();
      if (response.success) {
        setOrders(response.data || []);
      } else {
        setError(response.error || 'Failed to fetch orders');
      }
    } catch (err) {
      setError('Failed to fetch orders');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <FiClock className="h-4 w-4" />;
      case 'confirmed':
        return <FiCheckCircle className="h-4 w-4" />;
      case 'processing':
        return <FiPackage className="h-4 w-4" />;
      case 'shipped':
      case 'out_for_delivery':
        return <FiTruck className="h-4 w-4" />;
      case 'delivered':
        return <FiCheckCircle className="h-4 w-4" />;
      case 'cancelled':
        return <FiXCircle className="h-4 w-4" />;
      default:
        return <FiFileText className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'confirmed':
      case 'processing':
        return 'text-blue-600 bg-blue-100 border-blue-200';
      case 'shipped':
      case 'out_for_delivery':
        return 'text-purple-600 bg-purple-100 border-purple-200';
      case 'delivered':
        return 'text-green-600 bg-green-100 border-green-200';
      case 'cancelled':
        return 'text-red-600 bg-red-100 border-red-200';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getPaymentStatusIcon = (paymentStatus: string) => {
    switch (paymentStatus) {
      case 'pending':
      case 'pending_review':
        return <FiClock className="h-4 w-4" />;
      case 'under_review':
        return <FiAlertCircle className="h-4 w-4" />;
      case 'payment_approved':
      case 'paid':
        return <FiCheckCircle className="h-4 w-4" />;
      case 'payment_rejected':
      case 'failed':
        return <FiXCircle className="h-4 w-4" />;
      default:
        return <FiDollarSign className="h-4 w-4" />;
    }
  };

  const getPaymentStatusColor = (paymentStatus: string) => {
    switch (paymentStatus) {
      case 'pending':
      case 'pending_review':
        return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'under_review':
        return 'text-blue-600 bg-blue-100 border-blue-200';
      case 'payment_approved':
      case 'paid':
        return 'text-green-600 bg-green-100 border-green-200';
      case 'payment_rejected':
      case 'failed':
        return 'text-red-600 bg-red-100 border-red-200';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getPaymentStatusText = (paymentStatus: string) => {
    switch (paymentStatus) {
      case 'pending':
        return t('Pending Payment');
      case 'pending_review':
        return t('Pending Review');
      case 'under_review':
        return t('Under Review');
      case 'payment_approved':
        return t('Payment Approved');
      case 'payment_rejected':
        return t('Payment Rejected');
      case 'paid':
        return t('Paid');
      case 'failed':
        return t('Payment Failed');
      default:
        return paymentStatus;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(lang === 'ar' ? 'ar-EG' : 'en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!user) {
  return (
    <div className="container mx-auto py-10 px-4 max-w-2xl">
      <GlassCard>
        <div className="text-center py-12">
          <FiFileText size={64} className="mx-auto mb-4 text-[#d1b16a]" />
            <h1 className="text-2xl font-bold mb-4">{t('Please login to view your orders')}</h1>
        </div>
      </GlassCard>
    </div>
  );
}

  if (loading) {
    return (
      <div className="container mx-auto py-10 px-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">{t('My Orders')}</h1>
          <div className="space-y-6">
            {[1, 2, 3].map((i) => (
              <LoadingSkeleton key={i} className="h-32" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-10 px-4 max-w-2xl">
        <GlassCard>
          <div className="text-center py-12">
            <FiXCircle size={64} className="mx-auto mb-4 text-red-500" />
            <h1 className="text-2xl font-bold mb-4 text-red-600">{t('Error Loading Orders')}</h1>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={fetchOrders}
              className="bg-[#d1b16a] text-white px-6 py-2 rounded-lg hover:bg-[#b8a054] transition-colors"
            >
              {t('Retry')}
            </button>
          </div>
        </GlassCard>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="container mx-auto py-10 px-4 max-w-2xl">
        <GlassCard>
          <div className="text-center py-12">
            <FiFileText size={64} className="mx-auto mb-4 text-[#d1b16a]" />
            <h1 className="text-2xl font-bold mb-4">{t('No Orders Yet')}</h1>
            <p className="text-gray-600 mb-6">{t('You haven\'t placed any orders yet. Start shopping to see your orders here!')}</p>
            <a
              href="/products"
              className="bg-[#d1b16a] text-white px-6 py-3 rounded-lg hover:bg-[#b8a054] transition-colors inline-block"
            >
              {t('Start Shopping')}
            </a>
          </div>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-10 px-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">
          {t('My Orders')}
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Orders List */}
          <div className="space-y-6">
            {orders.map((order, index) => (
              <motion.div
                key={order.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <GlassCard 
                  className={`cursor-pointer transition-all hover:shadow-lg ${
                    selectedOrder?.id === order.id ? 'ring-2 ring-[#d1b16a]' : ''
                  }`}
                  onClick={() => setSelectedOrder(order)}
                >
                  <div className="p-6">
                    {/* Order Header */}
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {t('Order')} #{order.order_number}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {formatDate(order.created_at)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-[#d1b16a]">
                          {order.total_amount} {t('egp')}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {order.items?.length || 0} {t('items')}
                        </p>
                      </div>
                    </div>

                    {/* Status Badges */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(order.status)}`}>
                        {getStatusIcon(order.status)}
                        <span>{t(order.status)}</span>
                      </span>
                      <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium border ${getPaymentStatusColor(order.payment_status)}`}>
                        {getPaymentStatusIcon(order.payment_status)}
                        <span>{getPaymentStatusText(order.payment_status)}</span>
                      </span>
                    </div>

                    {/* Payment Method */}
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {t('Payment')}: {t(order.payment_method)}
                      </span>
                      <button className="text-[#d1b16a] hover:text-[#b8a054] text-sm font-medium">
                        <FiEye className="inline mr-1" />
                        {t('View Details')}
                      </button>
                    </div>
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </div>

          {/* Order Details */}
          <div className="lg:sticky lg:top-8">
            {selectedOrder ? (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                <GlassCard>
                  <div className="p-6">
                    <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
                      {t('Order Details')}
                    </h3>
                    
                    {/* Order Info */}
                    <div className="space-y-3 mb-6">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">{t('Order Number')}:</span>
                        <span className="font-medium">#{selectedOrder.order_number}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">{t('Date')}:</span>
                        <span className="font-medium">{formatDate(selectedOrder.created_at)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">{t('Total Amount')}:</span>
                        <span className="font-bold text-[#d1b16a]">{selectedOrder.total_amount} {t('egp')}</span>
                      </div>
                    </div>

                    {/* Order Items */}
                    {selectedOrder.items && selectedOrder.items.length > 0 && (
                      <div className="mb-6">
                        <h4 className="font-medium mb-3">{t('Items')}:</h4>
                        <div className="space-y-2">
                          {selectedOrder.items.map((item) => (
                            <div key={item.id} className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700 last:border-0">
                              <div>
                                <p className="font-medium text-sm">{item.product_name}</p>
                                <p className="text-xs text-gray-500">
                                  {t('Quantity')}: {item.quantity} × {item.unit_price} {t('egp')}
                                </p>
                              </div>
                              <span className="font-medium">{item.total_price} {t('egp')}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Shipping Address */}
                    <div className="mb-6">
                      <h4 className="font-medium mb-2">{t('Shipping Address')}:</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {selectedOrder.shipping_name}<br />
                        {selectedOrder.shipping_address_line1}<br />
                        {selectedOrder.shipping_address_line2 && (
                          <>{selectedOrder.shipping_address_line2}<br /></>
                        )}
                        {selectedOrder.shipping_city}, {selectedOrder.shipping_governorate}<br />
                        {t('Phone')}: {selectedOrder.shipping_phone}
                      </p>
                    </div>
                  </div>
                </GlassCard>

                {/* Payment Proof Section */}
                {selectedOrder.payment_method && ['bank_wallet', 'e_wallet'].includes(selectedOrder.payment_method) && (
                  <PaymentProofSection 
                    order={selectedOrder}
                    onProofUploaded={fetchOrders}
                  />
                )}
              </motion.div>
            ) : (
              <GlassCard>
                <div className="p-6 text-center">
                  <FiFileText size={48} className="mx-auto mb-4 text-gray-400" />
                  <p className="text-gray-500 dark:text-gray-400">
                    {t('Select an order to view details')}
                  </p>
                </div>
              </GlassCard>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrdersPage;