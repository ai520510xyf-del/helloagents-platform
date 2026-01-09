import { useRef, useEffect, useState } from 'react';
import Editor from '@monaco-editor/react';
import type { OnMount } from '@monaco-editor/react';
import type { editor } from 'monaco-editor';
import { helloAgentsDarkTheme, defaultEditorOptions } from '../lib/monacoTheme';

export interface CodeEditorProps {
  value: string;
  onChange?: (value: string | undefined) => void;
  onCursorChange?: (position: { line: number; column: number }) => void;
  language?: string;
  height?: string;
  readOnly?: boolean;
  className?: string;
  theme?: 'light' | 'dark';
  isMobile?: boolean;
}

export function CodeEditor({
  value,
  onChange,
  onCursorChange,
  language = 'python',
  height = '100%',
  readOnly = false,
  className = '',
  theme = 'dark',
  isMobile = false,
}: CodeEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const [isEditorReady, setIsEditorReady] = useState(false);

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;

    // 定义自定义暗色主题
    monaco.editor.defineTheme('helloagents-dark', helloAgentsDarkTheme);

    // 根据主题设置编辑器主题
    const monacoTheme = theme === 'dark' ? 'helloagents-dark' : 'vs';
    monaco.editor.setTheme(monacoTheme);

    // 监听光标位置变化
    if (onCursorChange) {
      editor.onDidChangeCursorPosition((e) => {
        onCursorChange({
          line: e.position.lineNumber,
          column: e.position.column,
        });
      });
    }

    // 移动端不自动聚焦，避免弹出键盘
    if (!isMobile) {
      editor.focus();
    }

    // 标记编辑器已准备就绪
    setIsEditorReady(true);
  };

  // 动态切换主题
  useEffect(() => {
    if (editorRef.current) {
      const monacoTheme = theme === 'dark' ? 'helloagents-dark' : 'vs';
      // @ts-expect-error - monaco is available on the editor instance
      editorRef.current._themeService?.setTheme(monacoTheme);
    }
  }, [theme]);

  // 移动端优化的编辑器选项
  const mobileEditorOptions = isMobile ? {
    fontSize: 14,
    lineHeight: 20,
    scrollbar: {
      verticalScrollbarSize: 10,
      horizontalScrollbarSize: 10,
      useShadows: false,
      verticalHasArrows: false,
      horizontalHasArrows: false,
      alwaysConsumeMouseWheel: false,
    },
    minimap: { enabled: false },
    wordWrap: 'on' as const,
    lineNumbers: 'on' as const,
    glyphMargin: false,
    folding: false,
    lineDecorationsWidth: 0,
    lineNumbersMinChars: 3,
    quickSuggestions: false,
    suggestOnTriggerCharacters: false,
    acceptSuggestionOnCommitCharacter: false,
    tabCompletion: 'off' as const,
    parameterHints: { enabled: false },
    hover: { enabled: false },
    contextmenu: false,
    links: false,
    renderLineHighlight: 'none' as const,
    occurrencesHighlight: 'off' as const,
    overviewRulerBorder: false,
    overviewRulerLanes: 0,
    hideCursorInOverviewRuler: true,
    scrollBeyondLastLine: false,
    smoothScrolling: true,
  } : {};

  return (
    <div className={`relative h-full w-full ${className}`}>
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={onChange}
        onMount={handleEditorDidMount}
        theme={theme === 'dark' ? 'helloagents-dark' : 'vs'}
        options={{
          ...defaultEditorOptions,
          ...mobileEditorOptions,
          readOnly,
        }}
        loading={
          <div className={`flex items-center justify-center h-full ${theme === 'dark' ? 'bg-bg-dark text-text-secondary' : 'bg-white text-gray-500'}`}>
            <div className="flex flex-col items-center gap-3">
              <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
              <p className="text-sm">加载编辑器...</p>
              {isMobile && (
                <p className="text-xs text-text-muted">移动端首次加载可能较慢</p>
              )}
            </div>
          </div>
        }
      />
      {/* 编辑器加载提示 */}
      {!isEditorReady && isMobile && (
        <div className="absolute inset-0 pointer-events-none flex items-end justify-center pb-8">
          <div className={`px-4 py-2 rounded-full ${theme === 'dark' ? 'bg-bg-elevated' : 'bg-gray-100'} text-xs ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
            提示：编辑器加载中，请稍候...
          </div>
        </div>
      )}
    </div>
  );
}

// 添加 displayName 以支持 React Fast Refresh
CodeEditor.displayName = 'CodeEditor';
