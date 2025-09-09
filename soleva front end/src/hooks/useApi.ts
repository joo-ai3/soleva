import { useState, useEffect, useCallback, useRef } from 'react';
import { apiService, ApiResponse, ApiError } from '../services/api';

interface UseApiOptions {
  immediate?: boolean;
  retries?: number;
  retryDelay?: number;
  onSuccess?: (data: any) => void;
  onError?: (error: ApiError) => void;
}

interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  execute: (...args: any[]) => Promise<ApiResponse<T>>;
  retry: () => Promise<ApiResponse<T>>;
  reset: () => void;
}

export function useApi<T = any>(
  apiFunction: (...args: any[]) => Promise<ApiResponse<T>>,
  options: UseApiOptions = {}
): UseApiReturn<T> {
  const {
    immediate = false,
    retries = 0,
    retryDelay = 1000,
    onSuccess,
    onError
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState<ApiError | null>(null);
  
  const argsRef = useRef<any[]>([]);
  const mountedRef = useRef(true);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const execute = useCallback(async (...args: any[]): Promise<ApiResponse<T>> => {
    argsRef.current = args;
    
    if (!mountedRef.current) return { data: null as T, success: false };
    
    setLoading(true);
    setError(null);

    try {
      let response: ApiResponse<T>;
      
      if (retries > 0) {
        response = await apiService.retryRequest(
          () => apiFunction(...args),
          retries + 1,
          retryDelay
        );
      } else {
        response = await apiFunction(...args);
      }

      if (!mountedRef.current) return response;

      if (response.success) {
        setData(response.data);
        onSuccess?.(response.data);
      } else {
        setError(response.error || { message: 'Unknown error occurred' });
        onError?.(response.error || { message: 'Unknown error occurred' });
      }

      return response;
    } catch (err) {
      const error = err as ApiError;
      if (mountedRef.current) {
        setError(error);
        onError?.(error);
      }
      return { data: null as T, success: false, error };
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [apiFunction, retries, retryDelay, onSuccess, onError]);

  const retry = useCallback(() => {
    return execute(...argsRef.current);
  }, [execute]);

  const reset = useCallback(() => {
    setData(null);
    setLoading(false);
    setError(null);
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  return {
    data,
    loading,
    error,
    execute,
    retry,
    reset
  };
}

// Specialized hooks for common patterns
export function useApiQuery<T = any>(
  apiFunction: () => Promise<ApiResponse<T>>,
  options: UseApiOptions = {}
): UseApiReturn<T> {
  return useApi(apiFunction, { immediate: true, ...options });
}

export function useApiMutation<T = any, P = any>(
  apiFunction: (params: P) => Promise<ApiResponse<T>>,
  options: UseApiOptions = {}
): UseApiReturn<T> {
  return useApi(apiFunction, { immediate: false, ...options });
}

// Hook for paginated data
export function usePaginatedApi<T = any>(
  apiFunction: (page: number, ...args: any[]) => Promise<ApiResponse<{ results: T[]; count: number; next: string | null; previous: string | null }>>,
  options: UseApiOptions = {}
) {
  const [allData, setAllData] = useState<T[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  
  const { data, loading, error, execute, retry, reset } = useApi(
    apiFunction,
    {
      ...options,
      onSuccess: (response) => {
        if (page === 1) {
          setAllData(response.results);
        } else {
          setAllData(prev => [...prev, ...response.results]);
        }
        setHasMore(!!response.next);
        options.onSuccess?.(response);
      }
    }
  );

  const loadMore = useCallback(async () => {
    if (!loading && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      await execute(nextPage);
    }
  }, [loading, hasMore, page, execute]);

  const refresh = useCallback(async () => {
    setPage(1);
    setAllData([]);
    setHasMore(true);
    await execute(1);
  }, [execute]);

  const resetPagination = useCallback(() => {
    setPage(1);
    setAllData([]);
    setHasMore(true);
    reset();
  }, [reset]);

  return {
    data: allData,
    loading,
    error,
    hasMore,
    loadMore,
    refresh,
    reset: resetPagination,
    retry
  };
}

// Hook for optimistic updates
export function useOptimisticApi<T = any>(
  apiFunction: (...args: any[]) => Promise<ApiResponse<T>>,
  options: UseApiOptions & {
    optimisticUpdate?: (currentData: T | null, ...args: any[]) => T | null;
    revertUpdate?: (currentData: T | null, originalData: T | null) => T | null;
  } = {}
): UseApiReturn<T> & { executeOptimistic: (...args: any[]) => Promise<ApiResponse<T>> } {
  const baseHook = useApi(apiFunction, options);
  const originalDataRef = useRef<T | null>(null);

  const executeOptimistic = useCallback(async (...args: any[]): Promise<ApiResponse<T>> => {
    const { optimisticUpdate, revertUpdate } = options;
    
    if (optimisticUpdate) {
      originalDataRef.current = baseHook.data;
      const optimisticData = optimisticUpdate(baseHook.data, ...args);
      if (optimisticData !== undefined) {
        // Directly update the data state for optimistic update
        (baseHook as any).setData?.(optimisticData);
      }
    }

    const response = await baseHook.execute(...args);

    if (!response.success && revertUpdate && optimisticUpdate) {
      // Revert optimistic update on failure
      const revertedData = revertUpdate(baseHook.data, originalDataRef.current);
      if (revertedData !== undefined) {
        (baseHook as any).setData?.(revertedData);
      }
    }

    return response;
  }, [baseHook, options]);

  return {
    ...baseHook,
    executeOptimistic
  };
}

export default useApi;