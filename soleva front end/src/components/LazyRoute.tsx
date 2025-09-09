import React, { Suspense } from 'react';
import LoadingSpinner from './ui/LoadingSpinner';
import ErrorBoundary from './ui/ErrorBoundary';

interface LazyRouteProps {
  component: React.LazyExoticComponent<React.ComponentType<any>>;
  fallback?: React.ComponentType;
}

const LazyRoute: React.FC<LazyRouteProps> = ({ 
  component: Component, 
  fallback: Fallback = LoadingSpinner 
}) => {
  return (
    <ErrorBoundary>
      <Suspense fallback={<Fallback />}>
        <Component />
      </Suspense>
    </ErrorBoundary>
  );
};

export default LazyRoute;
