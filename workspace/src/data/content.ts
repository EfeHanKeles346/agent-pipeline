import { env } from '@/config/env';

export interface PersonalInfo {
  name: string;
  title: string;
  description: string;
  email: string;
  github: string;
  linkedin: string;
  twitter?: string;
  resumeUrl?: string;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  technologies: string[];
  githubUrl?: string;
  demoUrl?: string;
  imageUrl?: string;
  featured: boolean;
}

export interface Skill {
  name: string;
  category: 'frontend' | 'backend' | 'tools' | 'other';
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  icon: string;
}

export interface Experience {
  company: string;
  position: string;
  duration: string;
  description: string;
}

export interface ContactInfo {
  title: string;
  description: string;
  email: string;
  socialLinks: Array<{
    name: string;
    url: string;
    icon: string;
  }>;
}

export interface KeyStat {
  label: string;
  value: string;
  icon: string;
}

// Personal Info - env.ts'den değerleri al
export const personalInfo: PersonalInfo = {
  name: env.personalName,
  title: env.personalTitle,
  description: "Passionate developer creating modern web applications with clean code and user-friendly interfaces. I specialize in React, TypeScript, and Node.js, always eager to learn new technologies and tackle challenging problems.",
  email: env.contactEmail,
  github: env.githubUrl,
  linkedin: env.linkedinUrl,
  twitter: env.twitterUrl,
  resumeUrl: env.resumeUrl
};

// Typing Animation Texts
export const typingTexts = [
  "Full Stack Developer",
  "React Specialist", 
  "Problem Solver",
  "UI/UX Enthusiast",
  "Clean Code Advocate"
];

// Key Stats for About section
export const keyStats: KeyStat[] = [
  { label: "Years Experience", value: "4+", icon: "Calendar" },
  { label: "Projects Completed", value: "50+", icon: "CheckCircle" },
  { label: "Happy Clients", value: "30+", icon: "Users" }
];

// Projects Array - 3 örnek proje
export const projects: Project[] = [
  {
    id: "ecommerce-platform",
    title: "E-Commerce Platform",
    description: "A full-stack e-commerce solution with user authentication, product management, shopping cart, and secure payment processing. Features include admin dashboard, order tracking, and responsive design.",
    technologies: ["React", "TypeScript", "Node.js", "Express", "PostgreSQL", "Stripe", "Tailwind CSS"],
    githubUrl: "https://github.com/johndeveloper/ecommerce-platform",
    demoUrl: "https://ecommerce-platform-demo.vercel.app",
    imageUrl: "/images/projects/ecommerce-platform.jpg",
    featured: true
  },
  {
    id: "task-management-app",
    title: "Task Management App",
    description: "A collaborative project management tool with real-time updates, team collaboration features, and intuitive drag-and-drop interface. Built for productivity and seamless workflow management.",
    technologies: ["React", "TypeScript", "Firebase", "Framer Motion", "React DnD", "Material-UI"],
    githubUrl: "https://github.com/johndeveloper/task-management",
    demoUrl: "https://task-management-demo.vercel.app",
    imageUrl: "/images/projects/task-management.jpg",
    featured: true
  },
  {
    id: "weather-dashboard",
    title: "Weather Dashboard",
    description: "A responsive weather application providing current conditions, 7-day forecasts, and weather maps. Features location-based weather, search functionality, and beautiful data visualizations.",
    technologies: ["React", "TypeScript", "Tailwind CSS", "Chart.js", "OpenWeather API"],
    githubUrl: "https://github.com/johndeveloper/weather-dashboard",
    demoUrl: "https://weather-dashboard-demo.vercel.app",
    imageUrl: "/images/projects/weather-dashboard.jpg",
    featured: false
  }
];

// Skills Array - Kategorize edilmiş ve icon property'leri eklendi
export const skills: Skill[] = [
  // Frontend Skills
  { name: "React", category: "frontend", level: "expert", icon: "Atom" },
  { name: "TypeScript", category: "frontend", level: "advanced", icon: "Code2" },
  { name: "JavaScript", category: "frontend", level: "expert", icon: "Code" },
  { name: "HTML5", category: "frontend", level: "expert", icon: "FileText" },
  { name: "CSS3", category: "frontend", level: "advanced", icon: "Palette" },
  { name: "Tailwind CSS", category: "frontend", level: "advanced", icon: "Paintbrush" },
  { name: "Next.js", category: "frontend", level: "intermediate", icon: "Zap" },
  { name: "Vue.js", category: "frontend", level: "intermediate", icon: "Component" },
  
  // Backend Skills
  { name: "Node.js", category: "backend", level: "advanced", icon: "Server" },
  { name: "Express.js", category: "backend", level: "advanced", icon: "Layers" },
  { name: "PostgreSQL", category: "backend", level: "intermediate", icon: "Database" },
  { name: "MongoDB", category: "backend", level: "intermediate", icon: "Database" },
  { name: "GraphQL", category: "backend", level: "intermediate", icon: "Share2" },
  { name: "REST APIs", category: "backend", level: "advanced", icon: "Globe" },
  
  // Tools & Others
  { name: "Git", category: "tools", level: "advanced", icon: "GitBranch" },
  { name: "Docker", category: "tools", level: "intermediate", icon: "Package" },
  { name: "Webpack", category: "tools", level: "intermediate", icon: "Box" },
  { name: "Vite", category: "tools", level: "advanced", icon: "Zap" },
  { name: "Jest", category: "tools", level: "intermediate", icon: "TestTube" },
  { name: "Figma", category: "tools", level: "intermediate", icon: "Figma" }
];

// Experience Array - 3 örnek iş tecrübesi
export const experience: Experience[] = [
  {
    company: "Tech Innovation Corp",
    position: "Senior Frontend Developer",
    duration: "2022 - Present",
    description: "Leading frontend development initiatives for enterprise applications. Architected and implemented scalable React applications serving 100k+ users. Mentored junior developers and established best practices for code quality and performance optimization."
  },
  {
    company: "Digital Solutions Ltd",
    position: "Full Stack Developer",
    duration: "2020 - 2022",
    description: "Developed and maintained full-stack web applications using React, Node.js, and PostgreSQL. Collaborated with cross-functional teams to deliver high-quality software solutions. Improved application performance by 40% through optimization techniques."
  },
  {
    company: "Creative Web Studio",
    position: "Frontend Developer",
    duration: "2019 - 2020",
    description: "Built responsive websites and web applications for diverse clients. Worked with modern JavaScript frameworks and collaborated closely with designers to implement pixel-perfect user interfaces. Delivered projects on time and within budget."
  }
];

// About Text - Çok paragraf destekli
export const aboutText = `I'm a passionate full-stack developer with over 4 years of experience in creating modern, scalable web applications. My journey in software development began with a curiosity for problem-solving and has evolved into a deep expertise in React, TypeScript, and Node.js.

I believe in the power of clean, maintainable code and user-centered design. Every project I work on is an opportunity to create something meaningful that makes a real difference for users and businesses alike.

When I'm not coding, you'll find me contributing to open-source projects, writing technical articles, or exploring the latest trends in web development. I'm always eager to learn new technologies and tackle challenging problems that push the boundaries of what's possible on the web.

My approach to development combines technical excellence with strong communication skills, ensuring that complex solutions are delivered efficiently and collaboratively.`;

// Contact Info
export const contactInfo: ContactInfo = {
  title: "Let's Work Together",
  description: "I'm always interested in hearing about new opportunities and exciting projects. Whether you have a question, want to discuss a potential collaboration, or just want to say hello, feel free to reach out!",
  email: personalInfo.email,
  socialLinks: [
    { name: "GitHub", url: personalInfo.github, icon: "Github" },
    { name: "LinkedIn", url: personalInfo.linkedin, icon: "Linkedin" },
    ...(personalInfo.twitter ? [{ name: "Twitter", url: personalInfo.twitter, icon: "Twitter" }] : [])
  ]
};
