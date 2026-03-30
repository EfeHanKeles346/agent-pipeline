import { motion } from 'framer-motion';
import * as LucideIcons from 'lucide-react';
import { Settings } from 'lucide-react';
import ProgressBar from './ProgressBar';
import { useIntersectionObserver } from '@/hooks/useIntersectionObserver';
import { getSkillLevelColor } from '@/lib/utils';

interface SkillCardProps {
  name: string;
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  icon: string;
  delay?: number;
}

const SkillCard = ({ name, level, icon, delay = 0 }: SkillCardProps) => {
  const { ref, isIntersecting } = useIntersectionObserver({
    threshold: 0.3,
    triggerOnce: true
  });

  // Dynamically get icon component with fallback
  const getIconComponent = (iconName: string) => {
    const iconMap = LucideIcons as any;
    return iconMap[iconName] || Settings;
  };

  const IconComponent = getIconComponent(icon);

  // Convert level to percentage
  const getLevelPercentage = (level: string): number => {
    const percentages = {
      beginner: 40,
      intermediate: 60,
      advanced: 75,
      expert: 90
    };
    return percentages[level as keyof typeof percentages] || 40;
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={{ 
        opacity: isIntersecting ? 1 : 0, 
        y: isIntersecting ? 0 : 30 
      }}
      transition={{ 
        duration: 0.6, 
        delay: isIntersecting ? delay : 0,
        ease: "easeOut"
      }}
      whileHover={{ 
        scale: 1.02,
        transition: { duration: 0.2 }
      }}
      className="bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-lg p-6 shadow-md hover:shadow-lg transition-all duration-300"
    >
      {/* Icon */}
      <div className="flex items-center justify-center w-12 h-12 mb-4 mx-auto">
        <IconComponent 
          className="w-8 h-8 text-primary-500 dark:text-primary-400" 
          aria-hidden="true"
        />
      </div>

      {/* Skill Name */}
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white text-center mb-3">
        {name}
      </h3>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-600 dark:text-gray-400 capitalize">
            {level}
          </span>
          <span className="text-gray-500 dark:text-gray-400 font-medium">
            {getLevelPercentage(level)}%
          </span>
        </div>
        
        <ProgressBar
          percentage={getLevelPercentage(level)}
          level={level}
          animate={isIntersecting}
        />
      </div>

      {/* Level indicator dot */}
      <div className="flex justify-center mt-4">
        <div 
          className={`w-3 h-3 rounded-full ${getSkillLevelColor(level)}`}
          title={`${level} level`}
          aria-label={`Skill level: ${level}`}
        />
      </div>
    </motion.div>
  );
};

export default SkillCard;
