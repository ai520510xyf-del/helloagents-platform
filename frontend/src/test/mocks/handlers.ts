/**
 * Mock API handlers for testing
 *
 * Note: MSW would be ideal here, but we'll use simple fetch mocks for now.
 * To use MSW, install it with: npm install --save-dev msw
 */

import { vi } from 'vitest'
import type {
  CodeExecutionResponse,
  AIHintResponse,
  LessonContentResponse,
  ChatResponse,
} from '@/services/api'
import type { MigrationResponse } from '@/utils/migrationHelper'

/**
 * Mock responses for API endpoints
 */
export const mockResponses = {
  // Code execution
  executeCode: {
    success: true,
    output: 'Hello, World!\n',
    execution_time: 0.123,
  } as CodeExecutionResponse,

  executeCodeError: {
    success: false,
    output: '',
    error: 'Syntax error on line 1',
    execution_time: 0.001,
  } as CodeExecutionResponse,

  // AI hints
  getAIHint: {
    current_context: 'You are working on a print statement',
    hint: 'Try using the print() function to output text',
    reference_code: 'print("Hello, World!")',
    key_concepts: ['print function', 'string literals', 'output'],
  } as AIHintResponse,

  // Lesson content
  getLessonContent: {
    lesson_id: '1-1',
    title: 'Introduction to Python',
    content: '# Welcome to Python\n\nLearn the basics of Python programming.',
    code_template: '# Write your code here\nprint("Hello, World!")',
  } as LessonContentResponse,

  // Chat
  chatWithAI: {
    message: 'Hello! How can I help you with your code?',
    success: true,
  } as ChatResponse,

  // Health check
  healthCheck: {
    status: 'healthy',
    timestamp: new Date().toISOString(),
  },

  // Migration
  migrateSuccess: {
    success: true,
    message: 'Migration completed successfully',
    user_id: 1,
    migrated_progress: 5,
    migrated_submissions: 10,
    migrated_chat_messages: 20,
  } as MigrationResponse,

  migrateError: {
    detail: 'Migration failed: Database connection error',
  },
}

/**
 * Create a mock fetch response
 */
export function createMockResponse(data: any, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: async () => data,
    text: async () => JSON.stringify(data),
    headers: new Headers(),
  } as Response)
}

/**
 * Setup fetch mocks for testing
 */
export function setupFetchMocks() {
  const originalFetch = global.fetch

  beforeEach(() => {
    global.fetch = vi.fn()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  return {
    restore: () => {
      global.fetch = originalFetch
    },
  }
}

/**
 * Mock specific API endpoint
 */
export function mockApiEndpoint(
  url: string | RegExp,
  response: any,
  status = 200
) {
  ;(global.fetch as any).mockImplementation((requestUrl: string) => {
    const matches =
      typeof url === 'string' ? requestUrl.includes(url) : url.test(requestUrl)

    if (matches) {
      return createMockResponse(response, status)
    }

    return createMockResponse({ error: 'Not found' }, 404)
  })
}
