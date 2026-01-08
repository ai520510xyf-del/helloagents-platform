/**
 * MigrationPrompt 组件测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { MigrationPrompt } from './MigrationPrompt'
import * as migrationHelper from '../utils/migrationHelper'

// Mock migration helper functions
vi.mock('../utils/migrationHelper', () => ({
  needsMigration: vi.fn(),
  getMigrationPreview: vi.fn(),
  performMigration: vi.fn(),
  collectLocalStorageData: vi.fn(),
}))

describe('MigrationPrompt', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    // Mock window.location.reload
    delete (window as any).location
    window.location = { reload: vi.fn() } as any
  })

  describe('初始状态和显示条件', () => {
    it('应该在不需要迁移时不显示任何内容', async () => {
      vi.mocked(migrationHelper.needsMigration).mockReturnValue(false)

      const { container } = render(<MigrationPrompt />)

      await waitFor(() => {
        expect(container.firstChild).toBeNull()
      })
    })

    it('应该在需要迁移时显示提示框', async () => {
      vi.mocked(migrationHelper.needsMigration).mockReturnValue(true)
      vi.mocked(migrationHelper.getMigrationPreview).mockReturnValue({
        progressCount: 5,
        codeCount: 10,
        chatCount: 20,
      })

      render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('检测到本地数据')).toBeInTheDocument()
      })
    })

    it('应该显示正确的数据预览', async () => {
      vi.mocked(migrationHelper.needsMigration).mockReturnValue(true)
      vi.mocked(migrationHelper.getMigrationPreview).mockReturnValue({
        progressCount: 5,
        codeCount: 10,
        chatCount: 20,
      })

      render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('5 个课程')).toBeInTheDocument()
        expect(screen.getByText('10 份代码')).toBeInTheDocument()
        expect(screen.getByText('20 条对话')).toBeInTheDocument()
      })
    })

    it('应该支持 light 主题', async () => {
      vi.mocked(migrationHelper.needsMigration).mockReturnValue(true)
      vi.mocked(migrationHelper.getMigrationPreview).mockReturnValue({
        progressCount: 1,
        codeCount: 1,
        chatCount: 1,
      })

      const { container } = render(<MigrationPrompt theme="light" />)

      await waitFor(() => {
        const card = container.querySelector('.bg-white')
        expect(card).toBeInTheDocument()
      })
    })
  })

  describe('用户交互', () => {
    beforeEach(() => {
      vi.mocked(migrationHelper.needsMigration).mockReturnValue(true)
      vi.mocked(migrationHelper.getMigrationPreview).mockReturnValue({
        progressCount: 5,
        codeCount: 10,
        chatCount: 20,
      })
    })

    it('应该在点击"稍后再说"时关闭提示框', async () => {
      const { container } = render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('检测到本地数据')).toBeInTheDocument()
      })

      const dismissButton = screen.getByText('稍后再说')

      act(() => {
        fireEvent.click(dismissButton)
      })

      await waitFor(() => {
        expect(container.firstChild).toBeNull()
      })

      // 应该设置 localStorage 标记
      expect(localStorage.getItem('helloagents_migration_dismissed')).toBe('true')
    })

    it('应该在点击关闭按钮时关闭提示框', async () => {
      const { container } = render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('检测到本地数据')).toBeInTheDocument()
      })

      // 找到关闭按钮（X 图标的父按钮）
      const closeButton = container.querySelector('button[class*="hover:bg-border"]')
      expect(closeButton).toBeInTheDocument()

      fireEvent.click(closeButton!)

      await waitFor(() => {
        expect(container.firstChild).toBeNull()
      })
    })

    it('应该在点击"立即迁移"时执行迁移', async () => {
      vi.mocked(migrationHelper.performMigration).mockResolvedValue({
        success: true,
        result: {
          success: true,
          message: 'Migration completed',
          user_id: 1,
          migrated_progress: 5,
          migrated_submissions: 10,
          migrated_chat_messages: 20,
        },
      })

      render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('立即迁移')).toBeInTheDocument()
      })

      const migrateButton = screen.getByText('立即迁移')

      await act(async () => {
        fireEvent.click(migrateButton)
      })

      await waitFor(() => {
        expect(migrationHelper.performMigration).toHaveBeenCalledTimes(1)
      })
    })

    it('应该在迁移进行中禁用按钮', async () => {
      vi.mocked(migrationHelper.performMigration).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({
          success: true,
          result: {
            success: true,
            message: 'Migration completed',
            user_id: 1,
            migrated_progress: 5,
            migrated_submissions: 10,
            migrated_chat_messages: 20,
          },
        }), 100))
      )

      render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('立即迁移')).toBeInTheDocument()
      })

      const migrateButton = screen.getByText('立即迁移')

      await act(async () => {
        fireEvent.click(migrateButton)
      })

      // 检查按钮是否被禁用
      await waitFor(() => {
        const loadingButton = screen.getByText('加载中...')
        expect(loadingButton).toBeDisabled()
      })
    })
  })

  describe('迁移成功场景', () => {
    beforeEach(() => {
      vi.mocked(migrationHelper.needsMigration).mockReturnValue(true)
      vi.mocked(migrationHelper.getMigrationPreview).mockReturnValue({
        progressCount: 5,
        codeCount: 10,
        chatCount: 20,
      })
    })

    it('应该在迁移成功后显示成功界面', async () => {
      vi.mocked(migrationHelper.performMigration).mockResolvedValue({
        success: true,
        result: {
          success: true,
          message: 'Migration completed',
          user_id: 1,
          migrated_progress: 5,
          migrated_submissions: 10,
          migrated_chat_messages: 20,
        },
      })

      render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('立即迁移')).toBeInTheDocument()
      })

      const migrateButton = screen.getByText('立即迁移')

      await act(async () => {
        fireEvent.click(migrateButton)
      })

      await waitFor(() => {
        expect(screen.getByText('迁移完成！')).toBeInTheDocument()
      })
    })

    it('应该显示迁移结果统计', async () => {
      vi.mocked(migrationHelper.performMigration).mockResolvedValue({
        success: true,
        result: {
          success: true,
          message: 'Migration completed',
          user_id: 1,
          migrated_progress: 5,
          migrated_submissions: 10,
          migrated_chat_messages: 20,
        },
      })

      render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('立即迁移')).toBeInTheDocument()
      })

      const migrateButton = screen.getByText('立即迁移')

      await act(async () => {
        fireEvent.click(migrateButton)
      })

      await waitFor(() => {
        expect(screen.getByText(/学习进度.*5 个/)).toBeInTheDocument()
        expect(screen.getByText(/代码提交.*10 份/)).toBeInTheDocument()
        expect(screen.getByText(/聊天记录.*20 条/)).toBeInTheDocument()
      })
    })

    it('应该在点击"完成"后刷新页面', async () => {
      vi.mocked(migrationHelper.performMigration).mockResolvedValue({
        success: true,
        result: {
          success: true,
          message: 'Migration completed',
          user_id: 1,
          migrated_progress: 5,
          migrated_submissions: 10,
          migrated_chat_messages: 20,
        },
      })

      render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('立即迁移')).toBeInTheDocument()
      })

      const migrateButton = screen.getByText('立即迁移')

      await act(async () => {
        fireEvent.click(migrateButton)
      })

      await waitFor(() => {
        expect(screen.getByText('完成')).toBeInTheDocument()
      })

      const completeButton = screen.getByText('完成')
      fireEvent.click(completeButton)

      expect(window.location.reload).toHaveBeenCalledTimes(1)
    })

    it('应该在迁移成功后隐藏关闭按钮', async () => {
      vi.mocked(migrationHelper.performMigration).mockResolvedValue({
        success: true,
        result: {
          success: true,
          message: 'Migration completed',
          user_id: 1,
          migrated_progress: 5,
          migrated_submissions: 10,
          migrated_chat_messages: 20,
        },
      })

      const { container } = render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('立即迁移')).toBeInTheDocument()
      })

      // 确认关闭按钮存在
      const closeButton = container.querySelector('button[class*="hover:bg-border"]')
      expect(closeButton).toBeInTheDocument()

      const migrateButton = screen.getByText('立即迁移')

      await act(async () => {
        fireEvent.click(migrateButton)
      })

      await waitFor(() => {
        expect(screen.getByText('迁移完成！')).toBeInTheDocument()
      })

      // 关闭按钮应该消失
      const closeButtonAfter = container.querySelector('button[class*="hover:bg-border"]')
      expect(closeButtonAfter).not.toBeInTheDocument()
    })
  })

  describe('迁移失败场景', () => {
    beforeEach(() => {
      vi.mocked(migrationHelper.needsMigration).mockReturnValue(true)
      vi.mocked(migrationHelper.getMigrationPreview).mockReturnValue({
        progressCount: 5,
        codeCount: 10,
        chatCount: 20,
      })
    })

    it('应该在迁移失败时显示错误信息', async () => {
      vi.mocked(migrationHelper.performMigration).mockResolvedValue({
        success: false,
        error: '数据库连接失败',
      })

      render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('立即迁移')).toBeInTheDocument()
      })

      const migrateButton = screen.getByText('立即迁移')

      await act(async () => {
        fireEvent.click(migrateButton)
      })

      await waitFor(() => {
        expect(screen.getByText('迁移失败')).toBeInTheDocument()
        expect(screen.getByText('数据库连接失败')).toBeInTheDocument()
      })
    })

    it('应该在迁移失败时保持在当前界面', async () => {
      vi.mocked(migrationHelper.performMigration).mockResolvedValue({
        success: false,
        error: '迁移失败',
      })

      render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('立即迁移')).toBeInTheDocument()
      })

      const migrateButton = screen.getByText('立即迁移')

      await act(async () => {
        fireEvent.click(migrateButton)
      })

      await waitFor(() => {
        expect(screen.getAllByText('迁移失败').length).toBeGreaterThan(0)
      })

      // 应该仍然显示迁移按钮
      expect(screen.getByText('立即迁移')).toBeInTheDocument()
      // 不应该显示成功界面
      expect(screen.queryByText('迁移完成！')).not.toBeInTheDocument()
    })

    it('应该处理迁移返回无结果的情况', async () => {
      vi.mocked(migrationHelper.performMigration).mockResolvedValue({
        success: true,
        result: undefined,
      })

      render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('立即迁移')).toBeInTheDocument()
      })

      const migrateButton = screen.getByText('立即迁移')

      await act(async () => {
        fireEvent.click(migrateButton)
      })

      await waitFor(() => {
        expect(screen.getByText('迁移失败')).toBeInTheDocument()
        expect(screen.getByText('迁移失败，请重试')).toBeInTheDocument()
      })
    })

    it('应该处理迁移抛出异常的情况', async () => {
      const errorMessage = '网络错误'
      vi.mocked(migrationHelper.performMigration).mockRejectedValue(
        new Error(errorMessage)
      )

      render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('立即迁移')).toBeInTheDocument()
      })

      const migrateButton = screen.getByText('立即迁移')

      await act(async () => {
        fireEvent.click(migrateButton)
      })

      await waitFor(() => {
        expect(screen.getByText('迁移失败')).toBeInTheDocument()
        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })
    })

    it('应该允许在失败后重试迁移', async () => {
      vi.mocked(migrationHelper.performMigration)
        .mockResolvedValueOnce({
          success: false,
          error: '第一次失败',
        })
        .mockResolvedValueOnce({
          success: true,
          result: {
            success: true,
            message: 'Migration completed',
            user_id: 1,
            migrated_progress: 5,
            migrated_submissions: 10,
            migrated_chat_messages: 20,
          },
        })

      render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('立即迁移')).toBeInTheDocument()
      })

      // 第一次尝试
      const migrateButton = screen.getByText('立即迁移')

      await act(async () => {
        fireEvent.click(migrateButton)
      })

      await waitFor(() => {
        expect(screen.getByText('第一次失败')).toBeInTheDocument()
      })

      // 第二次尝试
      const retryButton = screen.getByText('立即迁移')

      await act(async () => {
        fireEvent.click(retryButton)
      })

      await waitFor(() => {
        expect(screen.getByText('迁移完成！')).toBeInTheDocument()
      })

      expect(migrationHelper.performMigration).toHaveBeenCalledTimes(2)
    })
  })

  describe('边界情况', () => {
    it('应该处理零数据的情况', async () => {
      vi.mocked(migrationHelper.needsMigration).mockReturnValue(true)
      vi.mocked(migrationHelper.getMigrationPreview).mockReturnValue({
        progressCount: 0,
        codeCount: 0,
        chatCount: 0,
      })

      render(<MigrationPrompt />)

      await waitFor(() => {
        expect(screen.getByText('0 个课程')).toBeInTheDocument()
        expect(screen.getByText('0 份代码')).toBeInTheDocument()
        expect(screen.getByText('0 条对话')).toBeInTheDocument()
      })
    })

    it('应该处理检查迁移状态时的异常', async () => {
      vi.mocked(migrationHelper.needsMigration).mockImplementation(() => {
        throw new Error('检查失败')
      })

      const { container } = render(<MigrationPrompt />)

      // 应该不显示任何内容，不会崩溃
      await waitFor(() => {
        expect(container.firstChild).toBeNull()
      })
    })
  })
})
