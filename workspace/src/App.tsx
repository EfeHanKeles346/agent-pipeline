import { Suspense, lazy } from 'react';
import { motion } from 'framer-motion';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import ErrorBoundary from '@/components/common/ErrorBoundary';
import ScrollToTop from '@/components/ui/ScrollToTop';
// Lazy load sections for better performance
const Hero = lazy(() => import('@/components/sections/Hero'));
const About = lazy(() => import('@/components/sections/About'));
const Skills = lazy(() => import('@/components/sections/Skills'));
const Projects = lazy(() => import('@/components/sections/Projects'));
const Contact = lazy(() => import('@/components/sections/Contact'));

// Loading component for suspense fallback
const SectionSkeleton = () => (
  <div className="section-spacing">
    <div className="container mx-auto px-4">
      <div className="loading-skeleton h-8 w-64 mx-auto mb-4 rounded"></div>
      <div className="loading-skeleton h-4 w-96 mx-auto mb-12 rounded"></div>
      <div className="grid gap-8">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="loading-skeleton h-48 rounded-lg"></div>
        ))}
      </div>
    </div>
  </div>
);

function App() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-white dark:bg-dark-900">
        {/* Skip to main content for accessibility */}
        <a 
          href="#main" 
          className="skip-to-main no-print"
          tabIndex={1}
        >
          Skip to main content
        </a>

        <Navbar />
        
        <main id="main" role="main">
          <ErrorBoundary
            fallback={
              <div className="section-spacing flex items-center justify-center">
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                    Something went wrong
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mb-6">
                    Unable to load this section. Please try refreshing the page.
                  </p>
                  <button 
                    onClick={() => window.location.reload()}
                    className="btn-focus px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                  >
                    Refresh Page
                  </button>
                </div>
              </div>
            }
          >
            <Suspense fallback={<SectionSkeleton />}>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <Hero />
              </motion.div>
            </Suspense>

            <Suspense fallback={<SectionSkeleton />}>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <About />
              </motion.div>
            </Suspense>

            <Suspense fallback={<SectionSkeleton />}>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <Skills />
              </motion.div>
            </Suspense>

            <Suspense fallback={<SectionSkeleton />}>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                <Projects />
              </motion.div>
            </Suspense>

            <Suspense fallback={<SectionSkeleton />}>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                <Contact />
              </motion.div>
            </Suspense>
          </ErrorBoundary>
        </main>

        <Footer />
        <ScrollToTop />
      </div>
    </ErrorBoundary>
  );
}

export default App;
