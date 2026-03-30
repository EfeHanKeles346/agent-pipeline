# Project Memory

## Project Overview
- **Name:** DevPortfolio
- **Type:** Personal Portfolio Website
- **Tech Stack:** React 18, TypeScript, Tailwind CSS, Framer Motion
- **Package Manager:** npm
- **Target:** Responsive, modern, single-page portfolio site

## Architecture
- **Framework:** React with Vite
- **Styling:** Tailwind CSS (utility-first)
- **Animations:** Framer Motion
- **Routing:** Smooth scroll (section-based, no router needed)
- **Icons:** lucide-react
- **Deployment:** Static build (Vercel/Netlify ready)

## Folder Structure
```
src/
├── components/
│   ├── layout/        → Navbar, Footer
│   ├── sections/      → Hero, About, Projects, Skills, Contact
│   └── ui/            → Button, Card, SectionTitle (reusable)
├── data/
│   └── content.ts     → All text/project data in one place
├── hooks/             → Custom hooks
├── assets/            → Images
├── App.tsx
├── main.tsx
└── index.css          → Tailwind directives + custom styles
```

## Design Decisions
- Dark theme by default, light mode toggle
- Mobile-first responsive design
- All content centralized in `data/content.ts` for easy editing
- Sections: Hero → About → Skills → Projects → Contact
- Smooth scroll navigation between sections
- No backend, contact form uses mailto or formspree

## Constraints
- No external API calls
- Must load fast
- Accessibility: semantic HTML, aria labels
- SEO: proper meta tags
