/**
 * HelloAgents Platform - 全面性能测试脚本
 *
 * 测试内容:
 * 1. Lighthouse 性能审计
 * 2. 网络性能分析
 * 3. 资源加载分析
 * 4. Core Web Vitals
 */

import lighthouse from 'lighthouse';
import * as chromeLauncher from 'chrome-launcher';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 测试配置
const FRONTEND_URL = 'https://helloagents-platform.pages.dev';
const OUTPUT_DIR = './performance-reports';

// 确保输出目录存在
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * 运行 Lighthouse 测试
 */
async function runLighthouseTest() {
  console.log('\n📊 开始运行 Lighthouse 性能测试...\n');

  const chrome = await chromeLauncher.launch({
    chromeFlags: ['--headless', '--disable-gpu', '--no-sandbox']
  });

  const options = {
    logLevel: 'info',
    output: ['html', 'json'],
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
    port: chrome.port,
    // 使用移动端和桌面端配置
    formFactor: 'desktop',
    screenEmulation: {
      mobile: false,
      width: 1920,
      height: 1080,
      deviceScaleFactor: 1,
      disabled: false,
    },
    throttling: {
      rttMs: 40,
      throughputKbps: 10 * 1024,
      cpuSlowdownMultiplier: 1,
    },
  };

  try {
    // 桌面端测试
    console.log('🖥️  桌面端测试...');
    const desktopResult = await lighthouse(FRONTEND_URL, options);

    // 保存报告
    const desktopReportHtml = desktopResult.report[0];
    const desktopReportJson = desktopResult.report[1];

    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'lighthouse-desktop.html'),
      desktopReportHtml
    );
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'lighthouse-desktop.json'),
      desktopReportJson
    );

    // 移动端测试
    console.log('📱 移动端测试...');
    const mobileOptions = {
      ...options,
      formFactor: 'mobile',
      screenEmulation: {
        mobile: true,
        width: 375,
        height: 667,
        deviceScaleFactor: 2,
        disabled: false,
      },
      throttling: {
        rttMs: 150,
        throughputKbps: 1.6 * 1024,
        cpuSlowdownMultiplier: 4,
      },
    };

    const mobileResult = await lighthouse(FRONTEND_URL, mobileOptions);

    const mobileReportHtml = mobileResult.report[0];
    const mobileReportJson = mobileResult.report[1];

    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'lighthouse-mobile.html'),
      mobileReportHtml
    );
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'lighthouse-mobile.json'),
      mobileReportJson
    );

    // 输出摘要
    console.log('\n✅ Lighthouse 测试完成!\n');
    console.log('📊 桌面端分数:');
    printScores(JSON.parse(desktopReportJson));
    console.log('\n📊 移动端分数:');
    printScores(JSON.parse(mobileReportJson));

    // 分析 Core Web Vitals
    console.log('\n🎯 Core Web Vitals (桌面端):');
    printWebVitals(JSON.parse(desktopReportJson));
    console.log('\n🎯 Core Web Vitals (移动端):');
    printWebVitals(JSON.parse(mobileReportJson));

    // 性能建议
    console.log('\n💡 性能优化建议:');
    printOpportunities(JSON.parse(desktopReportJson));

  } catch (error) {
    console.error('❌ Lighthouse 测试失败:', error);
  } finally {
    await chrome.kill();
  }
}

/**
 * 打印性能分数
 */
function printScores(lhr) {
  const categories = lhr.categories;
  console.log(`  Performance: ${Math.round(categories.performance.score * 100)}/100`);
  console.log(`  Accessibility: ${Math.round(categories.accessibility.score * 100)}/100`);
  console.log(`  Best Practices: ${Math.round(categories['best-practices'].score * 100)}/100`);
  console.log(`  SEO: ${Math.round(categories.seo.score * 100)}/100`);
}

/**
 * 打印 Core Web Vitals
 */
function printWebVitals(lhr) {
  const audits = lhr.audits;

  // LCP - Largest Contentful Paint
  const lcp = audits['largest-contentful-paint'];
  console.log(`  LCP (Largest Contentful Paint): ${lcp.displayValue} ${getScoreEmoji(lcp.score)}`);

  // FID - First Input Delay (通过 TBT 估算)
  const tbt = audits['total-blocking-time'];
  console.log(`  TBT (Total Blocking Time): ${tbt.displayValue} ${getScoreEmoji(tbt.score)}`);

  // CLS - Cumulative Layout Shift
  const cls = audits['cumulative-layout-shift'];
  console.log(`  CLS (Cumulative Layout Shift): ${cls.displayValue} ${getScoreEmoji(cls.score)}`);

  // FCP - First Contentful Paint
  const fcp = audits['first-contentful-paint'];
  console.log(`  FCP (First Contentful Paint): ${fcp.displayValue} ${getScoreEmoji(fcp.score)}`);

  // SI - Speed Index
  const si = audits['speed-index'];
  console.log(`  SI (Speed Index): ${si.displayValue} ${getScoreEmoji(si.score)}`);

  // TTI - Time to Interactive
  const tti = audits['interactive'];
  console.log(`  TTI (Time to Interactive): ${tti.displayValue} ${getScoreEmoji(tti.score)}`);
}

/**
 * 打印性能优化机会
 */
function printOpportunities(lhr) {
  const audits = lhr.audits;
  const opportunities = [];

  // 收集所有可以改进的项目
  Object.keys(audits).forEach(key => {
    const audit = audits[key];
    if (audit.details && audit.details.type === 'opportunity' && audit.score < 1) {
      opportunities.push({
        title: audit.title,
        description: audit.description,
        savings: audit.details.overallSavingsMs || 0,
        score: audit.score,
      });
    }
  });

  // 按节省时间排序
  opportunities.sort((a, b) => b.savings - a.savings);

  // 打印前5个最重要的优化机会
  opportunities.slice(0, 5).forEach((opp, index) => {
    console.log(`  ${index + 1}. ${opp.title}`);
    console.log(`     节省: ~${Math.round(opp.savings)}ms`);
  });
}

/**
 * 获取分数对应的emoji
 */
function getScoreEmoji(score) {
  if (score === null) return '⚪';
  if (score >= 0.9) return '🟢';
  if (score >= 0.5) return '🟡';
  return '🔴';
}

/**
 * 主函数
 */
async function main() {
  console.log('🚀 HelloAgents Platform - 全面性能测试');
  console.log('=' .repeat(60));
  console.log(`📍 前端地址: ${FRONTEND_URL}`);
  console.log(`📁 报告目录: ${OUTPUT_DIR}`);
  console.log('=' .repeat(60));

  await runLighthouseTest();

  console.log('\n' + '='.repeat(60));
  console.log('✅ 所有测试完成!');
  console.log(`📁 详细报告已保存至: ${OUTPUT_DIR}`);
  console.log('=' .repeat(60) + '\n');
}

// 执行测试
main().catch(console.error);
