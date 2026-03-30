import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronUp, ArrowUp } from 'lucide-react';
import { useScrollPosition } from '@/lib/utils';

interface ScrollToTopProps {
  showProgress?: boolean;
  threshold?: number;
  offset?: number;
}

const ScrollToTop = ({
  showProgress = true,
  threshold = 300,
  offset: _offset = 100
}: ScrollToTopProps) => {
  const scrollPosition = useScrollPosition();
  const [isVisible, setIsVisible] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    const shouldShow = scrollPosition > threshold;
    setIsVisible(shouldShow);

    // Calculate scroll progress
    if (typeof window !== 'undefined') {
      const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = Math.min((scrollPosition / documentHeight) * 100, 100);
      setScrollProgress(progress);
    }
  }, [scrollPosition, threshold]);

  const handleScrollToTop = () => {
    if (typeof window !== 'undefined') {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleScrollToTop();
    }
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ 
            opacity: 0, 
            scale: 0,
            y: 20
          }}
          animate={{ 
            opacity: 1, 
            scale: 1,
            y: 0
          }}
          exit={{ 
            opacity: 0, 
            scale: 0,
            y: 20
          }}
          transition={{ 
            type: "spring",
            stiffness: 260,
            damping: 20,
            duration: 0.3
          }}
          className="fixed bottom-8 right-8 z-50 no-print"
          style={{ 
            filter: 'drop-shadow(0 4px 12px rgba(0, 0, 0, 0.15))' 
          }}
        >
          {/* Progress Ring (if enabled) */}
          {showProgress && (
            <svg
              className="absolute inset-0 w-14 h-14 transform -rotate-90"
              viewBox="0 0 56 56"
            >
              {/* Background circle */}
              <circle
                cx="28"
                cy="28"
                r="26"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                className="text-gray-300 dark:text-gray-600"
              />
              
              {/* Progress circle */}
              <motion.circle
                cx="28"
                cy="28"
                r="26"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                className="text-primary-500 dark:text-primary-400"
                style={{
                  pathLength: scrollProgress / 100,
                  strokeDasharray: "163.36 163.36", // 2 * π * 26
                }}
                initial={{ pathLength: 0 }}
                animate={{ pathLength: scrollProgress / 100 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
              />
            </svg>
          )}

          {/* Main Button */}
          <motion.button
            onClick={handleScrollToTop}
            onKeyDown={handleKeyDown}
            className={`
              relative flex items-center justify-center w-14 h-14 
              bg-white dark:bg-dark-800 
              border-2 border-primary-500 dark:border-primary-400
              text-primary-500 dark:text-primary-400
              rounded-full shadow-lg hover:shadow-xl 
              transition-all duration-300 
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 
              dark:focus:ring-primary-400 dark:focus:ring-offset-dark-900
              hover:bg-primary-50 dark:hover:bg-primary-900/20
              group gpu-accelerated
            `}
            whileHover={{ 
              scale: 1.05,
              y: -2,
            }}
            whileTap={{ 
              scale: 0.95,
              y: 0,
            }}
            aria-label={`Scroll to top (${scrollProgress.toFixed(0)}% scrolled)`}
            title={`Back to top - ${scrollProgress.toFixed(0)}% scrolled`}
          >
            {/* Icon with animation */}
            <motion.div
              animate={{ 
                y: scrollProgress > 90 ? -1 : 0 
              }}
              transition={{ duration: 0.2 }}
            >
              {scrollProgress > 90 ? (
                <ArrowUp className="h-6 w-6 group-hover:scale-110 transition-transform" />
              ) : (
                <ChevronUp className="h-6 w-6 group-hover:scale-110 transition-transform" />
              )}
            </motion.div>

            {/* Ripple effect on click */}
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-primary-500 dark:border-primary-400"
              initial={{ scale: 1, opacity: 0 }}
              animate={{ scale: 1.5, opacity: 0 }}
              transition={{ duration: 0.6, repeat: Infinity, repeatDelay: 2 }}
            />
          </motion.button>

          {/* Tooltip */}
          <motion.div
            initial={{ opacity: 0, x: 10 }}
            whileHover={{ opacity: 1, x: 0 }}
            className="absolute right-full mr-4 top-1/2 -translate-y-1/2 hidden md:block pointer-events-none"
          >
            <div className="bg-gray-900 dark:bg-white text-white dark:text-gray-900 text-sm px-3 py-2 rounded-lg whitespace-nowrap">
              Back to top
              <div className="absolute top-1/2 -translate-y-1/2 -right-1 w-2 h-2 bg-gray-900 dark:bg-white rotate-45" />
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ScrollToTop;
