import React, { useState } from 'react';
import { Heart, Image, Video, Sparkles, ExternalLink } from 'lucide-react';

const Gallery = ({ galleryItems, onRefresh }) => {
  const [filter, setFilter] = useState('all');

  const filteredItems = filter === 'all'
    ? galleryItems
    : galleryItems.filter(item => item.type === filter);

  const getTypeIcon = (type) => {
    switch (type) {
      case 'art':
        return <Sparkles size={20} className="text-purple-600" />;
      case 'image':
        return <Image size={20} className="text-pink-600" />;
      case 'video':
        return <Video size={20} className="text-blue-600" />;
      default:
        return <Heart size={20} className="text-red-600" />;
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'art':
        return 'bg-purple-100 text-purple-700';
      case 'image':
        return 'bg-pink-100 text-pink-700';
      case 'video':
        return 'bg-blue-100 text-blue-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">Your Gallery</h1>
          <p className="text-gray-600">Browse your emotional journey through visuals</p>
        </div>
        <button onClick={onRefresh} className="btn-secondary">
          Refresh
        </button>
      </div>

      {/* Filter Buttons */}
      <div className="glass-card p-2 flex gap-2 overflow-x-auto">
        {['all', 'art', 'image', 'video'].map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`
              px-6 py-3 rounded-xl font-medium whitespace-nowrap transition-all duration-200
              ${filter === type
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                : 'text-gray-700 hover:bg-gray-100'
              }
            `}
          >
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </button>
        ))}
      </div>

      {/* Gallery Grid */}
      {filteredItems.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredItems.map((item, index) => (
            <div
              key={item.id || index}
              className="glass-card overflow-hidden card-hover group"
            >
              {/* Image/Video Preview */}
              <div className="relative aspect-square bg-gradient-to-br from-gray-100 to-gray-200">
                {item.thumbnail ? (
                  <img
                    src={item.thumbnail}
                    alt={`Gallery item ${index}`}
                    className="w-full h-full object-cover"
                  />
                ) : item.preview_url ? (
                  <div className="w-full h-full flex items-center justify-center">
                    {getTypeIcon(item.type)}
                    <span className="ml-2 text-gray-600 capitalize">{item.type}</span>
                  </div>
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Heart size={48} className="text-gray-400" />
                  </div>
                )}
                
                {/* Overlay */}
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  {item.preview_url && (
                    <a
                      href={item.preview_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-3 bg-white rounded-full hover:bg-gray-100 transition-colors"
                    >
                      <ExternalLink size={24} className="text-gray-700" />
                    </a>
                  )}
                </div>
              </div>

              {/* Info */}
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getTypeColor(item.type)}`}>
                    {item.type.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(item.timestamp).toLocaleDateString()}
                  </span>
                </div>
                {item.emotion && (
                  <p className="mt-2 text-sm text-gray-600 capitalize">
                    Emotion: <span className="font-semibold">{item.emotion}</span>
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-card p-12 text-center">
          <Heart size={64} className="mx-auto mb-4 text-gray-300" />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No items yet</h3>
          <p className="text-gray-600 mb-6">
            Start expressing yourself to build your emotional gallery
          </p>
          <button
            onClick={onRefresh}
            className="btn-primary"
          >
            Refresh Gallery
          </button>
        </div>
      )}

      {/* Stats */}
      {galleryItems.length > 0 && (
        <div className="glass-card p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-3xl font-bold text-gray-800">{galleryItems.length}</p>
              <p className="text-sm text-gray-600">Total Items</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-purple-600">
                {galleryItems.filter(i => i.type === 'art').length}
              </p>
              <p className="text-sm text-gray-600">AI Art</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-pink-600">
                {galleryItems.filter(i => i.type === 'image').length}
              </p>
              <p className="text-sm text-gray-600">Images</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-blue-600">
                {galleryItems.filter(i => i.type === 'video').length}
              </p>
              <p className="text-sm text-gray-600">Videos</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Gallery;
