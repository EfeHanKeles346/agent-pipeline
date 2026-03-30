import { motion } from 'framer-motion';
import { Github, Linkedin, Twitter, Mail, ChevronUp } from 'lucide-react';
import { personalInfo } from '@/data/content';
import { scrollToTop, useScrollPosition } from '@/lib/utils';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  const scrollPosition = useScrollPosition();
  const showBackToTop = scrollPosition > 200;

  const socialLinks = [
    { icon: Github, href: personalInfo.github, label: 'GitHub' },
    { icon: Linkedin, href: personalInfo.linkedin, label: 'LinkedIn' },
    ...(personalInfo.twitter ? [{ icon: Twitter, href: personalInfo.twitter, label: 'Twitter' }] : []),
    { icon: Mail, href: `mailto:${personalInfo.email}`, label: 'Email' }
  ];

  const handleBackToTop = () => {
    scrollToTop();
  };

  return (
    <footer className="bg-gray-50 dark:bg-dark-800 border-t border-gray-200 dark:border-dark-700 relative">
      <div className="container mx-auto px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center"
        >
          {/* Social Links */}
          <div className="flex justify-center space-x-6 mb-8">
            {socialLinks.map(({ icon: Icon, href, label }) => (
              <motion.a
                key={label}
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-primary-500 dark:text-gray-400 dark:hover:text-primary-400 transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                aria-label={label}
              >
                <Icon className="h-6 w-6" />
              </motion.a>
            ))}
          </div>

          {/* Copyright */}
          <div className="border-t border-gray-200 dark:border-dark-700 pt-8">
            <p className="text-gray-600 dark:text-gray-400">
              © {currentYear} {personalInfo.name}. All rights reserved.
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
              Built with React, TypeScript, and Tailwind CSS
            </p>
          </div>
        </motion.div>
      </div>

      {/* Back to Top Button */}
      <motion.button
        onClick={handleBackToTop}
        className="fixed bottom-8 right-8 z-50 bg-primary-500 hover:bg-primary-600 text-white p-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-dark-900"
        initial={{ opacity: 0, scale: 0 }}
        animate={{ 
          opacity: showBackToTop ? 1 : 0,
          scale: showBackToTop ? 1 : 0 
        }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        whileHover={{ 
          scale: 1.1,
          y: -2,
          transition: { duration: 0.2 }
        }}
        whileTap={{ 
          scale: 0.95,
          transition: { duration: 0.1 }
        }}
        aria-label="Scroll to top"
        style={{ display: showBackToTop ? 'block' : 'none' }}
      >
        <ChevronUp className="h-6 w-6" />
      </motion.button>
    </footer>
  );
};

export default Footer;
