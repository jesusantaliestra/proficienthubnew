/**
 * HeyGen Streaming Avatar Component
 * 
 * Premium tier avatar with real-time video streaming, lip-sync, and emotions.
 * Uses @heygen/streaming-avatar SDK.
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import StreamingAvatar, { AvatarQuality, StreamingEvents } from '@heygen/streaming-avatar';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  Video,
  VideoOff,
  Volume2,
  VolumeX,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Crown
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Default avatar configurations
const HEYGEN_AVATARS = {
  nurse_female: {
    avatarId: 'Monica_public_3_20240108',
    voiceId: 'en-US-JennyNeural',
    name: 'Monica (Enfermera)',
  },
  doctor_male: {
    avatarId: 'josh_lite3_20230714', 
    voiceId: 'en-US-GuyNeural',
    name: 'Dr. Josh',
  },
  patient_elderly: {
    avatarId: 'Ann_public_20240108',
    voiceId: 'en-US-AriaNeural',
    name: 'Ann (Paciente)',
  },
  tutor_friendly: {
    avatarId: 'Anna_public_3_20240108',
    voiceId: 'en-US-JennyNeural',
    name: 'Anna (Tutora)',
  }
};

export default function HeyGenAvatar({ 
  sessionToken,
  avatarType = 'patient_elderly',
  onReady,
  onSpeakingStart,
  onSpeakingEnd,
  onError,
  className = ''
}) {
  const videoRef = useRef(null);
  const avatarRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [error, setError] = useState(null);

  const avatarConfig = HEYGEN_AVATARS[avatarType] || HEYGEN_AVATARS.patient_elderly;

  // Initialize avatar connection
  const initializeAvatar = useCallback(async () => {
    if (!sessionToken || avatarRef.current) return;

    setIsConnecting(true);
    setError(null);

    try {
      // Create StreamingAvatar instance
      const avatar = new StreamingAvatar({ token: sessionToken });
      avatarRef.current = avatar;

      // Set up event listeners
      avatar.on(StreamingEvents.STREAM_READY, (event) => {
        console.log('HeyGen stream ready');
        if (videoRef.current && event.detail) {
          videoRef.current.srcObject = event.detail;
          videoRef.current.play().catch(console.error);
        }
        setIsConnected(true);
        setIsConnecting(false);
        onReady?.();
      });

      avatar.on(StreamingEvents.AVATAR_START_TALKING, () => {
        console.log('Avatar started talking');
        setIsSpeaking(true);
        onSpeakingStart?.();
      });

      avatar.on(StreamingEvents.AVATAR_STOP_TALKING, () => {
        console.log('Avatar stopped talking');
        setIsSpeaking(false);
        onSpeakingEnd?.();
      });

      avatar.on(StreamingEvents.STREAM_DISCONNECTED, () => {
        console.log('Stream disconnected');
        setIsConnected(false);
        setIsConnecting(false);
      });

      // Start avatar session
      await avatar.createStartAvatar({
        avatarName: avatarConfig.avatarId,
        quality: AvatarQuality.Medium,
        voice: {
          voiceId: avatarConfig.voiceId,
          rate: 1.0,
          emotion: 'friendly'
        },
        language: 'en',
        disableIdleTimeout: true
      });

    } catch (err) {
      console.error('HeyGen initialization error:', err);
      setError(err.message || 'Error al conectar con el avatar');
      setIsConnecting(false);
      onError?.(err);
    }
  }, [sessionToken, avatarConfig, onReady, onSpeakingStart, onSpeakingEnd, onError]);

  // Initialize on mount
  useEffect(() => {
    if (sessionToken) {
      initializeAvatar();
    }

    return () => {
      // Cleanup on unmount
      if (avatarRef.current) {
        try {
          avatarRef.current.stopAvatar();
        } catch (e) {
          console.error('Error stopping avatar:', e);
        }
        avatarRef.current = null;
      }
    };
  }, [sessionToken, initializeAvatar]);

  // Speak text method
  const speak = useCallback(async (text, emotion = 'friendly') => {
    if (!avatarRef.current || !isConnected) {
      console.warn('Avatar not ready to speak');
      return false;
    }

    try {
      await avatarRef.current.speak({
        text,
        taskType: 'talk',
        taskMode: 'sync'
      });
      return true;
    } catch (err) {
      console.error('Speak error:', err);
      return false;
    }
  }, [isConnected]);

  // Interrupt speaking
  const interrupt = useCallback(async () => {
    if (!avatarRef.current) return;
    
    try {
      await avatarRef.current.interrupt();
    } catch (err) {
      console.error('Interrupt error:', err);
    }
  }, []);

  // Toggle mute
  const toggleMute = useCallback(() => {
    if (videoRef.current) {
      videoRef.current.muted = !videoRef.current.muted;
      setIsMuted(videoRef.current.muted);
    }
  }, []);

  // Expose methods via ref
  useEffect(() => {
    if (avatarRef.current) {
      avatarRef.current.speakText = speak;
      avatarRef.current.interruptSpeaking = interrupt;
    }
  }, [speak, interrupt]);

  // Render loading state
  if (isConnecting) {
    return (
      <div className={`relative bg-slate-800 rounded-lg overflow-hidden ${className}`}>
        <div className="aspect-video flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="w-12 h-12 text-yellow-400 animate-spin mx-auto mb-3" />
            <p className="text-slate-300">Conectando con avatar premium...</p>
            <p className="text-xs text-slate-500 mt-1">Esto puede tomar unos segundos</p>
          </div>
        </div>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className={`relative bg-slate-800 rounded-lg overflow-hidden ${className}`}>
        <div className="aspect-video flex items-center justify-center p-6">
          <div className="text-center">
            <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
            <p className="text-white font-medium mb-2">Error de Conexión</p>
            <p className="text-sm text-slate-400 mb-4">{error}</p>
            <Button 
              onClick={initializeAvatar}
              variant="outline"
              className="border-slate-600"
            >
              Reintentar
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative bg-slate-900 rounded-lg overflow-hidden ${className}`}>
      {/* Video container */}
      <div className="aspect-video bg-gradient-to-b from-slate-800 to-slate-900">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="w-full h-full object-cover"
        />
        
        {/* Status overlay */}
        <div className="absolute top-3 left-3 flex items-center gap-2">
          <Badge className="bg-yellow-500/20 text-yellow-300 text-xs">
            <Crown className="w-3 h-3 mr-1" />
            Premium
          </Badge>
          {isConnected && (
            <Badge className="bg-green-500/20 text-green-300 text-xs">
              <CheckCircle2 className="w-3 h-3 mr-1" />
              Conectado
            </Badge>
          )}
        </div>

        {/* Speaking indicator */}
        {isSpeaking && (
          <div className="absolute bottom-3 left-3 flex items-center gap-2 bg-black/60 px-3 py-1.5 rounded-full">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-sm text-white">Hablando...</span>
          </div>
        )}

        {/* Controls */}
        <div className="absolute bottom-3 right-3 flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleMute}
            className="bg-black/40 hover:bg-black/60 text-white"
          >
            {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </Button>
        </div>
      </div>

      {/* Avatar info */}
      <div className="p-3 border-t border-slate-800">
        <p className="text-white font-medium">{avatarConfig.name}</p>
        <p className="text-xs text-slate-400">Avatar HeyGen Premium</p>
      </div>
    </div>
  );
}

// Export speak function for external use
export const speakWithHeyGen = async (avatarInstance, text) => {
  if (avatarInstance?.speakText) {
    return await avatarInstance.speakText(text);
  }
  return false;
};
