/**
 * MobileLayout - 移动端专用布局组件
 *
 * 特性：
 * - Tab切换不同视图（目录、编辑器、内容、终端）
 * - 触摸友好的操作按钮
 * - 优化的滚动体验
 * - 支持暗黑/亮色主题
 */

import { useState, useCallback } from 'react';
import { Menu, Code, BookOpen, Terminal, Play, StopCircle, RotateCcw } from 'lucide-react';
import { CourseMenu } from './CourseMenu';
import { LazyCodeEditor } from '../LazyCodeEditor';
import { ContentPanel } from './ContentPanel';
import { TerminalOutput } from './TerminalOutput';
import { Button } from '../ui/Button';
import { type Lesson } from '../../data/courses';
import { type ChatMessage } from '../../services/api';

type MobileTab = 'menu' | 'editor' | 'content' | 'terminal';

interface MobileLayoutProps {
  // 课程相关
  currentLesson: Lesson;
  onLessonChange: (lessonId: string) => void;

  // 代码编辑器
  code: string;
  onCodeChange: (code: string) => void;
  cursorPosition: { line: number; column: number };
  onCursorChange: (position: { line: number; column: number }) => void;

  // 代码执行
  isRunning: boolean;
  output: string;
  onRun: () => void;
  onStop: () => void;
  onReset: () => void;
  onClearOutput: () => void;

  // 内容面板
  activeContentTab: 'content' | 'ai';
  onContentTabChange: (tab: 'content' | 'ai') => void;
  chatMessages: ChatMessage[];
  chatInput: string;
  onChatInputChange: (input: string) => void;
  isChatLoading: boolean;
  onSendMessage: () => void;
  onRegenerateMessage: (index: number) => void;

  // 主题
  theme: 'light' | 'dark';
}

export function MobileLayout({
  currentLesson,
  onLessonChange,
  code,
  onCodeChange,
  cursorPosition,
  onCursorChange,
  isRunning,
  output,
  onRun,
  onStop,
  onReset,
  onClearOutput,
  activeContentTab,
  onContentTabChange,
  chatMessages,
  chatInput,
  onChatInputChange,
  isChatLoading,
  onSendMessage,
  onRegenerateMessage,
  theme,
}: MobileLayoutProps) {
  const [activeTab, setActiveTab] = useState<MobileTab>('editor');

  const tabs = [
    { id: 'menu' as const, label: '目录', icon: Menu },
    { id: 'editor' as const, label: '编辑器', icon: Code },
    { id: 'content' as const, label: '课程', icon: BookOpen },
    { id: 'terminal' as const, label: '终端', icon: Terminal },
  ];

  const handleTabChange = useCallback((tab: MobileTab) => {
    setActiveTab(tab);
  }, []);

  return (
    <div className={`h-full flex flex-col ${theme === 'dark' ? 'bg-bg-dark text-text-primary' : 'bg-white text-gray-900'}`}>
      {/* 底部导航栏 */}
      <div className={`order-2 flex-shrink-0 border-t safe-area-inset-bottom ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-white border-gray-200'} shadow-lg`}>
        <div className="flex items-center justify-around h-16">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                className={`flex flex-col items-center justify-center flex-1 h-full gap-1 transition-all duration-200 touch-manipulation active:scale-95 relative ${
                  isActive
                    ? 'text-primary'
                    : (theme === 'dark' ? 'text-text-secondary hover:text-text-primary' : 'text-gray-500 hover:text-gray-900')
                }`}
                data-testid={`mobile-tab-${tab.id}`}
                aria-label={tab.label}
                aria-selected={isActive}
              >
                {/* 活动指示器 */}
                {isActive && (
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 w-12 h-1 bg-primary rounded-full" />
                )}
                <Icon className={`h-5 w-5 transition-transform ${isActive ? 'scale-110' : ''}`} />
                <span className="text-xs font-medium">{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 主内容区 - 使用 order-1 让它在上面 */}
      <div className="order-1 flex-1 overflow-hidden">
        {/* 课程目录 */}
        {activeTab === 'menu' && (
          <div className="h-full tab-transition">
            <CourseMenu
              currentLesson={currentLesson}
              theme={theme}
              onLessonChange={(lessonId) => {
                onLessonChange(lessonId);
                // 切换课程后自动跳转到编辑器
                setActiveTab('editor');
              }}
            />
          </div>
        )}

        {/* 代码编辑器 */}
        {activeTab === 'editor' && (
          <div className="h-full flex flex-col tab-transition">
            {/* 文件标签栏 */}
            <div className={`h-12 border-b flex items-center px-4 gap-2 flex-shrink-0 ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-100 border-gray-200'}`}>
              <div className={`flex items-center gap-2 px-3 py-1.5 border-t-2 border-primary text-sm ${theme === 'dark' ? 'bg-bg-dark' : 'bg-white'}`}>
                <span>lesson_{currentLesson.id.replace('.', '_')}.py</span>
              </div>
            </div>

            {/* Monaco Editor (Lazy Loaded) */}
            <div className="flex-1 min-h-0">
              <LazyCodeEditor
                value={code}
                onChange={(value) => onCodeChange(value || '')}
                onCursorChange={onCursorChange}
                language="python"
                height="100%"
                theme={theme}
                isMobile={true}
              />
            </div>

            {/* 操作栏 */}
            <div className={`h-16 border-t flex items-center justify-between px-4 gap-2 flex-shrink-0 ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-100 border-gray-200'}`}>
              <div className="flex items-center gap-2">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={onRun}
                  isLoading={isRunning}
                  disabled={isRunning}
                  className="touch-manipulation"
                  data-testid="mobile-run-button"
                >
                  <Play className="h-4 w-4" />
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={onStop}
                  disabled={!isRunning}
                  className="touch-manipulation"
                  data-testid="mobile-stop-button"
                >
                  <StopCircle className="h-4 w-4" />
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={onReset}
                  className={`touch-manipulation ${theme === 'dark' ? '' : 'border-gray-300 hover:bg-gray-100 text-gray-700'}`}
                  data-testid="mobile-reset-button"
                >
                  <RotateCcw className="h-4 w-4" />
                </Button>
              </div>

              <div className={`text-xs ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
                {cursorPosition.line}:{cursorPosition.column}
              </div>
            </div>
          </div>
        )}

        {/* 课程内容 */}
        {activeTab === 'content' && (
          <div className="h-full tab-transition">
            <ContentPanel
              activeTab={activeContentTab}
              onTabChange={onContentTabChange}
              currentLesson={currentLesson}
              theme={theme}
              chatMessages={chatMessages}
              chatInput={chatInput}
              onChatInputChange={onChatInputChange}
              isChatLoading={isChatLoading}
              onSendMessage={onSendMessage}
              onRegenerateMessage={onRegenerateMessage}
            />
          </div>
        )}

        {/* 终端输出 */}
        {activeTab === 'terminal' && (
          <div className="h-full tab-transition">
            <TerminalOutput
              output={output}
              isRunning={isRunning}
              theme={theme}
              onClear={onClearOutput}
            />
          </div>
        )}
      </div>
    </div>
  );
}

// 添加 displayName 以支持 React Fast Refresh
MobileLayout.displayName = 'MobileLayout';
