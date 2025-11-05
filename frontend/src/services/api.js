/**
 * API Service for MindMirror AI - Gradio Backend
 * Handles all backend communication with Gradio REST endpoints
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:7860';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Longer timeout for AI processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Session expired
      sessionStorage.removeItem('session_token');
      sessionStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Authentication APIs
export const authAPI = {
  googleLogin: async (googleToken) => {
    const response = await api.post('/auth/google', { token: googleToken });
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  logout: async () => {
    const response = await api.post('/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('google_token');
    return response.data;
  },
};

// Upload APIs
export const uploadAPI = {
  uploadText: async (content, title, tags, googleToken) => {
    const formData = new FormData();
    formData.append('google_token', googleToken);
    
    const response = await api.post('/upload/text', {
      content,
      title,
      tags,
    }, {
      params: { google_token: googleToken }
    });
    return response.data;
  },
  
  uploadVoice: async (audioFile, googleToken) => {
    const formData = new FormData();
    formData.append('file', audioFile);
    formData.append('google_token', googleToken);
    
    const response = await api.post('/upload/voice', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  uploadImage: async (imageFile, caption, googleToken) => {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('google_token', googleToken);
    if (caption) formData.append('caption', caption);
    
    const response = await api.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  uploadVideo: async (videoFile, caption, googleToken) => {
    const formData = new FormData();
    formData.append('file', videoFile);
    formData.append('google_token', googleToken);
    if (caption) formData.append('caption', caption);
    
    const response = await api.post('/upload/video', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Reflection APIs
export const reflectionAPI = {
  generateReflection: async (content, contentType, generateArt, generateVoice, googleToken) => {
    const formData = new FormData();
    formData.append('google_token', googleToken);
    
    const response = await api.post('/reflect/', {
      content,
      content_type: contentType,
      generate_art: generateArt,
      generate_voice: generateVoice,
    }, {
      params: { google_token: googleToken }
    });
    return response.data;
  },
  
  getReflection: async (reflectionId, googleToken) => {
    const response = await api.get(`/reflect/${reflectionId}`, {
      params: { google_token: googleToken }
    });
    return response.data;
  },
  
  quickEmotionCheck: async (content) => {
    const formData = new FormData();
    formData.append('content', content);
    
    const response = await api.post('/reflect/quick', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// History APIs
export const historyAPI = {
  getMoodTimeline: async (days, googleToken) => {
    const response = await api.get('/history/moods', {
      params: {
        google_token: googleToken,
        days: days || 30,
      },
    });
    return response.data;
  },
  
  getGallery: async (limit, googleToken) => {
    const response = await api.get('/history/gallery', {
      params: {
        google_token: googleToken,
        limit: limit || 50,
      },
    });
    return response.data;
  },
  
  getStatistics: async (googleToken) => {
    const response = await api.get('/history/stats', {
      params: {
        google_token: googleToken,
      },
    });
    return response.data;
  },
  
  exportData: async (googleToken) => {
    const response = await api.get('/history/export', {
      params: {
        google_token: googleToken,
      },
    });
    return response.data;
  },
};

export default api;
