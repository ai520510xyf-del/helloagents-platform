/**
 * useResponsiveLayout Hook
 * 检测屏幕尺寸并返回当前布局类型
 *
 * 布局断点：
 * - mobile: < 768px
 * - tablet: 768px - 1024px
 * - desktop: > 1024px
 */

import { useState, useEffect } from 'react';

export type LayoutType = 'mobile' | 'tablet' | 'desktop';

export interface ResponsiveLayout {
  layoutType: LayoutType;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  screenWidth: number;
  screenHeight: number;
  isLandscape: boolean;
  isPortrait: boolean;
}

const BREAKPOINTS = {
  mobile: 768,
  tablet: 1024,
} as const;

function getLayoutType(width: number, _height: number, isLandscape: boolean): LayoutType {
  // 横屏模式下，如果是小屏幕（手机），自动切换到平板布局
  if (isLandscape && width < BREAKPOINTS.tablet && width > BREAKPOINTS.mobile - 1) {
    return 'tablet';
  }

  if (width < BREAKPOINTS.mobile) return 'mobile';
  if (width < BREAKPOINTS.tablet) return 'tablet';
  return 'desktop';
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
  const layoutType = getLayoutType(screenWidth, screenHeight, isLandscape);

  return {
    layoutType,
    isMobile: layoutType === 'mobile',
    isTablet: layoutType === 'tablet',
    isDesktop: layoutType === 'desktop',
    screenWidth,
    screenHeight,
    isLandscape,
    isPortrait,
  };
}
