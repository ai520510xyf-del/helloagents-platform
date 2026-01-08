/**
 * 测试数据工厂函数
 * 使用 faker.js 生成测试数据
 */
import { faker } from '@faker-js/faker'

/**
 * 生成测试用户数据
 */
export function createMockUser(overrides?: Partial<{
  id: number
  username: string
  full_name: string
  created_at: string
  settings: any
}>) {
  return {
    id: faker.number.int({ min: 1, max: 10000 }),
    username: faker.internet.userName(),
    full_name: faker.person.fullName(),
    created_at: faker.date.past().toISOString(),
    settings: {
      theme: faker.helpers.arrayElement(['light', 'dark']),
      editor: {
        fontSize: faker.helpers.arrayElement([12, 14, 16, 18]),
        tabSize: faker.helpers.arrayElement([2, 4]),
      }
    },
    ...overrides,
  }
}

/**
 * 生成测试课程数据
 */
export function createMockLesson(overrides?: Partial<{
  id: number
  chapter_number: number
  lesson_number: number
  title: string
  content: string
  starter_code: string
  extra_data: any
}>) {
  const chapterNum = faker.number.int({ min: 1, max: 5 })
  const lessonNum = faker.number.int({ min: 1, max: 10 })

  return {
    id: faker.number.int({ min: 1, max: 1000 }),
    chapter_number: chapterNum,
    lesson_number: lessonNum,
    title: faker.lorem.sentence(),
    content: `# ${faker.lorem.sentence()}\n\n${faker.lorem.paragraphs(3)}`,
    starter_code: `# ${faker.lorem.sentence()}\nprint("${faker.lorem.word()}")`,
    extra_data: {
      difficulty: faker.helpers.arrayElement(['easy', 'medium', 'hard']),
      estimatedTime: faker.number.int({ min: 5, max: 60 }),
    },
    ...overrides,
  }
}

/**
 * 生成测试进度数据
 */
export function createMockProgress(overrides?: Partial<{
  id: number
  user_id: number
  lesson_id: number
  completed: number
  current_code: string
  last_updated: string
}>) {
  return {
    id: faker.number.int({ min: 1, max: 10000 }),
    user_id: faker.number.int({ min: 1, max: 1000 }),
    lesson_id: faker.number.int({ min: 1, max: 100 }),
    completed: faker.helpers.arrayElement([0, 1]),
    current_code: `print("${faker.lorem.word()}")`,
    last_updated: faker.date.recent().toISOString(),
    ...overrides,
  }
}

/**
 * 生成代码提交数据
 */
export function createMockCodeSubmission(overrides?: Partial<{
  id: number
  user_id: number
  lesson_id: number
  code: string
  success: boolean
  output: string
  error?: string
  submitted_at: string
}>) {
  const success = faker.datatype.boolean()

  return {
    id: faker.number.int({ min: 1, max: 10000 }),
    user_id: faker.number.int({ min: 1, max: 1000 }),
    lesson_id: faker.number.int({ min: 1, max: 100 }),
    code: faker.lorem.lines(5),
    success,
    output: success ? faker.lorem.paragraph() : '',
    error: success ? undefined : faker.lorem.sentence(),
    submitted_at: faker.date.recent().toISOString(),
    ...overrides,
  }
}

/**
 * 生成聊天消息数据
 */
export function createMockChatMessage(overrides?: Partial<{
  id: number
  user_id: number
  message: string
  response: string
  created_at: string
}>) {
  return {
    id: faker.number.int({ min: 1, max: 10000 }),
    user_id: faker.number.int({ min: 1, max: 1000 }),
    message: faker.lorem.sentence({ min: 5, max: 20 }),
    response: faker.lorem.paragraph(),
    created_at: faker.date.recent().toISOString(),
    ...overrides,
  }
}

/**
 * 生成代码执行响应
 */
export function createMockCodeExecutionResponse(overrides?: Partial<{
  success: boolean
  output: string
  error?: string
  execution_time: number
}>) {
  const success = faker.datatype.boolean()

  return {
    success,
    output: success ? faker.lorem.paragraph() : '',
    error: success ? undefined : faker.lorem.sentence(),
    execution_time: faker.number.float({ min: 0.001, max: 5.0, fractionDigits: 3 }),
    ...overrides,
  }
}

/**
 * 生成 AI 提示响应
 */
export function createMockAIHintResponse(overrides?: Partial<{
  current_context: string
  hint: string
  reference_code: string
  key_concepts: string[]
}>) {
  return {
    current_context: faker.lorem.sentence(),
    hint: faker.lorem.paragraph(),
    reference_code: faker.lorem.lines(3),
    key_concepts: faker.helpers.arrayElements(
      ['variables', 'functions', 'loops', 'conditionals', 'data types'],
      { min: 2, max: 4 }
    ),
    ...overrides,
  }
}

/**
 * 批量生成数据
 */
export function createMockArray<T>(
  factory: (index?: number) => T,
  count: number
): T[] {
  return Array.from({ length: count }, (_, index) => factory(index))
}

/**
 * 预设场景数据
 */
export const mockScenarios = {
  // 新用户场景
  newUser: () => createMockUser({
    id: 1,
    username: 'new_user',
    full_name: 'New User',
  }),

  // 完成多个课程的用户
  experiencedUser: () => createMockUser({
    id: 2,
    username: 'experienced_user',
    full_name: 'Experienced User',
  }),

  // 第一课
  firstLesson: () => createMockLesson({
    id: 1,
    chapter_number: 1,
    lesson_number: 1,
    title: 'Introduction to Programming',
    content: '# Welcome\n\nLearn the basics.',
  }),

  // 代码执行成功
  successfulExecution: () => createMockCodeExecutionResponse({
    success: true,
    output: 'Hello, World!\n',
    execution_time: 0.123,
  }),

  // 代码执行错误
  failedExecution: () => createMockCodeExecutionResponse({
    success: false,
    output: '',
    error: 'SyntaxError: invalid syntax',
    execution_time: 0.001,
  }),
}

/**
 * 重置 faker 种子（用于可重复测试）
 */
export function seedFaker(seed: number) {
  faker.seed(seed)
}

/**
 * 生成随机延迟（模拟网络请求）
 */
export function randomDelay(min = 100, max = 500): Promise<void> {
  const delay = faker.number.int({ min, max })
  return new Promise(resolve => setTimeout(resolve, delay))
}
