import { lazy } from 'react';

// Performance monitoring utilities
export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: Map<string, number> = new Map();
  private observers: PerformanceObserver[] = [];

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  // Measure component render time
  measureRender(componentName: string, renderFn: () => void): void {
    const startTime = performance.now();
    renderFn();
    const endTime = performance.now();
    
    this.metrics.set(`render_${componentName}`, endTime - startTime);
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`🎯 ${componentName} render time: ${(endTime - startTime).toFixed(2)}ms`);
    }
  }

  // Monitor Core Web Vitals
  monitorWebVitals(): void {
    if (typeof window === 'undefined' || !window.performance) return;

    // Largest Contentful Paint (LCP)
    this.observeMetric('largest-contentful-paint', (entries) => {
      const lcpEntry = entries[entries.length - 1];
      const lcp = lcpEntry.startTime;
      this.metrics.set('lcp', lcp);
      
      if (process.env.NODE_ENV === 'development') {
        console.log(`📊 LCP: ${lcp.toFixed(2)}ms`);
      }
    });

    // First Input Delay (FID)
    this.observeMetric('first-input', (entries) => {
      const fidEntry = entries[0] as PerformanceEventTiming;
      const fid = fidEntry.processingStart - fidEntry.startTime;
      this.metrics.set('fid', fid);
      
      if (process.env.NODE_ENV === 'development') {
        console.log(`⚡ FID: ${fid.toFixed(2)}ms`);
      }
    });

    // Cumulative Layout Shift (CLS)
    this.observeMetric('layout-shift', (entries) => {
      let clsValue = 0;
      for (const entry of entries) {
        if (!(entry as any).hadRecentInput) {
          clsValue += (entry as any).value;
        }
      }
      this.metrics.set('cls', clsValue);
      
      if (process.env.NODE_ENV === 'development') {
        console.log(`📐 CLS: ${clsValue.toFixed(4)}`);
      }
    });
  }

  private observeMetric(
    metricType: string,
    callback: (entries: PerformanceEntry[]) => void
  ): void {
    try {
      const observer = new PerformanceObserver((list) => {
        callback(list.getEntries());
      });
      
      observer.observe({ entryTypes: [metricType] });
      this.observers.push(observer);
    } catch (error) {
      console.warn(`Failed to observe ${metricType}:`, error);
    }
  }

  // Get all collected metrics
  getMetrics(): Record<string, number> {
    return Object.fromEntries(this.metrics);
  }

  // Clean up observers
  disconnect(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }
}

// Lazy loading utilities
export const createLazyComponent = (
  importFn: () => Promise<any>,
  componentName?: string
) => {
  return lazy(async () => {
    const start = performance.now();
    
    try {
      const module = await importFn();
      const end = performance.now();
      
      if (process.env.NODE_ENV === 'development' && componentName) {
        console.log(`🚀 ${componentName} loaded in ${(end - start).toFixed(2)}ms`);
      }
      
      return module;
    } catch (error) {
      console.error(`Failed to load component ${componentName || 'unknown'}:`, error);
      throw error;
    }
  });
};

// Image optimization utilities
export const createOptimizedImageSrc = (
  src: string,
  options: {
    width?: number;
    height?: number;
    quality?: number;
    format?: 'webp' | 'avif' | 'jpg' | 'png';
  } = {}
): string => {
  const { width, height, quality = 80, format } = options;
  
  // In a real app, you'd integrate with a service like Cloudinary, ImageKit, etc.
  // For now, return the original source
  let optimizedSrc = src;
  
  // Add query parameters for optimization services
  const params = new URLSearchParams();
  if (width) params.set('w', width.toString());
  if (height) params.set('h', height.toString());
  if (quality !== 80) params.set('q', quality.toString());
  if (format) params.set('f', format);
  
  if (params.toString()) {
    optimizedSrc += `?${params.toString()}`;
  }
  
  return optimizedSrc;
};

// Bundle analysis utilities
export const analyzeBundleSize = (): void => {
  if (process.env.NODE_ENV !== 'development') return;
  
  // Analyze chunk sizes
  const scripts = Array.from(document.querySelectorAll('script[src]'));
  const styles = Array.from(document.querySelectorAll('link[rel="stylesheet"]'));
  
  console.group('📦 Bundle Analysis');
  
  console.log('Scripts:', scripts.map(script => ({
    src: script.getAttribute('src'),
    async: script.hasAttribute('async'),
    defer: script.hasAttribute('defer')
  })));
  
  console.log('Stylesheets:', styles.map(link => ({
    href: link.getAttribute('href'),
    media: link.getAttribute('media') || 'all'
  })));
  
  // Check for render-blocking resources
  const renderBlocking = styles.filter(link => 
    !link.getAttribute('media') || link.getAttribute('media') === 'all'
  );
  
  if (renderBlocking.length > 0) {
    console.warn('⚠️ Render-blocking stylesheets found:', renderBlocking);
  }
  
  console.groupEnd();
};

// Memory usage monitoring
export const monitorMemoryUsage = (): void => {
  if (process.env.NODE_ENV !== 'development') return;
  if (typeof window === 'undefined' || !(performance as any).memory) return;
  
  const memory = (performance as any).memory;
  
  const formatBytes = (bytes: number): string => {
    return (bytes / 1024 / 1024).toFixed(2) + ' MB';
  };
  
  console.log('💾 Memory Usage:', {
    used: formatBytes(memory.usedJSHeapSize),
    total: formatBytes(memory.totalJSHeapSize),
    limit: formatBytes(memory.jsHeapSizeLimit)
  });
  
  // Warn if memory usage is high
  const usagePercentage = (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100;
  if (usagePercentage > 80) {
    console.warn(`⚠️ High memory usage: ${usagePercentage.toFixed(1)}%`);
  }
};

// Preload critical resources
export const preloadCriticalResources = (resources: string[]): void => {
  resources.forEach(resource => {
    const link = document.createElement('link');
    link.rel = 'preload';
    
    if (resource.endsWith('.js')) {
      link.as = 'script';
    } else if (resource.endsWith('.css')) {
      link.as = 'style';
    } else if (resource.match(/\.(jpg|jpeg|png|webp|avif)$/)) {
      link.as = 'image';
    } else if (resource.match(/\.(woff|woff2|ttf|otf)$/)) {
      link.as = 'font';
      link.crossOrigin = 'anonymous';
    }
    
    link.href = resource;
    document.head.appendChild(link);
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`🔗 Preloading: ${resource}`);
    }
  });
};

// Initialize performance monitoring
export const initializePerformanceMonitoring = (): void => {
  const monitor = PerformanceMonitor.getInstance();
  monitor.monitorWebVitals();
  
  // Monitor memory usage every 30 seconds in development
  if (process.env.NODE_ENV === 'development') {
    setInterval(monitorMemoryUsage, 30000);
    
    // Analyze bundle on load
    window.addEventListener('load', analyzeBundleSize);
  }
  
  // Preload critical resources
  preloadCriticalResources([
    '/fonts/inter-var.woff2', // Adjust based on your font setup
  ]);
};

// Export singleton instance
export const performanceMonitor = PerformanceMonitor.getInstance();
