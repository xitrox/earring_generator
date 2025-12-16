// API Configuration
// Use relative URLs by default - nginx in production proxies /api/ to backend
// For local development, set VITE_API_BASE_URL=http://localhost:5000 in .env
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// Helper function to build API URLs
export const apiUrl = (path) => `${API_BASE_URL}${path}`;
