import React, { useState } from 'react';
import { Download, Eye, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';
import { PaymentProof } from '../types';
import { useLang } from '../contexts/LangContext';

interface PaymentProofViewerProps {
  paymentProofs: PaymentProof[];
  className?: string;
  showVerificationStatus?: boolean;
}

const PaymentProofViewer: React.FC<PaymentProofViewerProps> = ({
  paymentProofs,
  className = '',
  showVerificationStatus = true
}) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const { t, isRtl } = useLang();

  const getVerificationStatusIcon = (status: string) => {
    switch (status) {
      case 'verified':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'rejected':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'needs_clarification':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      default:
        return <Clock className="h-5 w-5 text-blue-500" />;
    }
  };

  const getVerificationStatusText = (status: string) => {
    switch (status) {
      case 'verified':
        return t('Verified');
      case 'rejected':
        return t('Rejected');
      case 'needs_clarification':
        return t('Needs Clarification');
      default:
        return t('Pending Verification');
    }
  };

  const getVerificationStatusColor = (status: string) => {
    switch (status) {
      case 'verified':
        return 'text-green-600 bg-green-50 border-green-200 dark:text-green-400 dark:bg-green-900/20 dark:border-green-800';
      case 'rejected':
        return 'text-red-600 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-900/20 dark:border-red-800';
      case 'needs_clarification':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200 dark:text-yellow-400 dark:bg-yellow-900/20 dark:border-yellow-800';
      default:
        return 'text-blue-600 bg-blue-50 border-blue-200 dark:text-blue-400 dark:bg-blue-900/20 dark:border-blue-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(isRtl ? 'ar-EG' : 'en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDownload = (imageUrl: string, filename: string) => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!paymentProofs || paymentProofs.length === 0) {
    return null;
  }

  return (
    <>
      <div className={`space-y-4 ${className}`}>
        <h4 className="text-lg font-medium text-gray-900 dark:text-white">
          {t('Payment Proof')}
        </h4>
        
        {paymentProofs.map((proof) => (
          <div
            key={proof.id}
            className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 bg-gray-50 dark:bg-gray-700/50"
          >
            <div className="flex items-start space-x-4">
              {/* Image Thumbnail */}
              <div className="flex-shrink-0">
                <div className="relative group">
                  <img
                    src={proof.image}
                    alt={proof.original_filename}
                    className="h-20 w-20 object-cover rounded-lg cursor-pointer group-hover:opacity-80 transition-opacity"
                    onClick={() => setSelectedImage(proof.image)}
                  />
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black bg-opacity-50 rounded-lg">
                    <Eye className="h-6 w-6 text-white" />
                  </div>
                </div>
              </div>
              
              {/* Details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {proof.original_filename}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {proof.file_size_mb} MB • {t('Uploaded')} {formatDate(proof.created_at)}
                    </p>
                    {proof.uploaded_by_name && (
                      <p className="text-xs text-gray-400 dark:text-gray-500">
                        {t('By')}: {proof.uploaded_by_name}
                      </p>
                    )}
                  </div>
                  
                  {/* Actions */}
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setSelectedImage(proof.image)}
                      className="p-2 text-gray-400 hover:text-blue-500 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600"
                      title={t('View')}
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDownload(proof.image, proof.original_filename)}
                      className="p-2 text-gray-400 hover:text-green-500 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600"
                      title={t('Download')}
                    >
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                
                {/* Description */}
                {proof.description && (
                  <div className="mt-2">
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      <span className="font-medium">{t('Note')}:</span> {proof.description}
                    </p>
                  </div>
                )}
                
                {/* Verification Status */}
                {showVerificationStatus && (
                  <div className="mt-3">
                    <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-sm border ${getVerificationStatusColor(proof.verification_status)}`}>
                      {getVerificationStatusIcon(proof.verification_status)}
                      <span>{getVerificationStatusText(proof.verification_status)}</span>
                    </div>
                    
                    {proof.verification_notes && (
                      <div className="mt-2 p-3 bg-gray-100 dark:bg-gray-600 rounded-lg">
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                          <span className="font-medium">{t('Admin Note')}:</span> {proof.verification_notes}
                        </p>
                        {proof.verified_by_name && proof.verified_at && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {t('Verified by')} {proof.verified_by_name} {t('on')} {formatDate(proof.verified_at)}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Image Modal */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="relative max-w-4xl max-h-full">
            <img
              src={selectedImage}
              alt="Payment Proof"
              className="max-w-full max-h-full object-contain rounded-lg"
            />
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute top-4 right-4 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-colors"
            >
              <XCircle className="h-6 w-6" />
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default PaymentProofViewer;
