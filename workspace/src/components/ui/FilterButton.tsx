import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface FilterButtonProps {
  label: string;
  isActive: boolean;
  count: number;
  onClick: () => void;
}

const FilterButton = ({ label, isActive, count, onClick }: FilterButtonProps) => {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ 
        scale: 1.05,
        y: -2,
        transition: { duration: 0.2 }
      }}
      whileTap={{ 
        scale: 0.95,
        transition: { duration: 0.1 }
      }}
      className={cn(
        'relative px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-dark-900',
        isActive
          ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/25'
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-dark-700 dark:text-gray-300 dark:hover:bg-dark-600'
      )}
      aria-pressed={isActive}
      aria-label={`Filter by ${label} (${count} projects)`}
    >
      <span className="flex items-center space-x-2">
        <span>{label}</span>
        <motion.span
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className={cn(
            'inline-flex items-center justify-center w-5 h-5 text-xs font-bold rounded-full',
            isActive
              ? 'bg-white/20 text-white'
              : 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400'
          )}
        >
          {count}
        </motion.span>
      </span>

      {/* Active indicator */}
      {isActive && (
        <motion.div
          layoutId="activeFilter"
          className="absolute inset-0 bg-primary-500 rounded-full -z-10"
          transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
        />
      )}
    </motion.button>
  );
};

export default FilterButton;
