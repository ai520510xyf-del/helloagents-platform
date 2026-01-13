/**
 * ImageUpload 组件
 * 支持图片上传、预览和删除
 */

import { useRef, useState, useCallback } from 'react';
import { Image as ImageIcon, X, Upload } from 'lucide-react';

interface UploadedImage {
  id: string;
  name: string;
  size: number;
  base64: string;
  preview: string;
}

interface ImageUploadProps {
  images: UploadedImage[];
  onImagesChange: (images: UploadedImage[]) => void;
  theme: 'light' | 'dark';
  maxSizeMB?: number;
  maxImages?: number;
  disabled?: boolean;
}

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE_MB = 5;

export function ImageUpload({
  images,
  onImagesChange,
  theme,
  maxSizeMB = MAX_SIZE_MB,
  maxImages = 5,
  disabled = false,
}: ImageUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 压缩图片
  const compressImage = useCallback((file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement('canvas');
          let width = img.width;
          let height = img.height;

          // 如果图片太大，等比例缩放
          const MAX_WIDTH = 1920;
          const MAX_HEIGHT = 1080;

          if (width > MAX_WIDTH || height > MAX_HEIGHT) {
            const ratio = Math.min(MAX_WIDTH / width, MAX_HEIGHT / height);
            width = width * ratio;
            height = height * ratio;
          }

          canvas.width = width;
          canvas.height = height;

          const ctx = canvas.getContext('2d');
          if (!ctx) {
            reject(new Error('无法创建canvas上下文'));
            return;
          }

          ctx.drawImage(img, 0, 0, width, height);

          // 转换为 base64，使用 0.8 的质量压缩
          const base64 = canvas.toDataURL(file.type, 0.8);
          resolve(base64);
        };

        img.onerror = () => reject(new Error('图片加载失败'));
        img.src = e.target?.result as string;
      };

      reader.onerror = () => reject(new Error('文件读取失败'));
      reader.readAsDataURL(file);
    });
  }, []);

  // 处理文件选择
  const handleFiles = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setError(null);

    // 检查数量限制
    if (images.length + files.length > maxImages) {
      setError(`最多只能上传 ${maxImages} 张图片`);
      return;
    }

    const newImages: UploadedImage[] = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      // 检查文件类型
      if (!ALLOWED_TYPES.includes(file.type)) {
        setError(`不支持的文件格式：${file.name}`);
        continue;
      }

      // 检查文件大小
      if (file.size > maxSizeMB * 1024 * 1024) {
        setError(`文件太大：${file.name} (最大 ${maxSizeMB}MB)`);
        continue;
      }

      try {
        const base64 = await compressImage(file);

        newImages.push({
          id: `${Date.now()}_${i}`,
          name: file.name,
          size: file.size,
          base64,
          preview: base64,
        });
      } catch (err) {
        setError(`处理失败：${file.name}`);
      }
    }

    if (newImages.length > 0) {
      onImagesChange([...images, ...newImages]);
    }
  }, [images, maxImages, maxSizeMB, onImagesChange, compressImage]);

  // 删除图片
  const removeImage = useCallback((id: string) => {
    onImagesChange(images.filter(img => img.id !== id));
    setError(null);
  }, [images, onImagesChange]);

  // 点击上传
  const handleClick = () => {
    if (disabled) return;
    fileInputRef.current?.click();
  };

  // 拖拽事件
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (!disabled) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="space-y-2">
      {/* 上传按钮 */}
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled || images.length >= maxImages}
        className={`p-2 rounded transition-colors ${
          disabled || images.length >= maxImages
            ? theme === 'dark'
              ? 'text-text-muted cursor-not-allowed'
              : 'text-gray-400 cursor-not-allowed'
            : theme === 'dark'
            ? 'text-text-secondary hover:text-primary hover:bg-bg-elevated'
            : 'text-gray-600 hover:text-primary hover:bg-gray-100'
        }`}
        title={images.length >= maxImages ? `最多 ${maxImages} 张图片` : '上传图片'}
        aria-label="上传图片"
      >
        <ImageIcon className="h-5 w-5" />
      </button>

      {/* 隐藏的文件输入 */}
      <input
        ref={fileInputRef}
        type="file"
        accept={ALLOWED_TYPES.join(',')}
        multiple
        onChange={(e) => handleFiles(e.target.files)}
        className="hidden"
        disabled={disabled}
      />

      {/* 拖拽区域（仅在没有图片时显示） */}
      {images.length === 0 && !disabled && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClick}
          className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
            isDragging
              ? theme === 'dark'
                ? 'border-primary bg-primary/5'
                : 'border-primary bg-primary/5'
              : theme === 'dark'
              ? 'border-border hover:border-primary/50'
              : 'border-gray-300 hover:border-primary/50'
          }`}
        >
          <Upload className={`h-8 w-8 mx-auto mb-2 ${theme === 'dark' ? 'text-text-muted' : 'text-gray-400'}`} />
          <p className={`text-sm ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}>
            点击或拖拽上传图片
          </p>
          <p className={`text-xs mt-1 ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
            支持 JPG, PNG, WebP，最大 {maxSizeMB}MB
          </p>
        </div>
      )}

      {/* 图片预览列表 */}
      {images.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {images.map((image) => (
            <div
              key={image.id}
              className={`relative group rounded-lg overflow-hidden border ${
                theme === 'dark' ? 'border-border' : 'border-gray-200'
              }`}
            >
              <img
                src={image.preview}
                alt={image.name}
                className="w-16 h-16 object-cover"
              />
              {/* 删除按钮 */}
              <button
                type="button"
                onClick={() => removeImage(image.id)}
                disabled={disabled}
                className={`absolute top-1 right-1 p-1 rounded-full transition-opacity ${
                  disabled
                    ? 'opacity-0 cursor-not-allowed'
                    : 'bg-black/50 text-white opacity-0 group-hover:opacity-100 hover:bg-black/70'
                }`}
                title="删除"
                aria-label={`删除 ${image.name}`}
              >
                <X className="h-3 w-3" />
              </button>
              {/* 文件信息 */}
              <div
                className={`absolute bottom-0 left-0 right-0 px-1 py-0.5 text-xs truncate transition-opacity opacity-0 group-hover:opacity-100 ${
                  theme === 'dark' ? 'bg-black/70 text-white' : 'bg-black/70 text-white'
                }`}
                title={`${image.name} (${formatFileSize(image.size)})`}
              >
                {formatFileSize(image.size)}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 错误提示 */}
      {error && (
        <p className="text-xs text-red-500">
          {error}
        </p>
      )}

      {/* 提示信息 */}
      {images.length > 0 && (
        <p className={`text-xs ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
          {images.length}/{maxImages} 张图片
          {images.length > 0 && ' • 图片已上传，但当前AI模型暂不支持图片分析'}
        </p>
      )}
    </div>
  );
}

export type { UploadedImage };
