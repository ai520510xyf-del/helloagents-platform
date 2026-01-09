/**
 * LearnPage - 学习页面主组件（重构版）
 *
 * 采用组件化和自定义 Hooks 架构：
 * - 自定义 Hooks：useLesson, useChatMessages, useCodeExecution, useLocalStorage
 * - 拆分组件：NavigationBar, CourseMenu, CodeEditorPanel, ContentPanel, TerminalOutput
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { Panel, Group, Separator } from 'react-resizable-panels';
import { MigrationPrompt } from '../components/MigrationPrompt';
import { NavigationBar } from '../components/learn/NavigationBar';
import { CourseMenu } from '../components/learn/CourseMenu';
import { CodeEditorPanel } from '../components/learn/CodeEditorPanel';
import { ContentPanel } from '../components/learn/ContentPanel';
import { TerminalOutput } from '../components/learn/TerminalOutput';
import { MobileLayout } from '../components/learn/MobileLayout';
import { TabletLayout } from '../components/learn/TabletLayout';
import { calculateProgress } from '../data/courses';
import { useLesson } from '../hooks/useLesson';
import { useChatMessages } from '../hooks/useChatMessages';
import { useCodeExecution } from '../hooks/useCodeExecution';
import { useResponsiveLayout } from '../hooks/useResponsiveLayout';

const STORAGE_PREFIX = 'helloagents_lesson_code_';
const THEME_KEY = 'helloagents_theme';

export function LearnPage() {
  // 响应式布局检测
  const { layoutType } = useResponsiveLayout();

  // 课程管理
  const { currentLesson, changeLesson } = useLesson();

  // 主题管理
  const loadThemeFromStorage = (): 'light' | 'dark' => {
    try {
      const savedTheme = localStorage.getItem(THEME_KEY);
      return (savedTheme === 'light' || savedTheme === 'dark') ? savedTheme : 'dark';
    } catch (error) {
      console.error('加载主题失败:', error);
      return 'dark';
    }
  };

  const [theme, setTheme] = useState<'light' | 'dark'>(loadThemeFromStorage());

  // 代码编辑器状态
  const loadCodeFromStorage = (lessonId: string): string => {
    try {
      const savedCode = localStorage.getItem(STORAGE_PREFIX + lessonId);
      return savedCode || '';
    } catch (error) {
      console.error('加载本地缓存失败:', error);
      return '';
    }
  };

  const [code, setCode] = useState(loadCodeFromStorage(currentLesson.id));
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });
  const [activeTab, setActiveTab] = useState<'content' | 'ai'>('content');

  // 聊天消息管理
  const {
    chatMessages,
    chatInput,
    setChatInput,
    isChatLoading,
    sendMessage,
  } = useChatMessages(currentLesson.id, code);

  // 代码执行管理
  const { isRunning, output, runCode, stopExecution, clearOutput } = useCodeExecution();

  // 应用主题到 document
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (error) {
      console.error('保存主题失败:', error);
    }
  }, [theme]);

  // 自动保存代码到本地存储
  useEffect(() => {
    if (currentLesson) {
      try {
        localStorage.setItem(STORAGE_PREFIX + currentLesson.id, code);
      } catch (error) {
        console.error('保存本地缓存失败:', error);
      }
    }
  }, [code, currentLesson]);

  // 切换主题 - 使用 useCallback 稳定引用
  const toggleTheme = useCallback(() => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  }, []);

  // 切换课程 - 使用 useCallback 稳定引用
  const handleLessonChange = useCallback(async (lessonId: string) => {
    await changeLesson(lessonId);

    // 从本地缓存加载该课程的代码和聊天历史
    const savedCode = loadCodeFromStorage(lessonId);
    setCode(savedCode);

    // 重置其他状态
    clearOutput();
  }, [changeLesson, clearOutput]);

  // 重置代码 - 使用 useCallback 稳定引用
  const handleReset = useCallback(() => {
    if (!currentLesson) return;

    // 清除当前课程的本地缓存
    try {
      localStorage.removeItem(STORAGE_PREFIX + currentLesson.id);
    } catch (error) {
      console.error('清除本地缓存失败:', error);
    }

    // 重置代码区域为空
    setCode('');
    clearOutput();
  }, [currentLesson, clearOutput]);

  // 运行代码 - 使用 useCallback 稳定引用
  const handleRunCode = useCallback(() => {
    runCode(code);
  }, [code, runCode]);

  // 代码变更 - 使用 useCallback 稳定引用
  const handleCodeChange = useCallback((newCode: string) => {
    setCode(newCode);
  }, []);

  // 光标位置变更 - 使用 useCallback 稳定引用
  const handleCursorChange = useCallback((position: { line: number; column: number }) => {
    setCursorPosition(position);
  }, []);

  // 计算当前进度 - 使用 useMemo 缓存计算结果
  const progress = useMemo(() => calculateProgress(), []);

  // 移动端布局
  if (layoutType === 'mobile') {
    return (
      <>
        <MigrationPrompt theme={theme} />
        <div className={`h-screen flex flex-col ${theme === 'dark' ? 'bg-bg-dark text-text-primary' : 'bg-white text-gray-900'}`}>
          <NavigationBar
            currentLesson={currentLesson}
            progress={progress}
            theme={theme}
            onToggleTheme={toggleTheme}
          />
          <div className="flex-1 min-h-0" style={{ marginTop: '0.5rem' }}>
            <MobileLayout
              currentLesson={currentLesson}
              onLessonChange={handleLessonChange}
              code={code}
              onCodeChange={handleCodeChange}
              cursorPosition={cursorPosition}
              onCursorChange={handleCursorChange}
              isRunning={isRunning}
              output={output}
              onRun={handleRunCode}
              onStop={stopExecution}
              onReset={handleReset}
              onClearOutput={clearOutput}
              activeContentTab={activeTab}
              onContentTabChange={setActiveTab}
              chatMessages={chatMessages}
              chatInput={chatInput}
              onChatInputChange={setChatInput}
              isChatLoading={isChatLoading}
              onSendMessage={sendMessage}
              theme={theme}
            />
          </div>
        </div>
      </>
    );
  }

  // 平板布局
  if (layoutType === 'tablet') {
    return (
      <>
        <MigrationPrompt theme={theme} />
        <div className={`h-screen flex flex-col ${theme === 'dark' ? 'bg-bg-dark text-text-primary' : 'bg-white text-gray-900'}`}>
          <NavigationBar
            currentLesson={currentLesson}
            progress={progress}
            theme={theme}
            onToggleTheme={toggleTheme}
          />
          <div className="flex-1 min-h-0" style={{ marginTop: '0.5rem' }}>
            <TabletLayout
              currentLesson={currentLesson}
              onLessonChange={handleLessonChange}
              code={code}
              onCodeChange={handleCodeChange}
              cursorPosition={cursorPosition}
              onCursorChange={handleCursorChange}
              isRunning={isRunning}
              output={output}
              onRun={handleRunCode}
              onStop={stopExecution}
              onReset={handleReset}
              onClearOutput={clearOutput}
              activeContentTab={activeTab}
              onContentTabChange={setActiveTab}
              chatMessages={chatMessages}
              chatInput={chatInput}
              onChatInputChange={setChatInput}
              isChatLoading={isChatLoading}
              onSendMessage={sendMessage}
              theme={theme}
            />
          </div>
        </div>
      </>
    );
  }

  // 桌面布局（默认三栏布局）
  return (
    <>
      {/* 数据迁移提示 */}
      <MigrationPrompt theme={theme} />

      <div className={`h-screen flex flex-col ${theme === 'dark' ? 'bg-bg-dark text-text-primary' : 'bg-white text-gray-900'}`}>
        {/* 顶部导航栏 */}
        <NavigationBar
          currentLesson={currentLesson}
          progress={progress}
          theme={theme}
          onToggleTheme={toggleTheme}
        />

        {/* 主内容区 */}
        <div style={{ marginTop: '0.5rem', height: 'calc(100vh - 0.5rem - 70px)' }}>
          {/* 上半部分：三栏布局 */}
          <div style={{ height: '70%' }}>
            {/* @ts-expect-error - react-resizable-panels Group 类型定义问题 */}
            <Group direction="horizontal">
              {/* 左侧：课程目录 */}
              <Panel defaultSize={20} minSize={15} style={{ height: '100%', overflow: 'auto' }}>
                <CourseMenu
                  currentLesson={currentLesson}
                  theme={theme}
                  onLessonChange={handleLessonChange}
                />
              </Panel>

              <Separator className={`w-1 transition-colors ${
                theme === 'dark'
                  ? 'bg-gray-700 hover:bg-blue-400'
                  : 'bg-gray-300 hover:bg-blue-500'
              }`} />

              {/* 中间：代码编辑器 */}
              <Panel defaultSize={50} minSize={380} style={{ height: '100%', overflow: 'auto' }}>
                <CodeEditorPanel
                  code={code}
                  onCodeChange={handleCodeChange}
                  cursorPosition={cursorPosition}
                  onCursorChange={handleCursorChange}
                  currentLesson={currentLesson}
                  theme={theme}
                  isRunning={isRunning}
                  onRun={handleRunCode}
                  onStop={stopExecution}
                  onReset={handleReset}
                />
              </Panel>

              <Separator className={`w-1 transition-colors ${
                theme === 'dark'
                  ? 'bg-gray-700 hover:bg-blue-400'
                  : 'bg-gray-300 hover:bg-blue-500'
              }`} />

              {/* 右侧：课程内容 + AI 助手 */}
              <Panel defaultSize={30} minSize={20} style={{ height: '100%', overflow: 'auto' }}>
                <ContentPanel
                  activeTab={activeTab}
                  onTabChange={setActiveTab}
                  currentLesson={currentLesson}
                  theme={theme}
                  chatMessages={chatMessages}
                  chatInput={chatInput}
                  onChatInputChange={setChatInput}
                  isChatLoading={isChatLoading}
                  onSendMessage={sendMessage}
                />
              </Panel>
            </Group>
          </div>

          {/* 下半部分：终端输出 */}
          <div style={{ height: '30%' }}>
            <TerminalOutput
              output={output}
              isRunning={isRunning}
              theme={theme}
              onClear={clearOutput}
            />
          </div>
        </div>
      </div>
    </>
  );
}

// 添加 displayName 以支持 React Fast Refresh
LearnPage.displayName = 'LearnPage';
