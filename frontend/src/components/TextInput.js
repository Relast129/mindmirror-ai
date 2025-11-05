import React, { useState } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { journalAPI } from '../services/gradio-api';

const TextInput = ({ onReflectionGenerated }) => {
  const [content, setContent] = useState('');
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!content.trim()) {
      setError('Please write something before submitting');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const reflection = await journalAPI.submitText(content
      );

      onReflectionGenerated(reflection);
      setContent('');
      setTitle('');
    } catch (err) {
      console.error('Error generating reflection:', err);
      setError('Failed to generate reflection. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Title (Optional)
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Give your entry a title..."
          className="input-field"
          disabled={loading}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          How are you feeling? What's on your mind?
        </label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Express yourself freely... Share your thoughts, feelings, or what happened today. This is your safe space."
          rows={8}
          className="textarea-field"
          disabled={loading}
        />
        <p className="text-sm text-gray-500 mt-2">
          {content.length} characters
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={loading || !content.trim()}
        className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <div className="loader"></div>
            <span>Generating your reflection...</span>
          </>
        ) : (
          <>
            <Sparkles size={20} />
            <span>Generate Reflection</span>
            <Send size={20} />
          </>
        )}
      </button>

      <p className="text-sm text-gray-500 text-center">
        Your reflection will include emotional analysis, personalized poetry, and AI-generated art
      </p>
    </form>
  );
};

export default TextInput;
