/**
 * Monaco Editor 优化配置
 *
 * 只加载需要的语言支持，减少 bundle 大小
 * 默认只加载 Python 支持，其他语言按需加载
 */

import type * as Monaco from 'monaco-editor';

// 动态语言加载器映射
// 注意：Monaco 的基础语言模块没有类型定义，使用 any 类型
const languageLoaders: Record<string, () => Promise<any>> = {
  // @ts-expect-error - Monaco 基础语言模块没有类型定义
  python: () => import('monaco-editor/esm/vs/basic-languages/python/python.js'),
  // @ts-expect-error - Monaco 基础语言模块没有类型定义
  javascript: () => import('monaco-editor/esm/vs/basic-languages/javascript/javascript.js'),
  // @ts-expect-error - Monaco 基础语言模块没有类型定义
  typescript: () => import('monaco-editor/esm/vs/basic-languages/typescript/typescript.js'),
  // @ts-expect-error - Monaco 基础语言模块没有类型定义
  html: () => import('monaco-editor/esm/vs/basic-languages/html/html.js'),
  // @ts-expect-error - Monaco 基础语言模块没有类型定义
  css: () => import('monaco-editor/esm/vs/basic-languages/css/css.js'),
};

// 已加载的语言缓存
const loadedLanguages = new Set<string>(['python']); // Python 默认加载

/**
 * 按需加载语言支持
 * @param language 语言名称
 */
export async function loadLanguageSupport(language: string): Promise<void> {
  if (loadedLanguages.has(language)) {
    return; // 已经加载过了
  }

  const loader = languageLoaders[language];
  if (loader) {
    try {
      await loader();
      loadedLanguages.add(language);
      console.log(`[Monaco] Loaded language support: ${language}`);
    } catch (error) {
      console.error(`[Monaco] Failed to load language support for ${language}:`, error);
    }
  } else {
    console.warn(`[Monaco] No loader found for language: ${language}`);
  }
}

/**
 * 配置 Monaco Editor 环境
 * 优化 Worker 加载策略
 */
export function configureMonacoEnvironment(monaco: typeof Monaco): void {
  // 配置 Worker 路径
  (self as any).MonacoEnvironment = {
    getWorkerUrl: function (_moduleId: string, label: string) {
      // Python 不需要 Worker（基础语言支持）
      if (label === 'python') {
        return '';
      }

      // 其他语言的 Worker 按需加载
      switch (label) {
        case 'json':
          return new URL('monaco-editor/esm/vs/language/json/json.worker.js', import.meta.url).href;
        case 'css':
        case 'scss':
        case 'less':
          return new URL('monaco-editor/esm/vs/language/css/css.worker.js', import.meta.url).href;
        case 'html':
        case 'handlebars':
        case 'razor':
          return new URL('monaco-editor/esm/vs/language/html/html.worker.js', import.meta.url).href;
        case 'typescript':
        case 'javascript':
          return new URL('monaco-editor/esm/vs/language/typescript/ts.worker.js', import.meta.url).href;
        default:
          return new URL('monaco-editor/esm/vs/editor/editor.worker.js', import.meta.url).href;
      }
    },
  };

  // 配置编辑器默认选项
  monaco.editor.defineTheme('custom-dark', {
    base: 'vs-dark',
    inherit: true,
    rules: [],
    colors: {
      'editor.background': '#1e1e1e',
    },
  });

  console.log('[Monaco] Environment configured');
}

/**
 * 获取已加载的语言列表
 */
export function getLoadedLanguages(): string[] {
  return Array.from(loadedLanguages);
}

/**
 * 检查语言是否已加载
 */
export function isLanguageLoaded(language: string): boolean {
  return loadedLanguages.has(language);
}

/**
 * Monaco Editor 性能监控
 */
export function logMonacoPerformance(): void {
  if (typeof performance === 'undefined') return;

  const entries = performance.getEntriesByType('resource');
  const monacoResources = entries.filter(entry =>
    entry.name.includes('monaco-editor') ||
    entry.name.includes('worker')
  );

  if (monacoResources.length > 0) {
    console.group('[Monaco] Performance Metrics');
    monacoResources.forEach(resource => {
      const resourceEntry = resource as PerformanceResourceTiming;
      console.log(`${resource.name}:`, {
        size: `${(resourceEntry.transferSize / 1024).toFixed(2)} KB`,
        duration: `${resourceEntry.duration.toFixed(2)} ms`,
      });
    });
    console.groupEnd();
  }
}
