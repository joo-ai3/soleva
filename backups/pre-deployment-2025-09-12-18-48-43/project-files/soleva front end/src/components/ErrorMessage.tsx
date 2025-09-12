import { motion, AnimatePresence } from 'framer-motion';
import { FiAlertCircle } from 'react-icons/fi';

interface ErrorMessageProps {
  error?: string;
  className?: string;
}

export default function ErrorMessage({ error, className = '' }: ErrorMessageProps) {
  return (
    <AnimatePresence>
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10, height: 0 }}
          animate={{ opacity: 1, y: 0, height: 'auto' }}
          exit={{ opacity: 0, y: -10, height: 0 }}
          transition={{ duration: 0.2 }}
          className={`flex items-center gap-2 text-red-600 text-sm mt-1 ${className}`}
        >
          <FiAlertCircle className="flex-shrink-0" size={14} />
          <span>{error}</span>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
