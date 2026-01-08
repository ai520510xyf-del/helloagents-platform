/**
 * localStorage 数据迁移工具
 *
 * 将现有的 localStorage 数据迁移到数据库
 */

const API_BASE_URL = 'http://localhost:8000';

interface ProgressData {
  chapter: number;
  lesson: number;
  completed: boolean;
  code?: string;
}

interface ChatMessageData {
  role: string;
  content: string;
}

interface LessonChatData {
  lesson_key: string;  // e.g., "1-1"
  messages: ChatMessageData[];
}

interface MigrationData {
  username?: string;
  progress_list?: ProgressData[];
  last_code?: Record<string, string>;
  chat_history?: LessonChatData[];
}

export interface MigrationResponse {
  success: boolean;
  message: string;
  user_id: number;
  migrated_progress: number;
  migrated_submissions: number;
  migrated_chat_messages: number;
}

/**
 * 从 localStorage 收集所有数据
 */
export function collectLocalStorageData(): MigrationData {
  const data: MigrationData = {
    username: 'local_user',
    progress_list: [],
    last_code: {},
    chat_history: []
  };

  try {
    // 1. 收集学习进度
    const progressStr = localStorage.getItem('helloagents_progress');
    if (progressStr) {
      const progress = JSON.parse(progressStr);

      // 当前课程
      if (progress.currentLesson) {
        const { chapter, lesson } = progress.currentLesson;
        data.progress_list!.push({
          chapter,
          lesson,
          completed: false
        });
      }

      // 已完成的课程
      if (Array.isArray(progress.completedLessons)) {
        progress.completedLessons.forEach((item: any) => {
          data.progress_list!.push({
            chapter: item.chapter,
            lesson: item.lesson,
            completed: true
          });
        });
      }

      // 最后保存的代码
      if (progress.lastCode && typeof progress.lastCode === 'object') {
        data.last_code = progress.lastCode;
      }
    }

    // 2. 收集聊天历史
    // 假设格式：helloagents_chat_1-1, helloagents_chat_1-2, ...
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('helloagents_chat_')) {
        const lessonKey = key.replace('helloagents_chat_', '');
        const chatStr = localStorage.getItem(key);

        if (chatStr) {
          try {
            const messages = JSON.parse(chatStr);
            if (Array.isArray(messages)) {
              data.chat_history!.push({
                lesson_key: lessonKey,
                messages: messages.map((msg: any) => ({
                  role: msg.role || 'user',
                  content: msg.content || msg.message || ''
                }))
              });
            }
          } catch (e) {
            console.warn(`Failed to parse chat history for ${lessonKey}:`, e);
          }
        }
      }
    }

  } catch (error) {
    console.error('Error collecting localStorage data:', error);
  }

  return data;
}

/**
 * 执行数据迁移
 */
export async function migrateToDatabase(data?: MigrationData): Promise<MigrationResponse> {
  // 如果没有提供数据，自动收集
  const migrationData = data || collectLocalStorageData();

  console.log('Starting migration with data:', migrationData);

  try {
    const response = await fetch(`${API_BASE_URL}/api/migrate/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(migrationData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Migration failed');
    }

    const result: MigrationResponse = await response.json();
    console.log('Migration completed:', result);

    return result;

  } catch (error) {
    console.error('Migration error:', error);
    throw error;
  }
}

/**
 * 清理 localStorage（迁移成功后）
 */
export function clearLocalStorageAfterMigration() {
  const keysToRemove = [];

  // 收集需要清理的键
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith('helloagents_')) {
      keysToRemove.push(key);
    }
  }

  // 删除
  keysToRemove.forEach(key => {
    localStorage.removeItem(key);
    console.log(`Removed localStorage key: ${key}`);
  });

  console.log(`Cleared ${keysToRemove.length} localStorage keys`);
}

/**
 * 完整的迁移流程（带确认）
 */
export async function performMigration(): Promise<{
  success: boolean;
  result?: MigrationResponse;
  error?: string;
}> {
  try {
    // 1. 收集数据
    const data = collectLocalStorageData();

    // 检查是否有数据需要迁移
    const hasData =
      (data.progress_list && data.progress_list.length > 0) ||
      (data.last_code && Object.keys(data.last_code).length > 0) ||
      (data.chat_history && data.chat_history.length > 0);

    if (!hasData) {
      return {
        success: true,
        result: {
          success: true,
          message: '没有需要迁移的数据',
          user_id: 1,
          migrated_progress: 0,
          migrated_submissions: 0,
          migrated_chat_messages: 0
        }
      };
    }

    // 2. 执行迁移
    const result = await migrateToDatabase(data);

    // 3. 迁移成功，清理 localStorage
    if (result.success) {
      clearLocalStorageAfterMigration();
    }

    return {
      success: true,
      result
    };

  } catch (error) {
    console.error('Migration failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

/**
 * 检查是否需要迁移
 */
export function needsMigration(): boolean {
  // 检查是否存在旧的 localStorage 数据
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith('helloagents_')) {
      return true;
    }
  }
  return false;
}

/**
 * 获取迁移预览
 */
export function getMigrationPreview(): {
  progressCount: number;
  codeCount: number;
  chatCount: number;
} {
  const data = collectLocalStorageData();

  return {
    progressCount: data.progress_list?.length || 0,
    codeCount: Object.keys(data.last_code || {}).length,
    chatCount: data.chat_history?.length || 0
  };
}
