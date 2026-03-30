import { useState, useEffect, useRef } from 'react';
import { debounce } from '@/lib/utils';

interface UseScrollSpyOptions {
  threshold?: number;
  rootMargin?: string;
  offset?: number;
}

export const useScrollSpy = (
  sectionIds: string[],
  options: UseScrollSpyOptions = {}
): string => {
  const {
    threshold = 0.3,
    rootMargin = '0px 0px -50% 0px',
    offset = 100
  } = options;

  const [activeSection, setActiveSection] = useState<string>('');
  const observerRef = useRef<IntersectionObserver | null>(null);
  const sectionsRef = useRef<Map<string, IntersectionObserverEntry>>(new Map());

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Clean up previous observer
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    // Create intersection observer
    const observer = new IntersectionObserver(
      debounce((entries: IntersectionObserverEntry[]) => {
        // Update the entries map
        entries.forEach(entry => {
          sectionsRef.current.set(entry.target.id, entry);
        });

        // Find the most visible section
        let maxVisibility = 0;
        let mostVisibleSection = '';

        sectionsRef.current.forEach((entry, sectionId) => {
          if (entry.isIntersecting) {
            const visibility = entry.intersectionRatio;
            if (visibility > maxVisibility) {
              maxVisibility = visibility;
              mostVisibleSection = sectionId;
            }
          }
        });

        // If no section is intersecting, find the closest one
        if (!mostVisibleSection) {
          const scrollPosition = window.scrollY + offset;
          let closestSection = '';
          let minDistance = Infinity;

          sectionIds.forEach(sectionId => {
            const element = document.getElementById(sectionId);
            if (element) {
              const rect = element.getBoundingClientRect();
              const elementTop = rect.top + window.scrollY;
              const distance = Math.abs(scrollPosition - elementTop);
              
              if (distance < minDistance) {
                minDistance = distance;
                closestSection = sectionId;
              }
            }
          });

          mostVisibleSection = closestSection;
        }

        // Update active section if it changed
        if (mostVisibleSection && mostVisibleSection !== activeSection) {
          setActiveSection(mostVisibleSection);
        }
      }, 100), // Debounce for performance
      {
        threshold,
        rootMargin
      }
    );

    observerRef.current = observer;

    // Observe all sections
    const elementsToObserve: Element[] = [];
    sectionIds.forEach(sectionId => {
      const element = document.getElementById(sectionId);
      if (element) {
        observer.observe(element);
        elementsToObserve.push(element);
      }
    });

    // Set initial active section
    const handleInitialScroll = debounce(() => {
      const scrollPosition = window.scrollY + offset;
      let initialSection = sectionIds[0];

      for (let i = sectionIds.length - 1; i >= 0; i--) {
        const element = document.getElementById(sectionIds[i]);
        if (element) {
          const rect = element.getBoundingClientRect();
          const elementTop = rect.top + window.scrollY;
          
          if (scrollPosition >= elementTop - 100) {
            initialSection = sectionIds[i];
            break;
          }
        }
      }

      setActiveSection(initialSection);
    }, 50);

    // Handle initial load and resize
    handleInitialScroll();
    window.addEventListener('scroll', handleInitialScroll);
    window.addEventListener('resize', handleInitialScroll);

    // Cleanup
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
      window.removeEventListener('scroll', handleInitialScroll);
      window.removeEventListener('resize', handleInitialScroll);
    };
  }, [sectionIds, threshold, rootMargin, offset, activeSection]);

  return activeSection;
};

// Hook for single section visibility
export const useSectionVisible = (
  sectionId: string,
  options: UseScrollSpyOptions = {}
): boolean => {
  const {
    threshold = 0.3,
    rootMargin = '0px'
  } = options;

  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const element = document.getElementById(sectionId);
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsVisible(entry.isIntersecting);
      },
      {
        threshold,
        rootMargin
      }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [sectionId, threshold, rootMargin]);

  return isVisible;
};
