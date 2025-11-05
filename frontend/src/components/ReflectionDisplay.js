import React from 'react';
import { motion } from 'framer-motion';
import { X, Heart, Sparkles, Download } from 'lucide-react';

const ReflectionDisplay = ({ reflection, onClose }) => {
  const downloadArt = () => {
    if (reflection.art_base64) {
      const link = document.createElement('a');
      link.href = `data:image/png;base64,${reflection.art_base64}`;
      link.download = `mindmirror-art-${reflection.reflection_id}.png`;
      link.click();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        className="glass-card max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6 md:p-8"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div
              className="w-12 h-12 rounded-full flex items-center justify-center text-2xl"
              style={{ backgroundColor: reflection.color + '30' }}
            >
              {reflection.emoji}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Your Reflection</h2>
              <p className="text-sm text-gray-600">
                Emotion: <span className="font-semibold capitalize">{reflection.emotion}</span>
                {' '}({Math.round(reflection.emotion_confidence * 100)}% confidence)
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Emotion Summary */}
        <div
          className="p-4 rounded-xl mb-6"
          style={{ backgroundColor: reflection.color + '20', borderLeft: `4px solid ${reflection.color}` }}
        >
          <p className="text-gray-700 leading-relaxed">{reflection.emotion_summary}</p>
        </div>

        {/* AI Generated Art */}
        {reflection.art_base64 && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                <Sparkles size={20} className="text-purple-600" />
                Your Mood Art
              </h3>
              <button
                onClick={downloadArt}
                className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                <Download size={16} />
                Download
              </button>
            </div>
            <img
              src={`data:image/png;base64,${reflection.art_base64}`}
              alt="Mood Art"
              className="w-full rounded-xl shadow-lg"
            />
          </div>
        )}

        {/* Reflection Text */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <Heart size={20} className="text-pink-600" />
            Reflection
          </h3>
          <p className="text-gray-700 leading-relaxed bg-gradient-to-br from-blue-50 to-purple-50 p-4 rounded-xl">
            {reflection.reflection_text}
          </p>
        </div>

        {/* Poem */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Your Poem</h3>
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-xl">
            <pre className="font-serif text-gray-700 whitespace-pre-wrap leading-relaxed">
              {reflection.poem}
            </pre>
          </div>
        </div>

        {/* Advice */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Gentle Guidance</h3>
          <p className="text-gray-700 leading-relaxed bg-green-50 p-4 rounded-xl border-l-4 border-green-500">
            {reflection.advice}
          </p>
        </div>

        {/* Voice Reflection */}
        {reflection.voice_base64 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Listen to Your Reflection</h3>
            <audio
              src={`data:audio/mp3;base64,${reflection.voice_base64}`}
              controls
              className="w-full"
            />
          </div>
        )}

        {/* Footer */}
        <div className="text-center pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-500 mb-4">
            This reflection has been saved to your Google Drive
          </p>
          <button
            onClick={onClose}
            className="btn-primary"
          >
            Close Reflection
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ReflectionDisplay;
