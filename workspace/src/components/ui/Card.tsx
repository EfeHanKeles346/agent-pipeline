import { HTMLAttributes, forwardRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hover?: boolean;
  padding?: 'sm' | 'md' | 'lg';
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, children, hover = true, padding = 'md', ...props }, ref) => {
    const baseStyles = 'backdrop-blur-sm bg-white/80 dark:bg-dark-800/80 border border-gray-200/50 dark:border-dark-700/50 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300';
    
    const paddings = {
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8'
    };

    const CardContent = (
      <div
        className={cn(baseStyles, paddings[padding], className)}
        ref={ref}
        {...props}
      >
        {children}
      </div>
    );

    if (hover) {
      return (
        <motion.div
          whileHover={{ 
            y: -4,
            transition: { duration: 0.3, ease: "easeOut" }
          }}
          className="h-full"
        >
          {CardContent}
        </motion.div>
      );
    }

    return CardContent;
  }
);

Card.displayName = 'Card';

export default Card;
