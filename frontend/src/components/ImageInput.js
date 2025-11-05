import React, { useState, useRef } from 'react';
import { Upload, Image as ImageIcon, Sparkles, X } from 'lucide-react';
import { journalAPI } from '../services/gradio-api';

const ImageInput = ({ onReflectionGenerated }) => {
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [caption, setCaption] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file');
        return;
      }
      
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
      setError('');
    }
  };

  const handleSubmit = async () => {
    if (!imageFile) {
      setError('Please select an image');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Submit image to Gradio backend (handles upload + reflection)
      const reflection = await journalAPI.submitImage(imageFile);

      onReflectionGenerated(reflection);
      
      // Reset
      setImageFile(null);
      setImagePreview('');
      setCaption('');
    } catch (err) {
      console.error('Error processing image:', err);
      setError('Failed to process image. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const clearImage = () => {
    setImageFile(null);
    setImagePreview('');
    setCaption('');
    setError('');
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <p className="text-gray-600 mb-6">
          Upload a photo, drawing, or any image that expresses your emotions
        </p>

        {!imagePreview ? (
          <div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-full py-12 rounded-2xl border-2 border-dashed border-gray-300 hover:border-blue-500 transition-all duration-200 flex flex-col items-center gap-4 bg-gray-50 hover:bg-blue-50"
            >
              <ImageIcon size={64} className="text-gray-400" />
              <div>
                <p className="text-lg font-semibold text-gray-700">Click to upload image</p>
                <p className="text-sm text-gray-500 mt-1">PNG, JPG, GIF up to 10MB</p>
              </div>
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Image Preview */}
            <div className="relative glass-card p-4">
              <button
                onClick={clearImage}
                className="absolute top-6 right-6 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors z-10"
                disabled={loading}
              >
                <X size={20} />
              </button>
              <img
                src={imagePreview}
                alt="Preview"
                className="max-h-96 mx-auto rounded-xl shadow-lg"
              />
            </div>

            {/* Caption Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 text-left">
                Add a caption (optional)
              </label>
              <textarea
                value={caption}
                onChange={(e) => setCaption(e.target.value)}
                placeholder="Describe what this image means to you or how it makes you feel..."
                rows={3}
                className="textarea-field"
                disabled={loading}
              />
            </div>

            {/* Submit Button */}
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
        Your image will be safely stored in your Google Drive
      </p>
    </div>
  );
};

export default ImageInput;
