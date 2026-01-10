/**
 * HelloAgents Platform - 后端API性能测试脚本
 *
 * 测试内容:
 * 1. API响应时间测试
 * 2. 吞吐量测试
 * 3. 并发处理能力测试
 */

import https from 'https';
import http from 'http';

// 测试配置
const BACKEND_URL = 'https://helloagents-platform.onrender.com';
const TEST_ENDPOINTS = [
  { path: '/health', method: 'GET', name: 'Health Check' },
  { path: '/api/v1/ping', method: 'GET', name: 'Ping API' },
  { path: '/api/v1/skills', method: 'GET', name: 'List Skills' },
];

const CONCURRENCY_LEVELS = [1, 5, 10, 20, 50];
const REQUESTS_PER_LEVEL = 100;

/**
 * 发送HTTP请求
 */
function makeRequest(url, method = 'GET') {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const isHttps = urlObj.protocol === 'https:';
    const lib = isHttps ? https : http;

    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port || (isHttps ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method: method,
      headers: {
        'User-Agent': 'HelloAgents-Performance-Test/1.0',
      },
    };

    const startTime = Date.now();

    const req = lib.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        const endTime = Date.now();
        const responseTime = endTime - startTime;

        resolve({
          statusCode: res.statusCode,
          responseTime,
          success: res.statusCode >= 200 && res.statusCode < 300,
          headers: res.headers,
        });
      });
    });

    req.on('error', (error) => {
      const endTime = Date.now();
      const responseTime = endTime - startTime;

      resolve({
        statusCode: 0,
        responseTime,
        success: false,
        error: error.message,
      });
    });

    req.on('timeout', () => {
      req.destroy();
      const endTime = Date.now();
      const responseTime = endTime - startTime;

      resolve({
        statusCode: 0,
        responseTime,
        success: false,
        error: 'Request timeout',
      });
    });

    req.setTimeout(30000); // 30 second timeout
    req.end();
  });
}

/**
 * 测试单个端点的响应时间
 */
async function testEndpointLatency(endpoint) {
  console.log(`\n  测试端点: ${endpoint.name} (${endpoint.path})`);

  const results = [];
  const testRuns = 10;

  for (let i = 0; i < testRuns; i++) {
    const result = await makeRequest(`${BACKEND_URL}${endpoint.path}`, endpoint.method);
    results.push(result);
  }

  const successfulResults = results.filter((r) => r.success);
  const responseTimes = successfulResults.map((r) => r.responseTime);

  if (responseTimes.length === 0) {
    console.log('  ❌ 所有请求失败');
    return null;
  }

  const avgTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
  const minTime = Math.min(...responseTimes);
  const maxTime = Math.max(...responseTimes);
  const p50 = percentile(responseTimes, 50);
  const p95 = percentile(responseTimes, 95);
  const p99 = percentile(responseTimes, 99);

  console.log(`  ✓ 平均响应时间: ${avgTime.toFixed(2)}ms`);
  console.log(`  ✓ 最小响应时间: ${minTime}ms`);
  console.log(`  ✓ 最大响应时间: ${maxTime}ms`);
  console.log(`  ✓ P50: ${p50}ms`);
  console.log(`  ✓ P95: ${p95}ms`);
  console.log(`  ✓ P99: ${p99}ms`);
  console.log(`  ✓ 成功率: ${(successfulResults.length / results.length * 100).toFixed(2)}%`);

  return {
    endpoint: endpoint.name,
    avgTime,
    minTime,
    maxTime,
    p50,
    p95,
    p99,
    successRate: successfulResults.length / results.length,
  };
}

/**
 * 并发测试
 */
async function testConcurrency(endpoint, concurrency) {
  const results = [];
  const batches = Math.ceil(REQUESTS_PER_LEVEL / concurrency);

  const startTime = Date.now();

  for (let i = 0; i < batches; i++) {
    const promises = [];
    for (let j = 0; j < concurrency && (i * concurrency + j) < REQUESTS_PER_LEVEL; j++) {
      promises.push(makeRequest(`${BACKEND_URL}${endpoint.path}`, endpoint.method));
    }
    const batchResults = await Promise.all(promises);
    results.push(...batchResults);
  }

  const endTime = Date.now();
  const totalTime = endTime - startTime;

  const successfulResults = results.filter((r) => r.success);
  const responseTimes = successfulResults.map((r) => r.responseTime);

  if (responseTimes.length === 0) {
    return null;
  }

  const avgTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
  const p95 = percentile(responseTimes, 95);
  const throughput = (successfulResults.length / totalTime) * 1000; // requests per second

  return {
    concurrency,
    totalRequests: results.length,
    successfulRequests: successfulResults.length,
    failedRequests: results.length - successfulResults.length,
    avgTime,
    p95,
    throughput,
    successRate: successfulResults.length / results.length,
  };
}

/**
 * 计算百分位数
 */
function percentile(arr, p) {
  if (arr.length === 0) return 0;
  const sorted = arr.slice().sort((a, b) => a - b);
  const index = Math.ceil((p / 100) * sorted.length) - 1;
  return sorted[Math.max(0, index)];
}

/**
 * 主测试函数
 */
async function main() {
  console.log('🚀 HelloAgents Platform - 后端API性能测试');
  console.log('=' .repeat(60));
  console.log(`📍 后端地址: ${BACKEND_URL}`);
  console.log('=' .repeat(60));

  // 测试1: 基准延迟测试
  console.log('\n📊 1. 基准延迟测试\n');
  const latencyResults = [];

  for (const endpoint of TEST_ENDPOINTS) {
    const result = await testEndpointLatency(endpoint);
    if (result) {
      latencyResults.push(result);
    }
  }

  // 测试2: 并发测试 (使用第一个端点)
  console.log('\n\n📊 2. 并发处理能力测试\n');
  console.log(`  端点: ${TEST_ENDPOINTS[0].name}`);
  console.log(`  每级别请求数: ${REQUESTS_PER_LEVEL}\n`);

  const concurrencyResults = [];

  for (const concurrency of CONCURRENCY_LEVELS) {
    console.log(`  测试并发级别: ${concurrency}`);
    const result = await testConcurrency(TEST_ENDPOINTS[0], concurrency);

    if (result) {
      console.log(`    ✓ 平均响应时间: ${result.avgTime.toFixed(2)}ms`);
      console.log(`    ✓ P95: ${result.p95}ms`);
      console.log(`    ✓ 吞吐量: ${result.throughput.toFixed(2)} req/s`);
      console.log(`    ✓ 成功率: ${(result.successRate * 100).toFixed(2)}%`);
      console.log(`    ✓ 失败请求: ${result.failedRequests}\n`);

      concurrencyResults.push(result);
    } else {
      console.log(`    ❌ 测试失败\n`);
    }
  }

  // 输出总结
  console.log('\n' + '='.repeat(60));
  console.log('📈 测试总结');
  console.log('=' .repeat(60));

  if (latencyResults.length > 0) {
    console.log('\n📊 延迟测试结果:');
    console.log('  端点                    平均(ms)  P95(ms)  P99(ms)  成功率');
    console.log('  ' + '-'.repeat(58));
    latencyResults.forEach((result) => {
      const name = result.endpoint.padEnd(22);
      const avg = result.avgTime.toFixed(0).padStart(8);
      const p95 = result.p95.toString().padStart(7);
      const p99 = result.p99.toString().padStart(7);
      const rate = (result.successRate * 100).toFixed(1).padStart(6) + '%';
      console.log(`  ${name} ${avg} ${p95} ${p99} ${rate}`);
    });
  }

  if (concurrencyResults.length > 0) {
    console.log('\n📊 并发测试结果:');
    console.log('  并发数  平均(ms)  P95(ms)  吞吐量(req/s)  成功率');
    console.log('  ' + '-'.repeat(58));
    concurrencyResults.forEach((result) => {
      const conc = result.concurrency.toString().padStart(6);
      const avg = result.avgTime.toFixed(0).padStart(9);
      const p95 = result.p95.toString().padStart(8);
      const tput = result.throughput.toFixed(2).padStart(13);
      const rate = (result.successRate * 100).toFixed(1).padStart(6) + '%';
      console.log(`  ${conc} ${avg} ${p95} ${tput} ${rate}`);
    });
  }

  // 性能评估
  console.log('\n💡 性能评估:');

  const avgLatency = latencyResults.reduce((sum, r) => sum + r.avgTime, 0) / latencyResults.length;
  if (avgLatency < 100) {
    console.log('  🟢 响应时间: 优秀 (< 100ms)');
  } else if (avgLatency < 300) {
    console.log('  🟡 响应时间: 良好 (100-300ms)');
  } else if (avgLatency < 1000) {
    console.log('  🟠 响应时间: 一般 (300-1000ms)');
  } else {
    console.log('  🔴 响应时间: 需要优化 (> 1000ms)');
  }

  if (concurrencyResults.length > 0) {
    const lastConcurrency = concurrencyResults[concurrencyResults.length - 1];
    if (lastConcurrency.successRate > 0.95) {
      console.log(`  🟢 并发处理: 优秀 (${CONCURRENCY_LEVELS[CONCURRENCY_LEVELS.length - 1]}并发, ${(lastConcurrency.successRate * 100).toFixed(1)}%成功率)`);
    } else if (lastConcurrency.successRate > 0.9) {
      console.log(`  🟡 并发处理: 良好 (${CONCURRENCY_LEVELS[CONCURRENCY_LEVELS.length - 1]}并发, ${(lastConcurrency.successRate * 100).toFixed(1)}%成功率)`);
    } else {
      console.log(`  🔴 并发处理: 需要优化 (${CONCURRENCY_LEVELS[CONCURRENCY_LEVELS.length - 1]}并发, ${(lastConcurrency.successRate * 100).toFixed(1)}%成功率)`);
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log('✅ 测试完成!');
  console.log('=' .repeat(60) + '\n');
}

// 执行测试
main().catch(console.error);
