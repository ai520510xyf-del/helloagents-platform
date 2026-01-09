import { Page, expect } from '@playwright/test';

/**
 * 测试工具函数集合
 */

/**
 * 等待网络空闲
 */
export async function waitForNetworkIdle(page: Page, timeout = 5000) {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * 等待元素可见并点击
 */
export async function waitAndClick(page: Page, selector: string, timeout = 10000) {
  const element = page.locator(selector);
  await expect(element).toBeVisible({ timeout });
  await element.click();
}

/**
 * 等待元素可见并填充
 */
export async function waitAndFill(page: Page, selector: string, value: string, timeout = 10000) {
  const element = page.locator(selector);
  await expect(element).toBeVisible({ timeout });
  await element.fill(value);
}

/**
 * 模拟慢速输入（更接近真实用户行为）
 */
export async function slowType(page: Page, selector: string, text: string, delay = 50) {
  const element = page.locator(selector);
  await element.click();
  await page.keyboard.type(text, { delay });
}

/**
 * 滚动到元素
 */
export async function scrollToElement(page: Page, selector: string) {
  const element = page.locator(selector);
  await element.scrollIntoViewIfNeeded();
}

/**
 * 检查元素是否在视口内
 */
export async function isInViewport(page: Page, selector: string): Promise<boolean> {
  const element = page.locator(selector);
  return await element.evaluate((el) => {
    const rect = el.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= window.innerHeight &&
      rect.right <= window.innerWidth
    );
  });
}

/**
 * 等待指定时间
 */
export async function wait(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * 获取本地存储的值
 */
export async function getLocalStorage(page: Page, key: string): Promise<string | null> {
  return await page.evaluate((k) => localStorage.getItem(k), key);
}

/**
 * 设置本地存储的值
 */
export async function setLocalStorage(page: Page, key: string, value: string) {
  await page.evaluate(
    ({ k, v }) => localStorage.setItem(k, v),
    { k: key, v: value }
  );
}

/**
 * 清除本地存储
 */
export async function clearLocalStorage(page: Page) {
  await page.evaluate(() => localStorage.clear());
}

/**
 * 获取元素的 CSS 属性值
 */
export async function getCSSProperty(page: Page, selector: string, property: string): Promise<string> {
  const element = page.locator(selector);
  return await element.evaluate((el, prop) => {
    return window.getComputedStyle(el).getPropertyValue(prop);
  }, property);
}

/**
 * 检查元素是否有特定的 class
 */
export async function hasClass(page: Page, selector: string, className: string): Promise<boolean> {
  const element = page.locator(selector);
  const classes = await element.getAttribute('class');
  return classes ? classes.split(' ').includes(className) : false;
}

/**
 * 等待文本出现
 */
export async function waitForText(page: Page, text: string, timeout = 10000) {
  await page.waitForSelector(`text=${text}`, { timeout });
}

/**
 * 截图（带时间戳）
 */
export async function takeScreenshot(page: Page, name: string) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({ path: `test-results/${name}-${timestamp}.png`, fullPage: true });
}

/**
 * 检查控制台错误
 */
export function setupConsoleListener(page: Page): string[] {
  const errors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  return errors;
}

/**
 * 检查网络请求失败
 */
export function setupNetworkListener(page: Page): { url: string; status: number }[] {
  const failedRequests: { url: string; status: number }[] = [];
  page.on('response', (response) => {
    if (response.status() >= 400) {
      failedRequests.push({
        url: response.url(),
        status: response.status(),
      });
    }
  });
  return failedRequests;
}

/**
 * 模拟键盘快捷键
 */
export async function pressShortcut(page: Page, shortcut: string) {
  const keys = shortcut.split('+');
  for (const key of keys.slice(0, -1)) {
    await page.keyboard.down(key);
  }
  await page.keyboard.press(keys[keys.length - 1]);
  for (const key of keys.slice(0, -1).reverse()) {
    await page.keyboard.up(key);
  }
}

/**
 * 检查可访问性 - 简单版本
 */
export async function checkBasicAccessibility(page: Page) {
  // 检查页面标题
  const title = await page.title();
  expect(title).toBeTruthy();
  expect(title.length).toBeGreaterThan(0);

  // 检查是否有 main landmark
  const main = page.locator('main, [role="main"]');
  await expect(main).toHaveCount(1);

  // 检查按钮是否可访问
  const buttons = page.locator('button');
  const count = await buttons.count();
  for (let i = 0; i < count; i++) {
    const button = buttons.nth(i);
    const isVisible = await button.isVisible();
    if (isVisible) {
      const text = await button.innerText();
      const ariaLabel = await button.getAttribute('aria-label');
      const title = await button.getAttribute('title');
      // 按钮应该有文本或 aria-label 或 title
      expect(text || ariaLabel || title).toBeTruthy();
    }
  }
}

/**
 * 测量页面加载性能
 */
export async function measurePerformance(page: Page) {
  return await page.evaluate(() => {
    const perfData = window.performance.timing;
    return {
      domContentLoaded: perfData.domContentLoadedEventEnd - perfData.navigationStart,
      loadComplete: perfData.loadEventEnd - perfData.navigationStart,
      firstPaint: performance.getEntriesByType('paint').find((entry) => entry.name === 'first-paint')?.startTime || 0,
    };
  });
}

/**
 * 检查响应式设计
 */
export async function checkResponsive(page: Page, breakpoints: number[]) {
  const results: { width: number; isMobile: boolean }[] = [];

  for (const width of breakpoints) {
    await page.setViewportSize({ width, height: 800 });
    await page.waitForTimeout(500); // 等待布局调整

    const isMobile = await page.evaluate(() => window.innerWidth < 768);
    results.push({ width, isMobile });
  }

  return results;
}

/**
 * 等待动画完成
 */
export async function waitForAnimation(page: Page, selector: string, timeout = 3000) {
  const element = page.locator(selector);
  await element.evaluate(
    (el, t) =>
      new Promise((resolve) => {
        const checkAnimation = () => {
          const styles = window.getComputedStyle(el);
          const animationName = styles.animationName;
          const transitionProperty = styles.transitionProperty;

          if (animationName === 'none' && transitionProperty === 'none') {
            resolve(true);
          } else {
            setTimeout(checkAnimation, 100);
          }
        };
        checkAnimation();
        setTimeout(() => resolve(true), t);
      }),
    timeout
  );
}

/**
 * 模拟拖放操作
 */
export async function dragAndDrop(page: Page, sourceSelector: string, targetSelector: string) {
  const source = page.locator(sourceSelector);
  const target = page.locator(targetSelector);

  const sourceBox = await source.boundingBox();
  const targetBox = await target.boundingBox();

  if (!sourceBox || !targetBox) {
    throw new Error('Element not found or not visible');
  }

  await page.mouse.move(sourceBox.x + sourceBox.width / 2, sourceBox.y + sourceBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(targetBox.x + targetBox.width / 2, targetBox.y + targetBox.height / 2);
  await page.mouse.up();
}

/**
 * 检查图片是否加载成功
 */
export async function checkImagesLoaded(page: Page) {
  const images = page.locator('img');
  const count = await images.count();

  for (let i = 0; i < count; i++) {
    const img = images.nth(i);
    const isVisible = await img.isVisible();
    if (isVisible) {
      const naturalWidth = await img.evaluate((el) => (el as HTMLImageElement).naturalWidth);
      expect(naturalWidth).toBeGreaterThan(0);
    }
  }
}
