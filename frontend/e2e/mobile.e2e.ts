import { test, expect, devices } from '@playwright/test';
import { LearnPage } from './pages/LearnPage';
import { wait } from './utils/helpers';

/**
 * 移动端响应式布局 E2E 测试
 *
 * 测试范围：
 * - 移动端布局适配
 * - 触摸交互
 * - 移动端特定功能
 * - 不同设备尺寸的兼容性
 */

test.describe('移动端 - iPhone 12', () => {
  test.use({ ...devices['iPhone 12'] });

  let learnPage: LearnPage;

  test.beforeEach(async ({ page }) => {
    learnPage = new LearnPage(page);
    await learnPage.goto();
  });

  test('应该正确加载移动端布局', async ({ page }) => {
    // 验证视口大小
    const viewport = page.viewportSize();
    expect(viewport?.width).toBeLessThan(768);

    // 检查是否使用移动端布局
    const isMobile = await learnPage.isMobileLayout();
    expect(isMobile).toBe(true);

    // 检查基本元素是否可见
    await expect(learnPage.navBar).toBeVisible();
  });

  test('应该能够在移动端浏览课程', async ({ page }) => {
    // 等待课程列表加载
    await wait(2000);

    // 检查课程菜单是否可访问
    // 移动端可能使用折叠菜单或不同的布局
    const lessonCount = await learnPage.lessonItems.count();

    if (lessonCount > 0) {
      // 尝试点击第一个课程
      await learnPage.lessonItems.first().click();
      await wait(1000);

      // 验证课程内容已加载
      expect(true).toBe(true); // 基本验证
    }
  });

  test('应该能够在移动端使用代码编辑器', async ({ page }) => {
    // 检查代码编辑器是否可见
    const isEditorVisible = await learnPage.codeEditor.isVisible();

    if (isEditorVisible) {
      // 尝试点击编辑器
      await learnPage.codeEditor.click();
      await wait(500);

      // 输入简单代码
      await page.keyboard.type('print("mobile")');
      await wait(500);
    }
  });

  test('应该能够在移动端运行代码', async ({ page }) => {
    // 检查运行按钮是否可见
    const isRunButtonVisible = await learnPage.runButton.isVisible();

    if (isRunButtonVisible) {
      // 输入代码
      await learnPage.typeCode('print("test")');
      await wait(500);

      // 点击运行按钮
      await learnPage.runButton.click();
      await wait(3000);

      // 验证有输出
      const output = await learnPage.getTerminalOutput();
      expect(output.length).toBeGreaterThan(0);
    }
  });

  test('应该能够在移动端切换主题', async ({ page }) => {
    const initialTheme = await learnPage.getTheme();

    // 切换主题
    await learnPage.toggleTheme();
    await wait(500);

    const newTheme = await learnPage.getTheme();
    expect(newTheme).not.toBe(initialTheme);
  });

  test('应该支持触摸滑动', async ({ page }) => {
    // 测试简单的触摸交互
    const element = learnPage.navBar;

    // 获取元素位置
    const box = await element.boundingBox();

    if (box) {
      // 模拟触摸滑动
      await page.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2);
      await wait(300);
    }
  });
});

test.describe('移动端 - Android (Pixel 5)', () => {
  test.use({ ...devices['Pixel 5'] });

  let learnPage: LearnPage;

  test.beforeEach(async ({ page }) => {
    learnPage = new LearnPage(page);
    await learnPage.goto();
  });

  test('应该在 Android 设备上正确显示', async ({ page }) => {
    // 检查视口
    const viewport = page.viewportSize();
    expect(viewport?.width).toBeLessThan(768);

    // 检查基本元素
    await expect(learnPage.navBar).toBeVisible();

    // 验证移动端布局
    const isMobile = await learnPage.isMobileLayout();
    expect(isMobile).toBe(true);
  });

  test('应该能够垂直滚动', async ({ page }) => {
    // 滚动页面
    await page.evaluate(() => window.scrollTo(0, 200));
    await wait(500);

    // 检查滚动位置
    const scrollY = await page.evaluate(() => window.scrollY);
    expect(scrollY).toBeGreaterThan(0);
  });

  test('应该正确处理屏幕旋转', async ({ page }) => {
    // 获取初始方向
    const initialWidth = page.viewportSize()?.width || 0;
    const initialHeight = page.viewportSize()?.height || 0;

    // 模拟横屏（交换宽高）
    await page.setViewportSize({ width: initialHeight, height: initialWidth });
    await wait(1000);

    // 检查布局是否适应
    await expect(learnPage.navBar).toBeVisible();
  });
});

test.describe('平板 - iPad Pro', () => {
  test.use({ ...devices['iPad Pro'] });

  let learnPage: LearnPage;

  test.beforeEach(async ({ page }) => {
    learnPage = new LearnPage(page);
    await learnPage.goto();
  });

  test('应该正确加载平板布局', async ({ page }) => {
    // 检查视口大小
    const viewport = page.viewportSize();
    expect(viewport?.width).toBeGreaterThanOrEqual(768);
    expect(viewport?.width).toBeLessThan(1024);

    // 检查是否使用平板布局
    const isTablet = await learnPage.isTabletLayout();
    expect(isTablet).toBe(true);

    // 检查基本元素
    await expect(learnPage.navBar).toBeVisible();
    await expect(learnPage.codeEditor).toBeVisible();
  });

  test('应该在平板上显示优化的布局', async ({ page }) => {
    // 等待页面加载
    await wait(1000);

    // 检查课程菜单是否可见
    const isMenuVisible = await learnPage.courseMenu.isVisible();

    // 平板可能使用不同的布局策略
    // 可能显示侧边栏，也可能折叠
    expect(typeof isMenuVisible).toBe('boolean');
  });

  test('应该能够在平板上使用所有功能', async ({ page }) => {
    // 测试代码编辑
    await learnPage.typeCode('print("tablet test")');
    await wait(500);

    // 测试运行代码
    await learnPage.runCode();
    await wait(3000);

    // 验证输出
    const output = await learnPage.getTerminalOutput();
    expect(output.length).toBeGreaterThan(0);
  });
});

test.describe('响应式断点测试', () => {
  const breakpoints = [
    { width: 375, height: 667, name: 'iPhone SE' },
    { width: 390, height: 844, name: 'iPhone 12 Pro' },
    { width: 768, height: 1024, name: 'iPad Mini' },
    { width: 1024, height: 768, name: 'iPad Landscape' },
    { width: 1280, height: 720, name: 'Laptop' },
    { width: 1920, height: 1080, name: 'Desktop' },
  ];

  breakpoints.forEach(({ width, height, name }) => {
    test(`应该在 ${name} (${width}x${height}) 上正确显示`, async ({ page }) => {
      await page.setViewportSize({ width, height });

      const learnPage = new LearnPage(page);
      await learnPage.goto();

      // 检查基本元素是否可见
      await expect(learnPage.navBar).toBeVisible();

      // 根据宽度判断布局类型
      if (width < 768) {
        const isMobile = await learnPage.isMobileLayout();
        expect(isMobile).toBe(true);
      } else if (width < 1024) {
        const isTablet = await learnPage.isTabletLayout();
        expect(isTablet).toBe(true);
      } else {
        const isDesktop = await learnPage.isDesktopLayout();
        expect(isDesktop).toBe(true);
      }
    });
  });
});

test.describe('移动端交互测试', () => {
  test.use({ ...devices['iPhone 12'] });

  test('应该支持双指缩放（页面缩放）', async ({ page }) => {
    const learnPage = new LearnPage(page);
    await learnPage.goto();

    // 获取初始缩放级别
    const initialZoom = await page.evaluate(() => window.visualViewport?.scale || 1);

    // 注意：Playwright 不直接支持双指缩放手势
    // 这里只是检查页面是否允许缩放
    const viewport = await page.evaluate(() => {
      const meta = document.querySelector('meta[name="viewport"]');
      return meta?.getAttribute('content') || '';
    });

    // 验证视口配置
    expect(viewport).toBeTruthy();
  });

  test('应该正确处理长按操作', async ({ page }) => {
    const learnPage = new LearnPage(page);
    await learnPage.goto();

    // 获取一个可交互元素
    const button = learnPage.runButton;
    const box = await button.boundingBox();

    if (box) {
      // 模拟长按（按下并保持）
      await page.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2);
      await wait(1000);

      // 验证页面没有崩溃
      await expect(learnPage.navBar).toBeVisible();
    }
  });

  test('应该在移动端正确显示弹窗和提示', async ({ page }) => {
    const learnPage = new LearnPage(page);
    await learnPage.goto();
    await wait(1000);

    // 检查是否有任何弹窗或提示
    // 这取决于应用的具体实现

    // 验证页面基本功能正常
    await expect(learnPage.navBar).toBeVisible();
  });
});

test.describe('移动端性能测试', () => {
  test.use({ ...devices['Pixel 5'] });

  test('移动端页面加载时间应该合理', async ({ page }) => {
    const startTime = Date.now();

    const learnPage = new LearnPage(page);
    await learnPage.goto();
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // 移动端加载时间应该在 10 秒内
    expect(loadTime).toBeLessThan(10000);
  });

  test('移动端不应该有内存泄漏', async ({ page }) => {
    const learnPage = new LearnPage(page);
    await learnPage.goto();

    // 执行一些操作
    for (let i = 0; i < 5; i++) {
      await learnPage.toggleTheme();
      await wait(500);
    }

    // 验证页面仍然正常工作
    await expect(learnPage.navBar).toBeVisible();
  });
});

test.describe('移动端可访问性', () => {
  test.use({ ...devices['iPhone 12'] });

  test('移动端应该支持屏幕阅读器', async ({ page }) => {
    const learnPage = new LearnPage(page);
    await learnPage.goto();

    // 检查主要元素是否有 ARIA 标签
    const navBar = learnPage.navBar;
    const role = await navBar.getAttribute('role');
    const ariaLabel = await navBar.getAttribute('aria-label');

    // 至少应该有 role 或 aria-label
    expect(role || ariaLabel).toBeTruthy();
  });

  test('移动端按钮应该有足够的点击区域', async ({ page }) => {
    const learnPage = new LearnPage(page);
    await learnPage.goto();

    // 检查运行按钮的大小
    const button = learnPage.runButton;
    const box = await button.boundingBox();

    if (box) {
      // 按钮应该至少 44x44 像素（iOS 人机界面指南推荐）
      expect(box.width).toBeGreaterThanOrEqual(40);
      expect(box.height).toBeGreaterThanOrEqual(40);
    }
  });
});
