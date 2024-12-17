import React, { useRef, useEffect, useState } from 'react';
import { Camera, Mic, X, Check } from 'lucide-react';
import { Button } from '../../components/ui/button';
import { wsService } from '../services/websocket';

const CameraView = ({ onCapture, onRecordTerm }) => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [isRecording, setIsRecording] = useState(false);
    const [detectedObject, setDetectedObject] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        // Initialize camera and WebSocket when component mounts
        startCamera();
        wsService.connect().catch(err => {
            setError('Failed to connect to server');
            console.error('WebSocket connection error:', err);
        });

        return () => {
            stopCamera();
            wsService.disconnect();
        };
    }, []);

    const startCamera = async () => {
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
            console.error('Camera error:', err);
        }
    };

    const stopCamera = () => {
        if (videoRef.current?.srcObject) {
            const tracks = videoRef.current.srcObject.getTracks();
            tracks.forEach(track => track.stop());
        }
    };

    const handleCapture = async () => {
        if (!videoRef.current || isProcessing) return;

        setIsProcessing(true);
        setError('');
        
        try {
            const canvas = canvasRef.current;
            const video = videoRef.current;
            
            // Set canvas dimensions to match video
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            // Draw current video frame to canvas
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);

            // Get frame data
            const frameData = canvas.toDataURL('image/jpeg');

            // Send to backend for object detection
            const result = await wsService.detectObjects(frameData);
            
            if (result.success) {
                setDetectedObject(result.objects[0]); // Get first detected object
                if (onCapture) {
                    onCapture(result);
                }
            } else {
                throw new Error(result.error || 'Object detection failed');
            }
        } catch (err) {
            setError('Error processing image');
            console.error('Capture error:', err);
        } finally {
            setIsProcessing(false);
        }
    };

    const handleRecording = async () => {
        if (isProcessing) return;

        try {
            if (!isRecording) {
                // Start recording
                setIsRecording(true);
                if (onRecordTerm) {
                    await onRecordTerm.start();
                }
            } else {
                // Stop recording
                setIsRecording(false);
                if (onRecordTerm) {
                    const result = await onRecordTerm.stop();
                    if (result.success) {
                        // Handle successful recording
                        console.log('Recording successful:', result.text);
                    }
                }
            }
        } catch (err) {
            setError('Error with recording');
            console.error('Recording error:', err);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="relative w-full h-full bg-black rounded-lg overflow-hidden">
            {/* Camera feed */}
            <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full h-full object-cover"
            />

            {/* Object detection overlay */}
            {detectedObject && (
                <div 
                    className="absolute border-2 border-green-500"
                    style={{
                        left: `${(detectedObject.bbox[0] / videoRef.current?.videoWidth) * 100}%`,
                        top: `${(detectedObject.bbox[1] / videoRef.current?.videoHeight) * 100}%`,
                        width: `${((detectedObject.bbox[2] - detectedObject.bbox[0]) / videoRef.current?.videoWidth) * 100}%`,
                        height: `${((detectedObject.bbox[3] - detectedObject.bbox[1]) / videoRef.current?.videoHeight) * 100}%`
                    }}
                />
            )}

            {/* Capture canvas (hidden) */}
            <canvas ref={canvasRef} className="hidden" />

            {/* Controls */}
            <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/50 to-transparent">
                <div className="flex justify-center space-x-4">
                    {/* Capture button */}
                    <Button
                        onClick={handleCapture}
                        disabled={isProcessing}
                        size="lg"
                        className="rounded-full"
                    >
                        <Camera className={isProcessing ? 'animate-pulse' : ''} />
                    </Button>

                    {/* Record button - only show when object is detected */}
                    {detectedObject && (
                        <Button
                            onClick={handleRecording}
                            disabled={isProcessing}
                            size="lg"
                            className={`rounded-full ${isRecording ? 'bg-red-500 hover:bg-red-600' : ''}`}
                        >
                            <Mic className={isRecording ? 'animate-pulse' : ''} />
                        </Button>
                    )}
                </div>

                {/* Error message */}
                {error && (
                    <div className="mt-4 p-2 bg-red-500/80 text-white rounded text-center">
                        {error}
                    </div>
                )}
            </div>
        </div>
    );
};

export default CameraView;