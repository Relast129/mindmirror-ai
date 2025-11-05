/**
 * Gradio API Service for MindMirror AI
 * Handles all backend communication with Gradio REST endpoints
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:7860';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      sessionStorage.removeItem('session_token');
      sessionStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Helper to get session token
const getSessionToken = () => sessionStorage.getItem('session_token');

// Authentication APIs
export const authAPI = {
  // Start OAuth flow
  startLogin: async () => {
    try {
      const response = await api.post('/api/login', { code: null });
      return response.data;
    } catch (error) {
      console.error('Start login error:', error);
      throw error;
    }
  },

  // Complete OAuth with code
  completeLogin: async (code) => {
    try {
      const response = await api.post('/api/login', { code });
      if (response.data.session_token) {
        sessionStorage.setItem('session_token', response.data.session_token);
        sessionStorage.setItem('user', JSON.stringify(response.data.profile));
        sessionStorage.setItem('drive_folder_id', response.data.drive_folder_id);
      }
      return response.data;
    } catch (error) {
      console.error('Complete login error:', error);
      throw error;
    }
  },

  // Get current user from session
  getCurrentUser: () => {
    const userStr = sessionStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  // Logout
  logout: () => {
    sessionStorage.removeItem('session_token');
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('drive_folder_id');
  },
};

// Journal/Submit APIs
export const journalAPI = {
  // Submit text entry
  submitText: async (content) => {
    try {
      const response = await api.post('/api/submit', {
        session_token: getSessionToken(),
        input_type: 'text',
        text_content: content,
      });
      return response.data;
    } catch (error) {
      console.error('Submit text error:', error);
      throw error;
    }
  },

  // Submit voice recording
  submitVoice: async (audioFile) => {
    try {
      const formData = new FormData();
      formData.append('session_token', getSessionToken());
      formData.append('input_type', 'voice');
      formData.append('file_data', audioFile);

      const response = await api.post('/api/submit', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Submit voice error:', error);
      throw error;
    }
  },

  // Submit image
  submitImage: async (imageFile) => {
    try {
      const formData = new FormData();
      formData.append('session_token', getSessionToken());
      formData.append('input_type', 'image');
      formData.append('file_data', imageFile);

      const response = await api.post('/api/submit', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Submit image error:', error);
      throw error;
    }
  },

  // Submit drawing
  submitDrawing: async (drawingFile) => {
    try {
      const formData = new FormData();
      formData.append('session_token', getSessionToken());
      formData.append('input_type', 'drawing');
      formData.append('file_data', drawingFile);

      const response = await api.post('/api/submit', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Submit drawing error:', error);
      throw error;
    }
  },

  // Submit video
  submitVideo: async (videoFile) => {
    try {
      const formData = new FormData();
      formData.append('session_token', getSessionToken());
      formData.append('input_type', 'video');
      formData.append('file_data', videoFile);

      const response = await api.post('/api/submit', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Submit video error:', error);
      throw error;
    }
  },
};

// History APIs
export const historyAPI = {
  // Get journal history
  getHistory: async (limit = 50) => {
    try {
      const response = await api.get('/api/history', {
        params: {
          session_token: getSessionToken(),
          limit,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Get history error:', error);
      throw error;
    }
  },
};

// File APIs
export const fileAPI = {
  // Download file
  downloadFile: async (fileId) => {
    try {
      const response = await api.get('/api/download', {
        params: {
          session_token: getSessionToken(),
          file_id: fileId,
        },
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      console.error('Download file error:', error);
      throw error;
    }
  },

  // Get file URL
  getFileUrl: (fileId) => {
    return `${API_BASE_URL}/api/download?session_token=${getSessionToken()}&file_id=${fileId}`;
  },
};

// Feedback APIs
export const feedbackAPI = {
  // Add feedback to entry
  addFeedback: async (entryId, feedback) => {
    try {
      const response = await api.post('/api/feedback', {
        session_token: getSessionToken(),
        entry_id: entryId,
        feedback,
      });
      return response.data;
    } catch (error) {
      console.error('Add feedback error:', error);
      throw error;
    }
  },
};

const gradioAPI = {
  auth: authAPI,
  journal: journalAPI,
  history: historyAPI,
  file: fileAPI,
  feedback: feedbackAPI,
};

export default gradioAPI;
