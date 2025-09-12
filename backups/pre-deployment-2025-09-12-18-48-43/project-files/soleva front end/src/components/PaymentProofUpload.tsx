import React, { useState, useRef } from 'react';
import { Upload, FileImage, X, CheckCircle, AlertCircle } from 'lucide-react';
import { ordersApi } from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { useLang } from '../contexts/LangContext';

interface PaymentProofUploadProps {
  orderId: string;
  paymentMethod: string;
  onUploadSuccess?: (paymentProof: any) => void;
  onClose?: () => void;
  className?: string;
}

const PaymentProofUpload: React.FC<PaymentProofUploadProps> = ({
  orderId,
  paymentMethod,
  onUploadSuccess,
  onClose,
  className = ''
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [description, setDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const { addToast } = useToast();
  const { t, isRtl } = useLang();

  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  const maxSize = 10 * 1024 * 1024; // 10MB

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!allowedTypes.includes(file.type)) {
      addToast(t('Only JPEG, PNG, GIF, and WebP images are allowed'), 'error');
      return;
    }

    // Validate file size
    if (file.size > maxSize) {
      addToast(t('Image size cannot exceed 10MB'), 'error');
      return;
    }

    setSelectedFile(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      addToast(t('Please select an image first'), 'error');
      return;
    }

    setIsUploading(true);
    try {
      const response = await ordersApi.uploadPaymentProof(orderId, {
        image: selectedFile,
        description: description.trim() || undefined
      });

      if (response.success) {
        addToast(t('Payment proof uploaded successfully'), 'success');
        onUploadSuccess?.(response.data.payment_proof);
        onClose?.();
      } else {
        addToast(response.message || t('Failed to upload payment proof'), 'error');
      }
    } catch (error: any) {
      console.error('Upload error:', error);
      addToast(error.message || t('Failed to upload payment proof'), 'error');
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {t('Upload Payment Proof')}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {t('Please upload a screenshot or photo of your payment receipt for')} {paymentMethod}
          </p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            <X className="h-6 w-6" />
          </button>
        )}
      </div>

      {/* File Upload Area */}
      <div className="mb-6">
        {!selectedFile ? (
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
          >
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              {t('Click to upload payment proof')}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {t('JPEG, PNG, GIF, WebP up to 10MB')}
            </p>
          </div>
        ) : (
          <div className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
            <div className="flex items-start space-x-4">
              {/* Preview */}
              <div className="flex-shrink-0">
                {preview ? (
                  <img
                    src={preview}
                    alt="Preview"
                    className="h-20 w-20 object-cover rounded-lg"
                  />
                ) : (
                  <div className="h-20 w-20 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                    <FileImage className="h-8 w-8 text-gray-400" />
                  </div>
                )}
              </div>
              
              {/* File Info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {selectedFile.name}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {formatFileSize(selectedFile.size)}
                </p>
                <div className="mt-2 flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-green-600 dark:text-green-400">
                    {t('Ready to upload')}
                  </span>
                </div>
              </div>
              
              {/* Remove Button */}
              <button
                onClick={handleRemoveFile}
                className="flex-shrink-0 text-gray-400 hover:text-red-500"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}
        
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Description */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {t('Description')} ({t('Optional')})
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder={t('Add any additional notes about your payment...')}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          maxLength={500}
        />
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {description.length}/500 {t('characters')}
        </p>
      </div>

      {/* Upload Instructions */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
        <div className="flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800 dark:text-blue-200">
            <p className="font-medium mb-1">{t('Upload Guidelines')}:</p>
            <ul className="list-disc list-inside space-y-1 text-blue-700 dark:text-blue-300">
              <li>{t('Upload a clear screenshot or photo of your payment receipt')}</li>
              <li>{t('Make sure all transaction details are visible')}</li>
              <li>{t('Include transaction ID, amount, and timestamp if available')}</li>
              <li>{t('Your payment will be verified within 24 hours')}</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className={`flex space-x-4 ${isRtl ? 'flex-row-reverse' : ''}`}>
        <button
          onClick={handleUpload}
          disabled={!selectedFile || isUploading}
          className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isUploading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
              <span>{t('Uploading...')}</span>
            </div>
          ) : (
            t('Upload Payment Proof')
          )}
        </button>
        
        {onClose && (
          <button
            onClick={onClose}
            disabled={isUploading}
            className="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {t('Cancel')}
          </button>
        )}
      </div>
    </div>
  );
};

export default PaymentProofUpload;
