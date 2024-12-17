import React, { useState, useRef, useEffect } from 'react';
import { Camera, Mic, X, Check, Edit2, Eye, EyeOff } from 'lucide-react';

export default function ObjectLearningView({
  onCapture,
  onRecordTerm,
  onSaveTerm,
  language,
  region,
  dialect
}) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const overlayRef = useRef(null);
  
  const [mode, setMode] = useState('camera'); // camera, recording, review
  const [detectedObjects, setDetectedObjects] = useState([]);
  const [selectedObject, setSelectedObject] = useState(null);
  const [recordedTerm, setRecordedTerm] = useState('');
  const [showMasks, setShowMasks] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');

  // Camera setup
  useEffect(() => {
    async function setupCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: 'environment',
            width: { ideal: 1280 },
            height: { ideal: 720 }
          }
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        setError('Could not access camera');
      }
    }
    setupCamera();
    return () => {
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Handle canvas click for object selection
  const handleCanvasClick = async (e) => {
    if (mode !== 'camera' || isProcessing) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    setIsProcessing(true);
    try {
      // Detect object at click point
      const result = await onCapture({
        point: [x * scaleX, y * scaleY],
        frame: canvas.toDataURL('image/jpeg')
      });

      if (result.success) {
        setSelectedObject(result.object);
        drawObjectOverlay(result.object);
        setMode('recording');
      }
    } catch (err) {
      setError('Failed to detect object');
    } finally {
      setIsProcessing(false);
    }
  };

  // Draw segmentation mask overlay
  const drawObjectOverlay = (object) => {
    const overlay = overlayRef.current;
    const ctx = overlay.getContext('2d');
    ctx.clearRect(0, 0, overlay.width, overlay.height);

    if (!showMasks) return;

    // Draw segmentation mask
    if (object.mask) {
      ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';
      ctx.strokeStyle = 'rgba(0, 255, 0, 0.8)';
      ctx.lineWidth = 2;

      const imageData = new ImageData(
        new Uint8ClampedArray(object.mask.buffer),
        overlay.width,
        overlay.height
      );
      ctx.putImageData(imageData, 0, 0);
    }

    // Draw bounding box
    if (object.bbox) {
      const [x1, y1, x2, y2] = object.bbox;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
    }
  };

  // Handle voice recording
  const handleRecording = async () => {
    if (mode !== 'recording' || !selectedObject) return;

    setIsProcessing(true);
    try {
      const result = await onRecordTerm();
      if (result.success) {
        setRecordedTerm(result.text);
        setMode('review');
      }
    } catch (err) {
      setError('Failed to record term');
    } finally {
      setIsProcessing(false);
    }
  };

  // Save the term
  const handleSave = async () => {
    if (!selectedObject || !recordedTerm) return;

    setIsProcessing(true);
    try {
      await onSaveTerm({
        object: selectedObject,
        term: recordedTerm,
        language,
        region,
        dialect
      });
      
      // Reset state
      setSelectedObject(null);
      setRecordedTerm('');
      setMode('camera');
      const ctx = overlayRef.current.getContext('2d');
      ctx.clearRect(0, 0, overlayRef.current.width, overlayRef.current.height);
    } catch (err) {
      setError('Failed to save term');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="relative w-full h-full">
      {/* Camera view */}
      <video
        ref={videoRef}
        className="absolute top-0 left-0 w-full h-full object-cover"
        autoPlay
        playsInline
      />

      {/* Drawing canvas */}
      <canvas
        ref={canvasRef}
        className="absolute top-0 left-0 w-full h-full"
        onClick={handleCanvasClick}
      />

      {/* Overlay canvas */}
      <canvas
        ref={overlayRef}
        className="absolute top-0 left-0 w-full h-full pointer-events-none"
      />

      {/* Controls */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-black/50">
        <div className="flex items-center justify-between">
          {mode === 'camera' && (
            <button
              onClick={() => setShowMasks(!showMasks)}
              className="p-3 rounded-full bg-white/10 text-white"
            >
              {showMasks ? <Eye /> : <EyeOff />}
            </button>
          )}

          {mode === 'recording' && (
            <button
              onClick={handleRecording}
              className={`p-4 rounded-full ${isProcessing ? 'bg-red-500' : 'bg-white'}`}
            >
              <Mic className={isProcessing ? 'text-white animate-pulse' : 'text-black'} />
            </button>
          )}

          {mode === 'review' && (
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setMode('recording')}
                className="p-3 rounded-full bg-white/10 text-white"
              >
                <Edit2 />
              </button>
              <button
                onClick={handleSave}
                className="p-3 rounded-full bg-green-500 text-white"
              >
                <Check />
              </button>
              <button
                onClick={() => {
                  setMode('camera');
                  setSelectedObject(null);
                  setRecordedTerm('');
                }}
                className="p-3 rounded-full bg-red-500 text-white"
              >
                <X />
              </button>
            </div>
          )}
        </div>

        {/* Term display */}
        {recordedTerm && (
          <div className="mt-4 p-3 bg-white/90 rounded text-black">
            <p className="font-medium">{recordedTerm}</p>
            <p className="text-sm text-gray-600">
              {language} {dialect ? `(${dialect})` : ''}
            </p>
          </div>
        )}

        {/* Error display */}
        {error && (
          <div className="mt-4 p-3 bg-red-500/90 rounded text-white">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}