import React, { useState } from 'react';
import { Upload, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { Order } from '../types';
import { useLang } from '../contexts/LangContext';
import PaymentProofUpload from './PaymentProofUpload';
import PaymentProofViewer from './PaymentProofViewer';

interface PaymentProofSectionProps {
  order: Order;
  onProofUploaded?: () => void;
  className?: string;
}

const PaymentProofSection: React.FC<PaymentProofSectionProps> = ({
  order,
  onProofUploaded,
  className = ''
}) => {
  const [showUpload, setShowUpload] = useState(false);
  const { t } = useLang();

  // Check if payment method requires proof
  const requiresProof = order.payment_method === 'bank_wallet' || order.payment_method === 'e_wallet';
  
  // Check if proof is already uploaded
  const hasProof = order.payment_proofs && order.payment_proofs.length > 0;
  
  // Get payment method display name
  const getPaymentMethodName = () => {
    switch (order.payment_method) {
      case 'bank_wallet':
        return t('Bank Wallet Payment');
      case 'e_wallet':
        return t('E-Wallet Payment');
      case 'cash_on_delivery':
        return t('Cash on Delivery');
      default:
        return order.payment_method;
    }
  };

  const getStatusInfo = () => {
    if (!requiresProof) {
      return {
        icon: <CheckCircle className="h-5 w-5 text-green-500" />,
        text: t('No payment proof required'),
        color: 'text-green-600 bg-green-50 border-green-200 dark:text-green-400 dark:bg-green-900/20 dark:border-green-800'
      };
    }

    if (!hasProof) {
      return {
        icon: <Upload className="h-5 w-5 text-orange-500" />,
        text: t('Payment proof required'),
        color: 'text-orange-600 bg-orange-50 border-orange-200 dark:text-orange-400 dark:bg-orange-900/20 dark:border-orange-800'
      };
    }

    const latestProof = order.payment_proofs![0];
    switch (latestProof.verification_status) {
      case 'verified':
        return {
          icon: <CheckCircle className="h-5 w-5 text-green-500" />,
          text: t('Payment verified'),
          color: 'text-green-600 bg-green-50 border-green-200 dark:text-green-400 dark:bg-green-900/20 dark:border-green-800'
        };
      case 'rejected':
        return {
          icon: <AlertCircle className="h-5 w-5 text-red-500" />,
          text: t('Payment proof rejected'),
          color: 'text-red-600 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-900/20 dark:border-red-800'
        };
      case 'needs_clarification':
        return {
          icon: <AlertCircle className="h-5 w-5 text-yellow-500" />,
          text: t('Additional information needed'),
          color: 'text-yellow-600 bg-yellow-50 border-yellow-200 dark:text-yellow-400 dark:bg-yellow-900/20 dark:border-yellow-800'
        };
      default:
        return {
          icon: <Clock className="h-5 w-5 text-blue-500" />,
          text: t('Payment proof under review'),
          color: 'text-blue-600 bg-blue-50 border-blue-200 dark:text-blue-400 dark:bg-blue-900/20 dark:border-blue-800'
        };
    }
  };

  const statusInfo = getStatusInfo();

  const handleProofUploaded = () => {
    setShowUpload(false);
    onProofUploaded?.();
  };

  if (!requiresProof) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg p-6 ${className}`}>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          {t('Payment Information')}
        </h3>
        <div className="flex items-center space-x-3">
          <div className={`inline-flex items-center space-x-2 px-3 py-2 rounded-full text-sm border ${statusInfo.color}`}>
            {statusInfo.icon}
            <span>{statusInfo.text}</span>
          </div>
          <span className="text-gray-600 dark:text-gray-400">
            {getPaymentMethodName()}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          {t('Payment Information')}
        </h3>
        <div className={`inline-flex items-center space-x-2 px-3 py-2 rounded-full text-sm border ${statusInfo.color}`}>
          {statusInfo.icon}
          <span>{statusInfo.text}</span>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-gray-600 dark:text-gray-400">
          <span className="font-medium">{t('Payment Method')}:</span> {getPaymentMethodName()}
        </p>
      </div>

      {/* Show upload section if no proof or if rejected/needs clarification */}
      {(!hasProof || (hasProof && ['rejected', 'needs_clarification'].includes(order.payment_proofs![0].verification_status))) && (
        <div className="mb-6">
          {showUpload ? (
            <PaymentProofUpload
              orderId={order.id.toString()}
              paymentMethod={getPaymentMethodName()}
              onUploadSuccess={handleProofUploaded}
              onClose={() => setShowUpload(false)}
            />
          ) : (
            <div className="text-center py-6 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {hasProof 
                  ? t('Your previous payment proof needs attention. Please upload a new one.')
                  : t('Please upload your payment receipt to verify your payment.')
                }
              </p>
              <button
                onClick={() => setShowUpload(true)}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              >
                {hasProof ? t('Upload New Proof') : t('Upload Payment Proof')}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Show existing proofs */}
      {hasProof && (
        <PaymentProofViewer 
          paymentProofs={order.payment_proofs!}
          showVerificationStatus={true}
        />
      )}
    </div>
  );
};

export default PaymentProofSection;
