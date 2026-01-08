import { useState, useEffect } from 'react';
import { X, Database, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from './ui/Button';
import { Card, CardContent } from './ui/Card';
import {
  needsMigration,
  getMigrationPreview,
  performMigration,
  type MigrationResponse
} from '../utils/migrationHelper';

interface MigrationPromptProps {
  theme?: 'light' | 'dark';
}

export function MigrationPrompt({ theme = 'dark' }: MigrationPromptProps) {
  const [showPrompt, setShowPrompt] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [isMigrating, setIsMigrating] = useState(false);
  const [migrationComplete, setMigrationComplete] = useState(false);
  const [migrationResult, setMigrationResult] = useState<MigrationResponse | null>(null);
  const [migrationError, setMigrationError] = useState<string | null>(null);
  const [preview, setPreview] = useState({ progressCount: 0, codeCount: 0, chatCount: 0 });

  useEffect(() => {
    // 检查是否需要迁移
    const checkMigration = async () => {
      try {
        const needs = needsMigration();
        if (needs) {
          const previewData = getMigrationPreview();
          setPreview(previewData);
          setShowPrompt(true);
        }
      } catch (error) {
        console.error('检查迁移状态失败:', error);
      } finally {
        setIsChecking(false);
      }
    };

    checkMigration();
  }, []);

  const handleMigrate = async () => {
    setIsMigrating(true);
    setMigrationError(null);

    try {
      const result = await performMigration();

      if (result.success && result.result) {
        setMigrationResult(result.result);
        setMigrationComplete(true);
      } else {
        setMigrationError(result.error || '迁移失败，请重试');
      }
    } catch (error) {
      console.error('迁移失败:', error);
      setMigrationError(error instanceof Error ? error.message : '未知错误');
    } finally {
      setIsMigrating(false);
    }
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    // 添加标记，避免每次都显示提示
    localStorage.setItem('helloagents_migration_dismissed', 'true');
  };

  const handleClose = () => {
    setShowPrompt(false);
    // 迁移完成后刷新页面以加载新数据
    if (migrationComplete) {
      window.location.reload();
    }
  };

  // 如果不需要显示提示，不渲染任何内容
  if (!showPrompt || isChecking) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <Card className={`w-full max-w-md mx-4 ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-white border-gray-200'}`}>
        <CardContent className="p-6">
          {/* 标题栏 */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <Database className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className={`text-lg font-semibold ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>
                  检测到本地数据
                </h3>
                <p className={`text-sm ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
                  发现 localStorage 中的学习数据
                </p>
              </div>
            </div>
            {!migrationComplete && (
              <button
                onClick={handleDismiss}
                className={`p-1 rounded hover:bg-border transition-colors ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-500'}`}
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* 内容 */}
          {!migrationComplete ? (
            <>
              {/* 数据预览 */}
              <div className={`p-4 rounded-lg mb-4 ${theme === 'dark' ? 'bg-bg-dark' : 'bg-gray-50'}`}>
                <p className={`text-sm mb-3 ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}`}>
                  我们可以将您的学习数据迁移到数据库中：
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className={theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}>学习进度</span>
                    <span className="font-medium text-primary">{preview.progressCount} 个课程</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className={theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}>代码记录</span>
                    <span className="font-medium text-primary">{preview.codeCount} 份代码</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className={theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}>聊天历史</span>
                    <span className="font-medium text-primary">{preview.chatCount} 条对话</span>
                  </div>
                </div>
              </div>

              {/* 说明 */}
              <div className={`flex gap-2 p-3 rounded-lg mb-4 ${theme === 'dark' ? 'bg-warning/10 text-warning' : 'bg-yellow-50 text-yellow-800'}`}>
                <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
                <p className="text-xs leading-relaxed">
                  迁移后，您的数据将保存在数据库中，更加安全可靠。迁移完成后会自动清理 localStorage 数据。
                </p>
              </div>

              {/* 错误提示 */}
              {migrationError && (
                <div className={`flex gap-2 p-3 rounded-lg mb-4 ${theme === 'dark' ? 'bg-error/10 text-error' : 'bg-red-50 text-red-800'}`}>
                  <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
                  <div className="text-xs">
                    <p className="font-medium mb-1">迁移失败</p>
                    <p>{migrationError}</p>
                  </div>
                </div>
              )}

              {/* 操作按钮 */}
              <div className="flex gap-2">
                <Button
                  variant="primary"
                  onClick={handleMigrate}
                  isLoading={isMigrating}
                  disabled={isMigrating}
                  className="flex-1"
                >
                  立即迁移
                </Button>
                <Button
                  variant="secondary"
                  onClick={handleDismiss}
                  disabled={isMigrating}
                  className={theme === 'dark' ? '' : 'border-gray-300 hover:bg-gray-100'}
                >
                  稍后再说
                </Button>
              </div>

              <p className={`text-xs text-center mt-3 ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
                不迁移也可以继续使用，数据将保存在浏览器本地
              </p>
            </>
          ) : (
            /* 迁移完成 */
            <>
              <div className="text-center py-6">
                <div className="h-16 w-16 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="h-8 w-8 text-success" />
                </div>
                <h4 className={`text-lg font-semibold mb-2 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>
                  迁移完成！
                </h4>
                <p className={`text-sm mb-4 ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}>
                  您的学习数据已成功保存到数据库
                </p>

                {migrationResult && (
                  <div className={`p-4 rounded-lg mb-4 text-sm ${theme === 'dark' ? 'bg-bg-dark' : 'bg-gray-50'}`}>
                    <div className="space-y-1 text-left">
                      <p className={theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}>
                        ✅ 学习进度：{migrationResult.migrated_progress} 个
                      </p>
                      <p className={theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}>
                        ✅ 代码提交：{migrationResult.migrated_submissions} 份
                      </p>
                      <p className={theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}>
                        ✅ 聊天记录：{migrationResult.migrated_chat_messages} 条
                      </p>
                    </div>
                  </div>
                )}

                <Button
                  variant="primary"
                  onClick={handleClose}
                  className="w-full"
                >
                  完成
                </Button>

                <p className={`text-xs mt-3 ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
                  页面将自动刷新以加载新数据
                </p>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
