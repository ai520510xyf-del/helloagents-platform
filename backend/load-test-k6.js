/**
 * HelloAgents K6 负载测试脚本
 *
 * K6 是现代化的负载测试工具，支持多种测试场景
 *
 * 安装 K6:
 *   macOS: brew install k6
 *   Linux: sudo apt-get install k6
 *   Windows: choco install k6
 *
 * 运行方法:
 *   # 基准测试
 *   k6 run load-test-k6.js
 *
 *   # 指定场景
 *   k6 run --env SCENARIO=baseline load-test-k6.js
 *   k6 run --env SCENARIO=load load-test-k6.js
 *   k6 run --env SCENARIO=stress load-test-k6.js
 *   k6 run --env SCENARIO=spike load-test-k6.js
 *
 *   # 生成 HTML 报告
 *   k6 run load-test-k6.js --out json=results.json
 *   k6 run load-test-k6.js --summary-export=summary.json
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { htmlReport } from 'https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

// ============================================
// 自定义指标
// ============================================

const errorRate = new Rate('errors');
const successRate = new Rate('success');
const codeExecutionDuration = new Trend('code_execution_duration', true);
const apiCallDuration = new Trend('api_call_duration', true);
const totalRequests = new Counter('total_requests');

// ============================================
// 测试配置
// ============================================

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const SCENARIO = __ENV.SCENARIO || 'all';

export const options = {
  scenarios: {
    // 场景1: 基准测试（稳定负载）
    baseline: {
      executor: 'constant-vus',
      vus: 10,
      duration: '2m',
      tags: { scenario: 'baseline' },
      exec: 'baselineTest',
      startTime: '0s',
    },

    // 场景2: 负载测试（逐步增加）
    load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 20 },   // 爬升到 20
        { duration: '3m', target: 20 },   // 保持 20
        { duration: '1m', target: 50 },   // 爬升到 50
        { duration: '3m', target: 50 },   // 保持 50
        { duration: '1m', target: 100 },  // 爬升到 100
        { duration: '3m', target: 100 },  // 保持 100
        { duration: '1m', target: 0 },    // 降回 0
      ],
      tags: { scenario: 'load' },
      exec: 'loadTest',
      startTime: '2m',
    },

    // 场景3: 压力测试（超出预期负载）
    stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 100 },  // 快速爬升到 100
        { duration: '3m', target: 200 },  // 爬升到 200
        { duration: '2m', target: 300 },  // 爬升到 300
        { duration: '3m', target: 300 },  // 保持 300（压力）
        { duration: '1m', target: 0 },    // 降回 0
      ],
      tags: { scenario: 'stress' },
      exec: 'stressTest',
      startTime: '15m',
    },

    // 场景4: 峰值测试（突发流量）
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 500 },  // 快速爬升到 500
        { duration: '1m', target: 500 },   // 保持 500
        { duration: '10s', target: 0 },    // 快速降回 0
      ],
      tags: { scenario: 'spike' },
      exec: 'spikeTest',
      startTime: '25m',
    },

    // 场景5: 浸泡测试（长时间稳定负载）
    soak: {
      executor: 'constant-vus',
      vus: 30,
      duration: '30m',
      tags: { scenario: 'soak' },
      exec: 'soakTest',
      startTime: '27m',
    },
  },

  // 性能阈值
  thresholds: {
    // HTTP 请求总体指标
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],
    'http_req_duration{scenario:baseline}': ['p(95)<300'],
    'http_req_failed': ['rate<0.01'],  // 错误率 < 1%

    // 自定义指标
    'errors': ['rate<0.01'],
    'success': ['rate>0.99'],
    'code_execution_duration': ['p(95)<500', 'p(99)<1000'],
    'api_call_duration': ['p(95)<300'],

    // 特定端点阈值
    'http_req_duration{name:POST /api/v1/code/execute}': ['p(95)<500'],
    'http_req_duration{name:GET /api/v1/lessons}': ['p(95)<200'],
  },

  // 输出选项
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
};

// ============================================
// 测试数据
// ============================================

const CODE_SAMPLES = {
  simple: "print('Hello, World!')",

  medium: `
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

print(factorial(5))
`,

  complex: `
class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

calc = Calculator()
print(calc.add(10, 20))
print(calc.multiply(5, 6))
`,
};

// ============================================
// 辅助函数
// ============================================

function checkResponse(response, expectedStatus, operationName) {
  totalRequests.add(1);

  const success = check(response, {
    [`${operationName}: status is ${expectedStatus}`]: (r) => r.status === expectedStatus,
    [`${operationName}: response time < 500ms`]: (r) => r.timings.duration < 500,
    [`${operationName}: response time < 1000ms`]: (r) => r.timings.duration < 1000,
    [`${operationName}: has valid body`]: (r) => r.body && r.body.length > 0,
  });

  if (success) {
    successRate.add(1);
  } else {
    errorRate.add(1);
    console.error(`❌ ${operationName} failed:`, {
      status: response.status,
      duration: response.timings.duration,
      body: response.body ? response.body.substring(0, 200) : 'empty',
    });
  }

  apiCallDuration.add(response.timings.duration);

  return success;
}

function getRandomCode() {
  const types = ['simple', 'medium', 'complex'];
  const weights = [0.6, 0.3, 0.1];  // 60% simple, 30% medium, 10% complex

  const random = Math.random();
  let sum = 0;

  for (let i = 0; i < weights.length; i++) {
    sum += weights[i];
    if (random < sum) {
      return CODE_SAMPLES[types[i]];
    }
  }

  return CODE_SAMPLES.simple;
}

// ============================================
// 测试场景
// ============================================

export function baselineTest() {
  group('Baseline - 基准测试', () => {
    // 浏览课程
    const lessonsRes = http.get(`${BASE_URL}/api/v1/lessons`, {
      tags: { name: 'GET /api/v1/lessons' },
    });
    checkResponse(lessonsRes, 200, '浏览课程');

    sleep(1);

    // 执行简单代码
    const executeRes = http.post(
      `${BASE_URL}/api/v1/code/execute`,
      JSON.stringify({
        code: CODE_SAMPLES.simple,
        language: 'python',
        timeout: 30,
      }),
      {
        headers: { 'Content-Type': 'application/json' },
        tags: { name: 'POST /api/v1/code/execute' },
      }
    );

    const executeSuccess = checkResponse(executeRes, 200, '执行代码');

    if (executeSuccess) {
      const data = JSON.parse(executeRes.body);
      if (data.execution_time) {
        codeExecutionDuration.add(data.execution_time * 1000);
      }
    }

    sleep(1);
  });
}

export function loadTest() {
  group('Load - 负载测试', () => {
    // 1. 获取课程列表
    const lessonsRes = http.get(`${BASE_URL}/api/v1/lessons`, {
      tags: { name: 'GET /api/v1/lessons' },
    });
    checkResponse(lessonsRes, 200, '获取课程列表');

    sleep(0.5);

    // 2. 查看课程详情
    const lessonId = Math.floor(Math.random() * 20) + 1;
    const lessonRes = http.get(`${BASE_URL}/api/v1/lessons/${lessonId}`, {
      tags: { name: 'GET /api/v1/lessons/{id}' },
    });
    checkResponse(lessonRes, 200, '课程详情');

    sleep(1);

    // 3. 执行代码（混合复杂度）
    const code = getRandomCode();
    const executeRes = http.post(
      `${BASE_URL}/api/v1/code/execute`,
      JSON.stringify({
        code: code,
        language: 'python',
        timeout: 30,
      }),
      {
        headers: { 'Content-Type': 'application/json' },
        tags: { name: 'POST /api/v1/code/execute' },
      }
    );

    const executeSuccess = checkResponse(executeRes, 200, '执行代码');

    if (executeSuccess) {
      const data = JSON.parse(executeRes.body);
      if (data.execution_time) {
        codeExecutionDuration.add(data.execution_time * 1000);
      }
    }

    sleep(1);

    // 4. 保存进度
    const userId = __VU;  // 使用虚拟用户 ID
    const progressRes = http.post(
      `${BASE_URL}/api/v1/progress`,
      JSON.stringify({
        user_id: userId,
        lesson_id: lessonId,
        completed: Math.random() > 0.5 ? 1 : 0,
        current_code: code,
      }),
      {
        headers: { 'Content-Type': 'application/json' },
        tags: { name: 'POST /api/v1/progress' },
      }
    );
    checkResponse(progressRes, 200, '保存进度');

    sleep(1);
  });
}

export function stressTest() {
  group('Stress - 压力测试', () => {
    // 高频执行代码
    const executeRes = http.post(
      `${BASE_URL}/api/v1/code/execute`,
      JSON.stringify({
        code: CODE_SAMPLES.simple,
        language: 'python',
        timeout: 30,
      }),
      {
        headers: { 'Content-Type': 'application/json' },
        tags: { name: 'POST /api/v1/code/execute (stress)' },
      }
    );

    checkResponse(executeRes, 200, '压力执行');

    sleep(0.5);
  });
}

export function spikeTest() {
  group('Spike - 峰值测试', () => {
    // 突发请求，无等待
    const executeRes = http.post(
      `${BASE_URL}/api/v1/code/execute`,
      JSON.stringify({
        code: CODE_SAMPLES.simple,
        language: 'python',
        timeout: 30,
      }),
      {
        headers: { 'Content-Type': 'application/json' },
        tags: { name: 'POST /api/v1/code/execute (spike)' },
      }
    );

    checkResponse(executeRes, 200, '峰值执行');
  });
}

export function soakTest() {
  group('Soak - 浸泡测试', () => {
    // 模拟真实用户行为
    const actions = [
      () => {
        const res = http.get(`${BASE_URL}/api/v1/lessons`);
        checkResponse(res, 200, '浸泡-浏览');
      },
      () => {
        const res = http.post(
          `${BASE_URL}/api/v1/code/execute`,
          JSON.stringify({
            code: getRandomCode(),
            language: 'python',
          }),
          { headers: { 'Content-Type': 'application/json' } }
        );
        checkResponse(res, 200, '浸泡-执行');
      },
    ];

    // 随机选择操作
    const action = actions[Math.floor(Math.random() * actions.length)];
    action();

    sleep(Math.random() * 3 + 1);  // 1-4 秒随机等待
  });
}

// ============================================
// 报告生成
// ============================================

export function handleSummary(data) {
  // 计算自定义统计
  const totalReqs = data.metrics.total_requests.values.count || 0;
  const successReqs = data.metrics.success.values.rate * totalReqs || 0;
  const errorReqs = data.metrics.errors.values.rate * totalReqs || 0;

  return {
    'summary.html': htmlReport(data),
    'summary.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }) + '\n' + customSummary(data),
  };
}

function customSummary(data) {
  const httpReqs = data.metrics.http_reqs.values.count || 0;
  const httpFailed = data.metrics.http_req_failed.values.rate * httpReqs || 0;
  const totalReqs = data.metrics.total_requests.values.count || 0;

  const httpDuration = data.metrics.http_req_duration.values;
  const codeDuration = data.metrics.code_execution_duration.values;

  return `
  ╔════════════════════════════════════════════════════════════╗
  ║           HelloAgents 性能测试总结                        ║
  ╚════════════════════════════════════════════════════════════╝

  📊 请求统计:
    ├─ 总请求数:        ${totalReqs}
    ├─ HTTP 请求数:     ${httpReqs}
    ├─ 失败请求:        ${httpFailed.toFixed(0)} (${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%)
    └─ 成功率:          ${((1 - data.metrics.http_req_failed.values.rate) * 100).toFixed(2)}%

  ⏱️  响应时间 (HTTP):
    ├─ 平均:            ${httpDuration.avg.toFixed(2)}ms
    ├─ 最小:            ${httpDuration.min.toFixed(2)}ms
    ├─ 最大:            ${httpDuration.max.toFixed(2)}ms
    ├─ P50:             ${httpDuration.med.toFixed(2)}ms
    ├─ P95:             ${httpDuration['p(95)'].toFixed(2)}ms
    └─ P99:             ${httpDuration['p(99)'].toFixed(2)}ms

  🐍 代码执行时间:
    ├─ 平均:            ${codeDuration.avg.toFixed(2)}ms
    ├─ P95:             ${codeDuration['p(95)'].toFixed(2)}ms
    └─ P99:             ${codeDuration['p(99)'].toFixed(2)}ms

  ✅ 性能目标检查:
    ├─ P95 < 500ms:     ${httpDuration['p(95)'] < 500 ? '✅ PASS' : '❌ FAIL'}
    ├─ P99 < 1000ms:    ${httpDuration['p(99)'] < 1000 ? '✅ PASS' : '❌ FAIL'}
    └─ 错误率 < 1%:     ${data.metrics.http_req_failed.values.rate < 0.01 ? '✅ PASS' : '❌ FAIL'}

  ═══════════════════════════════════════════════════════════════
  `;
}

// ============================================
// 使用说明
// ============================================

/*
K6 负载测试使用指南:

1. 基准测试 (10 VUs, 2 分钟)
   k6 run --env SCENARIO=baseline load-test-k6.js

2. 负载测试 (逐步增加到 100 VUs)
   k6 run --env SCENARIO=load load-test-k6.js

3. 压力测试 (300 VUs)
   k6 run --env SCENARIO=stress load-test-k6.js

4. 峰值测试 (500 VUs 突发)
   k6 run --env SCENARIO=spike load-test-k6.js

5. 浸泡测试 (30 VUs, 30 分钟)
   k6 run --env SCENARIO=soak load-test-k6.js

6. 运行所有场景
   k6 run load-test-k6.js

7. 生成报告
   k6 run load-test-k6.js --out json=results.json
   k6 run load-test-k6.js --summary-export=summary.json

8. 使用 K6 Cloud
   k6 cloud load-test-k6.js

9. 自定义 BASE_URL
   k6 run --env BASE_URL=http://production-server:8000 load-test-k6.js

性能目标:
  - P95 响应时间: < 500ms
  - P99 响应时间: < 1000ms
  - 错误率: < 1%
  - 吞吐量: > 100 RPS
*/
