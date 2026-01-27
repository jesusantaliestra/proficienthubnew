import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useRive, useStateMachineInput } from '@rive-app/react-canvas';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Simple animated avatar using CSS animations (fallback if Rive not available)
const SimpleAnimatedAvatar = ({ isSpeaking, avatarStyle = 'teacher' }) => {
  const avatarStyles = {
    teacher: {
      bg: 'from-blue-500 to-indigo-600',
      icon: '👨‍🏫',
      name: 'Prof. Smith'
    },
    female_teacher: {
      bg: 'from-pink-500 to-purple-600',
      icon: '👩‍🏫',
      name: 'Ms. Johnson'
    },
    friendly: {
      bg: 'from-green-500 to-teal-600',
      icon: '🧑‍💼',
      name: 'Alex'
    }
  };

  const style = avatarStyles[avatarStyle] || avatarStyles.teacher;

  return (
    <div className="relative w-48 h-48 mx-auto">
      {/* Avatar circle with gradient */}
      <div className={`w-full h-full rounded-full bg-gradient-to-br ${style.bg} flex items-center justify-center shadow-xl`}>
        <span className={`text-7xl ${isSpeaking ? 'animate-bounce' : ''}`}>
          {style.icon}
        </span>
      </div>
      
      {/* Speaking indicator */}
      {isSpeaking && (
        <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
          </div>
        </div>
      )}
      
      {/* Sound waves when speaking */}
      {isSpeaking && (
        <>
          <div className="absolute inset-0 rounded-full border-4 border-blue-300 animate-ping opacity-20"></div>
          <div className="absolute inset-2 rounded-full border-2 border-blue-200 animate-ping opacity-10" style={{ animationDelay: '0.5s' }}></div>
        </>
      )}
      
      {/* Name tag */}
      <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 bg-white px-4 py-1 rounded-full shadow-md">
        <span className="text-sm font-semibold text-gray-700">{style.name}</span>
      </div>
    </div>
  );
};

// Rive Avatar Component (premium animated avatar)
const RiveAvatar = ({ isSpeaking, riveFile }) => {
  const { RiveComponent, rive } = useRive({
    src: riveFile || '/assets/tutor-avatar.riv',
    stateMachines: 'State Machine 1',
    autoplay: true,
  });

  const speakingInput = useStateMachineInput(rive, 'State Machine 1', 'isSpeaking');

  useEffect(() => {
    if (speakingInput) {
      speakingInput.value = isSpeaking;
    }
  }, [isSpeaking, speakingInput]);

  return (
    <div className="w-64 h-64 mx-auto">
      <RiveComponent />
    </div>
  );
};

// HeyGen Video Avatar (Premium - realistic AI avatar)
const HeyGenAvatar = ({ videoUrl, isLoading }) => {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && videoUrl) {
      videoRef.current.play();
    }
  }, [videoUrl]);

  if (isLoading) {
    return (
      <div className="w-64 h-64 mx-auto rounded-2xl bg-gradient-to-br from-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white text-sm">Generating avatar...</p>
        </div>
      </div>
    );
  }

  if (!videoUrl) {
    return (
      <div className="w-64 h-64 mx-auto rounded-2xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
        <div className="text-center text-white">
          <span className="text-6xl">🎬</span>
          <p className="text-sm mt-2">HeyGen Avatar</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-64 h-64 mx-auto rounded-2xl overflow-hidden shadow-xl">
      <video
        ref={videoRef}
        src={videoUrl}
        className="w-full h-full object-cover"
        autoPlay
        playsInline
      />
    </div>
  );
};

// Main AI Avatar Component - Supports multiple modes
export default function AIAvatar({ 
  mode = 'simple', // 'simple' | 'rive' | 'heygen'
  isSpeaking = false,
  text = '',
  avatarStyle = 'teacher',
  heygenConfig = null,
  onVideoReady = null,
  onError = null 
}) {
  const [heygenVideoUrl, setHeygenVideoUrl] = useState(null);
  const [heygenLoading, setHeygenLoading] = useState(false);
  const [currentMode, setCurrentMode] = useState(mode);

  // Generate HeyGen video when text changes (for heygen mode)
  const generateHeyGenVideo = useCallback(async (scriptText) => {
    if (!heygenConfig?.enabled || !scriptText || scriptText.length < 10) return;

    setHeygenLoading(true);
    try {
      const response = await axios.post(`${API_URL}/avatar/heygen/generate`, {
        script_text: scriptText,
        avatar_id: heygenConfig.avatar_id || 'default',
        voice_id: heygenConfig.voice_id || 'en-US-1'
      });

      const videoId = response.data.video_id;
      
      // Poll for completion
      const pollStatus = async (attempts = 0) => {
        if (attempts > 60) {
          throw new Error('Video generation timeout');
        }

        const statusRes = await axios.get(`${API_URL}/avatar/heygen/status/${videoId}`);
        
        if (statusRes.data.status === 'completed') {
          setHeygenVideoUrl(statusRes.data.video_url);
          setHeygenLoading(false);
          onVideoReady?.(statusRes.data.video_url);
        } else if (statusRes.data.status === 'failed') {
          throw new Error('Video generation failed');
        } else {
          setTimeout(() => pollStatus(attempts + 1), 2000);
        }
      };

      await pollStatus();
    } catch (error) {
      console.error('HeyGen error:', error);
      setHeygenLoading(false);
      onError?.(error.message);
      toast.error('Failed to generate avatar video');
      // Fallback to simple avatar
      setCurrentMode('simple');
    }
  }, [heygenConfig, onVideoReady, onError]);

  useEffect(() => {
    if (mode === 'heygen' && text && text.length > 10) {
      generateHeyGenVideo(text);
    }
  }, [mode, text, generateHeyGenVideo]);

  // Render based on mode
  switch (currentMode) {
    case 'heygen':
      return (
        <HeyGenAvatar 
          videoUrl={heygenVideoUrl} 
          isLoading={heygenLoading}
        />
      );
    
    case 'rive':
      return (
        <RiveAvatar 
          isSpeaking={isSpeaking}
          riveFile={heygenConfig?.rive_file}
        />
      );
    
    case 'simple':
    default:
      return (
        <SimpleAnimatedAvatar 
          isSpeaking={isSpeaking}
          avatarStyle={avatarStyle}
        />
      );
  }
}

// Avatar Selection Component for Settings
export function AvatarSelector({ value, onChange, heygenEnabled = false }) {
  const avatarOptions = [
    { id: 'teacher', name: 'Prof. Smith', icon: '👨‍🏫', type: 'simple' },
    { id: 'female_teacher', name: 'Ms. Johnson', icon: '👩‍🏫', type: 'simple' },
    { id: 'friendly', name: 'Alex', icon: '🧑‍💼', type: 'simple' },
  ];

  if (heygenEnabled) {
    avatarOptions.push(
      { id: 'heygen_sarah', name: 'Sarah (AI)', icon: '🎬', type: 'heygen', premium: true },
      { id: 'heygen_james', name: 'James (AI)', icon: '🎬', type: 'heygen', premium: true }
    );
  }

  return (
    <div className="grid grid-cols-3 gap-3">
      {avatarOptions.map((avatar) => (
        <button
          key={avatar.id}
          onClick={() => onChange(avatar.id)}
          className={`p-4 rounded-xl border-2 transition-all ${
            value === avatar.id 
              ? 'border-[#58CC02] bg-green-50' 
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          <span className="text-3xl block mb-2">{avatar.icon}</span>
          <span className="text-sm font-medium text-gray-700">{avatar.name}</span>
          {avatar.premium && (
            <span className="block text-xs text-purple-600 mt-1">Premium</span>
          )}
        </button>
      ))}
    </div>
  );
}

// Export avatar utilities
export const getAvatarMode = (avatarId) => {
  if (avatarId?.startsWith('heygen_')) return 'heygen';
  return 'simple';
};

export const getAvatarStyle = (avatarId) => {
  if (avatarId?.startsWith('heygen_')) {
    return avatarId.replace('heygen_', '');
  }
  return avatarId || 'teacher';
};
