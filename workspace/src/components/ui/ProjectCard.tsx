import { motion } from 'framer-motion';
import { Github, ExternalLink, Image } from 'lucide-react';
import { Project } from '@/data/content';
import Button from './Button';

interface ProjectCardProps {
  project: Project;
  index: number;
}

const ProjectCard = ({ project, index }: ProjectCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      whileHover={{ 
        y: -8,
        transition: { duration: 0.3 }
      }}
      className="group bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden h-full flex flex-col"
    >
      {/* Project Image */}
      <div className="relative h-48 bg-gray-200 dark:bg-dark-700 overflow-hidden">
        {project.imageUrl ? (
          <img
            src={project.imageUrl}
            alt={project.title}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
              target.nextElementSibling?.classList.remove('hidden');
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Image className="h-16 w-16 text-gray-400 dark:text-gray-500" />
          </div>
        )}
        
        {/* Placeholder fallback */}
        <div className={`${project.imageUrl ? 'hidden' : ''} absolute inset-0 flex items-center justify-center bg-gray-200 dark:bg-dark-700`}>
          <div className="text-center text-gray-400 dark:text-gray-500">
            <Image className="h-16 w-16 mx-auto mb-2" />
            <span className="text-sm">Project Image</span>
          </div>
        </div>

        {/* Hover Overlay with Links */}
        <motion.div
          initial={{ opacity: 0 }}
          whileHover={{ opacity: 1 }}
          transition={{ duration: 0.2 }}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center space-x-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        >
          {project.githubUrl && (
            <Button
              variant="secondary"
              size="sm"
              asChild
              className="bg-white/90 text-gray-900 hover:bg-white"
            >
              <a
                href={project.githubUrl}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`View ${project.title} source code`}
                onClick={(e) => e.stopPropagation()}
              >
                <Github className="h-4 w-4 mr-1" />
                Code
              </a>
            </Button>
          )}
          
          {project.demoUrl && (
            <Button
              size="sm"
              asChild
              className="bg-primary-500 text-white hover:bg-primary-600"
            >
              <a
                href={project.demoUrl}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`View ${project.title} live demo`}
                onClick={(e) => e.stopPropagation()}
              >
                <ExternalLink className="h-4 w-4 mr-1" />
                Demo
              </a>
            </Button>
          )}
        </motion.div>
      </div>

      {/* Project Content */}
      <div className="p-6 flex-1 flex flex-col">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3 group-hover:text-primary-500 dark:group-hover:text-primary-400 transition-colors">
          {project.title}
        </h3>
        
        <p className="text-gray-600 dark:text-gray-300 mb-4 flex-1 leading-relaxed">
          {project.description}
        </p>
        
        {/* Technologies */}
        <div className="flex flex-wrap gap-2 mb-6">
          {project.technologies.map((tech) => (
            <motion.span
              key={tech}
              whileHover={{ scale: 1.05 }}
              className="px-3 py-1 text-xs font-medium bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300 rounded-full transition-transform"
            >
              {tech}
            </motion.span>
          ))}
        </div>
        
        {/* Links - Desktop fallback (shown when not hovering image) */}
        <div className="flex space-x-3 mt-auto md:opacity-100 group-hover:md:opacity-0 transition-opacity duration-300">
          {project.githubUrl && (
            <Button variant="outline" size="sm" asChild>
              <a
                href={project.githubUrl}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`View ${project.title} source code`}
              >
                <Github className="h-4 w-4 mr-2" />
                Code
              </a>
            </Button>
          )}
          
          {project.demoUrl && (
            <Button size="sm" asChild>
              <a
                href={project.demoUrl}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`View ${project.title} live demo`}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Demo
              </a>
            </Button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default ProjectCard;
