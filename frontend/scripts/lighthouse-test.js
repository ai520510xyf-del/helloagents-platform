#!/usr/bin/env node

/**
 * Lighthouse 性能测试脚本
 *
 * 使用方式:
 *   node scripts/lighthouse-test.js [url] [options]
 *
 * 示例:
 *   node scripts/lighthouse-test.js http://localhost:5173
 *   node scripts/lighthouse-test.js https://helloagents.example.com --mobile
 */

import { chromeLauncher } from 'chrome-launcher';
import lighthouse from 'lighthouse';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 配置
const DEFAULT_URL = 'http://localhost:5173';
const OUTPUT_DIR = path.join(__dirname, '../performance-reports');

// 确保输出目录存在
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// 解析命令行参数
const args = process.argv.slice(2);
const url = args[0] || DEFAULT_URL;
const isMobile = args.includes('--mobile');
const isDesktop = args.includes('--desktop');
const outputJson = args.includes('--json');
const outputHtml = args.includes('--html') || !outputJson;

// Lighthouse 配置
const lighthouseConfig = {
  extends: 'lighthouse:default',
  settings: {
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
    formFactor: isMobile ? 'mobile' : 'desktop',
    throttling: {
      rttMs: 40,
      throughputKbps: 10 * 1024,
      cpuSlowdownMultiplier: 1,
      requestLatencyMs: 0,
      downloadThroughputKbps: 0,
      uploadThroughputKbps: 0,
    },
    screenEmulation: {
      mobile: isMobile,
      width: isMobile ? 375 : 1920,
      height: isMobile ? 667 : 1080,
      deviceScaleFactor: isMobile ? 2 : 1,
    },
    emulatedUserAgent: isMobile
      ? 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36'
      : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Safari/537.36',
  },
};

// Chrome 启动配置
const chromeFlags = [
  '--no-sandbox',
  '--headless',
  '--disable-gpu',
  '--disable-dev-shm-usage',
];

/**
 * 运行 Lighthouse 测试
 */
async function runLighthouse() {
  console.log('🚀 Starting Lighthouse test...');
  console.log('📍 URL:', url);
  console.log('📱 Device:', isMobile ? 'Mobile' : 'Desktop');

  let chrome;
  try {
    // 启动 Chrome
    chrome = await chromeLauncher.launch({ chromeFlags });
    const options = {
      logLevel: 'info',
      output: outputJson ? 'json' : 'html',
      port: chrome.port,
    };

    // 运行 Lighthouse
    const runnerResult = await lighthouse(url, options, lighthouseConfig);

    // 生成报告
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const deviceType = isMobile ? 'mobile' : 'desktop';

    if (outputHtml) {
      const htmlPath = path.join(OUTPUT_DIR, `lighthouse-${deviceType}-${timestamp}.html`);
      fs.writeFileSync(htmlPath, runnerResult.report);
      console.log('✅ HTML report saved:', htmlPath);
    }

    if (outputJson) {
      const jsonPath = path.join(OUTPUT_DIR, `lighthouse-${deviceType}-${timestamp}.json`);
      fs.writeFileSync(jsonPath, JSON.stringify(runnerResult.lhr, null, 2));
      console.log('✅ JSON report saved:', jsonPath);
    }

    // 打印性能指标
    console.log('\n📊 Performance Metrics:');
    const { lhr } = runnerResult;

    // 评分
    console.log('\n🎯 Scores:');
    console.log('  Performance:', getScoreEmoji(lhr.categories.performance.score), lhr.categories.performance.score * 100);
    console.log('  Accessibility:', getScoreEmoji(lhr.categories.accessibility.score), lhr.categories.accessibility.score * 100);
    console.log('  Best Practices:', getScoreEmoji(lhr.categories['best-practices'].score), lhr.categories['best-practices'].score * 100);
    console.log('  SEO:', getScoreEmoji(lhr.categories.seo.score), lhr.categories.seo.score * 100);

    // Core Web Vitals
    console.log('\n⚡ Core Web Vitals:');
    const metrics = lhr.audits;
    console.log('  FCP:', formatMs(metrics['first-contentful-paint'].numericValue), getRating(metrics['first-contentful-paint'].score));
    console.log('  LCP:', formatMs(metrics['largest-contentful-paint'].numericValue), getRating(metrics['largest-contentful-paint'].score));
    console.log('  CLS:', metrics['cumulative-layout-shift'].numericValue.toFixed(3), getRating(metrics['cumulative-layout-shift'].score));
    console.log('  TBT:', formatMs(metrics['total-blocking-time'].numericValue), getRating(metrics['total-blocking-time'].score));
    console.log('  SI:', formatMs(metrics['speed-index'].numericValue), getRating(metrics['speed-index'].score));

    // 资源统计
    console.log('\n📦 Resource Summary:');
    const resourceSummary = metrics['resource-summary'].details.items;
    resourceSummary.forEach((item) => {
      console.log(`  ${item.resourceType}:`, formatBytes(item.transferSize));
    });

    // 机会
    console.log('\n💡 Opportunities:');
    const opportunities = Object.values(metrics)
      .filter((audit) => audit.details && audit.details.type === 'opportunity')
      .sort((a, b) => b.numericValue - a.numericValue)
      .slice(0, 5);

    opportunities.forEach((opp) => {
      console.log(`  - ${opp.title}: ${formatMs(opp.numericValue)} savings`);
    });

    // 检查是否通过
    const performanceScore = lhr.categories.performance.score;
    if (performanceScore < 0.9) {
      console.log('\n❌ Performance score is below 90!');
      process.exit(1);
    } else {
      console.log('\n✅ All checks passed!');
    }
  } catch (error) {
    console.error('❌ Error running Lighthouse:', error);
    process.exit(1);
  } finally {
    if (chrome) {
      await chrome.kill();
    }
  }
}

/**
 * 辅助函数
 */
function getScoreEmoji(score) {
  if (score >= 0.9) return '🟢';
  if (score >= 0.5) return '🟡';
  return '🔴';
}

function getRating(score) {
  if (score >= 0.9) return '✅ Good';
  if (score >= 0.5) return '⚠️ Needs Improvement';
  return '❌ Poor';
}

function formatMs(ms) {
  return `${(ms / 1000).toFixed(2)}s`;
}

function formatBytes(bytes) {
  return `${(bytes / 1024).toFixed(2)} KB`;
}

// 运行测试
runLighthouse();
