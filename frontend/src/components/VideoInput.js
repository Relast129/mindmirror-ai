import React, { useState, useRef } from 'react';
import { Video as VideoIcon, Sparkles, X } from 'lucide-react';
import { journalAPI } from '../services/gradio-api';

const VideoInput = ({ onReflectionGenerated }) => {
  const [videoFile, setVideoFile] = useState(null);
  const [videoPreview, setVideoPreview] = useState('');
  const [caption, setCaption] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('video/')) {
        setError('Please select a video file');
        return;
      }
      
      setVideoFile(file);
      setVideoPreview(URL.createObjectURL(file));
      setError('');
    }
  };

  const handleSubmit = async () => {
    if (!videoFile) {
      setError('Please select a video');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Submit video to Gradio backend (handles upload + processing + reflection)
      const reflection = await journalAPI.submitVideo(videoFile);

      onReflectionGenerated(reflection);
      
      // Reset
      setVideoFile(null);
      setVideoPreview('');
      setCaption('');
    } catch (err) {
      console.error('Error processing video:', err);
      setError('Failed to process video. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const clearVideo = () => {
    setVideoFile(null);
    setVideoPreview('');
    setCaption('');
    setError('');
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <p className="text-gray-600 mb-6">
          Upload a short video clip to capture your emotional moment
        </p>

        {!videoPreview ? (
          <div>
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-full py-12 rounded-2xl border-2 border-dashed border-gray-300 hover:border-blue-500 transition-all duration-200 flex flex-col items-center gap-4 bg-gray-50 hover:bg-blue-50"
            >
              <VideoIcon size={64} className="text-gray-400" />
              <div>
                <p className="text-lg font-semibold text-gray-700">Click to upload video</p>
                <p className="text-sm text-gray-500 mt-1">MP4, MOV, AVI up to 50MB</p>
              </div>
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative glass-card p-4">
              <button
                onClick={clearVideo}
                className="absolute top-6 right-6 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors z-10"
                disabled={loading}
              >
                <X size={20} />
              </button>
              <video
                src={videoPreview}
                controls
                className="max-h-96 mx-auto rounded-xl shadow-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 text-left">
                Add a caption (optional)
              </label>
              <textarea
                value={caption}
                onChange={(e) => setCaption(e.target.value)}
                placeholder="Describe what this video means to you..."
                rows={3}
                className="textarea-field"
                disabled={loading}
              />
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="loader"></div>
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  <span>Generate Reflection</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
          {error}
        </div>
      )}

      <p className="text-sm text-gray-500 text-center">
        Audio from your video will be transcribed and analyzed
      </p>
    </div>
  );
};

export default VideoInput;
