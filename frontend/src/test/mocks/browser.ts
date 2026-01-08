/**
 * MSW Browser 配置
 * 用于浏览器环境（开发时手动 mock）
 */
import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

// 创建 MSW worker 实例
export const worker = setupWorker(...handlers)
