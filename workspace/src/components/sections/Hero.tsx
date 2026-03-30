import React from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, Download, ExternalLink, Github, Linkedin, Twitter, Mail } from 'lucide-react';
import { ReactTyped } from 'react-typed';
import { personalInfo, typingTexts } from '@/data/content';
import Button from '@/components/ui/Button';

const Hero = () => {

  const socialLinks = [
    { icon: Github, href: personalInfo.github, label: 'GitHub' },
    { icon: Linkedin, href: personalInfo.linkedin, label: 'LinkedIn' },
    ...(personalInfo.twitter ? [{ icon: Twitter, href: personalInfo.twitter, label: 'Twitter' }] : []),
    { icon: Mail, href: `mailto:${personalInfo.email}`, label: 'Email' }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: "easeOut"
      }
    }
  };

  const handleContactClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    const contactSection = document.getElementById('contact');
    if (contactSection) {
      contactSection.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  };

  const handleProjectsClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    const projectsSection = document.getElementById('projects');
    if (projectsSection) {
      projectsSection.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  };

  const handleScrollClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    const aboutSection = document.getElementById('about');
    if (aboutSection) {
      aboutSection.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  };

  return (
    <section id="hero" className="min-h-screen flex items-center justify-center pt-16 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50/50 via-transparent to-primary-100/30 dark:from-primary-900/10 dark:via-transparent dark:to-primary-800/5" />
      
      <div className="container mx-auto px-4 text-center relative z-10">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="max-w-4xl mx-auto"
        >
          {/* Greeting */}
          <motion.p
            variants={itemVariants}
            className="text-primary-500 dark:text-primary-400 font-medium text-lg mb-4"
          >
            Hi, my name is
          </motion.p>

          {/* Name */}
          <motion.h1
            variants={itemVariants}
            className="text-4xl md:text-6xl lg:text-7xl font-bold text-gray-900 dark:text-white mb-4"
          >
            <span className="bg-gradient-to-r from-gray-900 via-primary-600 to-gray-900 dark:from-white dark:via-primary-400 dark:to-white bg-clip-text text-transparent">
              {personalInfo.name}
            </span>
          </motion.h1>

          {/* Typing Title */}
          <motion.div
            variants={itemVariants}
            className="text-2xl md:text-4xl lg:text-5xl font-bold text-gray-600 dark:text-gray-300 mb-6 min-h-[1.2em]"
          >
            I'm a{' '}
            <span className="text-primary-500 dark:text-primary-400">
              <ReactTyped
                strings={typingTexts}
                typeSpeed={50}
                backSpeed={30}
                backDelay={2000}
                loop
                showCursor={true}
                cursorChar="|"
              />
            </span>
          </motion.div>

          {/* Static Title */}
          <motion.p
            variants={itemVariants}
            className="text-xl md:text-2xl text-gray-500 dark:text-gray-400 mb-6"
          >
            {personalInfo.title}
          </motion.p>

          {/* Description */}
          <motion.p
            variants={itemVariants}
            className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto mb-12 leading-relaxed"
          >
            {personalInfo.description}
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            variants={itemVariants}
            className="flex flex-col sm:flex-row gap-4 justify-center mb-12"
          >
            <Button size="lg" asChild>
              <a href="#projects" onClick={handleProjectsClick}>
                View My Work
                <ExternalLink className="ml-2 h-4 w-4" />
              </a>
            </Button>
            
            <Button variant="outline" size="lg" asChild>
              <a href="#contact" onClick={handleContactClick}>
                Contact Me
                <Mail className="ml-2 h-4 w-4" />
              </a>
            </Button>

            {personalInfo.resumeUrl && (
              <Button variant="secondary" size="lg" asChild>
                <a href={personalInfo.resumeUrl} target="_blank" rel="noopener noreferrer">
                  Download Resume
                  <Download className="ml-2 h-4 w-4" />
                </a>
              </Button>
            )}
          </motion.div>

          {/* Social Links */}
          <motion.div
            variants={itemVariants}
            className="flex justify-center space-x-6 mb-16"
          >
            {socialLinks.map(({ icon: Icon, href, label }) => (
              <motion.a
                key={label}
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-primary-500 dark:text-gray-400 dark:hover:text-primary-400 transition-colors"
                whileHover={{ 
                  scale: 1.2,
                  y: -3,
                  transition: { duration: 0.2 }
                }}
                whileTap={{ 
                  scale: 0.9,
                  transition: { duration: 0.1 }
                }}
                aria-label={label}
              >
                <Icon className="h-6 w-6" />
              </motion.a>
            ))}
          </motion.div>

          {/* Scroll Indicator */}
          <motion.a
            href="#about"
            onClick={handleScrollClick}
            variants={itemVariants}
            className="inline-block text-gray-400 hover:text-primary-500 dark:hover:text-primary-400 transition-colors"
            whileHover={{ 
              y: 5,
              transition: { duration: 0.2 }
            }}
            aria-label="Scroll to About section"
          >
            <ChevronDown className="h-8 w-8 animate-bounce" />
          </motion.a>
        </motion.div>
      </div>

      {/* Decorative elements */}
      <motion.div
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 1, duration: 1 }}
        className="absolute top-20 left-10 w-20 h-20 bg-primary-100 dark:bg-primary-900/20 rounded-full blur-xl"
      />
      
      <motion.div
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 1.2, duration: 1 }}
        className="absolute bottom-20 right-10 w-32 h-32 bg-primary-200 dark:bg-primary-800/20 rounded-full blur-xl"
      />
    </section>
  );
};

export default Hero;
