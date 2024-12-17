const { contextBridge, ipcRenderer } = require('electron');
const WebSocket = require('ws');

// API exposed to renderer process
contextBridge.exposeInMainWorld('api', {
    // Media devices
    getMediaDevices: () => ipcRenderer.invoke('get-media-devices'),
    getCameraPermissions: () => ipcRenderer.invoke('get-camera-permissions'),
    getAudioPermissions: () => ipcRenderer.invoke('get-audio-permissions'),

    // Object detection
    detectObject: async (data) => {
        try {
            const response = await fetch('http://localhost:8000/detect-object', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            return response.json();
        } catch (error) {
            console.error('Failed to detect object:', error);
            throw error;
        }
    },

    // Voice recording
    recordTerm: async (data) => {
        try {
            const response = await fetch('http://localhost:8000/record-term', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            return response.json();
        } catch (error) {
            console.error('Failed to record term:', error);
            throw error;
        }
    },

    // Term management
    saveTerm: async (data) => {
        try {
            const response = await fetch('http://localhost:8000/save-term', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            return response.json();
        } catch (error) {
            console.error('Failed to save term:', error);
            throw error;
        }
    },

    getStoredTerms: async (language) => {
        try {
            const response = await fetch(`http://localhost:8000/terms/${language}`);
            return response.json();
        } catch (error) {
            console.error('Failed to get terms:', error);
            throw error;
        }
    },

    // WebSocket connection
    connectWebSocket: (callbacks) => {
        const ws = new WebSocket('ws://localhost:8000/ws');

        ws.onopen = () => {
            callbacks.onOpen?.();
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            callbacks.onMessage?.(data);
        };

        ws.onerror = (error) => {
            callbacks.onError?.(error);
        };

        ws.onclose = () => {
            callbacks.onClose?.();
        };

        return {
            send: (message) => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify(message));
                }
            },
            close: () => ws.close()
        };
    }
});

// Listen for backend process status
ipcRenderer.on('python-output', (event, data) => {
    console.log('Python output:', data);
});

ipcRenderer.on('python-error', (event, data) => {
    console.error('Python error:', data);
});
