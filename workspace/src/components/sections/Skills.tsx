import { motion } from 'framer-motion';
import SectionTitle from '@/components/ui/SectionTitle';
import SkillCard from '@/components/ui/SkillCard';
import { skills } from '@/data/content';

const Skills = () => {
  const skillCategories = {
    frontend: 'Frontend Development',
    backend: 'Backend Development', 
    tools: 'Tools & Technologies'
  };

  // Group skills by category
  const groupedSkills = skills.reduce((acc, skill) => {
    if (!acc[skill.category]) {
      acc[skill.category] = [];
    }
    acc[skill.category].push(skill);
    return acc;
  }, {} as Record<string, typeof skills>);

  // Filter out 'other' category and ensure we only show defined categories
  const orderedCategories = ['frontend', 'backend', 'tools'].filter(
    category => groupedSkills[category] && groupedSkills[category].length > 0
  );

  return (
    <section id="skills" className="py-20 bg-gray-50 dark:bg-dark-800">
      <div className="container mx-auto px-4">
        <SectionTitle
          title="Skills & Technologies"
          subtitle="Technologies I work with and my proficiency levels"
        />

        <div className="space-y-16">
          {orderedCategories.map((category) => (
            <div key={category}>
              {/* Category Title */}
              <motion.h3
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5 }}
                className="text-2xl font-bold text-gray-900 dark:text-white mb-8 text-center"
              >
                {skillCategories[category as keyof typeof skillCategories]}
              </motion.h3>

              {/* Skills Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {groupedSkills[category].map((skill, index) => (
                  <SkillCard
                    key={skill.name}
                    name={skill.name}
                    level={skill.level}
                    icon={skill.icon}
                    delay={index * 0.1}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Skills Legend */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex justify-center mt-16"
        >
          <div className="bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-lg p-6 shadow-md">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4 text-center">
              Proficiency Levels
            </h4>
            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-skill-expert" />
                <span className="text-gray-600 dark:text-gray-300">Expert (90%)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-skill-advanced" />
                <span className="text-gray-600 dark:text-gray-300">Advanced (75%)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-skill-intermediate" />
                <span className="text-gray-600 dark:text-gray-300">Intermediate (60%)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-skill-beginner" />
                <span className="text-gray-600 dark:text-gray-300">Beginner (40%)</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Skills;
