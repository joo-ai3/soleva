import React, { useState, useEffect } from 'react';
import { WifiOff, Wifi } from 'lucide-react';
import { apiService } from '../../services/api';

export const OfflineIndicator: React.FC = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isServerReachable, setIsServerReachable] = useState(true);
  const [showNotification, setShowNotification] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      checkServerConnection();
    };

    const handleOffline = () => {
      setIsOnline(false);
      setIsServerReachable(false);
      setShowNotification(true);
    };

    const checkServerConnection = async () => {
      const status = apiService.getNetworkStatus();
      setIsServerReachable(status.isServerReachable);
      
      if (!status.isServerReachable && isOnline) {
        setShowNotification(true);
      }
    };

    // Initial check
    checkServerConnection();

    // Listen to online/offline events
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Periodic server health check
    const interval = setInterval(checkServerConnection, 30000); // Check every 30 seconds

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(interval);
    };
  }, [isOnline]);

  useEffect(() => {
    if (isOnline && isServerReachable && showNotification) {
      // Auto-hide notification when connection is restored
      const timer = setTimeout(() => {
        setShowNotification(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isOnline, isServerReachable, showNotification]);

  if (!showNotification && isOnline && isServerReachable) {
    return null;
  }

  const getStatus = () => {
    if (!isOnline) {
      return {
        icon: <WifiOff className="h-5 w-5" />,
        message: 'No internet connection',
        description: 'Please check your network settings',
        bgColor: 'bg-red-500',
        textColor: 'text-white'
      };
    } else if (!isServerReachable) {
      return {
        icon: <WifiOff className="h-5 w-5" />,
        message: 'Server unavailable',
        description: 'Our services are temporarily down',
        bgColor: 'bg-orange-500',
        textColor: 'text-white'
      };
    } else {
      return {
        icon: <Wifi className="h-5 w-5" />,
        message: 'Connection restored',
        description: 'You are back online',
        bgColor: 'bg-green-500',
        textColor: 'text-white'
      };
    }
  };

  const status = getStatus();

  return (
    <div className={`fixed top-0 left-0 right-0 z-50 ${status.bgColor} ${status.textColor} p-3 text-center shadow-lg transition-transform duration-300 ${showNotification ? 'translate-y-0' : '-translate-y-full'}`}>
      <div className="flex items-center justify-center space-x-2">
        {status.icon}
        <div className="text-sm">
          <span className="font-medium">{status.message}</span>
          {status.description && (
            <span className="ml-2 opacity-90">• {status.description}</span>
          )}
        </div>
        {(isOnline && isServerReachable) && (
          <button
            onClick={() => setShowNotification(false)}
            className="ml-4 text-white hover:text-gray-200 transition-colors"
            aria-label="Dismiss notification"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
};

export default OfflineIndicator;
