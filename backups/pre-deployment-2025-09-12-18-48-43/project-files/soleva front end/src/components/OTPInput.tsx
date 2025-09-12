import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

interface OTPInputProps {
  length?: number;
  value: string;
  onChange: (value: string) => void;
  onComplete?: (value: string) => void;
  disabled?: boolean;
  error?: boolean;
  autoFocus?: boolean;
  className?: string;
  placeholder?: string;
}

export default function OTPInput({
  length = 6,
  value,
  onChange,
  onComplete,
  disabled = false,
  error = false,
  autoFocus = true,
  className = '',
  placeholder = '•'
}: OTPInputProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Initialize refs array
  useEffect(() => {
    inputRefs.current = inputRefs.current.slice(0, length);
  }, [length]);

  // Auto-focus first input
  useEffect(() => {
    if (autoFocus && inputRefs.current[0]) {
      inputRefs.current[0].focus();
    }
  }, [autoFocus]);

  // Handle input change
  const handleChange = useCallback((index: number, inputValue: string) => {
    // Only allow numbers
    const numericValue = inputValue.replace(/[^0-9]/g, '');
    
    if (numericValue.length > 1) {
      // Handle paste operation
      const pastedValue = numericValue.slice(0, length);
      onChange(pastedValue);
      
      // Focus the last filled input or the next empty one
      const nextIndex = Math.min(pastedValue.length, length - 1);
      setTimeout(() => {
        inputRefs.current[nextIndex]?.focus();
        setActiveIndex(nextIndex);
      }, 0);
      
      // Check if complete
      if (pastedValue.length === length) {
        onComplete?.(pastedValue);
      }
      return;
    }

    // Single character input
    const newValue = value.split('');
    newValue[index] = numericValue;
    
    // Remove any undefined elements and join
    const finalValue = newValue.slice(0, length).join('').replace(/undefined/g, '');
    onChange(finalValue);

    // Move to next input if value was entered
    if (numericValue && index < length - 1) {
      setTimeout(() => {
        inputRefs.current[index + 1]?.focus();
        setActiveIndex(index + 1);
      }, 0);
    }

    // Check if complete
    if (finalValue.length === length) {
      onComplete?.(finalValue);
    }
  }, [value, onChange, onComplete, length]);

  // Handle key down events
  const handleKeyDown = useCallback((index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace') {
      e.preventDefault();
      
      if (value[index]) {
        // Clear current input
        const newValue = value.split('');
        newValue[index] = '';
        onChange(newValue.join('').replace(/undefined/g, ''));
      } else if (index > 0) {
        // Move to previous input and clear it
        const newValue = value.split('');
        newValue[index - 1] = '';
        onChange(newValue.join('').replace(/undefined/g, ''));
        
        setTimeout(() => {
          inputRefs.current[index - 1]?.focus();
          setActiveIndex(index - 1);
        }, 0);
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      e.preventDefault();
      inputRefs.current[index - 1]?.focus();
      setActiveIndex(index - 1);
    } else if (e.key === 'ArrowRight' && index < length - 1) {
      e.preventDefault();
      inputRefs.current[index + 1]?.focus();
      setActiveIndex(index + 1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (value.length === length) {
        onComplete?.(value);
      }
    }
  }, [value, onChange, onComplete, length]);

  // Handle focus
  const handleFocus = useCallback((index: number) => {
    setActiveIndex(index);
  }, []);

  // Handle paste
  const handlePaste = useCallback((e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text');
    const numericValue = pastedData.replace(/[^0-9]/g, '').slice(0, length);
    
    if (numericValue) {
      onChange(numericValue);
      
      // Focus the last filled input
      const nextIndex = Math.min(numericValue.length - 1, length - 1);
      setTimeout(() => {
        inputRefs.current[nextIndex]?.focus();
        setActiveIndex(nextIndex);
      }, 0);
      
      // Check if complete
      if (numericValue.length === length) {
        onComplete?.(numericValue);
      }
    }
  }, [onChange, onComplete, length]);

  // Generate array of input values
  const inputValues = Array.from({ length }, (_, index) => value[index] || '');

  return (
    <div className={clsx('flex gap-3 justify-center items-center', className)}>
      {inputValues.map((inputValue, index) => (
        <motion.div
          key={index}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: index * 0.1 }}
          className="relative"
        >
          <input
            ref={(el) => (inputRefs.current[index] = el)}
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={1}
            value={inputValue}
            onChange={(e) => handleChange(index, e.target.value)}
            onKeyDown={(e) => handleKeyDown(index, e)}
            onFocus={() => handleFocus(index)}
            onPaste={handlePaste}
            disabled={disabled}
            placeholder={placeholder}
            className={clsx(
              'w-14 h-14 sm:w-16 sm:h-16 text-center text-2xl font-bold rounded-xl border-2 transition-all duration-300',
              'focus:outline-none focus:ring-4',
              {
                // Normal state
                'border-gray-300 bg-white text-gray-900 focus:border-[#d1b16a] focus:ring-[#d1b16a]/20': !error && !disabled,
                
                // Error state
                'border-red-300 bg-red-50 text-red-900 focus:border-red-500 focus:ring-red-500/20': error && !disabled,
                
                // Disabled state
                'border-gray-200 bg-gray-100 text-gray-500 cursor-not-allowed': disabled,
                
                // Active state
                'border-[#d1b16a] ring-4 ring-[#d1b16a]/20 transform scale-105': activeIndex === index && !disabled && !error,
                
                // Filled state
                'border-[#d1b16a] bg-[#d1b16a]/5': inputValue && !error && !disabled,
                
                // Dark mode
                'dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100': !error && !disabled,
                'dark:focus:border-[#d1b16a] dark:focus:ring-[#d1b16a]/20': !error && !disabled,
              }
            )}
            style={{
              fontFamily: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace',
              // Prevent zoom on iOS
              fontSize: '16px'
            }}
          />
          
          {/* Animated border for focus */}
          <motion.div
            className={clsx(
              'absolute inset-0 rounded-xl border-2 pointer-events-none',
              activeIndex === index && !disabled && !error ? 'border-[#d1b16a]' : 'border-transparent'
            )}
            animate={{
              scale: activeIndex === index && !disabled && !error ? 1.05 : 1,
              opacity: activeIndex === index && !disabled && !error ? 1 : 0,
            }}
            transition={{ duration: 0.2 }}
          />
          
          {/* Success indicator */}
          {inputValue && !error && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full flex items-center justify-center"
            >
              <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </motion.div>
          )}
        </motion.div>
      ))}
    </div>
  );
}
