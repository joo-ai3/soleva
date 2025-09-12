import React, { createContext, useContext, useState } from 'react';
import { translations } from '../constants/translations';

interface LangContextType {
  lang: string;
  setLang: (lang: string) => void;
}

const LangContext = createContext<LangContextType | undefined>(undefined);

export function LangProvider({ children }: { children: React.ReactNode }) {
  const getDefaultLang = () => {
    const navLang = (navigator.language || "en").toLowerCase();
    if (navLang.startsWith("ar")) return "ar";
    return "en";
  };
  
  const [lang, setLang] = useState(getDefaultLang);
  
  return (
    <LangContext.Provider value={{ lang, setLang }}>
      {children}
    </LangContext.Provider>
  );
}

export function useLang() {
  const context = useContext(LangContext);
  if (!context) {
    throw new Error('useLang must be used within LangProvider');
  }
  return context;
}

export function useTranslation() {
  const { lang } = useLang();
  return (key: string) => translations[lang as keyof typeof translations][key as keyof typeof translations.en] || key;
}