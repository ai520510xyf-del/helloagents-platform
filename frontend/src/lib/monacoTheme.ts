import { editor } from 'monaco-editor';

/**
 * HelloAgents 深色主题配置
 * 基于 UI/UX Pro Max Developer Tool/IDE 配色方案
 */
export const helloAgentsDarkTheme: editor.IStandaloneThemeData = {
  base: 'vs-dark',
  inherit: true,
  rules: [
    // 注释 - 灰色斜体
    { token: 'comment', foreground: '64748B', fontStyle: 'italic' },

    // 关键字 - AI紫色加粗
    { token: 'keyword', foreground: 'A855F7', fontStyle: 'bold' },

    // 字符串 - 成功绿色
    { token: 'string', foreground: '10B981' },

    // 数字 - 警告橙色
    { token: 'number', foreground: 'F59E0B' },

    // 函数 - 主色蓝
    { token: 'function', foreground: '3B82F6' },

    // 变量 - 主文字色
    { token: 'variable', foreground: 'F1F5F9' },

    // 类名 - CTA蓝
    { token: 'type', foreground: '2563EB' },

    // 常量 - 橙色
    { token: 'constant', foreground: 'F59E0B' },
  ],
  colors: {
    // 编辑器背景
    'editor.background': '#0F172A', // bg-dark
    'editor.foreground': '#F1F5F9', // text-primary

    // 行高亮
    'editor.lineHighlightBackground': '#1E293B', // bg-surface
    'editor.lineHighlightBorder': '#00000000', // 透明

    // 选中文本
    'editor.selectionBackground': '#334155', // bg-elevated
    'editor.selectionHighlightBackground': '#1E293B80', // bg-surface 半透明

    // 光标
    'editorCursor.foreground': '#3B82F6', // primary

    // 行号
    'editorLineNumber.foreground': '#64748B', // text-muted
    'editorLineNumber.activeForeground': '#94A3B8', // text-secondary

    // 缩进参考线
    'editorIndentGuide.background': '#334155', // border
    'editorIndentGuide.activeBackground': '#475569', // border-light

    // 空白字符
    'editorWhitespace.foreground': '#33415550', // border 半透明

    // 滚动条
    'scrollbarSlider.background': '#33415580', // border 半透明
    'scrollbarSlider.hoverBackground': '#47556980', // border-light 半透明
    'scrollbarSlider.activeBackground': '#475569', // border-light

    // 查找/替换
    'editor.findMatchBackground': '#F59E0B40', // warning 半透明
    'editor.findMatchHighlightBackground': '#F59E0B20', // warning 更透明

    // 错误/警告
    'editorError.foreground': '#EF4444', // error
    'editorWarning.foreground': '#F59E0B', // warning
    'editorInfo.foreground': '#3B82F6', // info

    // 括号匹配
    'editorBracketMatch.background': '#33415550', // border 半透明
    'editorBracketMatch.border': '#3B82F6', // primary
  },
};

/**
 * Monaco Editor 默认配置选项
 */
export const defaultEditorOptions: editor.IStandaloneEditorConstructionOptions = {
  // 字体设置
  fontSize: 14,
  fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
  lineHeight: 24,
  letterSpacing: 0.5,
  fontLigatures: true, // 启用连字

  // 小地图
  minimap: {
    enabled: false // 关闭小地图，保持简洁
  },

  // 滚动
  scrollBeyondLastLine: false,
  smoothScrolling: true,

  // 自动换行
  wordWrap: 'on',

  // 行号
  lineNumbers: 'on',

  // 空白字符
  renderWhitespace: 'selection',

  // 自动布局
  automaticLayout: true,

  // 缩进
  tabSize: 4,
  insertSpaces: true,
  detectIndentation: true,

  // 代码建议
  quickSuggestions: true,
  suggestOnTriggerCharacters: true,
  acceptSuggestionOnCommitCharacter: true,
  suggestSelection: 'first',

  // 光标
  cursorBlinking: 'smooth',
  cursorSmoothCaretAnimation: 'on',
  cursorStyle: 'line',

  // 滚动条
  scrollbar: {
    vertical: 'visible',
    horizontal: 'visible',
    verticalScrollbarSize: 10,
    horizontalScrollbarSize: 10,
  },

  // 折叠
  folding: true,
  foldingStrategy: 'indentation',

  // 括号对齐线
  guides: {
    indentation: true,
    bracketPairs: true,
  },

  // 括号高亮
  matchBrackets: 'always',

  // 格式化
  formatOnPaste: true,
  formatOnType: false,

  // 只读模式
  readOnly: false,

  // 其他
  contextmenu: true,
  mouseWheelZoom: false,
  links: true,

  // 语义高亮
  'semanticHighlighting.enabled': true,
};
