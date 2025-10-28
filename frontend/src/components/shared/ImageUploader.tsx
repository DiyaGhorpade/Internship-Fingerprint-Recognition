import { useState, useCallback } from "react";
import { Upload, Image as ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import Spinner from "./Spinner";

interface ImageUploaderProps {
  onAnalyze: (file: File) => void;
  isLoading: boolean;
  title: string;
  description: string;
}

const ImageUploader = ({ onAnalyze, isLoading, title, description }: ImageUploaderProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileSelect = useCallback((file: File) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
  };

  const handleAnalyzeClick = () => {
    if (selectedFile) {
      onAnalyze(selectedFile);
    }
  };

  return (
    <div className="space-y-4">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
          isDragging
            ? 'border-primary bg-primary/5 glow-primary'
            : 'border-border hover:border-primary/50'
        }`}
      >
        {previewUrl ? (
          <div className="space-y-4">
            <img
              src={previewUrl}
              alt="Preview"
              className="max-h-64 mx-auto rounded-lg border border-border"
            />
            <p className="text-sm text-muted-foreground">{selectedFile?.name}</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-center">
              <div className="p-4 bg-primary/10 rounded-full glow-primary">
                <Upload className="w-8 h-8 text-primary" />
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">{title}</h3>
              <p className="text-sm text-muted-foreground mb-4">{description}</p>
            </div>
            <div>
              <label htmlFor="file-input">
                <Button variant="outline" className="cursor-pointer" asChild>
                  <span>
                    <ImageIcon className="w-4 h-4 mr-2" />
                    Select Image
                  </span>
                </Button>
              </label>
              <input
                id="file-input"
                type="file"
                accept="image/*"
                onChange={handleInputChange}
                className="hidden"
              />
            </div>
            <p className="text-xs text-muted-foreground">
              or drag and drop an image here
            </p>
          </div>
        )}
      </div>

      {selectedFile && (
        <Button
          onClick={handleAnalyzeClick}
          disabled={isLoading}
          className="w-full glow-hover"
          size="lg"
        >
          {isLoading ? (
            <>
              <Spinner />
              <span className="ml-2">Analyzing...</span>
            </>
          ) : (
            'Analyze Image'
          )}
        </Button>
      )}
    </div>
  );
};

export default ImageUploader;
