import { motion } from 'framer-motion';

interface ProgressBarProps {
  percentage: number;
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  animate: boolean;
}

const ProgressBar = ({ percentage, level, animate }: ProgressBarProps) => {
  // Map level to Tailwind color classes for the bar
  const getBarColor = (level: string): string => {
    const colors = {
      expert: 'bg-skill-expert',
      advanced: 'bg-skill-advanced', 
      intermediate: 'bg-skill-intermediate',
      beginner: 'bg-skill-beginner'
    };
    return colors[level as keyof typeof colors] || 'bg-gray-500';
  };

  return (
    <div className="relative">
      {/* Background bar */}
      <div className="w-full h-2 bg-gray-200 dark:bg-dark-700 rounded-full overflow-hidden">
        {/* Animated fill bar */}
        <motion.div
          className={`h-full rounded-full ${getBarColor(level)}`}
          initial={{ width: 0 }}
          animate={{ 
            width: animate ? `${percentage}%` : 0 
          }}
          transition={{ 
            duration: 1.5, 
            delay: animate ? 0.5 : 0,
            ease: "easeOut"
          }}
        />
      </div>

      {/* Glow effect for expert level */}
      {level === 'expert' && (
        <motion.div
          className="absolute inset-0 h-2 bg-skill-expert rounded-full opacity-50 blur-sm"
          initial={{ width: 0 }}
          animate={{ 
            width: animate ? `${percentage}%` : 0 
          }}
          transition={{ 
            duration: 1.5, 
            delay: animate ? 0.7 : 0,
            ease: "easeOut"
          }}
        />
      )}
    </div>
  );
};

export default ProgressBar;
