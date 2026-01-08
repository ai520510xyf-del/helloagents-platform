import { useRef, useEffect } from 'react';
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
}: CodeEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

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

    // 聚焦编辑器
    editor.focus();
  };

  // 动态切换主题
  useEffect(() => {
    if (editorRef.current) {
      const monacoTheme = theme === 'dark' ? 'helloagents-dark' : 'vs';
      // @ts-ignore - monaco is available on the editor instance
      editorRef.current._themeService?.setTheme(monacoTheme);
    }
  }, [theme]);

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
          readOnly,
        }}
        loading={
          <div className="flex items-center justify-center h-full bg-bg-dark text-text-secondary">
            <div className="flex flex-col items-center gap-3">
              <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
              <p className="text-sm">加载编辑器...</p>
            </div>
          </div>
        }
      />
    </div>
  );
}

// 添加 displayName 以支持 React Fast Refresh
CodeEditor.displayName = 'CodeEditor';
