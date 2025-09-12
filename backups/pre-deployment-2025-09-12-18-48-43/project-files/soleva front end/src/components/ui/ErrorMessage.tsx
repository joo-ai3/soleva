import React from 'react';
import { AlertCircle, RefreshCw, WifiOff, Server, Clock } from 'lucide-react';
import { ApiError } from '../../services/api';

interface ErrorMessageProps {
  error: ApiError | string;
  onRetry?: () => void;
  className?: string;
  showRetryButton?: boolean;
  inline?: boolean;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  error,
  onRetry,
  className = '',
  showRetryButton = true,
  inline = false
}) => {
  const errorObj = typeof error === 'string' ? { message: error } : error;
  
  const getErrorIcon = () => {
    switch (errorObj.code) {
      case 'NETWORK_ERROR':
        return <WifiOff className="h-8 w-8 text-red-500" />;
      case 'TIMEOUT_ERROR':
        return <Clock className="h-8 w-8 text-orange-500" />;
      case 'HTTP_500':
      case 'HTTP_502':
      case 'HTTP_503':
      case 'HTTP_504':
        return <Server className="h-8 w-8 text-red-500" />;
      default:
        return <AlertCircle className="h-8 w-8 text-red-500" />;
    }
  };

  const getErrorTitle = () => {
    switch (errorObj.code) {
      case 'NETWORK_ERROR':
        return 'Connection Problem';
      case 'TIMEOUT_ERROR':
        return 'Request Timeout';
      case 'HTTP_500':
      case 'HTTP_502':
      case 'HTTP_503':
      case 'HTTP_504':
        return 'Server Error';
      default:
        return 'Something went wrong';
    }
  };

  const getSuggestion = () => {
    switch (errorObj.code) {
      case 'NETWORK_ERROR':
        return 'Please check your internet connection and try again.';
      case 'TIMEOUT_ERROR':
        return 'The server is taking too long to respond. Please try again.';
      case 'HTTP_500':
      case 'HTTP_502':
      case 'HTTP_503':
      case 'HTTP_504':
        return 'Our servers are experiencing issues. Please try again in a few moments.';
      default:
        return 'Please try again or contact support if the problem persists.';
    }
  };

  if (inline) {
    return (
      <div className={`flex items-center p-3 bg-red-50 border border-red-200 rounded-lg ${className}`}>
        <AlertCircle className="h-5 w-5 text-red-500 mr-3 flex-shrink-0" />
        <div className="flex-1">
          <p className="text-sm text-red-800">{errorObj.message}</p>
        </div>
        {showRetryButton && onRetry && (
          <button
            onClick={onRetry}
            className="ml-3 flex-shrink-0 bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded text-sm transition-colors"
          >
            Try Again
          </button>
        )}
      </div>
    );
  }

  return (
    <div className={`text-center p-8 ${className}`}>
      <div className="flex justify-center mb-4">
        {getErrorIcon()}
      </div>
      
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {getErrorTitle()}
      </h3>
      
      <p className="text-gray-600 mb-2">
        {errorObj.message}
      </p>
      
      <p className="text-sm text-gray-500 mb-6">
        {getSuggestion()}
      </p>

      {showRetryButton && onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Try Again
        </button>
      )}
    </div>
  );
};

export const NetworkErrorMessage: React.FC<{ onRetry?: () => void }> = ({ onRetry }) => (
  <ErrorMessage
    error={{
      message: 'Unable to connect to our servers',
      code: 'NETWORK_ERROR'
    }}
    onRetry={onRetry}
  />
);

export const ServerErrorMessage: React.FC<{ onRetry?: () => void }> = ({ onRetry }) => (
  <ErrorMessage
    error={{
      message: 'Our servers are temporarily unavailable',
      code: 'HTTP_503'
    }}
    onRetry={onRetry}
  />
);

export const TimeoutErrorMessage: React.FC<{ onRetry?: () => void }> = ({ onRetry }) => (
  <ErrorMessage
    error={{
      message: 'Request timed out',
      code: 'TIMEOUT_ERROR'
    }}
    onRetry={onRetry}
  />
);

export default ErrorMessage;
