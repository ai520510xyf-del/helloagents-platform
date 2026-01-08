/**
 * 测试工具函数
 */
import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'

/**
 * 自定义渲染函数
 * 可以添加全局 Provider（如 Router, Theme 等）
 */
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { ...options })
}

/**
 * 等待异步操作
 */
export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * 模拟 API 响应
 */
export function mockApiResponse<T>(data: T, delay = 100): Promise<T> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(data), delay)
  })
}

/**
 * 模拟 API 错误
 */
export function mockApiError(message: string, delay = 100): Promise<never> {
  return new Promise((_, reject) => {
    setTimeout(() => reject(new Error(message)), delay)
  })
}
