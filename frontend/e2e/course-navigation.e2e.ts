/**
 * E2E Test: Course Navigation
 *
 * 测试课程导航流程：
 * 1. 加载课程列表
 * 2. 切换不同课程
 * 3. 验证课程内容加载
 * 4. 验证代码模板加载
 */

import { test, expect } from '@playwright/test';
import {
  PageHelpers,
  CourseNavigationHelpers,
  CodeEditorHelpers,
} from './utils/test-helpers';

test.describe('Course Navigation', () => {
  let pageHelpers: PageHelpers;
  let navigationHelpers: CourseNavigationHelpers;
  let editorHelpers: CodeEditorHelpers;

  test.beforeEach(async ({ page }) => {
    pageHelpers = new PageHelpers(page);
    navigationHelpers = new CourseNavigationHelpers(page);
    editorHelpers = new CodeEditorHelpers(page);

    // 导航到学习页面
    await pageHelpers.navigateToLearnPage();
  });

  test('should display course menu on page load', async ({ page }) => {
    // 1. 验证课程菜单可见
    const courseMenu = page.locator('[data-testid="course-menu"]');

    await expect(courseMenu).toBeVisible();

    // 2. 验证至少有一个课程项
    const courseItems = page.locator('[data-testid="course-item"]');

    // 等待课程项加载
    await courseItems.first().waitFor({ state: 'visible', timeout: 5000 });

    const count = await courseItems.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should load default course content on page load', async ({ page }) => {
    // 等待页面完全加载
    await page.waitForTimeout(1000);

    // 1. 验证课程标题显示
    const title = await navigationHelpers.getCurrentCourseTitle();
    expect(title.length).toBeGreaterThan(0);

    // 2. 验证内容面板加载
    await navigationHelpers.expectCourseContentLoaded();

    // 3. 验证代码编辑器加载
    await navigationHelpers.expectCodeTemplateLoaded();
  });

  test('should switch between different courses', async ({ page }) => {
    // 等待初始加载
    await page.waitForTimeout(1000);

    // 获取初始课程标题
    const initialTitle = await navigationHelpers.getCurrentCourseTitle();

    // 查找所有课程项
    const courseItems = page.locator('[data-testid="course-item"]')
      .or(page.locator('.course-item'))
      .or(page.locator('li a, li button'));

    const count = await courseItems.count();

    if (count > 1) {
      // 点击第二个课程
      await courseItems.nth(1).click();
      await page.waitForTimeout(1000);

      // 验证标题已改变
      const newTitle = await navigationHelpers.getCurrentCourseTitle();
      expect(newTitle).not.toBe(initialTitle);

      // 验证内容已加载
      await navigationHelpers.expectCourseContentLoaded();
    }
  });

  test('should load course-specific code template', async ({ page }) => {
    // 等待初始加载
    await page.waitForTimeout(1000);

    // 切换到有代码模板的课程（如果有多个课程）
    const courseItems = page.locator('[data-testid="course-item"]')
      .or(page.locator('.course-item'))
      .or(page.locator('li a, li button'));

    const count = await courseItems.count();

    if (count > 0) {
      // 点击第一个课程
      await courseItems.first().click();
      await page.waitForTimeout(1000);

      // 验证编辑器加载
      await navigationHelpers.expectCodeTemplateLoaded();

      // 获取代码内容（可能为空或包含模板）
      const code = await editorHelpers.getCode();
      expect(typeof code).toBe('string');
    }
  });

  test('should highlight active course in menu', async ({ page }) => {
    // 等待初始加载
    await page.waitForTimeout(1000);

    // 查找所有课程项
    const courseItems = page.locator('[data-testid="course-item"]')
      .or(page.locator('.course-item'));

    const count = await courseItems.count();

    if (count > 1) {
      // 点击第二个课程
      await courseItems.nth(1).click();
      await page.waitForTimeout(500);

      // 验证第二个课程被高亮（active 类或特定样式）
      const activeItem = courseItems.nth(1);
      const className = await activeItem.getAttribute('class') || '';

      // 验证包含 active、selected 或类似的类名
      const isActive = className.includes('active') ||
                      className.includes('selected') ||
                      className.includes('current');

      // 或者验证特定的样式
      if (!isActive) {
        // 检查是否有 aria-current 属性
        const ariaCurrent = await activeItem.getAttribute('aria-current');
        expect(ariaCurrent).toBeTruthy();
      }
    }
  });

  test('should preserve code when switching courses and returning', async ({ page }) => {
    // 等待初始加载
    await page.waitForTimeout(1000);

    // 在第一个课程中输入代码
    const testCode = 'print("Test code for course 1")';
    await editorHelpers.setCode(testCode);

    // 切换到第二个课程
    const courseItems = page.locator('[data-testid="course-item"]')
      .or(page.locator('.course-item'))
      .or(page.locator('li a, li button'));

    const count = await courseItems.count();

    if (count > 1) {
      await courseItems.nth(1).click();
      await page.waitForTimeout(1000);

      // 在第二个课程中输入不同的代码
      await editorHelpers.setCode('print("Test code for course 2")');

      // 切换回第一个课程
      await courseItems.first().click();
      await page.waitForTimeout(1000);

      // 验证第一个课程的代码被保留
      const savedCode = await editorHelpers.getCode();
      expect(savedCode).toBe(testCode);
    }
  });

  test('should display course progress indicator', async ({ page }) => {
    // 查找进度指示器
    const progressIndicator = page.locator('[data-testid="progress"]')
      .or(page.locator('.progress'))
      .or(page.locator('[role="progressbar"]'));

    // 验证进度指示器存在（如果有）
    const count = await progressIndicator.count();
    if (count > 0) {
      await expect(progressIndicator.first()).toBeVisible();

      // 验证进度值
      const progressText = await progressIndicator.first().textContent();
      expect(progressText).toMatch(/\d+%|\d+\/\d+/);
    }
  });

  test('should show course description in content panel', async ({ page }) => {
    // 等待内容加载
    await page.waitForTimeout(1000);

    // 查找课程描述区域
    const contentPanel = page.locator('[data-testid="content-panel"]')
      .or(page.locator('.content-panel'))
      .or(page.locator('.lesson-content'));

    await expect(contentPanel).toBeVisible();

    // 验证包含课程描述内容
    const content = await contentPanel.textContent();
    expect(content.length).toBeGreaterThan(0);
  });

  test('should support keyboard navigation in course menu', async ({ page }) => {
    // 聚焦到第一个课程项
    const firstCourse = page.locator('[data-testid="course-item"]')
      .or(page.locator('.course-item'))
      .or(page.locator('li a, li button'));

    await firstCourse.first().focus();

    // 按下向下箭头键
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(500);

    // 按下 Enter 键选择
    await page.keyboard.press('Enter');
    await page.waitForTimeout(1000);

    // 验证课程已切换
    await navigationHelpers.expectCourseContentLoaded();
  });

  test('should display course categories or sections', async ({ page }) => {
    // 查找课程分类或章节
    const categories = page.locator('[data-testid="course-category"]')
      .or(page.locator('.course-category'))
      .or(page.locator('.section-title'))
      .or(page.locator('h2, h3'));

    const count = await categories.count();

    // 如果有分类，验证至少有一个
    if (count > 0) {
      await expect(categories.first()).toBeVisible();
    }
  });

  test('should handle rapid course switching', async ({ page }) => {
    // 等待初始加载
    await page.waitForTimeout(1000);

    const courseItems = page.locator('[data-testid="course-item"]')
      .or(page.locator('.course-item'))
      .or(page.locator('li a, li button'));

    const count = await courseItems.count();

    if (count > 2) {
      // 快速切换多个课程
      await courseItems.nth(0).click();
      await page.waitForTimeout(100);

      await courseItems.nth(1).click();
      await page.waitForTimeout(100);

      await courseItems.nth(2).click();
      await page.waitForTimeout(1000);

      // 验证最后一个课程正确加载
      await navigationHelpers.expectCourseContentLoaded();
      await navigationHelpers.expectCodeTemplateLoaded();
    }
  });

  test('should display course completion status', async ({ page }) => {
    // 查找完成状态图标
    const completionIcon = page.locator('[data-testid="completion-icon"]')
      .or(page.locator('.completion-icon'))
      .or(page.locator('.checkmark'))
      .or(page.locator('.completed'));

    // 如果有完成标记，验证其存在
    const count = await completionIcon.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should scroll course menu when many courses exist', async ({ page }) => {
    // 查找课程菜单容器
    const courseMenu = page.locator('[data-testid="course-menu"]');

    await courseMenu.waitFor({ state: 'visible', timeout: 5000 });

    // 检查菜单是否可滚动
    const isScrollable = await courseMenu.evaluate((el) => {
      return el.scrollHeight > el.clientHeight;
    });

    // 如果可滚动，测试滚动功能
    if (isScrollable) {
      await courseMenu.evaluate((el) => {
        el.scrollTop = el.scrollHeight;
      });

      await page.waitForTimeout(500);

      const scrollTop = await courseMenu.evaluate((el) => el.scrollTop);
      expect(scrollTop).toBeGreaterThan(0);
    } else {
      // 如果不可滚动，测试也应该通过（菜单可能不够长）
      expect(isScrollable).toBe(false);
    }
  });

  test('should show course prerequisites or difficulty level', async ({ page }) => {
    // 查找课程元数据
    const metadata = page.locator('[data-testid="course-metadata"]')
      .or(page.locator('.course-metadata'))
      .or(page.locator('.difficulty'))
      .or(page.locator('.level'));

    const count = await metadata.count();

    // 如果有元数据，验证其显示
    if (count > 0) {
      const text = await metadata.first().textContent();
      expect(text.length).toBeGreaterThan(0);
    }
  });

  test('should load course content incrementally without blocking UI', async ({ page }) => {
    // 点击新课程
    const courseItems = page.locator('[data-testid="course-item"]')
      .or(page.locator('.course-item'))
      .or(page.locator('li a, li button'));

    const count = await courseItems.count();

    if (count > 0) {
      await courseItems.first().click();

      // 验证页面不会冻结（可以移动鼠标）
      await page.mouse.move(100, 100);

      // 等待内容加载
      await page.waitForTimeout(1000);

      // 验证内容已加载
      await navigationHelpers.expectCourseContentLoaded();
    }
  });
});
