import { motion } from 'framer-motion';
import { Calendar, CheckCircle, Users, Download } from 'lucide-react';
import SectionTitle from '@/components/ui/SectionTitle';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { aboutText, keyStats, personalInfo } from '@/data/content';

const About = () => {
  const iconMap = {
    Calendar,
    CheckCircle,
    Users
  };

  return (
    <section id="about" className="py-20">
      <div className="container mx-auto px-4">
        <SectionTitle
          title="About Me"
          subtitle="Get to know more about my background and experience"
        />

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Left Side - Profile Image & Bio */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="space-y-8"
          >
            {/* Profile Image Placeholder */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="flex justify-center md:justify-start"
            >
              <div 
                className="w-48 h-48 bg-gray-200 dark:bg-dark-700 border-4 border-white dark:border-dark-800 rounded-full shadow-xl flex items-center justify-center"
                role="img"
                aria-label="Profile placeholder"
              >
                <div className="text-center text-gray-500 dark:text-gray-400">
                  <Users className="h-16 w-16 mx-auto mb-2" />
                  <span className="text-sm">Profile Photo</span>
                </div>
              </div>
            </motion.div>

            {/* Bio Text */}
            <div className="prose prose-lg dark:prose-invert max-w-none text-center md:text-left">
              {aboutText.split('\n\n').map((paragraph, index) => (
                <motion.p
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="text-gray-600 dark:text-gray-300 leading-relaxed mb-4"
                >
                  {paragraph.trim()}
                </motion.p>
              ))}
            </div>
          </motion.div>

          {/* Right Side - Stats & CV Button */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="space-y-8"
          >
            {/* Key Stats */}
            <div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center md:text-left">
                Key Statistics
              </h3>
              
              <div className="grid grid-cols-1 gap-4">
                {keyStats.map((stat, index) => {
                  const IconComponent = iconMap[stat.icon as keyof typeof iconMap];
                  
                  return (
                    <motion.div
                      key={stat.label}
                      initial={{ opacity: 0, y: 20 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.4, delay: index * 0.1 }}
                    >
                      <Card padding="md" hover={true}>
                        <div className="text-center">
                          <IconComponent className="h-8 w-8 text-primary-500 dark:text-primary-400 mx-auto mb-3" />
                          <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                            {stat.value}
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-300">
                            {stat.label}
                          </div>
                        </div>
                      </Card>
                    </motion.div>
                  );
                })}
              </div>
            </div>

            {/* Download Resume Button */}
            {personalInfo.resumeUrl && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="flex justify-center md:justify-start"
              >
                <Button 
                  size="lg" 
                  asChild
                  aria-label="Download my resume"
                >
                  <a 
                    href={personalInfo.resumeUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download Resume
                  </a>
                </Button>
              </motion.div>
            )}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default About;
