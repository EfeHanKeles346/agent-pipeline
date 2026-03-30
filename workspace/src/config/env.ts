interface EnvConfig {
  contactEmail: string;
  personalName: string;
  personalTitle: string;
  githubUrl: string;
  linkedinUrl: string;
  twitterUrl?: string;
  resumeUrl?: string;
  emailTimeout: number;
}

const getEnvVar = (key: string, defaultValue: string): string => {
  const value = import.meta.env[key];
  return value || defaultValue;
};

export const env: EnvConfig = {
  contactEmail: getEnvVar('VITE_CONTACT_EMAIL', 'john@example.com'),
  personalName: getEnvVar('VITE_PERSONAL_NAME', 'John Developer'),
  personalTitle: getEnvVar('VITE_PERSONAL_TITLE', 'Full Stack Developer'),
  githubUrl: getEnvVar('VITE_GITHUB_URL', 'https://github.com/johndeveloper'),
  linkedinUrl: getEnvVar('VITE_LINKEDIN_URL', 'https://linkedin.com/in/johndeveloper'),
  twitterUrl: import.meta.env.VITE_TWITTER_URL,
  resumeUrl: import.meta.env.VITE_RESUME_URL,
  emailTimeout: parseInt(getEnvVar('VITE_EMAIL_TIMEOUT', '1500'), 10)
};
