/**
 * useResponsiveLayout Hook
 * 检测屏幕尺寸并返回当前布局类型
 *
 * 布局断点（简化为2种）：
 * - mobile: <= 768px - 使用移动端单栏布局
 * - desktop: > 768px - 使用桌面端两栏布局
 */

import { useState, useEffect } from 'react';

export type LayoutType = 'mobile' | 'desktop';

export interface ResponsiveLayout {
  layoutType: LayoutType;
  isMobile: boolean;
  isDesktop: boolean;
  screenWidth: number;
  screenHeight: number;
  isLandscape: boolean;
  isPortrait: boolean;
}

const MOBILE_BREAKPOINT = 768;

function getLayoutType(width: number): LayoutType {
  return width <= MOBILE_BREAKPOINT ? 'mobile' : 'desktop';
}

export function useResponsiveLayout(): ResponsiveLayout {
  const [screenWidth, setScreenWidth] = useState(window.innerWidth);
  const [screenHeight, setScreenHeight] = useState(window.innerHeight);

  useEffect(() => {
    // 防抖处理，避免频繁触发
    let timeoutId: number;

    const handleResize = () => {
      clearTimeout(timeoutId);
      timeoutId = window.setTimeout(() => {
        setScreenWidth(window.innerWidth);
        setScreenHeight(window.innerHeight);
      }, 150);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const isLandscape = screenWidth > screenHeight;
  const isPortrait = screenHeight >= screenWidth;
  const layoutType = getLayoutType(screenWidth);

  return {
    layoutType,
    isMobile: layoutType === 'mobile',
    isDesktop: layoutType === 'desktop',
    screenWidth,
    screenHeight,
    isLandscape,
    isPortrait,
  };
}
