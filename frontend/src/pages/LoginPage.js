import React, { useState } from 'react';
import { Brain, Heart, Sparkles, Shield, Lock, Cloud } from 'lucide-react';
import { motion } from 'framer-motion';

const LoginPage = ({ onLogin }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Call backend to get OAuth URL using standard REST API
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:7860';
      const response = await fetch(`${API_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: null })
      });
      
      const data = await response.json();
      
      if (data.auth_url) {
        // Redirect to Google OAuth
        window.location.href = data.auth_url;
      } else {
        setError('Failed to start login. Please try again.');
        setLoading(false);
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Failed to connect to server. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-6xl w-full grid md:grid-cols-2 gap-8 items-center">
        
        {/* Left side - Branding */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center md:text-left"
        >
          <div className="flex items-center justify-center md:justify-start gap-3 mb-6">
            <div className="relative">
              <Brain className="w-16 h-16 text-blue-600 animate-float" />
              <div className="absolute inset-0 bg-blue-400 blur-xl opacity-30 animate-pulse-slow"></div>
            </div>
            <h1 className="text-5xl font-display font-bold gradient-text">
              MindMirror AI
            </h1>
          </div>
          
          <p className="text-2xl text-gray-700 mb-8 font-medium">
            Your Privacy-First Emotional Reflection Dashboard
          </p>
          
          <p className="text-lg text-gray-600 mb-12 leading-relaxed">
            Express yourself through text, voice, images, or videos. 
            Get AI-powered insights, personalized poetry, and mood-based art—all 
            while keeping your data 100% private in your Google Drive.
          </p>
          
          <div className="grid grid-cols-2 gap-4 mb-8">
            <FeatureCard icon={<Shield />} title="100% Private" />
            <FeatureCard icon={<Brain />} title="AI-Powered" />
            <FeatureCard icon={<Heart />} title="Youth-Friendly" />
            <FeatureCard icon={<Sparkles />} title="Multi-Modal" />
          </div>
        </motion.div>
        
        {/* Right side - Login Card */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="glass-card p-8 md:p-12"
        >
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-3">
              Welcome Back
            </h2>
            <p className="text-gray-600">
              Sign in to continue your emotional wellness journey
            </p>
          </div>
          
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6"
            >
              {error}
            </motion.div>
          )}
          
          <button
            onClick={() => handleGoogleLogin()}
            disabled={loading}
            className="w-full bg-white border-2 border-gray-200 hover:border-blue-500 text-gray-700 font-semibold py-4 px-6 rounded-xl flex items-center justify-center gap-3 transition-all duration-200 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            {loading ? (
              <>
                <div className="loader"></div>
                <span>Signing in...</span>
              </>
            ) : (
              <>
                <svg className="w-6 h-6" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                <span className="group-hover:text-blue-600 transition-colors">
                  Continue with Google
                </span>
              </>
            )}
          </button>
          
          <div className="mt-8 space-y-4">
            <PrivacyNote icon={<Lock />} text="Your data stays in YOUR Google Drive" />
            <PrivacyNote icon={<Shield />} text="No third-party access to your reflections" />
            <PrivacyNote icon={<Cloud />} text="100% privacy-first architecture" />
          </div>
          
          <p className="text-sm text-gray-500 text-center mt-8">
            By signing in, you agree to our Terms of Service and Privacy Policy
          </p>
        </motion.div>
      </div>
    </div>
  );
};

const FeatureCard = ({ icon, title }) => (
  <div className="glass-card p-4 flex flex-col items-center gap-2 card-hover">
    <div className="text-blue-600">{React.cloneElement(icon, { size: 32 })}</div>
    <span className="font-semibold text-gray-700">{title}</span>
  </div>
);

const PrivacyNote = ({ icon, text }) => (
  <div className="flex items-center gap-3 text-sm text-gray-600">
    <div className="text-green-600">{React.cloneElement(icon, { size: 18 })}</div>
    <span>{text}</span>
  </div>
);

export default LoginPage;
