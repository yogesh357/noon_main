/**
 * Barcode Scanner Detection
 *
 * USB/Bluetooth barcode scanners emulate keyboard input with rapid keystrokes
 * followed by Enter. This module detects scanner input vs normal typing by
 * measuring the speed of character input.
 *
 * Scanner: characters arrive < 50ms apart
 * Human typing: characters arrive > 50ms apart
 */

class BarcodeScanner {
    constructor(options = {}) {
        this.minLength = options.minLength || 4;
        this.maxDelay = options.maxDelay || 50; // ms between keystrokes
        this.onScan = options.onScan || (() => {});
        this.onError = options.onError || (() => {});

        this._buffer = '';
        this._lastKeyTime = 0;
        this._listening = false;
    }

    start() {
        if (this._listening) return;
        this._listening = true;
        this._handler = this._handleKeyDown.bind(this);
        document.addEventListener('keydown', this._handler);
    }

    stop() {
        this._listening = false;
        document.removeEventListener('keydown', this._handler);
    }

    _handleKeyDown(event) {
        const now = Date.now();
        const timeDiff = now - this._lastKeyTime;

        if (event.key === 'Enter') {
            if (this._buffer.length >= this.minLength) {
                event.preventDefault();
                this.onScan(this._buffer);
            }
            this._buffer = '';
            this._lastKeyTime = 0;
            return;
        }

        // Only accept printable characters
        if (event.key.length !== 1) return;

        // If too slow, reset buffer (human typing)
        if (timeDiff > this.maxDelay && this._buffer.length > 0) {
            this._buffer = '';
        }

        this._buffer += event.key;
        this._lastKeyTime = now;
    }
}

// Export for use in templates
window.BarcodeScanner = BarcodeScanner;
