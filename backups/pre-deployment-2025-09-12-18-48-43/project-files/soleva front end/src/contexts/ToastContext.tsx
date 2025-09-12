import React, { createContext, useContext, useState } from 'react';
import * as Toast from '@radix-ui/react-toast';

interface ToastContextType {
  showToast: (message: string) => void;
  addToast: (message: string, type?: 'success' | 'error' | 'info' | 'warning') => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [msg, setMsg] = useState("");
  
  const showToast = (message: string) => {
    setMsg(message);
    setOpen(false);
    setTimeout(() => setOpen(true), 50);
  };

  const addToast = (message: string) => {
    showToast(message);
  };
  
  return (
    <ToastContext.Provider value={{ showToast, addToast }}>
      <Toast.Provider swipeDirection="right">
        {children}
        <Toast.Root 
          open={open} 
          onOpenChange={setOpen} 
          className="fixed bottom-6 left-1/2 -translate-x-1/2 glass px-7 py-4 shadow-lg z-[9999] flex items-center gap-3 text-lg font-semibold text-[#111]"
        >
          <Toast.Title>{msg}</Toast.Title>
        </Toast.Root>
        <Toast.Viewport />
      </Toast.Provider>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}