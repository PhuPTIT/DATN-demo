// components/PagePreview.tsx
import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AlertCircle, Download, Loader2 } from 'lucide-react';

interface PagePreviewProps {
  url: string;
}

const PagePreview: React.FC<PagePreviewProps> = ({ url }) => {
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const captureScreenshot = async () => {
    if (!url) {
      setError('Please enter a valid URL');
      return;
    }

    setLoading(true);
    setError(null);
    setScreenshot(null);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8002';
      
      // Call backend API to capture screenshot
      const response = await fetch(`${apiUrl}/api/capture_screenshot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error(`Failed to capture screenshot: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.screenshot) {
        // Convert base64 to data URL if needed
        const imageData = data.screenshot.startsWith('data:') 
          ? data.screenshot 
          : `data:image/png;base64,${data.screenshot}`;
        setScreenshot(imageData);
      } else {
        throw new Error('No screenshot data received');
      }
    } catch (error) {
      console.error('Error capturing screenshot:', error);
      setError(error instanceof Error ? error.message : 'Failed to capture screenshot');
    } finally {
      setLoading(false);
    }
  };

  // Auto-capture when URL changes
  useEffect(() => {
    const timer = setTimeout(() => {
      if (url) {
        captureScreenshot();
      }
    }, 500); // Debounce to avoid too many requests

    return () => clearTimeout(timer);
  }, [url]);

  const downloadScreenshot = () => {
    if (!screenshot) return;
    
    const link = document.createElement('a');
    link.download = `preview-${new Date().toISOString().slice(0, 10)}.png`;
    link.href = screenshot;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Button
          onClick={captureScreenshot}
          disabled={loading || !url}
          className="gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Capturing...
            </>
          ) : (
            'Capture Preview'
          )}
        </Button>

        {screenshot && (
          <Button
            onClick={downloadScreenshot}
            variant="outline"
            className="gap-2"
          >
            <Download className="w-4 h-4" />
            Download
          </Button>
        )}
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {screenshot && (
        <div className="space-y-2">
          <h3 className="font-semibold">Preview:</h3>
          <img
            src={screenshot}
            alt="Website preview"
            className="w-full border rounded-lg"
          />
        </div>
      )}

      {loading && (
        <div className="flex justify-center py-8">
          <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
        </div>
      )}
    </div>
  );
};

export default PagePreview;