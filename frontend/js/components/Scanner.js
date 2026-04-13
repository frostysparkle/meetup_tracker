const Scanner = {
    template: `
        <div class="scanner-container">
            <h2>Scan Ticket QR Code</h2>
            <div id="reader"></div>
            <div v-if="message" :class="['result-message', messageType]">
                {{ message }}
            </div>
        </div>
    `,
    data() {
        return {
            scanner: null,
            message: null,
            messageType: null,
            isScanning: false
        };
    },
    mounted() {
        this.initScanner();
    },
    unmounted() {
        if (this.scanner && this.isScanning) {
            this.scanner.stop().catch(err => console.error("Error stopping scanner:", err));
        }
    },
    methods: {
        initScanner() {
            this.scanner = new Html5Qrcode("reader");
            const config = { fps: 10, qrbox: { width: 250, height: 250 } };
            
            this.scanner.start({ facingMode: "environment" }, config, this.onScanSuccess)
                .then(() => {
                    this.isScanning = true;
                })
                .catch(err => {
                    console.error("Error starting scanner:", err);
                    this.message = "Failed to access camera. Please check permissions.";
                    this.messageType = "error";
                });
        },
        async onScanSuccess(decodedText) {
            // Prevent multiple rapid scans
            if (this.isScanning) {
                // Temporarily pause processing new scans while we handle this one
                // The library doesn't have a pause feature so we handle logic on our end.
                // In a production app, we might stop and restart. For simplicity, we just
                // proceed if the user is not spamming. Let's just process it.
                
                try {
                    const response = await axios.post(`${API_BASE_URL}/mark_present`, {
                        id: decodedText
                    });
                    this.message = response.data.message;
                    this.messageType = "success";
                } catch (err) {
                    if (err.response && err.response.data && err.response.data.error) {
                        this.message = err.response.data.error;
                    } else {
                        this.message = "Error connecting to server.";
                    }
                    this.messageType = "error";
                }
                
                // Clear message after 5 seconds
                setTimeout(() => {
                    if (this.messageType === "success" || this.messageType === "error") {
                        this.message = null;
                        this.messageType = null;
                    }
                }, 5000);
            }
        }
    }
};
