/**
 * OptimizedImage 组件
 *
 * 性能优化的图片组件:
 * - 支持响应式图片 (srcSet + sizes)
 * - 支持现代图片格式 (WebP, AVIF)
 * - 支持懒加载 (Intersection Observer)
 * - 支持占位符和渐进式加载
 * - 支持加载优先级 (fetchpriority)
 */

import { useState, useEffect, useRef } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  loading?: 'lazy' | 'eager';
  priority?: boolean;
  sizes?: string;
  quality?: number;
  placeholder?: 'blur' | 'empty';
  blurDataURL?: string;
  onLoad?: () => void;
  onError?: () => void;
}

/**
 * 生成响应式图片 srcSet
 */
function generateSrcSet(src: string, widths: number[] = [640, 750, 828, 1080, 1200, 1920, 2048]): string {
  // 如果是外部 CDN 链接，直接返回
  if (src.startsWith('http')) {
    return src;
  }

  // 生成不同尺寸的图片 URL
  const srcSet = widths
    .map((width) => {
      const url = src.replace(/\.(jpg|jpeg|png|webp)$/i, `-${width}.$1`);
      return `${url} ${width}w`;
    })
    .join(', ');

  return srcSet;
}

/**
 * 生成 WebP/AVIF 格式的图片 URL
 */
function generateWebPUrl(src: string): string {
  if (src.startsWith('http')) {
    return src;
  }
  return src.replace(/\.(jpg|jpeg|png)$/i, '.webp');
}

function generateAVIFUrl(src: string): string {
  if (src.startsWith('http')) {
    return src;
  }
  return src.replace(/\.(jpg|jpeg|png)$/i, '.avif');
}

/**
 * OptimizedImage 组件
 */
export function OptimizedImage({
  src,
  alt,
  width,
  height,
  className = '',
  loading = 'lazy',
  priority = false,
  sizes = '100vw',
  placeholder = 'empty',
  blurDataURL,
  onLoad,
  onError,
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(priority || loading === 'eager');
  const imgRef = useRef<HTMLImageElement>(null);

  // 使用 Intersection Observer 实现懒加载
  useEffect(() => {
    if (priority || loading === 'eager' || !imgRef.current) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.disconnect();
          }
        });
      },
      {
        rootMargin: '50px', // 提前 50px 开始加载
      }
    );

    observer.observe(imgRef.current);

    return () => observer.disconnect();
  }, [priority, loading]);

  // 处理图片加载完成
  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  // 处理图片加载失败
  const handleError = () => {
    onError?.();
  };

  // 占位符样式
  const placeholderStyle = placeholder === 'blur' && blurDataURL
    ? {
        backgroundImage: `url(${blurDataURL})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }
    : {};

  // 容器样式（保持宽高比，避免 CLS）
  const aspectRatio = width && height ? `${width} / ${height}` : undefined;

  return (
    <div
      className={`relative overflow-hidden ${className}`}
      style={{
        aspectRatio,
        ...placeholderStyle,
      }}
    >
      {isInView ? (
        <picture>
          {/* AVIF - 最新最小的格式 */}
          <source
            type="image/avif"
            srcSet={generateSrcSet(generateAVIFUrl(src))}
            sizes={sizes}
          />

          {/* WebP - 广泛支持的现代格式 */}
          <source
            type="image/webp"
            srcSet={generateSrcSet(generateWebPUrl(src))}
            sizes={sizes}
          />

          {/* 原始格式 - 降级方案 */}
          <img
            ref={imgRef}
            src={src}
            srcSet={generateSrcSet(src)}
            sizes={sizes}
            alt={alt}
            width={width}
            height={height}
            loading={loading}
            decoding="async"
            fetchPriority={priority ? 'high' : 'auto'}
            onLoad={handleLoad}
            onError={handleError}
            className={`
              w-full h-full object-cover transition-opacity duration-300
              ${isLoaded ? 'opacity-100' : 'opacity-0'}
            `}
          />
        </picture>
      ) : (
        // 占位符
        <div
          className="w-full h-full bg-gray-200 animate-pulse"
          style={placeholderStyle}
        />
      )}

      {/* 加载指示器 */}
      {!isLoaded && isInView && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-gray-300 border-t-blue-500 rounded-full animate-spin" />
        </div>
      )}
    </div>
  );
}

/**
 * useImagePreload Hook
 * 预加载图片
 */
export function useImagePreload(src: string) {
  const [isPreloaded, setIsPreloaded] = useState(false);

  useEffect(() => {
    const img = new Image();
    img.src = src;

    img.onload = () => setIsPreloaded(true);
    img.onerror = () => setIsPreloaded(false);
  }, [src]);

  return isPreloaded;
}

/**
 * preloadImages 函数
 * 批量预加载图片
 */
export function preloadImages(urls: string[]): Promise<void[]> {
  return Promise.all(
    urls.map((url) => {
      return new Promise<void>((resolve, reject) => {
        const img = new Image();
        img.src = url;
        img.onload = () => resolve();
        img.onerror = () => reject(new Error(`Failed to load image: ${url}`));
      });
    })
  );
}
