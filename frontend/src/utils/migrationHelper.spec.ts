/**
 * 迁移工具函数测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  needsMigration,
  getMigrationPreview,
  collectLocalStorageData
} from './migrationHelper'

describe('migrationHelper', () => {
  beforeEach(() => {
    // 清空 localStorage
    localStorage.clear()
    vi.clearAllMocks()
  })

  describe('needsMigration', () => {
    it('应该在 localStorage 中有 helloagents_ 数据时返回 true', () => {
      localStorage.setItem('helloagents_lesson_code_1', 'print("test")')
      expect(needsMigration()).toBe(true)
    })

    it('应该在 localStorage 中没有 helloagents_ 数据时返回 false', () => {
      localStorage.setItem('other_key', 'value')
      expect(needsMigration()).toBe(false)
    })

    it('应该在 localStorage 为空时返回 false', () => {
      expect(needsMigration()).toBe(false)
    })
  })

  describe('getMigrationPreview', () => {
    it('应该返回正确的数据预览', () => {
      // 设置测试数据
      localStorage.setItem('helloagents_progress', JSON.stringify({
        currentLesson: { chapter: 1, lesson: 1 },
        completedLessons: [{ chapter: 1, lesson: 1 }, { chapter: 1, lesson: 2 }],
        lastCode: { '1-1': 'code1', '1-2': 'code2' }
      }))
      localStorage.setItem('helloagents_chat_1-1', JSON.stringify([
        { role: 'user', content: 'Hello' }
      ]))

      const preview = getMigrationPreview()

      expect(preview.progressCount).toBe(3) // 1 current + 2 completed
      expect(preview.codeCount).toBe(2)
      expect(preview.chatCount).toBe(1)
    })

    it('应该在没有数据时返回零值', () => {
      const preview = getMigrationPreview()

      expect(preview.progressCount).toBe(0)
      expect(preview.codeCount).toBe(0)
      expect(preview.chatCount).toBe(0)
    })
  })

  describe('collectLocalStorageData', () => {
    it('应该正确收集学习进度数据', () => {
      localStorage.setItem('helloagents_progress', JSON.stringify({
        currentLesson: { chapter: 1, lesson: 1 },
        completedLessons: [{ chapter: 1, lesson: 2 }]
      }))

      const data = collectLocalStorageData()

      expect(data.progress_list).toHaveLength(2)
      expect(data.progress_list?.[0]).toMatchObject({
        chapter: 1,
        lesson: 1,
        completed: false
      })
      expect(data.progress_list?.[1]).toMatchObject({
        chapter: 1,
        lesson: 2,
        completed: true
      })
    })

    it('应该正确收集代码数据', () => {
      localStorage.setItem('helloagents_progress', JSON.stringify({
        lastCode: { '1-1': 'print("test")', '1-2': 'print("test2")' }
      }))

      const data = collectLocalStorageData()

      expect(data.last_code).toMatchObject({
        '1-1': 'print("test")',
        '1-2': 'print("test2")'
      })
    })

    it('应该正确收集聊天历史', () => {
      localStorage.setItem('helloagents_chat_1-1', JSON.stringify([
        { role: 'user', content: 'Hello' },
        { role: 'assistant', content: 'Hi' }
      ]))

      const data = collectLocalStorageData()

      expect(data.chat_history).toHaveLength(1)
      expect(data.chat_history?.[0].lesson_key).toBe('1-1')
      expect(data.chat_history?.[0].messages).toHaveLength(2)
    })

    it('应该处理无效的 JSON 数据', () => {
      localStorage.setItem('helloagents_progress', 'invalid json')

      const data = collectLocalStorageData()

      // 应该返回空数据而不是抛出错误
      expect(data.progress_list).toEqual([])
    })

    it('应该处理不完整的进度数据', () => {
      localStorage.setItem('helloagents_progress', JSON.stringify({
        currentLesson: null,
        completedLessons: []
      }))

      const data = collectLocalStorageData()

      expect(data.progress_list).toEqual([])
    })
  })
})
