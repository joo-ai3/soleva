import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Package, Clock, CheckCircle, XCircle, Upload, Eye } from 'lucide-react';
import { useLang, useTranslation } from '../contexts/LangContext';
import { useApiQuery, useApiMutation } from '../hooks/useApi';
import { apiService } from '../services/api';

import GlassCard from '../components/GlassCard';
import GlassButton from '../components/GlassButton';
import SectionTitle from '../components/SectionTitle';
import ErrorMessage from '../components/ui/ErrorMessage';
import { LoadingSpinner, PageLoadingSpinner, InlineLoadingSpinner } from '../components/ui/LoadingSpinner';
import { Order, PaymentProof } from '../types';

// API Functions
const fetchOrders = () => apiService.get<Order[]>('/orders/');
const uploadPaymentProof = (data: { order_id: number; image: File; description?: string }) => {
  const formData = new FormData();
  formData.append('order_id', data.order_id.toString());
  formData.append('image', data.image);
  if (data.description) {
    formData.append('description', data.description);
  }
  return apiService.post<PaymentProof>('/payment-proofs/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const OrdersPageWithApi: React.FC = () => {
  const { lang } = useLang();
  const t = useTranslation();
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [uploadingProof, setUploadingProof] = useState<number | null>(null);

  // Fetch orders with error handling
  const {
    data: orders,
    loading: ordersLoading,
    error: ordersError,
    retry: retryOrders
  } = useApiQuery(fetchOrders, {
    retries: 2,
    onError: (error) => {
      console.error('Failed to fetch orders:', error);
    }
  });

  // Upload payment proof mutation
  const {
    error: uploadError,
    execute: executeUpload
  } = useApiMutation(uploadPaymentProof, {
    onSuccess: (data) => {
      console.log('Payment proof uploaded successfully:', data);
      setUploadingProof(null);
      retryOrders(); // Refresh orders list
    },
    onError: (error) => {
      console.error('Failed to upload payment proof:', error);
    }
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
      case 'pending_review':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'under_review':
        return <Eye className="h-5 w-5 text-blue-500" />;
      case 'payment_approved':
      case 'delivered':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'payment_rejected':
      case 'cancelled':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Package className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    const statusMap: Record<string, { en: string; ar: string }> = {
      pending: { en: 'Pending', ar: 'في الانتظار' },
      pending_review: { en: 'Pending Review', ar: 'في انتظار المراجعة' },
      under_review: { en: 'Under Review', ar: 'قيد المراجعة' },
      payment_approved: { en: 'Payment Approved', ar: 'تم قبول الدفع' },
      payment_rejected: { en: 'Payment Rejected', ar: 'تم رفض الدفع' },
      confirmed: { en: 'Confirmed', ar: 'مؤكد' },
      processing: { en: 'Processing', ar: 'قيد المعالجة' },
      shipped: { en: 'Shipped', ar: 'تم الشحن' },
      delivered: { en: 'Delivered', ar: 'تم التسليم' },
      cancelled: { en: 'Cancelled', ar: 'ملغي' }
    };
    return statusMap[status]?.[lang as 'en' | 'ar'] || status;
  };

  const handleFileUpload = async (orderId: number, file: File) => {
    setUploadingProof(orderId);
    await executeUpload({
      order_id: orderId,
      image: file,
      description: 'Payment proof uploaded by customer'
    });
  };

  // Show loading state
  if (ordersLoading && !orders) {
    return <PageLoadingSpinner text={t('Loading your orders...')} />;
  }

  // Show error state with retry option
  if (ordersError && !orders) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full">
          <ErrorMessage
            error={ordersError}
            onRetry={retryOrders}
            className="p-8"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <SectionTitle className="mb-4">{t('My Orders')}</SectionTitle>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            {lang === 'ar' 
              ? 'تتبع طلباتك وحالة الدفع والشحن'
              : 'Track your orders, payment status, and shipping updates'
            }
          </p>
        </motion.div>

        {/* Refresh Button */}
        <div className="flex justify-end mb-6">
          <GlassButton
            onClick={retryOrders}
            disabled={ordersLoading}
            className="flex items-center gap-2"
          >
            {ordersLoading ? (
              <LoadingSpinner size="sm" />
            ) : (
              <Package className="h-4 w-4" />
            )}
            {t('Refresh')}
          </GlassButton>
        </div>

        {/* Orders List */}
        {!orders || orders.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-16"
          >
            <GlassCard className="max-w-md mx-auto">
              <div className="text-6xl mb-4">📦</div>
              <h3 className="text-xl font-semibold mb-2">
                {lang === 'ar' ? 'لا توجد طلبات' : 'No Orders Found'}
              </h3>
              <p className="text-gray-600 mb-6">
                {lang === 'ar' 
                  ? 'لم تقم بأي طلبات بعد. ابدأ التسوق الآن!'
                  : "You haven't placed any orders yet. Start shopping now!"
                }
              </p>
              <Link to="/products">
                <GlassButton variant="primary">
                  {t('Start Shopping')}
                </GlassButton>
              </Link>
            </GlassCard>
          </motion.div>
        ) : (
          <div className="space-y-6">
            {orders.map((order, index) => (
              <motion.div
                key={order.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <GlassCard className="overflow-hidden">
                  {/* Order Header */}
                  <div className="border-b border-gray-200 p-6">
                    <div className="flex flex-wrap justify-between items-start gap-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {t('Order')} #{order.order_number}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {new Date(order.created_at).toLocaleDateString(lang === 'ar' ? 'ar-EG' : 'en-US')}
                        </p>
                      </div>
                      
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(order.payment_status)}
                          <span className="text-sm font-medium">
                            {getStatusText(order.payment_status)}
                          </span>
                        </div>
                        <div className="text-lg font-bold text-gray-900">
                          {order.total_amount} {t('egp')}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Order Content */}
                  <div className="p-6">
                    {/* Order Items */}
                    <div className="space-y-3 mb-6">
                      {order.items?.map((item) => (
                        <div key={item.id} className="flex items-center gap-4">
                          <img
                            src={item.product_image || '/placeholder-product.jpg'}
                            alt={item.product_name}
                            className="w-16 h-16 rounded-lg object-cover"
                          />
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900">{item.product_name}</h4>
                            <p className="text-sm text-gray-600">
                              {t('Quantity')}: {item.quantity} × {item.unit_price} {t('egp')}
                            </p>
                          </div>
                          <div className="font-semibold text-gray-900">
                            {item.total_price} {t('egp')}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Payment Proof Upload */}
                    {order.payment_status === 'pending' && (!order.payment_proofs || order.payment_proofs.length === 0) && (
                      <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
                        <div className="flex items-start gap-3">
                          <Upload className="h-5 w-5 text-orange-500 mt-0.5" />
                          <div className="flex-1">
                            <h4 className="font-medium text-orange-800">
                              {t('Payment Proof Required')}
                            </h4>
                            <p className="text-sm text-orange-700 mb-3">
                              {lang === 'ar' 
                                ? 'يرجى رفع إيصال الدفع لتأكيد طلبك'
                                : 'Please upload your payment receipt to confirm your order'
                              }
                            </p>
                            
                            {uploadingProof === order.id ? (
                              <InlineLoadingSpinner text={t('Uploading...')} />
                            ) : (
                              <div>
                                <input
                                  type="file"
                                  accept="image/*"
                                  onChange={(e) => {
                                    const file = e.target.files?.[0];
                                    if (file) {
                                      handleFileUpload(order.id, file);
                                    }
                                  }}
                                  className="hidden"
                                  id={`file-upload-${order.id}`}
                                />
                                <label
                                  htmlFor={`file-upload-${order.id}`}
                                  className="inline-flex items-center gap-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors cursor-pointer"
                                >
                                  <Upload className="h-4 w-4" />
                                  {t('Upload Receipt')}
                                </label>
                              </div>
                            )}

                            {uploadError && (
                              <ErrorMessage
                                error={uploadError}
                                inline
                                className="mt-3"
                                onRetry={() => {
                                  // Re-trigger file input
                                  const input = document.getElementById(`file-upload-${order.id}`) as HTMLInputElement;
                                  input?.click();
                                }}
                              />
                            )}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Payment Proof Status */}
                    {order.payment_proofs && order.payment_proofs.length > 0 && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                        <div className="flex items-center gap-3">
                          <CheckCircle className="h-5 w-5 text-blue-500" />
                          <div>
                            <h4 className="font-medium text-blue-800">
                              {t('Payment Proof Uploaded')}
                            </h4>
                            <p className="text-sm text-blue-700">
                              {order.payment_status === 'payment_approved' 
                                ? (lang === 'ar' ? 'تم التحقق من الدفع' : 'Payment verified')
                                : (lang === 'ar' ? 'في انتظار التحقق' : 'Awaiting verification')
                              }
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Order Actions */}
                    <div className="flex flex-wrap gap-3">
                      <GlassButton
                        onClick={() => setSelectedOrder(selectedOrder?.id === order.id ? null : order)}
                        variant="ghost"
                      >
                        {selectedOrder?.id === order.id ? t('Hide Details') : t('View Details')}
                      </GlassButton>
                      
                      {order.can_be_cancelled && (
                        <GlassButton variant="ghost" className="text-red-600 hover:text-red-700">
                          {t('Cancel Order')}
                        </GlassButton>
                      )}
                    </div>

                    {/* Order Details (Expandable) */}
                    {selectedOrder?.id === order.id && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-6 pt-6 border-t border-gray-200"
                      >
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {/* Shipping Address */}
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-2">{t('Shipping Address')}</h4>
                            <div className="text-sm text-gray-600">
                              <p>{order.shipping_name}</p>
                              <p>{order.shipping_address_line1}</p>
                              {order.shipping_address_line2 && <p>{order.shipping_address_line2}</p>}
                              <p>{order.shipping_city}, {order.shipping_governorate}</p>
                              <p>{order.shipping_phone}</p>
                            </div>
                          </div>

                          {/* Order Summary */}
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-2">{t('Order Summary')}</h4>
                            <div className="text-sm space-y-1">
                              <div className="flex justify-between">
                                <span>{t('Subtotal')}</span>
                                <span>{order.subtotal} {t('egp')}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>{t('Shipping')}</span>
                                <span>{order.shipping_cost} {t('egp')}</span>
                              </div>
                              {order.discount_amount > 0 && (
                                <div className="flex justify-between text-green-600">
                                  <span>{t('Discount')}</span>
                                  <span>-{order.discount_amount} {t('egp')}</span>
                                </div>
                              )}
                              <div className="flex justify-between font-semibold text-gray-900 pt-2 border-t">
                                <span>{t('Total')}</span>
                                <span>{order.total_amount} {t('egp')}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
