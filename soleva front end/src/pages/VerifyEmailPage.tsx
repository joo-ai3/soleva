import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import OTPVerificationForm from '../components/OTPVerificationForm';
import { useToast } from '../contexts/ToastContext';

export default function VerifyEmailPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { showToast } = useToast();
  
  const email = searchParams.get('email') || '';
  const otpType = (searchParams.get('type') as 'registration' | 'password_reset' | 'email_verification') || 'email_verification';
  const returnTo = searchParams.get('returnTo') || '/';

  const handleVerificationSuccess = async (otpRequestId: string) => {
    showToast('Email verified successfully!', 'success');
    
    // Redirect based on OTP type
    switch (otpType) {
      case 'registration':
        navigate('/login?message=Registration completed successfully. Please log in.');
        break;
      case 'password_reset':
        navigate(`/reset-password?email=${encodeURIComponent(email)}&token=${otpRequestId}`);
        break;
      default:
        navigate(returnTo);
        break;
    }
  };

  const handleBack = () => {
    switch (otpType) {
      case 'registration':
        navigate('/register');
        break;
      case 'password_reset':
        navigate('/forgot-password');
        break;
      default:
        navigate('/');
        break;
    }
  };

  if (!email) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Invalid Verification Link
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            The verification link is invalid or expired.
          </p>
          <button
            onClick={() => navigate('/')}
            className="btn btn-primary"
          >
            Go Home
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        <OTPVerificationForm
          email={email}
          otpType={otpType}
          onVerificationSuccess={handleVerificationSuccess}
          onBack={handleBack}
          autoGenerate={true}
        />
      </div>
    </div>
  );
}
