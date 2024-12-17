const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// specific electron APIs through a secure bridge.
contextBridge.exposeInMainWorld(
    'api', {
        // Camera methods
        requestCamera: () => ipcRenderer.invoke('request-camera'),
        stopCamera: () => ipcRenderer.invoke('stop-camera'),

        // Audio methods
        requestMicrophone: () => ipcRenderer.invoke('request-microphone'),
        startRecording: () => ipcRenderer.invoke('start-recording'),
        stopRecording: () => ipcRenderer.invoke('stop-recording'),

        // File system methods
        saveData: (data) => ipcRenderer.invoke('save-data', data),
        loadData: () => ipcRenderer.invoke('load-data'),

        // System methods
        getVersion: () => ipcRenderer.invoke('get-version'),
        getLanguages: () => ipcRenderer.invoke('get-languages'),

        // Event listeners
        on: (channel, callback) => {
            // Whitelist channels we allow
            const validChannels = [
                'camera-frame',
                'recording-data',
                'object-detected',
                'term-saved',
                'error'
            ];
            if (validChannels.includes(channel)) {
                ipcRenderer.on(channel, (event, ...args) => callback(...args));
            }
        },
        off: (channel, callback) => {
            const validChannels = [
                'camera-frame',
                'recording-data',
                'object-detected',
                'term-saved',
                'error'
            ];
            if (validChannels.includes(channel)) {
                ipcRenderer.removeListener(channel, callback);
            }
        }
    }
);