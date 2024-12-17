class WebSocketService {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectTimeout = null;
        this.messageQueue = [];
    }

    connect() {
        return new Promise((resolve, reject) => {
            try {
                console.log('Attempting to connect to WebSocket...');
                this.ws = new WebSocket('ws://127.0.0.1:8000/ws');

                this.ws.onopen = () => {
                    console.log('WebSocket connected successfully');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this._processQueue();
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    console.log('Received message:', data);
                    if (data.type === 'error') {
                        console.error('Server error:', data.message);
                    }
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    if (!this.isConnected) {
                        reject(error);
                    }
                };

                this.ws.onclose = () => {
                    console.log('WebSocket connection closed');
                    this.isConnected = false;
                    this._attemptReconnect();
                };

            } catch (error) {
                console.error('WebSocket setup error:', error);
                reject(error);
            }
        });
    }

    async _attemptReconnect() {
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
        }

        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            this.reconnectTimeout = setTimeout(async () => {
                try {
                    await this.connect();
                } catch (error) {
                    console.error('Reconnection failed:', error);
                    this._attemptReconnect();
                }
            }, 2000 * Math.pow(2, this.reconnectAttempts - 1)); // Exponential backoff
        }
    }

    async detectObjects(imageData) {
        if (!this.ws || !this.isConnected) {
            console.log('WebSocket not connected, queueing message...');
            return new Promise((resolve, reject) => {
                this.messageQueue.push({
                    type: 'detect',
                    data: imageData,
                    resolve,
                    reject
                });
            });
        }

        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Detection timeout'));
            }, 30000); // 30 second timeout

            const messageHandler = (event) => {
                clearTimeout(timeout);
                this.ws.removeEventListener('message', messageHandler);
                try {
                    const response = JSON.parse(event.data);
                    resolve(response);
                } catch (error) {
                    reject(error);
                }
            };

            this.ws.addEventListener('message', messageHandler);

            try {
                this.ws.send(JSON.stringify({
                    type: 'detect',
                    image: imageData
                }));
            } catch (error) {
                clearTimeout(timeout);
                this.ws.removeEventListener('message', messageHandler);
                reject(error);
            }
        });
    }

    async _processQueue() {
        while (this.messageQueue.length > 0 && this.isConnected) {
            const { type, data, resolve, reject } = this.messageQueue.shift();
            try {
                if (type === 'detect') {
                    const result = await this.detectObjects(data);
                    resolve(result);
                }
            } catch (error) {
                reject(error);
            }
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
        }
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.messageQueue = [];
    }
}

export const wsService = new WebSocketService();