import React, { useState, useRef } from 'react';

interface ScanStatus {
  state: 'idle' | 'recording' | 'processing' | 'completed' | 'error';
  message: string;
}

export const VideoInventoryScanner: React.FC = () => {
  const [status, setStatus] = useState<ScanStatus>({ state: 'idle', message: 'Scanner ready.' });
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const startWalkthroughCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }

      const recorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
      const chunks: BlobPart[] = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunks.push(event.data);
      };

      recorder.onstop = () => {
        const fullBlob = new Blob(chunks, { type: 'video/webm' });
        setRecordedBlob(fullBlob);
        setStatus({ state: 'idle', message: 'Capture complete. Ready to ingest into DuckDB vault.' });
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setStatus({ state: 'recording', message: 'Recording warehouse floor plan and inventory...' });
    } catch (err) {
      setStatus({ state: 'error', message: 'Camera permission denied or device unconfigured.' });
    }
  };

  const stopWalkthroughCapture = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
    }
  };

  const transmitToCloudVault = async () => {
    if (!recordedBlob) return;
    setStatus({ state: 'processing', message: 'Streaming video to Vertex AI Multimodal Ingress...' });

    const formData = new FormData();
    formData.append('walkthrough_video', recordedBlob, 'inventory_walkthrough.webm');

    try {
      const response = await fetch('/api/inventory/multimodal-video-ingest', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Ingestion pipeline returned fault.');
      const result = await response.json();
      setStatus({
        state: 'completed',
        message: 'Inventory cataloged successfully: ' + result.items_cataloged + ' items parsed.',
      });
    } catch (error) {
      setStatus({ state: 'error', message: 'Telemetry transmission failed. Checked local queue.' });
    }
  };

  return (
    <div className="p-6 bg-slate-950 text-amber-50 rounded-xl border border-amber-500/20 shadow-2xl max-w-xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold tracking-wide">Optical Inventory Walk-Through</h2>
        <span className="text-xs px-2 py-1 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
          Pillar III & Pillar VII Telemetry
        </span>
      </div>

      <div className="relative aspect-video bg-black rounded-lg overflow-hidden border border-slate-800 mb-4 flex items-center justify-center">
        <video ref={videoRef} className="w-full h-full object-cover" muted playsInline />
        {status.state !== 'recording' && !recordedBlob && (
          <p className="absolute text-slate-500 text-sm">Camera standby mode</p>
        )}
      </div>

      <div className="flex gap-3 mb-4">
        {status.state !== 'recording' ? (
          <button
            onClick={startWalkthroughCapture}
            className="flex-1 bg-amber-500 hover:bg-amber-600 text-black font-semibold py-2 px-4 rounded transition-all"
          >
            Start Optical Scan
          </button>
        ) : (
          <button
            onClick={stopWalkthroughCapture}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded animate-pulse"
          >
            Stop Capture
          </button>
        )}

        {recordedBlob && status.state !== 'processing' && (
          <button
            onClick={transmitToCloudVault}
            className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2 px-4 rounded transition-all"
          >
            Commit to Vault
          </button>
        )}
      </div>

      <div className="text-xs font-mono bg-slate-900 p-3 rounded border border-slate-800 text-slate-300">
        Status: {status.message}
      </div>
    </div>
  );
};
