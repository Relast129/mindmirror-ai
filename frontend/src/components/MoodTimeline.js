import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Calendar, TrendingUp } from 'lucide-react';

const MoodTimeline = ({ moodData, onRefresh }) => {
  // Process data for charts
  const emotionColors = {
    joy: '#FFD700',
    sadness: '#4169E1',
    anger: '#DC143C',
    fear: '#9370DB',
    love: '#FF69B4',
    surprise: '#FF8C00',
    neutral: '#808080',
  };

  // Count emotions for pie chart
  const emotionCounts = {};
  moodData.forEach(entry => {
    emotionCounts[entry.emotion] = (emotionCounts[entry.emotion] || 0) + 1;
  });

  const pieData = Object.entries(emotionCounts).map(([emotion, count]) => ({
    name: emotion,
    value: count,
    color: emotionColors[emotion.toLowerCase()] || '#808080'
  }));

  // Prepare timeline data
  const timelineData = moodData.slice(0, 30).reverse().map((entry, index) => ({
    date: new Date(entry.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    confidence: entry.confidence * 100,
    emotion: entry.emotion,
  }));

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">Mood Timeline</h1>
          <p className="text-gray-600">Track your emotional journey over time</p>
        </div>
        <button onClick={onRefresh} className="btn-secondary">
          Refresh
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Emotion Distribution */}
        <div className="glass-card p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <TrendingUp size={24} className="text-blue-600" />
            Emotion Distribution
          </h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-12">No data yet. Start journaling!</p>
          )}
        </div>

        {/* Confidence Timeline */}
        <div className="glass-card p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Calendar size={24} className="text-purple-600" />
            Confidence Over Time
          </h3>
          {timelineData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="confidence" stroke="#8b5cf6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-12">No data yet. Start journaling!</p>
          )}
        </div>
      </div>

      {/* Recent Entries */}
      <div className="glass-card p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Recent Entries</h3>
        <div className="space-y-3">
          {moodData.slice(0, 10).map((entry, index) => (
            <div
              key={index}
              className="p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center font-bold text-white"
                    style={{ backgroundColor: emotionColors[entry.emotion.toLowerCase()] }}
                  >
                    {entry.emotion.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-800 capitalize">{entry.emotion}</p>
                    <p className="text-sm text-gray-600">{entry.content_preview}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">
                    {new Date(entry.timestamp).toLocaleDateString()}
                  </p>
                  <p className="text-xs text-gray-500">
                    {Math.round(entry.confidence * 100)}% confidence
                  </p>
                </div>
              </div>
            </div>
          ))}
          {moodData.length === 0 && (
            <p className="text-gray-500 text-center py-12">
              No entries yet. Start expressing yourself to see your mood timeline!
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default MoodTimeline;
