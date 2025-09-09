import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

interface CountdownTimerProps {
  initialTime: number; // Time in seconds
  onComplete?: () => void;
  onTick?: (timeLeft: number) => void;
  showProgress?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'danger' | 'warning';
  className?: string;
}

export default function CountdownTimer({
  initialTime,
  onComplete,
  onTick,
  showProgress = true,
  size = 'md',
  variant = 'default',
  className = ''
}: CountdownTimerProps) {
  const [timeLeft, setTimeLeft] = useState(initialTime);
  const [isActive, setIsActive] = useState(true);

  useEffect(() => {
    setTimeLeft(initialTime);
    setIsActive(true);
  }, [initialTime]);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prevTime) => {
          const newTime = prevTime - 1;
          onTick?.(newTime);
          
          if (newTime <= 0) {
            setIsActive(false);
            onComplete?.();
          }
          
          return newTime;
        });
      }, 1000);
    } else if (timeLeft <= 0) {
      setIsActive(false);
      onComplete?.();
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive, timeLeft, onComplete, onTick]);

  // Format time as MM:SS
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Calculate progress percentage
  const progress = initialTime > 0 ? ((initialTime - timeLeft) / initialTime) * 100 : 0;

  // Get variant colors
  const getVariantColors = () => {
    switch (variant) {
      case 'danger':
        return {
          text: 'text-red-600 dark:text-red-400',
          progress: 'from-red-500 to-red-600',
          bg: 'bg-red-100 dark:bg-red-900/20',
          border: 'border-red-200 dark:border-red-800'
        };
      case 'warning':
        return {
          text: 'text-amber-600 dark:text-amber-400',
          progress: 'from-amber-500 to-amber-600',
          bg: 'bg-amber-100 dark:bg-amber-900/20',
          border: 'border-amber-200 dark:border-amber-800'
        };
      default:
        return {
          text: 'text-[#d1b16a] dark:text-[#d1b16a]',
          progress: 'from-[#d1b16a] to-[#b8965a]',
          bg: 'bg-[#d1b16a]/10 dark:bg-[#d1b16a]/20',
          border: 'border-[#d1b16a]/20 dark:border-[#d1b16a]/30'
        };
    }
  };

  // Get size classes
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return {
          container: 'px-3 py-2',
          text: 'text-sm',
          progress: 'h-1'
        };
      case 'lg':
        return {
          container: 'px-6 py-4',
          text: 'text-xl',
          progress: 'h-2'
        };
      default:
        return {
          container: 'px-4 py-3',
          text: 'text-base',
          progress: 'h-1.5'
        };
    }
  };

  const colors = getVariantColors();
  const sizes = getSizeClasses();

  // Determine if we should show warning state (last 30 seconds)
  const isWarning = timeLeft <= 30 && timeLeft > 0;
  const isDanger = timeLeft <= 10 && timeLeft > 0;

  const currentColors = isDanger ? getVariantColors() : isWarning ? { ...getVariantColors(), ...({ text: 'text-amber-600 dark:text-amber-400' }) } : colors;

  if (timeLeft <= 0) {
    return (
      <motion.div
        initial={{ opacity: 1 }}
        animate={{ opacity: 0.6 }}
        className={clsx(
          'inline-flex items-center justify-center rounded-lg border',
          'bg-gray-100 dark:bg-gray-800 border-gray-200 dark:border-gray-700',
          'text-gray-500 dark:text-gray-400',
          sizes.container,
          sizes.text,
          className
        )}
      >
        <span className="font-mono font-semibold">00:00</span>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={clsx(
        'inline-flex flex-col items-center justify-center rounded-lg border',
        currentColors.bg,
        currentColors.border,
        sizes.container,
        className
      )}
    >
      {/* Timer display */}
      <motion.div
        animate={{
          scale: isDanger ? [1, 1.05, 1] : 1,
        }}
        transition={{
          duration: 1,
          repeat: isDanger ? Infinity : 0,
          repeatType: "reverse"
        }}
        className={clsx('font-mono font-semibold', currentColors.text, sizes.text)}
      >
        {formatTime(timeLeft)}
      </motion.div>

      {/* Progress bar */}
      {showProgress && (
        <div className={clsx('w-full mt-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden', sizes.progress)}>
          <motion.div
            className={clsx('h-full bg-gradient-to-r', currentColors.progress)}
            initial={{ width: '0%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
      )}

      {/* Pulse animation for danger state */}
      {isDanger && (
        <motion.div
          className={clsx(
            'absolute inset-0 rounded-lg border-2',
            'border-red-500 pointer-events-none'
          )}
          animate={{
            opacity: [0, 1, 0],
            scale: [1, 1.05, 1],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            repeatType: "reverse"
          }}
        />
      )}
    </motion.div>
  );
}
