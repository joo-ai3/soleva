# Frontend API Error Handling System

Complete error handling implementation for the Soleva frontend to ensure robust user experience even when the backend is unavailable.

## 🎯 Overview

The error handling system provides:
- **Centralized API service** with automatic error formatting
- **React error boundaries** for component-level error catching
- **Custom hooks** for API calls with built-in error handling
- **Loading states** and user-friendly error messages
- **Offline/online detection** with appropriate UI feedback
- **Retry mechanisms** for failed requests
- **Network status monitoring**

## 🔧 Core Components

### 1. API Service (`src/services/api.ts`)

Centralized service for all API calls with comprehensive error handling.

**Features:**
- Automatic token refresh for 401 errors
- Network status monitoring
- Request/response interceptors
- Standardized error formatting
- Timeout handling
- Retry mechanism with exponential backoff

**Usage:**
```typescript
import { apiService } from '../services/api';

// GET request
const response = await apiService.get<Product[]>('/products/');
if (response.success) {
  console.log(response.data);
} else {
  console.error(response.error);
}

// POST request
const response = await apiService.post('/orders/', orderData);
```

### 2. Custom Hooks (`src/hooks/useApi.ts`)

React hooks for API calls with built-in loading states and error handling.

**Available Hooks:**
- `useApi()` - Base hook for any API call
- `useApiQuery()` - For GET requests (immediate execution)
- `useApiMutation()` - For POST/PUT/DELETE (manual execution)
- `usePaginatedApi()` - For paginated data
- `useOptimisticApi()` - For optimistic updates

**Usage Examples:**

```typescript
// Query hook (automatic execution)
const { data, loading, error, retry } = useApiQuery(
  () => apiService.get('/orders/'),
  {
    retries: 2,
    onError: (error) => console.error('Failed to load orders:', error)
  }
);

// Mutation hook (manual execution)
const { execute, loading, error } = useApiMutation(
  (orderData) => apiService.post('/orders/', orderData),
  {
    onSuccess: (data) => console.log('Order created:', data),
    onError: (error) => console.error('Order creation failed:', error)
  }
);

// Execute the mutation
await execute(orderData);
```

### 3. Error Boundary (`src/components/ui/ErrorBoundary.tsx`)

React component that catches JavaScript errors in the component tree.

**Features:**
- Catches and displays component errors gracefully
- Development error details
- Retry functionality
- Navigation options

**Usage:**
```tsx
<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>

// Custom fallback
<ErrorBoundary fallback={<CustomErrorUI />}>
  <YourComponent />
</ErrorBoundary>
```

### 4. Loading Components (`src/components/ui/LoadingSpinner.tsx`)

Various loading indicators for different use cases.

**Available Components:**
- `LoadingSpinner` - Basic spinner with customizable size
- `PageLoadingSpinner` - Full-page loading state
- `InlineLoadingSpinner` - Inline loading for sections
- `ButtonLoadingSpinner` - Small spinner for buttons

**Usage:**
```tsx
// Page loading
{loading && <PageLoadingSpinner text="Loading products..." />}

// Button loading
<button disabled={loading}>
  {loading && <ButtonLoadingSpinner />}
  Submit
</button>

// Inline loading
{loading ? <InlineLoadingSpinner /> : <YourContent />}
```

### 5. Error Messages (`src/components/ui/ErrorMessage.tsx`)

User-friendly error message components.

**Features:**
- Contextual error icons and messages
- Retry functionality
- Inline and full-page variants
- Multilingual support

**Usage:**
```tsx
// Standard error message
<ErrorMessage 
  error={error} 
  onRetry={retryFunction}
/>

// Inline error
<ErrorMessage 
  error="Something went wrong"
  inline
  showRetryButton={false}
/>

// Predefined error types
<NetworkErrorMessage onRetry={retryFunction} />
<ServerErrorMessage onRetry={retryFunction} />
<TimeoutErrorMessage onRetry={retryFunction} />
```

### 6. Offline Indicator (`src/components/ui/OfflineIndicator.tsx`)

Displays network status and connectivity issues.

**Features:**
- Automatic online/offline detection
- Server reachability monitoring
- Auto-dismissing notifications
- Contextual messages

## 📱 Implementation Examples

### Basic Page with Error Handling

```tsx
import React from 'react';
import { useApiQuery } from '../hooks/useApi';
import { apiService } from '../services/api';
import ErrorMessage from '../components/ui/ErrorMessage';
import { PageLoadingSpinner } from '../components/ui/LoadingSpinner';

const ProductsPage: React.FC = () => {
  const {
    data: products,
    loading,
    error,
    retry
  } = useApiQuery(() => apiService.get('/products/'));

  if (loading && !products) {
    return <PageLoadingSpinner text="Loading products..." />;
  }

  if (error && !products) {
    return (
      <ErrorMessage 
        error={error}
        onRetry={retry}
        className="min-h-screen flex items-center justify-center"
      />
    );
  }

  return (
    <div>
      {/* Your products UI */}
      {products?.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
};
```

### Form with Error Handling

```tsx
const CheckoutForm: React.FC = () => {
  const [formData, setFormData] = useState({});
  
  const {
    execute: submitOrder,
    loading,
    error
  } = useApiMutation(
    (data) => apiService.post('/orders/', data),
    {
      onSuccess: (order) => {
        // Redirect to success page
        navigate(`/order-confirmation/${order.id}`);
      },
      onError: (error) => {
        // Error will be displayed in UI
        console.error('Order submission failed:', error);
      }
    }
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    await submitOrder(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <ErrorMessage 
          error={error}
          inline
          className="mb-4"
        />
      )}
      
      {/* Form fields */}
      
      <button type="submit" disabled={loading}>
        {loading && <ButtonLoadingSpinner />}
        Place Order
      </button>
    </form>
  );
};
```

### Cart with Optimistic Updates

```tsx
const CartPage: React.FC = () => {
  const {
    data: cart,
    loading,
    error,
    retry
  } = useApiQuery(() => apiService.get('/cart/'));

  const {
    executeOptimistic: updateQuantity,
    loading: updating
  } = useOptimisticApi(
    ({ itemId, quantity }) => apiService.patch(`/cart/items/${itemId}/`, { quantity }),
    {
      optimisticUpdate: (currentCart, { itemId, quantity }) => {
        // Update cart optimistically
        return {
          ...currentCart,
          items: currentCart.items.map(item =>
            item.id === itemId ? { ...item, quantity } : item
          )
        };
      },
      revertUpdate: (currentCart, originalCart) => originalCart,
      onSuccess: () => retry() // Refresh from server
    }
  );

  const handleQuantityChange = (itemId, newQuantity) => {
    updateQuantity({ itemId, quantity: newQuantity });
  };

  // Rest of component...
};
```

## 🛡️ Error Types and Handling

### Network Errors
- **No internet connection**: Clear message with retry option
- **Server unreachable**: Fallback UI with offline mode
- **Timeout**: Retry with exponential backoff

### HTTP Errors
- **400 Bad Request**: Show validation errors
- **401 Unauthorized**: Automatic token refresh or redirect to login
- **403 Forbidden**: Clear permission denied message
- **404 Not Found**: Resource not found message
- **429 Too Many Requests**: Rate limit message with retry timer
- **5xx Server Errors**: Server maintenance message

### Application Errors
- **Component crashes**: Error boundary with recovery options
- **Invalid data**: Graceful degradation with partial data
- **Feature unavailable**: Alternative actions or workarounds

## 🔄 Retry Strategies

### Automatic Retry
- Network timeouts: 3 retries with exponential backoff
- Server errors (5xx): 2 retries with delay
- Rate limiting: Retry after specified delay

### Manual Retry
- User-initiated retry buttons
- Pull-to-refresh functionality
- Background refresh on network recovery

### No Retry
- Client errors (4xx except 429)
- Invalid authentication
- Forbidden operations

## 🌍 Offline Support

### Detection
- Browser online/offline events
- Server connectivity checks
- Periodic health checks

### Fallback Behavior
- Show cached data when available
- Queue mutations for later execution
- Offline-first UI patterns

### Recovery
- Automatic sync on reconnection
- Conflict resolution for data changes
- User notification of sync status

## 📊 Monitoring and Logging

### Error Tracking
- Component error boundaries
- API error logging
- User action tracking

### Performance Monitoring
- API response times
- Error rates by endpoint
- Network quality metrics

### User Experience
- Loading time tracking
- Error recovery rates
- Offline usage patterns

## 🎨 User Experience Guidelines

### Loading States
- Immediate feedback for user actions
- Progressive loading for large datasets
- Skeleton screens for content placeholders

### Error Messages
- Clear, actionable error descriptions
- Consistent visual design
- Appropriate tone and language

### Recovery Options
- Always provide retry mechanisms
- Offer alternative actions when possible
- Guide users to successful completion

## ⚙️ Configuration

### Environment Variables
```env
VITE_API_BASE_URL=https://thesoleva.com/api
VITE_API_TIMEOUT=30000
VITE_RETRY_ATTEMPTS=3
VITE_RETRY_DELAY=1000
```

### API Service Configuration
```typescript
// Configure API service
const apiService = new ApiService({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  retries: 3,
  retryDelay: 1000
});
```

## 🧪 Testing

### Error Scenarios to Test
1. **Network disconnection** during API calls
2. **Server downtime** and recovery
3. **Slow connections** and timeouts
4. **Invalid responses** and malformed data
5. **Authentication expiration**
6. **Rate limiting** scenarios
7. **Component crashes** and recovery

### Testing Tools
- Network throttling in dev tools
- API mocking for error responses
- Offline mode testing
- Error injection utilities

## 📈 Best Practices

### Implementation
1. **Always handle errors** - Never let API calls fail silently
2. **Provide feedback** - Show loading states and error messages
3. **Enable recovery** - Always offer retry mechanisms
4. **Graceful degradation** - Show partial data when possible
5. **Cache strategically** - Store data for offline access

### User Experience
1. **Be transparent** - Explain what went wrong
2. **Be helpful** - Suggest next steps
3. **Be forgiving** - Allow easy recovery
4. **Be consistent** - Use standard patterns
5. **Be responsive** - Handle all device types

### Performance
1. **Minimize requests** - Batch operations when possible
2. **Cache responses** - Reduce redundant calls
3. **Optimize retries** - Use exponential backoff
4. **Monitor metrics** - Track error rates and performance
5. **Preload data** - Anticipate user needs

---

This error handling system ensures that the Soleva frontend remains functional and user-friendly even when the backend is experiencing issues. Users will always receive appropriate feedback and have options to recover from error states.
