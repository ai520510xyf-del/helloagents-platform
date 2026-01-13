/**
 * LearnPage - 学习页面主组件（重构版）
 *
 * 采用组件化和自定义 Hooks 架构：
 * - 自定义 Hooks：useLesson, useChatMessages, useCodeExecution, useLocalStorage
 * - 拆分组件：NavigationBar, CourseMenu, CodeEditorPanel, ContentPanel, TerminalOutput
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { MigrationPrompt } from '../components/MigrationPrompt';
import { NavigationBar } from '../components/learn/NavigationBar';
import { MobileLayout } from '../components/learn/MobileLayout';
import { TabletLayout } from '../components/learn/TabletLayout';
import { calculateProgress } from '../data/courses';
import { useLesson } from '../hooks/useLesson';
import { useChatMessages } from '../hooks/useChatMessages';
import { useCodeExecution } from '../hooks/useCodeExecution';
import { useResponsiveLayout } from '../hooks/useResponsiveLayout';
import { lessonStorage, themeStorage } from '../utils/storage';

export function LearnPage() {
  // 响应式布局检测
  const { layoutType } = useResponsiveLayout();

  // 课程管理
  const { currentLesson, changeLesson } = useLesson();

  // 主题管理
  const loadThemeFromStorage = (): 'light' | 'dark' => {
    const savedTheme = themeStorage.get<'light' | 'dark'>('theme', 'dark');
    return savedTheme === 'light' || savedTheme === 'dark' ? savedTheme : 'dark';
  };

  const [theme, setTheme] = useState<'light' | 'dark'>(loadThemeFromStorage());

  // 代码编辑器状态
  const loadCodeFromStorage = (lessonId: string): string => {
    return lessonStorage.get<string>(`code_${lessonId}`, '') || '';
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
    regenerateMessage,
    uploadedImages,
    setUploadedImages,
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
    themeStorage.set('theme', theme);
  }, [theme]);

  // 初始化时清除可能导致布局异常的旧版本缓存
  useEffect(() => {
    try {
      const cached = localStorage.getItem('react-resizable-panels:desktop-main-panels');
      if (cached) {
        const layout = JSON.parse(cached);
        // 检查是否有异常的面板尺寸（小于10%可能是异常值）
        if (Array.isArray(layout) && layout.some((size: number) => typeof size === 'number' && size < 10)) {
          console.log('[LearnPage] 检测到异常的面板布局缓存，已清除');
          localStorage.removeItem('react-resizable-panels:desktop-main-panels');
        }
      }
    } catch {
      // 解析失败，清除缓存
      localStorage.removeItem('react-resizable-panels:desktop-main-panels');
    }
  }, []);

  // 自动保存代码到本地存储
  useEffect(() => {
    if (currentLesson) {
      lessonStorage.set(`code_${currentLesson.id}`, code);
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
    lessonStorage.remove(`code_${currentLesson.id}`);

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
          <main className="flex-1 min-h-0" style={{ marginTop: '0.5rem' }}>
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
              onRegenerateMessage={regenerateMessage}
              uploadedImages={uploadedImages}
              onImagesChange={setUploadedImages}
              theme={theme}
            />
          </main>
        </div>
      </>
    );
  }

  // 桌面布局（使用两栏布局）
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
        <main className="flex-1 min-h-0" style={{ marginTop: '0.5rem' }}>
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
            onRegenerateMessage={regenerateMessage}
            uploadedImages={uploadedImages}
            onImagesChange={setUploadedImages}
            theme={theme}
          />
        </main>
      </div>
    </>
  );
}

// 添加 displayName 以支持 React Fast Refresh
LearnPage.displayName = 'LearnPage';
