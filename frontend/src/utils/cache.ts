/**
 * 前端缓存管理系统
 *
 * 使用 IndexedDB 缓存课程内容，提升加载性能
 * 配合 Service Worker 实现完整的离线体验
 */

import { performanceMarker } from './performance';

// IndexedDB 配置
const DB_NAME = 'HelloAgentsCache';
const DB_VERSION = 1;
const LESSON_STORE = 'lessons';
const ASSET_STORE = 'assets';

// 缓存过期时间 (24小时)
const CACHE_EXPIRY_MS = 24 * 60 * 60 * 1000;

// 缓存项接口
interface CacheItem<T> {
  data: T;
  timestamp: number;
  version: string;
}

// 课程内容接口
interface LessonContent {
  lesson_id: string;
  title: string;
  content: string;
  code_template: string;
}

/**
 * 初始化 IndexedDB
 */
function initDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;

      // 创建课程存储
      if (!db.objectStoreNames.contains(LESSON_STORE)) {
        db.createObjectStore(LESSON_STORE, { keyPath: 'lesson_id' });
      }

      // 创建资源存储
      if (!db.objectStoreNames.contains(ASSET_STORE)) {
        db.createObjectStore(ASSET_STORE, { keyPath: 'url' });
      }
    };
  });
}

/**
 * 缓存管理类
 */
class CacheManager {
  private db: IDBDatabase | null = null;
  private initPromise: Promise<void> | null = null;

  /**
   * 初始化缓存管理器
   */
  async init(): Promise<void> {
    if (this.db) return;

    if (!this.initPromise) {
      this.initPromise = initDB().then((db) => {
        this.db = db;
      });
    }

    return this.initPromise;
  }

  /**
   * 获取存储对象
   */
  private getStore(storeName: string, mode: IDBTransactionMode = 'readonly'): IDBObjectStore {
    if (!this.db) {
      throw new Error('Database not initialized');
    }
    const transaction = this.db.transaction(storeName, mode);
    return transaction.objectStore(storeName);
  }

  /**
   * 检查缓存是否过期
   */
  private isExpired(timestamp: number): boolean {
    return Date.now() - timestamp > CACHE_EXPIRY_MS;
  }

  /**
   * 获取课程内容（带缓存）
   */
  async getLessonContent(lessonId: string): Promise<LessonContent | null> {
    try {
      await this.init();
      performanceMarker.start(`cache-read-lesson-${lessonId}`);

      const store = this.getStore(LESSON_STORE);
      const request = store.get(lessonId);

      const cacheItem = await new Promise<CacheItem<LessonContent> | undefined>((resolve, reject) => {
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });

      performanceMarker.end(`cache-read-lesson-${lessonId}`);

      // 检查缓存是否存在且未过期
      if (cacheItem && !this.isExpired(cacheItem.timestamp)) {
        console.log(`✅ Cache hit: Lesson ${lessonId}`);
        return cacheItem.data;
      }

      console.log(`❌ Cache miss: Lesson ${lessonId}`);
      return null;
    } catch (error) {
      console.error('Failed to get lesson from cache:', error);
      return null;
    }
  }

  /**
   * 缓存课程内容
   */
  async setLessonContent(lessonContent: LessonContent): Promise<void> {
    try {
      await this.init();
      performanceMarker.start(`cache-write-lesson-${lessonContent.lesson_id}`);

      const cacheItem: CacheItem<LessonContent> = {
        data: lessonContent,
        timestamp: Date.now(),
        version: '1.0.0', // 可以用于版本控制
      };

      const store = this.getStore(LESSON_STORE, 'readwrite');
      const request = store.put(cacheItem);

      await new Promise<void>((resolve, reject) => {
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });

      performanceMarker.end(`cache-write-lesson-${lessonContent.lesson_id}`);
      console.log(`💾 Cached: Lesson ${lessonContent.lesson_id}`);
    } catch (error) {
      console.error('Failed to cache lesson:', error);
    }
  }

  /**
   * 预加载课程内容
   */
  async prefetchLesson(lessonId: string, fetchFn: () => Promise<LessonContent>): Promise<LessonContent> {
    // 先尝试从缓存读取
    const cachedLesson = await this.getLessonContent(lessonId);
    if (cachedLesson) {
      return cachedLesson;
    }

    // 缓存未命中，从网络获取
    console.log(`🌐 Fetching from network: Lesson ${lessonId}`);
    const lesson = await fetchFn();

    // 保存到缓存
    await this.setLessonContent(lesson);

    return lesson;
  }

  /**
   * 批量预加载课程
   */
  async prefetchLessons(lessonIds: string[], fetchFn: (id: string) => Promise<LessonContent>): Promise<void> {
    console.log(`🚀 Prefetching ${lessonIds.length} lessons...`);

    // 使用 requestIdleCallback 在空闲时预加载
    if ('requestIdleCallback' in window) {
      for (const lessonId of lessonIds) {
        await new Promise<void>((resolve) => {
          requestIdleCallback(async () => {
            try {
              await this.prefetchLesson(lessonId, () => fetchFn(lessonId));
            } catch (error) {
              console.error(`Failed to prefetch lesson ${lessonId}:`, error);
            }
            resolve();
          });
        });
      }
    } else {
      // 降级：使用 setTimeout
      for (const lessonId of lessonIds) {
        await new Promise<void>((resolve) => {
          setTimeout(async () => {
            try {
              await this.prefetchLesson(lessonId, () => fetchFn(lessonId));
            } catch (error) {
              console.error(`Failed to prefetch lesson ${lessonId}:`, error);
            }
            resolve();
          }, 0);
        });
      }
    }

    console.log(`✅ Prefetch complete`);
  }

  /**
   * 清除过期缓存
   */
  async clearExpiredCache(): Promise<void> {
    try {
      await this.init();

      const store = this.getStore(LESSON_STORE, 'readwrite');
      const request = store.openCursor();

      let clearedCount = 0;

      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest<IDBCursorWithValue>).result;
        if (cursor) {
          const cacheItem = cursor.value as CacheItem<LessonContent>;
          if (this.isExpired(cacheItem.timestamp)) {
            cursor.delete();
            clearedCount++;
          }
          cursor.continue();
        } else {
          if (clearedCount > 0) {
            console.log(`🗑️ Cleared ${clearedCount} expired cache items`);
          }
        }
      };

      request.onerror = () => {
        console.error('Failed to clear expired cache:', request.error);
      };
    } catch (error) {
      console.error('Failed to clear expired cache:', error);
    }
  }

  /**
   * 清除所有缓存
   */
  async clearAllCache(): Promise<void> {
    try {
      await this.init();

      const lessonStore = this.getStore(LESSON_STORE, 'readwrite');
      const assetStore = this.getStore(ASSET_STORE, 'readwrite');

      await Promise.all([
        new Promise<void>((resolve, reject) => {
          const request = lessonStore.clear();
          request.onsuccess = () => resolve();
          request.onerror = () => reject(request.error);
        }),
        new Promise<void>((resolve, reject) => {
          const request = assetStore.clear();
          request.onsuccess = () => resolve();
          request.onerror = () => reject(request.error);
        }),
      ]);

      console.log('🗑️ All cache cleared');
    } catch (error) {
      console.error('Failed to clear all cache:', error);
    }
  }

  /**
   * 获取缓存统计
   */
  async getCacheStats(): Promise<{ lessonCount: number; totalSize: number }> {
    try {
      await this.init();

      const store = this.getStore(LESSON_STORE);
      const countRequest = store.count();

      const lessonCount = await new Promise<number>((resolve, reject) => {
        countRequest.onsuccess = () => resolve(countRequest.result);
        countRequest.onerror = () => reject(countRequest.error);
      });

      // 估算总大小（简化版本）
      const totalSize = lessonCount * 10; // 假设每个课程约 10KB

      return { lessonCount, totalSize };
    } catch (error) {
      console.error('Failed to get cache stats:', error);
      return { lessonCount: 0, totalSize: 0 };
    }
  }
}

// 导出单例
export const cacheManager = new CacheManager();

/**
 * 初始化缓存系统
 */
export async function initCacheSystem() {
  try {
    await cacheManager.init();
    console.log('💾 Cache system initialized');

    // 清除过期缓存
    await cacheManager.clearExpiredCache();

    // 打印缓存统计
    const stats = await cacheManager.getCacheStats();
    console.log(`📊 Cache stats: ${stats.lessonCount} lessons, ~${stats.totalSize}KB`);
  } catch (error) {
    console.error('Failed to initialize cache system:', error);
  }
}
