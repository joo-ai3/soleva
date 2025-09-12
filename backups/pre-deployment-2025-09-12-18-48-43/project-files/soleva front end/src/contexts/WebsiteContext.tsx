import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { SiteConfiguration, getCachedSiteConfig } from '../services/websiteManagementApi';

interface WebsiteContextType {
  siteConfig: SiteConfiguration | null;
  loading: boolean;
  refreshConfig: () => Promise<void>;
}

const WebsiteContext = createContext<WebsiteContextType | undefined>(undefined);

export const useWebsite = () => {
  const context = useContext(WebsiteContext);
  if (context === undefined) {
    throw new Error('useWebsite must be used within a WebsiteProvider');
  }
  return context;
};

interface WebsiteProviderProps {
  children: ReactNode;
}

export const WebsiteProvider = ({ children }: WebsiteProviderProps) => {
  const [siteConfig, setSiteConfig] = useState<SiteConfiguration | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchConfig = async () => {
    try {
      const config = await getCachedSiteConfig();
      setSiteConfig(config);
    } catch (error) {
      console.error('Failed to fetch site configuration:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshConfig = async () => {
    setLoading(true);
    await fetchConfig();
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  const value: WebsiteContextType = {
    siteConfig,
    loading,
    refreshConfig,
  };

  return (
    <WebsiteContext.Provider value={value}>
      {children}
    </WebsiteContext.Provider>
  );
};
