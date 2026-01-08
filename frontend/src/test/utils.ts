/**
 * 测试工具函数
 */
import { ReactElement } from 'react'
import { render, RenderOptions, screen, within, waitFor as rtlWaitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from './mocks/server'

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
 * 设置用户事件（推荐方式）
 * @returns userEvent 实例
 */
export function setupUser() {
  return userEvent.setup()
}

/**
 * Mock 特定的 API 端点（运行时覆盖）
 * 用于在测试中动态修改 API 响应
 */
export function mockApiEndpoint(
  method: 'get' | 'post' | 'put' | 'delete' | 'patch',
  url: string,
  response: any,
  statusCode = 200
) {
  const handler = http[method](url, () => {
    if (statusCode >= 200 && statusCode < 300) {
      return HttpResponse.json(response, { status: statusCode })
    }
    return HttpResponse.json(response, { status: statusCode })
  })

  server.use(handler)
}

/**
 * Mock API 错误响应
 */
export function mockApiError(
  method: 'get' | 'post' | 'put' | 'delete' | 'patch',
  url: string,
  errorMessage: string,
  statusCode = 500
) {
  mockApiEndpoint(method, url, { detail: errorMessage }, statusCode)
}

/**
 * 查询辅助函数：通过 data-testid 查找元素
 */
export function getByTestId(testId: string) {
  return screen.getByTestId(testId)
}

/**
 * 查询辅助函数：通过 role 查找元素
 */
export function getByRole(role: string, options?: any) {
  return screen.getByRole(role, options)
}

/**
 * 等待元素出现
 */
export async function waitForElement(callback: () => HTMLElement, timeout = 3000) {
  return rtlWaitFor(callback, { timeout })
}

/**
 * 等待元素消失
 */
export async function waitForElementToBeRemoved(callback: () => HTMLElement, timeout = 3000) {
  return rtlWaitFor(() => {
    const element = callback()
    if (element) {
      throw new Error('Element still exists')
    }
  }, { timeout })
}

/**
 * 模拟输入框输入
 */
export async function typeIntoInput(input: HTMLElement, text: string) {
  const user = setupUser()
  await user.clear(input)
  await user.type(input, text)
}

/**
 * 模拟按钮点击
 */
export async function clickButton(button: HTMLElement) {
  const user = setupUser()
  await user.click(button)
}

/**
 * 在容器内查找元素
 */
export function withinElement(element: HTMLElement) {
  return within(element)
}

/**
 * localStorage 测试辅助函数
 */
export const localStorageHelpers = {
  setItem: (key: string, value: any) => {
    localStorage.setItem(key, JSON.stringify(value))
  },
  getItem: (key: string) => {
    const item = localStorage.getItem(key)
    return item ? JSON.parse(item) : null
  },
  clear: () => {
    localStorage.clear()
  },
  hasItem: (key: string) => {
    return localStorage.getItem(key) !== null
  }
}

/**
 * 断言辅助函数
 */
export const assertHelpers = {
  // 检查元素是否可见
  isVisible: (element: HTMLElement) => {
    return element && element.style.display !== 'none' && element.offsetParent !== null
  },

  // 检查元素是否有特定类名
  hasClass: (element: HTMLElement, className: string) => {
    return element.classList.contains(className)
  },

  // 检查元素是否禁用
  isDisabled: (element: HTMLElement) => {
    return (element as HTMLInputElement | HTMLButtonElement).disabled
  }
}
