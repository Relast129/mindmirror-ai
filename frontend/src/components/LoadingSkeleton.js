import React from 'react';

export const SkeletonCard = () => (
  <div className="animate-pulse bg-white rounded-xl p-6 shadow-sm">
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
    <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
    <div className="h-3 bg-gray-200 rounded w-2/3"></div>
  </div>
);

export const SkeletonStat = () => (
  <div className="animate-pulse bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl p-6">
    <div className="h-8 w-8 bg-gray-200 rounded-lg mb-3"></div>
    <div className="h-8 bg-gray-200 rounded w-16 mb-2"></div>
    <div className="h-3 bg-gray-200 rounded w-24"></div>
  </div>
);

export const SkeletonTimeline = () => (
  <div className="animate-pulse space-y-4">
    {[1, 2, 3, 4].map((i) => (
      <div key={i} className="flex items-center gap-4">
        <div className="h-12 w-12 bg-gray-200 rounded-full"></div>
        <div className="flex-1">
          <div className="h-4 bg-gray-200 rounded w-32 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-48"></div>
        </div>
      </div>
    ))}
  </div>
);

export const SkeletonGallery = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {[1, 2, 3, 4, 5, 6].map((i) => (
      <div key={i} className="animate-pulse">
        <div className="aspect-square bg-gray-200 rounded-xl mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-3/4"></div>
      </div>
    ))}
  </div>
);

const LoadingSkeletons = { SkeletonCard, SkeletonStat, SkeletonTimeline, SkeletonGallery };
export default LoadingSkeletons;
