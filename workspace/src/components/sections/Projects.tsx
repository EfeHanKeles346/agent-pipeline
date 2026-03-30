import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import SectionTitle from '@/components/ui/SectionTitle';
import ProjectCard from '@/components/ui/ProjectCard';
import FilterButton from '@/components/ui/FilterButton';
import { projects } from '@/data/content';

const Projects = () => {
  const [selectedFilter, setSelectedFilter] = useState<string>('All');

  // Extract all unique technologies from projects
  const allTechnologies = useMemo(() => {
    const techSet = new Set<string>();
    projects.forEach(project => {
      project.technologies.forEach(tech => techSet.add(tech));
    });
    return Array.from(techSet).sort();
  }, []);

  // Create filter options with counts
  const filterOptions = useMemo(() => {
    const options = [
      {
        label: 'All',
        count: projects.length
      }
    ];

    allTechnologies.forEach(tech => {
      const count = projects.filter(project => 
        project.technologies.includes(tech)
      ).length;
      
      options.push({
        label: tech,
        count
      });
    });

    return options;
  }, [allTechnologies]);

  // Filter projects based on selected technology
  const filteredProjects = useMemo(() => {
    if (selectedFilter === 'All') {
      return projects;
    }
    return projects.filter(project => 
      project.technologies.includes(selectedFilter)
    );
  }, [selectedFilter]);

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
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <section id="projects" className="py-20">
      <div className="container mx-auto px-4">
        <SectionTitle
          title="Projects"
          subtitle="Explore my recent work and side projects"
        />

        {/* Filter Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="flex flex-wrap justify-center gap-3 mb-12 sticky top-20 z-10 bg-white/80 dark:bg-dark-900/80 backdrop-blur-sm py-4 -mx-4 px-4 rounded-lg"
        >
          {filterOptions.map(({ label, count }) => (
            <FilterButton
              key={label}
              label={label}
              count={count}
              isActive={selectedFilter === label}
              onClick={() => setSelectedFilter(label)}
            />
          ))}
        </motion.div>

        {/* Projects Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          key={selectedFilter} // Re-animate when filter changes
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          {filteredProjects.map((project, index) => (
            <motion.div
              key={project.id}
              variants={itemVariants}
              layout
              className="h-full"
            >
              <ProjectCard
                project={project}
                index={index}
              />
            </motion.div>
          ))}
        </motion.div>

        {/* Empty State */}
        {filteredProjects.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="text-center py-16"
          >
            <div className="text-gray-400 dark:text-gray-500 mb-4">
              <svg
                className="mx-auto h-16 w-16"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0-1.125.504-1.125 1.125V11.25a9 9 0 00-9-9z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              No projects found
            </h3>
            <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
              No projects match the selected technology filter. Try selecting a different technology or view all projects.
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setSelectedFilter('All')}
              className="mt-4 px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-dark-900"
            >
              Show All Projects
            </motion.button>
          </motion.div>
        )}

        {/* Project Count Info */}
        {filteredProjects.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-center mt-12"
          >
            <p className="text-gray-600 dark:text-gray-400">
              Showing <span className="font-semibold text-primary-500">{filteredProjects.length}</span> 
              {filteredProjects.length === 1 ? ' project' : ' projects'}
              {selectedFilter !== 'All' && (
                <span> with <span className="font-semibold">{selectedFilter}</span></span>
              )}
            </p>
          </motion.div>
        )}
      </div>
    </section>
  );
};

export default Projects;
