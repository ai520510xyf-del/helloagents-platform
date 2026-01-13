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
  const [isCodeEditorCollapsed, setIsCodeEditorCollapsed] = useState(false);
  const [isCourseMenuCollapsed, setIsCourseMenuCollapsed] = useState(false);
  const [isLessonLoading, setIsLessonLoading] = useState(false);

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

  // 切换代码编辑器折叠状态
  const toggleCodeEditorCollapse = useCallback(() => {
    setIsCodeEditorCollapsed(prev => !prev);
  }, []);

  // 切换课程菜单折叠状态
  const toggleCourseMenuCollapse = useCallback(() => {
    setIsCourseMenuCollapsed(prev => !prev);
  }, []);

  // 切换课程 - 使用 useCallback 稳定引用
  const handleLessonChange = useCallback(async (lessonId: string) => {
    setIsLessonLoading(true);
    try {
      await changeLesson(lessonId);

      // 从本地缓存加载该课程的代码和聊天历史
      const savedCode = loadCodeFromStorage(lessonId);
      setCode(savedCode);

      // 重置其他状态
      clearOutput();
    } finally {
      setIsLessonLoading(false);
    }
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

        {/* 主内容区 - 使用垂直可调整布局 */}
        <main className="flex-1 min-h-0">
          {/* @ts-expect-error - react-resizable-panels Group 类型定义问题 */}
          <Group direction="vertical" id="desktop-vertical-group">
            {/* 上半部分：三栏布局 */}
            <Panel id="desktop-top-section" defaultSize={70} minSize={30}>
              {/* @ts-expect-error - react-resizable-panels Group 类型定义问题 */}
              <Group direction="horizontal" id="desktop-main-panels">
                {/* 左侧：课程目录 */}
                <Panel
                  id="course-menu"
                  defaultSize={isCourseMenuCollapsed ? 5 : 20}
                  minSize={isCourseMenuCollapsed ? 5 : 15}
                  maxSize={isCourseMenuCollapsed ? 5 : 30}
                  collapsible={true}
                  style={{ height: '100%', overflow: 'auto' }}
                >
                  <CourseMenu
                    currentLesson={currentLesson}
                    theme={theme}
                    onLessonChange={handleLessonChange}
                    isCollapsed={isCourseMenuCollapsed}
                    onToggleCollapse={toggleCourseMenuCollapse}
                  />
                </Panel>

                <Separator className={`w-1 transition-colors resizable-separator resizable-separator-vertical ${
                  theme === 'dark'
                    ? 'bg-gray-700 hover:bg-blue-400 active:bg-blue-500'
                    : 'bg-gray-300 hover:bg-blue-500 active:bg-blue-600'
                }`} />

                {/* 中间：代码编辑器 */}
                <Panel
                  id="code-editor"
                  defaultSize={isCodeEditorCollapsed ? 5 : 50}
                  minSize={isCodeEditorCollapsed ? 5 : 30}
                  maxSize={isCodeEditorCollapsed ? 5 : 70}
                  collapsible={true}
                  style={{ height: '100%', overflow: 'auto' }}
                >
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
                    isCollapsed={isCodeEditorCollapsed}
                    onToggleCollapse={toggleCodeEditorCollapse}
                  />
                </Panel>

                <Separator className={`w-1 transition-colors resizable-separator resizable-separator-vertical ${
                  theme === 'dark'
                    ? 'bg-gray-700 hover:bg-blue-400 active:bg-blue-500'
                    : 'bg-gray-300 hover:bg-blue-500 active:bg-blue-600'
                }`} />

                {/* 右侧：课程内容 + AI 助手 */}
                <Panel id="content-panel" defaultSize={30} minSize={20} style={{ height: '100%', overflow: 'auto' }}>
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
                    onRegenerateMessage={regenerateMessage}
                    isContentLoading={isLessonLoading}
                    uploadedImages={uploadedImages}
                    onImagesChange={setUploadedImages}
                  />
                </Panel>
              </Group>
            </Panel>

            {/* 可拖动的水平分割线 */}
            <Separator className={`h-1 transition-colors resizable-separator resizable-separator-horizontal ${
              theme === 'dark'
                ? 'bg-gray-700 hover:bg-blue-400 active:bg-blue-500'
                : 'bg-gray-300 hover:bg-blue-500 active:bg-blue-600'
            }`} />

            {/* 下半部分：终端输出 */}
            <Panel id="terminal-panel" defaultSize={30} minSize={15}>
              <TerminalOutput
                output={output}
                isRunning={isRunning}
                theme={theme}
                onClear={clearOutput}
              />
            </Panel>
          </Group>
        </main>
      </div>
    </>
  );
}

// 添加 displayName 以支持 React Fast Refresh
LearnPage.displayName = 'LearnPage';
