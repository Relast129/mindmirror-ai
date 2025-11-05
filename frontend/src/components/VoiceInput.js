import React, { useState, useRef } from 'react';
import { Mic, Square, Upload, Sparkles } from 'lucide-react';
import { journalAPI } from '../services/gradio-api';

const VoiceInput = ({ onReflectionGenerated }) => {
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioURL, setAudioURL] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [transcription, setTranscription] = useState('');
  
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const fileInputRef = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        setAudioURL(URL.createObjectURL(blob));
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setRecording(true);
      setError('');
    } catch (err) {
      console.error('Error accessing microphone:', err);
      setError('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAudioBlob(file);
      setAudioURL(URL.createObjectURL(file));
      setError('');
    }
  };

  const handleSubmit = async () => {
    if (!audioBlob) {
      setError('Please record or upload an audio file');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Convert blob to file
      const audioFile = new File([audioBlob], 'voice_note.webm', { type: audioBlob.type });
      
      // Submit voice to Gradio backend (handles transcription + reflection)
      const reflection = await journalAPI.submitVoice(audioFile);

      onReflectionGenerated(reflection);
      
      // Reset
      setAudioBlob(null);
      setAudioURL('');
      setTranscription('');
    } catch (err) {
      console.error('Error processing voice:', err);
      setError('Failed to process voice recording. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <p className="text-gray-600 mb-6">
          Record your voice or upload an audio file to express your feelings
        </p>

        {!audioURL ? (
          <div className="space-y-4">
            {/* Record Button */}
            <button
              onClick={recording ? stopRecording : startRecording}
              className={`
                w-full py-8 rounded-2xl font-semibold text-lg
                transition-all duration-200 flex flex-col items-center gap-4
                ${recording
                  ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                  : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:shadow-lg text-white'
                }
              `}
            >
              {recording ? (
                <>
                  <Square size={48} />
                  <span>Stop Recording</span>
                  <span className="text-sm opacity-90">Recording in progress...</span>
                </>
              ) : (
                <>
                  <Mic size={48} />
                  <span>Start Recording</span>
                  <span className="text-sm opacity-90">Click to record your voice</span>
                </>
              )}
            </button>

            {/* Upload Button */}
            <div className="relative">
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*"
                onChange={handleFileUpload}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="w-full btn-secondary flex items-center justify-center gap-2"
              >
                <Upload size={20} />
                <span>Upload Audio File</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Audio Player */}
            <div className="glass-card p-6">
              <audio src={audioURL} controls className="w-full mb-4" />
              
              {transcription && (
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-left">
                  <p className="text-sm font-medium text-blue-900 mb-2">Transcription:</p>
                  <p className="text-gray-700">{transcription}</p>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setAudioBlob(null);
                  setAudioURL('');
                  setTranscription('');
                }}
                className="flex-1 btn-secondary"
                disabled={loading}
              >
                Record Again
              </button>
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="flex-1 btn-primary flex items-center justify-center gap-2"
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
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
          {error}
        </div>
      )}

      <p className="text-sm text-gray-500 text-center">
        Your voice will be transcribed and analyzed for emotional insights
      </p>
    </div>
  );
};

export default VoiceInput;
