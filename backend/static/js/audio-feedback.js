/**
 * Audio Feedback for Warehouse Operations
 *
 * Plays success/error sounds during barcode scanning workflow.
 * Uses Web Audio API for low-latency playback.
 */

class AudioFeedback {
    constructor() {
        this._context = null;
        this._buffers = {};
        this._loaded = false;
    }

    async init() {
        if (this._loaded) return;

        this._context = new (window.AudioContext || window.webkitAudioContext)();

        try {
            const [successBuffer, errorBuffer] = await Promise.all([
                this._loadSound('/static/sounds/scan-success.mp3'),
                this._loadSound('/static/sounds/scan-error.mp3'),
            ]);
            this._buffers.success = successBuffer;
            this._buffers.error = errorBuffer;
            this._loaded = true;
        } catch (err) {
            console.warn('Audio feedback: Could not load sound files', err);
        }
    }

    async _loadSound(url) {
        const response = await fetch(url);
        const arrayBuffer = await response.arrayBuffer();
        return await this._context.decodeAudioData(arrayBuffer);
    }

    play(type) {
        if (!this._loaded || !this._buffers[type]) return;

        // Resume context if suspended (browser autoplay policy)
        if (this._context.state === 'suspended') {
            this._context.resume();
        }

        const source = this._context.createBufferSource();
        source.buffer = this._buffers[type];
        source.connect(this._context.destination);
        source.start(0);
    }

    playSuccess() {
        this.play('success');
    }

    playError() {
        this.play('error');
    }
}

// Export for use in templates
window.AudioFeedback = AudioFeedback;
