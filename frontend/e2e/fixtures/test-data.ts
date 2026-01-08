/**
 * E2E Test Data Fixtures
 *
 * 测试数据和常量定义
 */

export const TEST_DATA = {
  // 测试代码示例
  codeExamples: {
    simple: `print("Hello, World!")`,
    withInput: `name = input("Enter your name: ")
print(f"Hello, {name}!")`,
    withError: `print(undefined_variable)`,
    loop: `for i in range(5):
    print(f"Count: {i}")`,
  },

  // AI 助手测试问题
  aiQuestions: {
    simple: '什么是 Python 变量？',
    code: '如何在 Python 中定义一个函数？',
    debug: '为什么我的代码报错了？',
  },

  // 课程 ID
  courses: {
    intro: 'intro-to-python',
    variables: 'python-variables',
    functions: 'python-functions',
  },

  // 超时时间
  timeouts: {
    codeExecution: 10000,
    aiResponse: 15000,
    pageLoad: 5000,
  },

  // API 端点
  apiEndpoints: {
    execute: '/api/execute',
    chat: '/api/chat',
    lessons: '/api/lessons',
  },
};

/**
 * 错误场景测试数据
 */
export const ERROR_SCENARIOS = {
  // API 错误
  apiErrors: {
    networkError: {
      status: 0,
      message: 'Network Error',
    },
    serverError: {
      status: 500,
      message: 'Internal Server Error',
    },
    timeout: {
      status: 408,
      message: 'Request Timeout',
    },
  },

  // 代码执行错误
  codeErrors: {
    syntaxError: `print("unclosed string`,
    nameError: `print(undefined_variable)`,
    typeError: `"string" + 123`,
  },
};

/**
 * 期望结果
 */
export const EXPECTED_RESULTS = {
  codeExecution: {
    simple: 'Hello, World!',
    loop: /Count: [0-4]/,
  },

  toastMessages: {
    success: /执行成功|Success/i,
    error: /错误|Error/i,
    networkError: /网络错误|Network Error/i,
  },
};
