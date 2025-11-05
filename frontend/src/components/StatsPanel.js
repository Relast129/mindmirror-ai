import React from 'react';
import { Award, TrendingUp, Calendar, Heart, PenTool, Mic, Image, Video } from 'lucide-react';

const StatsPanel = ({ stats, onRefresh }) => {
  if (!stats) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <div className="loader mx-auto mb-4"></div>
        <p className="text-gray-600">Loading your statistics...</p>
      </div>
    );
  }

  const StatCard = ({ icon, label, value, color }) => (
    <div className="glass-card p-6 card-hover">
      <div className="flex items-center gap-4">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
          {icon}
        </div>
        <div>
          <p className="text-3xl font-bold text-gray-800">{value}</p>
          <p className="text-sm text-gray-600">{label}</p>
        </div>
      </div>
    </div>
  );

  const emotionColors = {
    joy: 'bg-yellow-100 text-yellow-600',
    sadness: 'bg-blue-100 text-blue-600',
    anger: 'bg-red-100 text-red-600',
    fear: 'bg-purple-100 text-purple-600',
    love: 'bg-pink-100 text-pink-600',
    surprise: 'bg-orange-100 text-orange-600',
    neutral: 'bg-gray-100 text-gray-600',
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">Your Statistics</h1>
          <p className="text-gray-600">Track your emotional wellness journey</p>
        </div>
        <button onClick={onRefresh} className="btn-secondary">
          Refresh
        </button>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<PenTool size={24} />}
          label="Total Entries"
          value={stats.total_entries}
          color="bg-blue-100 text-blue-600"
        />
        <StatCard
          icon={<Heart size={24} />}
          label="Reflections"
          value={stats.total_reflections}
          color="bg-pink-100 text-pink-600"
        />
        <StatCard
          icon={<Award size={24} />}
          label="Current Streak"
          value={`${stats.current_streak} days`}
          color="bg-yellow-100 text-yellow-600"
        />
        <StatCard
          icon={<TrendingUp size={24} />}
          label="Longest Streak"
          value={`${stats.longest_streak} days`}
          color="bg-green-100 text-green-600"
        />
      </div>

      {/* Entries by Type */}
      <div className="glass-card p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Entries by Type</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl">
            <PenTool size={32} className="mx-auto mb-2 text-blue-600" />
            <p className="text-2xl font-bold text-gray-800">{stats.entries_by_type.text || 0}</p>
            <p className="text-sm text-gray-600">Text</p>
          </div>
          <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl">
            <Mic size={32} className="mx-auto mb-2 text-purple-600" />
            <p className="text-2xl font-bold text-gray-800">{stats.entries_by_type.voice || 0}</p>
            <p className="text-sm text-gray-600">Voice</p>
          </div>
          <div className="text-center p-4 bg-gradient-to-br from-pink-50 to-pink-100 rounded-xl">
            <Image size={32} className="mx-auto mb-2 text-pink-600" />
            <p className="text-2xl font-bold text-gray-800">{stats.entries_by_type.image || 0}</p>
            <p className="text-sm text-gray-600">Images</p>
          </div>
          <div className="text-center p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl">
            <Video size={32} className="mx-auto mb-2 text-orange-600" />
            <p className="text-2xl font-bold text-gray-800">{stats.entries_by_type.video || 0}</p>
            <p className="text-sm text-gray-600">Videos</p>
          </div>
        </div>
      </div>

      {/* Emotion Distribution */}
      <div className="glass-card p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Emotion Distribution</h3>
        <div className="space-y-3">
          {Object.entries(stats.emotion_distribution).map(([emotion, count]) => {
            const total = Object.values(stats.emotion_distribution).reduce((a, b) => a + b, 0);
            const percentage = ((count / total) * 100).toFixed(1);
            
            return (
              <div key={emotion}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700 capitalize">{emotion}</span>
                  <span className="text-sm text-gray-600">{count} ({percentage}%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${
                      emotionColors[emotion.toLowerCase()]?.replace('text-', 'bg-').split(' ')[0] || 'bg-gray-400'
                    }`}
                    style={{ width: `${percentage}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Most Common Emotion */}
      <div className="glass-card p-6 bg-gradient-to-br from-purple-50 to-pink-50">
        <div className="text-center">
          <h3 className="text-xl font-semibold text-gray-800 mb-2">Your Most Common Emotion</h3>
          <p className="text-5xl font-bold gradient-text capitalize mb-2">{stats.most_common_emotion}</p>
          <p className="text-gray-600">
            This emotion appears most frequently in your reflections
          </p>
        </div>
      </div>

      {/* Last Entry */}
      {stats.last_entry_date && (
        <div className="glass-card p-6">
          <div className="flex items-center gap-3">
            <Calendar size={24} className="text-blue-600" />
            <div>
              <p className="text-sm text-gray-600">Last Entry</p>
              <p className="text-lg font-semibold text-gray-800">
                {new Date(stats.last_entry_date).toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Encouragement */}
      <div className="glass-card p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-center">
        <h3 className="text-2xl font-bold mb-2">Keep Going! 🎉</h3>
        <p className="text-lg opacity-90">
          You've made {stats.total_entries} entries. Every reflection is a step toward better emotional wellness.
        </p>
      </div>
    </div>
  );
};

export default StatsPanel;
