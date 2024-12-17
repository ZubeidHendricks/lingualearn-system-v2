const { app, BrowserWindow, session } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

function createWindow() {
    // Create the browser window.
    const mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            worldSafeExecuteJavaScript: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    // Set up proper Content Security Policy
    session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
        callback({
            responseHeaders: {
                ...details.responseHeaders,
                'Content-Security-Policy': [
                    `default-src 'self';
                    script-src 'self';
                    style-src 'self' 'unsafe-inline';
                    img-src 'self' data:;
                    connect-src 'self' http://localhost:* ws://localhost:*;
                    font-src 'self';
                    media-src 'self';`
                ]
            }
        });
    });

    // Load the app
    if (isDev) {
        mainWindow.loadURL('http://localhost:3000');
        // Open DevTools in development mode
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, '../build/index.html'));
    }

    // Handle closing event
    mainWindow.on('closed', () => {
        app.quit();
    });
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
app.whenReady().then(createWindow);

// Quit when all windows are closed.
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('An uncaught error occurred:', error);
});
