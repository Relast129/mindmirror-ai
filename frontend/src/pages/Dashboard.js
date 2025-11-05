import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain, LogOut, PenTool, Mic, Image, Video, Sparkles,
  TrendingUp, Calendar, Award, Heart, Menu, X, Moon, Sun
} from 'lucide-react';
import TextInput from '../components/TextInput';
import VoiceInput from '../components/VoiceInput';
import ImageInput from '../components/ImageInput';
import VideoInput from '../components/VideoInput';
import ReflectionDisplay from '../components/ReflectionDisplay';
import MoodTimeline from '../components/MoodTimeline';
import StatsPanel from '../components/StatsPanel';
import Gallery from '../components/Gallery';
import { ToastContainer, useToast } from '../components/Toast';
import { SkeletonStat, SkeletonTimeline, SkeletonGallery } from '../components/LoadingSkeleton';
import { authAPI, historyAPI } from '../services/gradio-api';

const Dashboard = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('text');
  const [showReflection, setShowReflection] = useState(false);
  const [currentReflection, setCurrentReflection] = useState(null);
  const [stats, setStats] = useState(null);
  const [moodData, setMoodData] = useState([]);
  const [galleryItems, setGalleryItems] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeView, setActiveView] = useState('input'); // input, timeline, gallery, stats
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const { toasts, addToast, removeToast } = useToast();

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      // Load history from Gradio backend
      const historyData = await historyAPI.getHistory(50);
      
      if (historyData && historyData.entries) {
        // Process entries for stats, mood timeline, and gallery
        const entries = historyData.entries;
        
        // Calculate stats
        setStats({
          total_entries: entries.length,
          total_emotions: [...new Set(entries.flatMap(e => e.emotion_labels || []))].length,
          streak_days: calculateStreak(entries)
        });
        
        // Process mood timeline
        setMoodData(entries.map(e => ({
          date: e.timestamp,
          emotions: e.emotion_labels || [],
          scores: e.emotion_scores || {}
        })));
        
        // Process gallery items
        setGalleryItems(entries.map(e => ({
          id: e.id,
          type: e.input_type,
          timestamp: e.timestamp,
          emotions: e.emotion_labels || [],
          art_urls: e.art_file_ids || []
        })));
      }
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  };
  
  const calculateStreak = (entries) => {
    // Simple streak calculation
    if (!entries || entries.length === 0) return 0;
    let streak = 1;
    const sortedEntries = [...entries].sort((a, b) => 
      new Date(b.timestamp) - new Date(a.timestamp)
    );
    for (let i = 0; i < sortedEntries.length - 1; i++) {
      const current = new Date(sortedEntries[i].timestamp);
      const next = new Date(sortedEntries[i + 1].timestamp);
      const diffDays = Math.floor((current - next) / (1000 * 60 * 60 * 24));
      if (diffDays === 1) streak++;
      else break;
    }
    return streak;
  };

  const handleReflectionGenerated = (reflection) => {
    setCurrentReflection(reflection);
    setShowReflection(true);
    loadUserData(); // Refresh data
  };

  const handleLogout = async () => {
    try {
      authAPI.logout();
      onLogout();
    } catch (error) {
      console.error('Logout error:', error);
      onLogout(); // Logout anyway
    }
  };

  const tabs = [
    { id: 'text', label: 'Text', icon: <PenTool size={20} /> },
    { id: 'voice', label: 'Voice', icon: <Mic size={20} /> },
    { id: 'image', label: 'Image', icon: <Image size={20} /> },
    { id: 'video', label: 'Video', icon: <Video size={20} /> },
  ];

  const views = [
    { id: 'input', label: 'Express', icon: <Sparkles size={20} /> },
    { id: 'timeline', label: 'Timeline', icon: <Calendar size={20} /> },
    { id: 'gallery', label: 'Gallery', icon: <Heart size={20} /> },
    { id: 'stats', label: 'Stats', icon: <TrendingUp size={20} /> },
  ];

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      
      {/* Sidebar */}
      <aside className={`
        fixed md:static inset-y-0 left-0 z-50 w-64 glass-card
        transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        md:rounded-none md:border-r md:border-gray-200
      `}>
        <div className="h-full flex flex-col p-6">
          
          {/* Logo */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-2">
              <Brain className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-bold gradient-text">MindMirror</span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="md:hidden text-gray-500 hover:text-gray-700"
            >
              <X size={24} />
            </button>
          </div>

          {/* User Profile */}
          <div className="mb-8 p-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl">
            <div className="flex items-center gap-3 mb-2">
              {user.picture ? (
                <img
                  src={user.picture}
                  alt={user.name}
                  className="w-12 h-12 rounded-full border-2 border-white shadow"
                />
              ) : (
                <div className="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
                  {user.name?.charAt(0)}
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-800 truncate">{user.name}</p>
                <p className="text-sm text-gray-600 truncate">{user.email}</p>
              </div>
            </div>
            {stats && (
              <div className="flex items-center gap-2 mt-3 text-sm">
                <Award className="w-4 h-4 text-yellow-500" />
                <span className="text-gray-700">
                  {stats.current_streak} day streak 🔥
                </span>
              </div>
            )}
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-2">
            {views.map((view) => (
              <button
                key={view.id}
                onClick={() => {
                  setActiveView(view.id);
                  setSidebarOpen(false);
                }}
                className={`
                  w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium
                  transition-all duration-200
                  ${activeView === view.id
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-gray-100'
                  }
                `}
              >
                {view.icon}
                <span>{view.label}</span>
              </button>
            ))}
          </nav>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-red-600 hover:bg-red-50 transition-all duration-200"
          >
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Mobile Menu Button */}
      <button
        onClick={() => setSidebarOpen(true)}
        className="md:hidden fixed top-4 left-4 z-40 p-3 glass-card rounded-xl shadow-lg"
      >
        <Menu size={24} className="text-gray-700" />
      </button>

      {/* Main Content */}
      <main className="flex-1 p-4 md:p-8 overflow-y-auto">
        <AnimatePresence mode="wait">
          {activeView === 'input' && (
            <motion.div
              key="input"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">
                  Express Yourself
                </h1>
                <p className="text-gray-600 mb-8">
                  Share your thoughts, feelings, and moments in any way that feels right
                </p>

                {/* Tab Selector */}
                <div className="glass-card p-2 mb-6 flex gap-2 overflow-x-auto">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`
                        flex items-center gap-2 px-6 py-3 rounded-xl font-medium
                        transition-all duration-200 whitespace-nowrap
                        ${activeTab === tab.id
                          ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                          : 'text-gray-700 hover:bg-gray-100'
                        }
                      `}
                    >
                      {tab.icon}
                      <span>{tab.label}</span>
                    </button>
                  ))}
                </div>

                {/* Input Components */}
                <div className="glass-card p-6 md:p-8">
                  {activeTab === 'text' && (
                    <TextInput onReflectionGenerated={handleReflectionGenerated} />
                  )}
                  {activeTab === 'voice' && (
                    <VoiceInput onReflectionGenerated={handleReflectionGenerated} />
                  )}
                  {activeTab === 'image' && (
                    <ImageInput onReflectionGenerated={handleReflectionGenerated} />
                  )}
                  {activeTab === 'video' && (
                    <VideoInput onReflectionGenerated={handleReflectionGenerated} />
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {activeView === 'timeline' && (
            <motion.div
              key="timeline"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <MoodTimeline moodData={moodData} onRefresh={loadUserData} />
            </motion.div>
          )}

          {activeView === 'gallery' && (
            <motion.div
              key="gallery"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Gallery galleryItems={galleryItems} onRefresh={loadUserData} />
            </motion.div>
          )}

          {activeView === 'stats' && (
            <motion.div
              key="stats"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <StatsPanel stats={stats} onRefresh={loadUserData} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Reflection Modal */}
      <AnimatePresence>
        {showReflection && currentReflection && (
          <ReflectionDisplay
            reflection={currentReflection}
            onClose={() => setShowReflection(false)}
          />
        )}
      </AnimatePresence>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default Dashboard;
