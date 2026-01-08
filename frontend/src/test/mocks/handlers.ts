/**
 * MSW Mock API Handlers
 * 使用 Mock Service Worker 拦截和模拟 API 请求
 */

import { http, HttpResponse } from 'msw'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * MSW Request Handlers
 */
export const handlers = [
  // Health Check
  http.get(`${API_BASE_URL}/api/v1/health`, () => {
    return HttpResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
    })
  }),

  // Execute Code
  http.post(`${API_BASE_URL}/api/v1/execute`, async ({ request }) => {
    const body = await request.json() as any
    const code = body.code || ''

    // 模拟代码执行成功
    if (!code.includes('error')) {
      return HttpResponse.json({
        success: true,
        output: 'Hello, World!\n',
        execution_time: 0.123,
      })
    }

    // 模拟代码执行错误
    return HttpResponse.json({
      success: false,
      output: '',
      error: 'Syntax error on line 1',
      execution_time: 0.001,
    })
  }),

  // Get AI Hint
  http.post(`${API_BASE_URL}/api/v1/hint`, async ({ request }) => {
    const body = await request.json() as any
    const lessonId = body.lesson_id

    return HttpResponse.json({
      current_context: `You are working on lesson ${lessonId}`,
      hint: 'Try using the print() function to output text',
      reference_code: 'print("Hello, World!")',
      key_concepts: ['print function', 'string literals', 'output'],
    })
  }),

  // Get Lesson Content
  http.get(`${API_BASE_URL}/api/v1/lessons/:chapterNum/:lessonNum`, ({ params }) => {
    const { chapterNum, lessonNum } = params

    return HttpResponse.json({
      id: 1,
      chapter_number: parseInt(chapterNum as string),
      lesson_number: parseInt(lessonNum as string),
      title: `Lesson ${chapterNum}.${lessonNum}`,
      content: '# Welcome to the lesson\n\nLearn the basics of programming.',
      starter_code: '# Write your code here\nprint("Hello, World!")',
      extra_data: { difficulty: 'easy' },
    })
  }),

  // Chat with AI
  http.post(`${API_BASE_URL}/api/v1/chat`, async ({ request }) => {
    const body = await request.json() as any
    const message = body.message

    return HttpResponse.json({
      message: `AI response to: ${message}`,
      success: true,
    })
  }),

  // Get User Progress
  http.get(`${API_BASE_URL}/api/v1/users/:userId/progress`, ({ params }) => {
    const { userId } = params

    return HttpResponse.json({
      user_id: parseInt(userId as string),
      completed_lessons: 5,
      current_lesson: { chapter: 1, lesson: 2 },
      total_code_submissions: 15,
    })
  }),

  // Update User Progress
  http.put(`${API_BASE_URL}/api/v1/users/:userId/progress`, async ({ params, request }) => {
    const { userId } = params
    const body = await request.json() as any

    return HttpResponse.json({
      user_id: parseInt(userId as string),
      lesson_id: body.lesson_id,
      completed: body.completed,
      current_code: body.current_code,
    })
  }),

  // Submit Code
  http.post(`${API_BASE_URL}/api/v1/submissions`, async ({ request }) => {
    const body = await request.json() as any

    return HttpResponse.json({
      id: 1,
      user_id: body.user_id,
      lesson_id: body.lesson_id,
      code: body.code,
      success: true,
      output: 'Code executed successfully',
      submitted_at: new Date().toISOString(),
    })
  }),

  // Migration API
  http.post(`${API_BASE_URL}/api/v1/migrate`, async ({ request }) => {
    const body = await request.json() as any

    // 模拟成功的迁移
    if (body.username && body.full_name) {
      return HttpResponse.json({
        success: true,
        message: 'Migration completed successfully',
        user_id: 1,
        migrated_progress: 5,
        migrated_submissions: 10,
        migrated_chat_messages: 20,
      })
    }

    // 模拟迁移错误
    return HttpResponse.json(
      {
        detail: 'Migration failed: Invalid data',
      },
      { status: 400 }
    )
  }),

  // Get Chat History
  http.get(`${API_BASE_URL}/api/v1/users/:userId/chat-history`, ({ params }) => {
    const { userId } = params

    return HttpResponse.json([
      {
        id: 1,
        user_id: parseInt(userId as string),
        message: 'Hello, AI!',
        response: 'Hello! How can I help you?',
        created_at: new Date().toISOString(),
      },
      {
        id: 2,
        user_id: parseInt(userId as string),
        message: 'How do I use loops?',
        response: 'Loops allow you to repeat code...',
        created_at: new Date().toISOString(),
      },
    ])
  }),

  // Get All Lessons
  http.get(`${API_BASE_URL}/api/v1/lessons`, () => {
    return HttpResponse.json([
      {
        id: 1,
        chapter_number: 1,
        lesson_number: 1,
        title: 'Introduction to Programming',
        content: '# Lesson 1.1',
      },
      {
        id: 2,
        chapter_number: 1,
        lesson_number: 2,
        title: 'Variables and Data Types',
        content: '# Lesson 1.2',
      },
    ])
  }),
]

/**
 * Mock Data for Testing
 * 可以在测试中直接使用的 mock 数据
 */
export const mockData = {
  user: {
    id: 1,
    username: 'test_user',
    full_name: 'Test User',
    created_at: new Date().toISOString(),
  },

  lesson: {
    id: 1,
    chapter_number: 1,
    lesson_number: 1,
    title: 'Introduction to Programming',
    content: '# Lesson Content',
    starter_code: 'print("Hello")',
  },

  codeExecution: {
    success: {
      success: true,
      output: 'Hello, World!\n',
      execution_time: 0.123,
    },
    error: {
      success: false,
      output: '',
      error: 'Syntax error on line 1',
      execution_time: 0.001,
    },
  },

  progress: {
    user_id: 1,
    lesson_id: 1,
    completed: 1,
    current_code: 'print("test")',
  },
}
