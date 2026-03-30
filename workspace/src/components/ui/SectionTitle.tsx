import { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface SectionTitleProps {
  title: string;
  subtitle?: string;
  centered?: boolean;
  className?: string;
}

const SectionTitle = forwardRef<HTMLDivElement, SectionTitleProps>(
  ({ className, title, subtitle, centered = true }, ref) => {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className={cn('mb-12', centered && 'text-center', className)}
        ref={ref}
      >
        <div className="relative inline-block">
          <h2 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-gray-900 via-primary-600 to-gray-900 dark:from-white dark:via-primary-400 dark:to-white bg-clip-text text-transparent mb-4">
            {title}
          </h2>
          
          {/* Animated Decorative Underline */}
          <motion.div
            initial={{ width: 0 }}
            whileInView={{ width: '100%' }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.3, ease: "easeOut" }}
            className="absolute -bottom-2 left-0 h-1 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full"
          />
          
          {/* Decorative dots */}
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.6 }}
            className="absolute -bottom-1 -right-2 w-2 h-2 bg-primary-500 rounded-full"
          />
          
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.8 }}
            className="absolute -bottom-1 -right-6 w-1 h-1 bg-primary-400 rounded-full"
          />
        </div>
        
        {subtitle && (
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto mt-6"
          >
            {subtitle}
          </motion.p>
        )}
      </motion.div>
    );
  }
);

SectionTitle.displayName = 'SectionTitle';

export default SectionTitle;
