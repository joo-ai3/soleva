import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiMail, FiRefreshCw, FiCheckCircle, FiAlertCircle, FiClock } from 'react-icons/fi';
import clsx from 'clsx';
import OTPInput from './OTPInput';
import CountdownTimer from './CountdownTimer';
import { useToast } from '../contexts/ToastContext';

interface OTPVerificationFormProps {
  email: string;
  otpType: 'registration' | 'password_reset' | 'login_verification' | 'email_verification';
  onVerificationSuccess: (otpRequestId: string) => void;
  onBack?: () => void;
  autoGenerate?: boolean;
  className?: string;
}

interface OTPStatus {
  has_otp: boolean;
  is_valid?: boolean;
  can_resend: boolean;
  resend_countdown: number;
  attempts_remaining: number;
  expires_at?: string;
  created_at?: string;
}

export default function OTPVerificationForm({
  email,
  otpType,
  onVerificationSuccess,
  onBack,
  autoGenerate = true,
  className = ''
}: OTPVerificationFormProps) {
  const [otpCode, setOtpCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [otpStatus, setOtpStatus] = useState<OTPStatus | null>(null);
  const { showToast } = useToast();

  // Fetch current OTP status
  const fetchOTPStatus = useCallback(async () => {
    try {
      const response = await fetch(`/api/otp/status/?email=${encodeURIComponent(email)}&otp_type=${otpType}`);
      const data = await response.json();
      
      if (data.success) {
        setOtpStatus(data.otp_status);
      }
    } catch {
      console.error('Error fetching OTP status:', error);
    }
  }, [email, otpType]);

  // Auto-generate OTP on mount if requested
  useEffect(() => {
    if (autoGenerate) {
      handleGenerateOTP();
    } else {
      fetchOTPStatus();
    }
  }, [autoGenerate, fetchOTPStatus]);

  // Poll OTP status for real-time updates
  useEffect(() => {
    if (otpStatus?.has_otp) {
      const interval = setInterval(fetchOTPStatus, 5000); // Poll every 5 seconds
      return () => clearInterval(interval);
    }
  }, [otpStatus?.has_otp, fetchOTPStatus]);

  // Generate OTP
  const handleGenerateOTP = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/otp/generate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          otp_type: otpType
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setOtpStatus(data.otp_status);
        showToast('Verification code sent successfully!');
      } else {
        setError(data.message || 'Failed to send verification code');
        showToast(data.message || 'Failed to send verification code');
      }
    } catch {
      const errorMessage = 'Network error. Please check your connection.';
      setError(errorMessage);
      showToast(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Resend OTP
  const handleResendOTP = async () => {
    setIsResending(true);
    setError('');
    setOtpCode('');
    
    try {
      const response = await fetch('/api/otp/resend/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          otp_type: otpType
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setOtpStatus(data.otp_status);
        showToast('Verification code resent successfully!');
      } else {
        setError(data.message || 'Failed to resend verification code');
        showToast(data.message || 'Failed to resend verification code');
      }
    } catch {
      const errorMessage = 'Network error. Please check your connection.';
      setError(errorMessage);
      showToast(errorMessage);
    } finally {
      setIsResending(false);
    }
  };

  // Verify OTP
  const handleVerifyOTP = async (code: string) => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/otp/verify/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          code,
          otp_type: otpType
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setSuccess(true);
        showToast('Verification successful!');
        setTimeout(() => {
          onVerificationSuccess(data.otp_request_id);
        }, 1000);
      } else {
        setError(data.message || 'Invalid verification code');
        setOtpCode('');
        if (data.otp_status) {
          setOtpStatus(data.otp_status);
        }
        showToast(data.message || 'Invalid verification code');
      }
    } catch {
      const errorMessage = 'Network error. Please check your connection.';
      setError(errorMessage);
      setOtpCode('');
      showToast(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle OTP input completion
  const handleOTPComplete = (code: string) => {
    if (code.length === 6 && !isLoading) {
      handleVerifyOTP(code);
    }
  };

  // Get display text based on OTP type
  const getDisplayText = () => {
    switch (otpType) {
      case 'registration':
        return {
          title: 'Verify Your Email',
          subtitle: 'Complete your registration',
          instruction: 'Enter the 6-digit code sent to your email'
        };
      case 'password_reset':
        return {
          title: 'Reset Password',
          subtitle: 'Verify your identity',
          instruction: 'Enter the 6-digit code sent to your email'
        };
      case 'login_verification':
        return {
          title: 'Verify Login',
          subtitle: 'Secure your account',
          instruction: 'Enter the 6-digit code sent to your email'
        };
      default:
        return {
          title: 'Email Verification',
          subtitle: 'Verify your email address',
          instruction: 'Enter the 6-digit code sent to your email'
        };
    }
  };

  const displayText = getDisplayText();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={clsx('max-w-md mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8', className)}
    >
      {/* Header */}
      <div className="text-center mb-8">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2 }}
          className="w-16 h-16 bg-[#d1b16a]/10 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <FiMail className="w-8 h-8 text-[#d1b16a]" />
        </motion.div>
        
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {displayText.title}
        </h1>
        <p className="text-gray-600 dark:text-gray-400 text-sm">
          {displayText.subtitle}
        </p>
      </div>

      {/* Email display */}
      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-6">
        <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
          Code sent to:
        </p>
        <p className="font-medium text-gray-900 dark:text-white text-center">
          {email}
        </p>
      </div>

      {/* Instructions */}
      <p className="text-center text-gray-600 dark:text-gray-400 mb-6">
        {displayText.instruction}
      </p>

      {/* OTP Input */}
      <div className="mb-6">
        <OTPInput
          value={otpCode}
          onChange={setOtpCode}
          onComplete={handleOTPComplete}
          disabled={isLoading || success}
          error={!!error}
          autoFocus={true}
        />
      </div>

      {/* Error message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-4"
          >
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 flex items-center gap-2">
              <FiAlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
              <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Success message */}
      <AnimatePresence>
        {success && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-4"
          >
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3 flex items-center gap-2">
              <FiCheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
              <p className="text-green-700 dark:text-green-400 text-sm">
                Verification successful! Redirecting...
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Status info */}
      {otpStatus && (
        <div className="mb-6 space-y-3">
          {/* Attempts remaining */}
          {otpStatus.attempts_remaining > 0 && (
            <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <FiAlertCircle className="w-4 h-4" />
              <span>{otpStatus.attempts_remaining} attempts remaining</span>
            </div>
          )}

          {/* Expiry timer */}
          {otpStatus.expires_at && (
            <div className="flex items-center justify-center gap-2">
              <FiClock className="w-4 h-4 text-gray-600 dark:text-gray-400" />
              <span className="text-sm text-gray-600 dark:text-gray-400">Expires in:</span>
              <CountdownTimer
                initialTime={Math.max(0, Math.floor((new Date(otpStatus.expires_at).getTime() - Date.now()) / 1000))}
                size="sm"
                showProgress={false}
                onComplete={() => {
                  setError('Verification code has expired. Please request a new one.');
                  setOtpCode('');
                }}
              />
            </div>
          )}
        </div>
      )}

      {/* Resend section */}
      <div className="text-center mb-6">
        {otpStatus?.can_resend ? (
          <button
            onClick={handleResendOTP}
            disabled={isResending}
            className="inline-flex items-center gap-2 text-[#d1b16a] hover:text-[#b8965a] font-medium text-sm transition-colors disabled:opacity-50"
          >
            <FiRefreshCw className={clsx('w-4 h-4', isResending && 'animate-spin')} />
            {isResending ? 'Sending...' : 'Resend Code'}
          </button>
        ) : (
          <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
            <span>Resend code in:</span>
            <CountdownTimer
              initialTime={otpStatus?.resend_countdown || 0}
              size="sm"
              showProgress={false}
              onComplete={fetchOTPStatus}
            />
          </div>
        )}
      </div>

      {/* Back button */}
      {onBack && (
        <button
          onClick={onBack}
          className="w-full py-3 px-4 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          Back
        </button>
      )}

      {/* Help text */}
      <p className="text-center text-xs text-gray-500 mt-4">
        Didn't receive the code? Check your spam folder or try resending.
      </p>
    </motion.div>
  );
}
