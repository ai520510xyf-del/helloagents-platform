/**
 * TabletLayout - 平板端布局组件
 *
 * 特性：
 * - 两栏布局：编辑器 + 内容/AI助手
 * - 可折叠的课程目录侧边栏
 * - 底部终端可收起/展开
 * - 优化的触摸交互
 */

import { useState, useCallback } from 'react';
import { Menu, X, ChevronUp, ChevronDown, Play, StopCircle, RotateCcw } from 'lucide-react';
import { Panel, Group, Separator } from 'react-resizable-panels';
import { CourseMenu } from './CourseMenu';
import { LazyCodeEditor } from '../LazyCodeEditor';
import { ContentPanel } from './ContentPanel';
import { Button } from '../ui/Button';
import { type Lesson } from '../../data/courses';
import { type ChatMessage } from '../../services/api';

interface TabletLayoutProps {
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

export function TabletLayout({
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
}: TabletLayoutProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isTerminalExpanded, setIsTerminalExpanded] = useState(false);

  const toggleMenu = useCallback(() => {
    setIsMenuOpen(prev => !prev);
  }, []);

  const toggleTerminal = useCallback(() => {
    setIsTerminalExpanded(prev => !prev);
  }, []);

  return (
    <div className={`h-full flex flex-col ${theme === 'dark' ? 'bg-bg-dark text-text-primary' : 'bg-white text-gray-900'}`}>
      {/* 主内容区 */}
      <div className={`flex-1 min-h-0 relative`}>
        {/* 课程目录侧边栏 - 可折叠 */}
        <div
          className={`absolute left-0 top-0 bottom-0 w-64 z-20 transform transition-transform duration-300 ${
            isMenuOpen ? 'translate-x-0' : '-translate-x-full'
          } ${theme === 'dark' ? 'bg-bg-surface' : 'bg-white'} shadow-lg`}
        >
          <div className="h-full flex flex-col">
            <div className={`h-12 flex items-center justify-between px-4 border-b ${theme === 'dark' ? 'border-border' : 'border-gray-200'}`}>
              <span className="font-semibold">课程目录</span>
              <button
                onClick={toggleMenu}
                className={`p-1 rounded hover:bg-opacity-10 hover:bg-gray-500 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <CourseMenu
                currentLesson={currentLesson}
                theme={theme}
                onLessonChange={(lessonId) => {
                  onLessonChange(lessonId);
                  setIsMenuOpen(false);
                }}
              />
            </div>
          </div>
        </div>

        {/* 遮罩层 */}
        {isMenuOpen && (
          <div
            className="absolute inset-0 bg-black bg-opacity-50 z-10"
            onClick={toggleMenu}
          />
        )}

        {/* 两栏布局 */}
        <div className="h-full">
          {/* @ts-expect-error - react-resizable-panels Group 类型定义问题 */}
          <Group direction="horizontal">
            {/* 左侧：代码编辑器 */}
            <Panel defaultSize={55} minSize={40} style={{ height: '100%', overflow: 'auto' }}>
              <div className="h-full flex flex-col">
                {/* 文件标签栏 + 菜单按钮 */}
                <div className={`h-12 border-b flex items-center px-4 gap-2 ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-100 border-gray-200'}`}>
                  <button
                    onClick={toggleMenu}
                    className={`p-1.5 rounded transition-colors ${
                      theme === 'dark'
                        ? 'hover:bg-bg-elevated text-text-primary'
                        : 'hover:bg-gray-200 text-gray-900'
                    }`}
                    data-testid="tablet-menu-toggle"
                  >
                    <Menu className="h-5 w-5" />
                  </button>
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
                  />
                </div>

                {/* 操作栏 */}
                <div className={`h-14 border-t flex items-center justify-between px-4 ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-100 border-gray-200'}`}>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={onRun}
                      isLoading={isRunning}
                      disabled={isRunning}
                      className="touch-manipulation"
                      data-testid="tablet-run-button"
                    >
                      <Play className="h-4 w-4 mr-1" />
                      运行
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={onStop}
                      disabled={!isRunning}
                      className="touch-manipulation"
                      data-testid="tablet-stop-button"
                    >
                      <StopCircle className="h-4 w-4 mr-1" />
                      停止
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={onReset}
                      className={`touch-manipulation ${theme === 'dark' ? '' : 'border-gray-300 hover:bg-gray-100 text-gray-700'}`}
                      data-testid="tablet-reset-button"
                    >
                      <RotateCcw className="h-4 w-4 mr-1" />
                      重置
                    </Button>
                  </div>

                  <div className={`text-xs ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
                    行 {cursorPosition.line}, 列 {cursorPosition.column}
                  </div>
                </div>
              </div>
            </Panel>

            <Separator className={`w-1 transition-colors ${
              theme === 'dark'
                ? 'bg-gray-700 hover:bg-blue-400'
                : 'bg-gray-300 hover:bg-blue-500'
            }`} />

            {/* 右侧：课程内容 + AI 助手 */}
            <Panel defaultSize={45} minSize={30} style={{ height: '100%', overflow: 'auto' }}>
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
            </Panel>
          </Group>
        </div>
      </div>

      {/* 终端输出 - 可收起 */}
      <div
        className={`border-t transition-all duration-300 ${
          isTerminalExpanded ? 'h-64' : 'h-12'
        } ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-white border-gray-200'}`}
      >
        <div className={`h-12 flex items-center justify-between px-4 border-b ${theme === 'dark' ? 'border-border' : 'border-gray-200'}`}>
          <div className={`flex items-center gap-2 text-sm ${theme === 'dark' ? '' : 'text-gray-900'}`}>
            <span>📟</span>
            <span className="font-medium">终端输出</span>
            {isRunning && (
              <span className="text-xs text-warning flex items-center gap-1">
                <span className="animate-pulse">⏳</span>
                运行中
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {isTerminalExpanded && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClearOutput}
                className="text-xs"
              >
                清空
              </Button>
            )}
            <button
              onClick={toggleTerminal}
              className={`p-1 rounded transition-colors ${
                theme === 'dark'
                  ? 'hover:bg-bg-elevated text-text-primary'
                  : 'hover:bg-gray-200 text-gray-900'
              }`}
              data-testid="tablet-terminal-toggle"
            >
              {isTerminalExpanded ? (
                <ChevronDown className="h-5 w-5" />
              ) : (
                <ChevronUp className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>

        {isTerminalExpanded && (
          <div className="h-52 overflow-y-auto custom-scrollbar p-4 font-mono text-sm">
            {output ? (
              <pre className={`whitespace-pre-wrap ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}`}>{output}</pre>
            ) : (
              <div className={`text-center py-8 ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
                点击 "运行" 按钮开始执行
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// 添加 displayName 以支持 React Fast Refresh
TabletLayout.displayName = 'TabletLayout';
