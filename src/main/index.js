const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = require('electron-is-dev');

let mainWindow;
let pythonProcess;

function createWindow() {
    // Create the browser window
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    // Load the app
    if (isDev) {
        mainWindow.loadURL('http://localhost:3000');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, '../build/index.html'));
    }

    // Start Python backend
    startPythonBackend();
}

function startPythonBackend() {
    const pythonScript = isDev ?
        path.join(__dirname, '../lingualearn/api/bridge.py') :
        path.join(process.resourcesPath, 'backend/bridge.py');

    pythonProcess = spawn('python', [pythonScript]);

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python stdout: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python stderr: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
    });
}

// Handle app lifecycle
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
    // Kill Python process
    if (pythonProcess) {
        pythonProcess.kill();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// IPC Communication
ipcMain.handle('get-media-devices', async () => {
    try {
        const devices = await mainWindow.webContents.executeJavaScript(
            `navigator.mediaDevices.enumerateDevices()`
        );
        return devices;
    } catch (error) {
        console.error('Failed to get media devices:', error);
        throw error;
    }
});

ipcMain.handle('get-camera-permissions', async () => {
    try {
        const result = await mainWindow.webContents.executeJavaScript(`
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(() => true)
                .catch(() => false)
        `);
        return result;
    } catch (error) {
        console.error('Failed to get camera permissions:', error);
        return false;
    }
});

ipcMain.handle('get-audio-permissions', async () => {
    try {
        const result = await mainWindow.webContents.executeJavaScript(`
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(() => true)
                .catch(() => false)
        `);
        return result;
    } catch (error) {
        console.error('Failed to get audio permissions:', error);
        return false;
    }
});