import { useState, useCallback, useRef, useEffect } from 'react';
import { Audio, AVPlaybackStatus } from 'expo-av';

interface UseVoiceReturn {
  // Recording
  isRecording: boolean;
  recordingDuration: number;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<string | null>;
  cancelRecording: () => Promise<void>;
  
  // Playback
  isPlaying: boolean;
  playbackProgress: number;
  playAudio: (uri: string) => Promise<void>;
  pauseAudio: () => Promise<void>;
  stopPlayback: () => Promise<void>;
  seekTo: (position: number) => Promise<void>;
  
  // State
  error: string | null;
}

export const useVoice = (): UseVoiceReturn => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackProgress, setPlaybackProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const recordingRef = useRef<Audio.Recording | null>(null);
  const soundRef = useRef<Audio.Sound | null>(null);
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recordingRef.current) {
        recordingRef.current.stopAndUnloadAsync();
      }
      if (soundRef.current) {
        soundRef.current.unloadAsync();
      }
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }
    };
  }, []);

  const startRecording = useCallback(async () => {
    try {
      setError(null);
      
      // Request permissions
      const { granted } = await Audio.requestPermissionsAsync();
      if (!granted) {
        setError('Microphone permission is required');
        return;
      }

      // Set audio mode for recording
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      // Create and start recording
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      
      recordingRef.current = recording;
      setIsRecording(true);
      setRecordingDuration(0);

      // Track duration
      durationIntervalRef.current = setInterval(() => {
        setRecordingDuration((prev) => prev + 1);
      }, 1000);

    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Failed to start recording');
    }
  }, []);

  const stopRecording = useCallback(async (): Promise<string | null> => {
    try {
      if (!recordingRef.current) return null;

      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }

      await recordingRef.current.stopAndUnloadAsync();
      const uri = recordingRef.current.getURI();
      
      // Reset audio mode
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
      });

      recordingRef.current = null;
      setIsRecording(false);

      return uri;
    } catch (err) {
      console.error('Error stopping recording:', err);
      setError('Failed to stop recording');
      return null;
    }
  }, []);

  const cancelRecording = useCallback(async () => {
    try {
      if (recordingRef.current) {
        if (durationIntervalRef.current) {
          clearInterval(durationIntervalRef.current);
        }
        await recordingRef.current.stopAndUnloadAsync();
        recordingRef.current = null;
      }
      setIsRecording(false);
      setRecordingDuration(0);
    } catch (err) {
      console.error('Error canceling recording:', err);
    }
  }, []);

  const playAudio = useCallback(async (uri: string) => {
    try {
      setError(null);

      // Stop any existing playback
      if (soundRef.current) {
        await soundRef.current.unloadAsync();
      }

      // Create and play sound
      const { sound } = await Audio.Sound.createAsync(
        { uri },
        { shouldPlay: true },
        (status: AVPlaybackStatus) => {
          if (status.isLoaded) {
            if (status.didJustFinish) {
              setIsPlaying(false);
              setPlaybackProgress(0);
            } else if (status.durationMillis) {
              setPlaybackProgress(status.positionMillis / status.durationMillis);
            }
          }
        }
      );

      soundRef.current = sound;
      setIsPlaying(true);

    } catch (err) {
      console.error('Error playing audio:', err);
      setError('Failed to play audio');
    }
  }, []);

  const pauseAudio = useCallback(async () => {
    try {
      if (soundRef.current) {
        await soundRef.current.pauseAsync();
        setIsPlaying(false);
      }
    } catch (err) {
      console.error('Error pausing audio:', err);
    }
  }, []);

  const stopPlayback = useCallback(async () => {
    try {
      if (soundRef.current) {
        await soundRef.current.stopAsync();
        setIsPlaying(false);
        setPlaybackProgress(0);
      }
    } catch (err) {
      console.error('Error stopping playback:', err);
    }
  }, []);

  const seekTo = useCallback(async (position: number) => {
    try {
      if (soundRef.current) {
        const status = await soundRef.current.getStatusAsync();
        if (status.isLoaded && status.durationMillis) {
          await soundRef.current.setPositionAsync(position * status.durationMillis);
        }
      }
    } catch (err) {
      console.error('Error seeking:', err);
    }
  }, []);

  return {
    isRecording,
    recordingDuration,
    startRecording,
    stopRecording,
    cancelRecording,
    isPlaying,
    playbackProgress,
    playAudio,
    pauseAudio,
    stopPlayback,
    seekTo,
    error,
  };
};
