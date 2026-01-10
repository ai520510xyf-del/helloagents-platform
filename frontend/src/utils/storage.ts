/**
 * LocalStorage 工具类
 *
 * 提供类型安全的 localStorage 操作，统一错误处理
 */

import { logger } from './logger';

export class StorageManager {
  private prefix: string;

  constructor(prefix: string = '') {
    this.prefix = prefix;
  }

  /**
   * 获取完整的存储 key
   */
  private getKey(key: string): string {
    return this.prefix ? `${this.prefix}${key}` : key;
  }

  /**
   * 设置存储项
   */
  set<T>(key: string, value: T): boolean {
    try {
      const fullKey = this.getKey(key);
      const serialized = JSON.stringify(value);
      localStorage.setItem(fullKey, serialized);
      return true;
    } catch (error) {
      logger.error(`Failed to save to localStorage: ${key}`, error);
      return false;
    }
  }

  /**
   * 获取存储项
   */
  get<T>(key: string, defaultValue?: T): T | undefined {
    try {
      const fullKey = this.getKey(key);
      const item = localStorage.getItem(fullKey);

      if (item === null) {
        return defaultValue;
      }

      return JSON.parse(item) as T;
    } catch (error) {
      logger.error(`Failed to load from localStorage: ${key}`, error);
      return defaultValue;
    }
  }

  /**
   * 删除存储项
   */
  remove(key: string): boolean {
    try {
      const fullKey = this.getKey(key);
      localStorage.removeItem(fullKey);
      return true;
    } catch (error) {
      logger.error(`Failed to remove from localStorage: ${key}`, error);
      return false;
    }
  }

  /**
   * 清除所有带前缀的存储项
   */
  clear(): boolean {
    try {
      if (!this.prefix) {
        localStorage.clear();
        return true;
      }

      // 只清除带前缀的项
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(this.prefix)) {
          localStorage.removeItem(key);
        }
      });
      return true;
    } catch (error) {
      logger.error('Failed to clear localStorage', error);
      return false;
    }
  }

  /**
   * 检查存储项是否存在
   */
  has(key: string): boolean {
    const fullKey = this.getKey(key);
    return localStorage.getItem(fullKey) !== null;
  }

  /**
   * 获取所有键
   */
  keys(): string[] {
    const allKeys = Object.keys(localStorage);
    if (!this.prefix) {
      return allKeys;
    }
    return allKeys
      .filter(key => key.startsWith(this.prefix))
      .map(key => key.slice(this.prefix.length));
  }
}

// 导出默认实例
export const storage = new StorageManager();

// 导出特定用途的实例
export const lessonStorage = new StorageManager('helloagents_lesson_');
export const chatStorage = new StorageManager('helloagents_chat_');
export const themeStorage = new StorageManager('helloagents_');
