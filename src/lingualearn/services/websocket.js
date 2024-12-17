class WebSocketService {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket('ws://localhost:8000/ws');

                this.ws.onopen = () => {
                    console.log('WebSocket connected');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    resolve();
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    reject(error);
                };

                this.ws.onclose = () => {
                    console.log('WebSocket closed');
                    this.isConnected = false;
                    this._attemptReconnect();
                };

            } catch (error) {
                console.error('WebSocket connection error:', error);
                reject(error);
            }
        });
    }

    async _attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            try {
                await this.connect();
            } catch (error) {
                console.error('Reconnection failed:', error);
                setTimeout(() => this._attemptReconnect(), 2000);
            }
        }
    }

    async detectObjects(imageData) {
        if (!this.isConnected) {
            throw new Error('WebSocket not connected');
        }

        return new Promise((resolve, reject) => {
            const messageHandler = (event) => {
                const response = JSON.parse(event.data);
                this.ws.removeEventListener('message', messageHandler);
                resolve(response);
            };

            this.ws.addEventListener('message', messageHandler);

            this.ws.send(JSON.stringify({
                type: 'detect',
                image: imageData
            }));
        });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

export const wsService = new WebSocketService();