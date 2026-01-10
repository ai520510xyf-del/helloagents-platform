/**
 * ContentPanel 组件
 * 右侧面板，包含课程内容和 AI 助手
 */

import { Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Button } from '../ui/Button';
import { MessageActions } from './MessageActions';
import { CodeBlock } from './CodeBlock';
import { type Lesson } from '../../data/courses';
import { type ChatMessage } from '../../services/api';

interface ContentPanelProps {
  activeTab: 'content' | 'ai';
  onTabChange: (tab: 'content' | 'ai') => void;
  currentLesson: Lesson;
  theme: 'light' | 'dark';
  chatMessages: ChatMessage[];
  chatInput: string;
  onChatInputChange: (input: string) => void;
  isChatLoading: boolean;
  onSendMessage: () => void;
  onRegenerateMessage: (index: number) => void;
  isContentLoading?: boolean;
}

export function ContentPanel({
  activeTab,
  onTabChange,
  currentLesson,
  theme,
  chatMessages,
  chatInput,
  onChatInputChange,
  isChatLoading,
  onSendMessage,
  onRegenerateMessage,
  isContentLoading = false
}: ContentPanelProps) {
  return (
    <div className={`h-full flex flex-col border-l ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-50 border-gray-200'}`}>
      {/* 标签切换 */}
      <div className={`h-12 border-b flex items-center gap-1 px-2 flex-shrink-0 ${theme === 'dark' ? 'border-border' : 'border-gray-200'}`}>
        <button
          onClick={() => onTabChange('content')}
          className={`flex-1 px-3 py-2 text-sm font-medium rounded transition-all duration-200 active:scale-95 touch-manipulation relative ${
            activeTab === 'content'
              ? 'bg-primary/10 text-primary'
              : (theme === 'dark' ? 'text-text-secondary hover:bg-bg-elevated hover:text-text-primary' : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900')
          }`}
          role="tab"
          aria-selected={activeTab === 'content'}
          data-testid="content-tab"
        >
          {activeTab === 'content' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
          )}
          📖 课程内容
        </button>
        <button
          onClick={() => onTabChange('ai')}
          className={`flex-1 px-3 py-2 text-sm font-medium rounded transition-all duration-200 active:scale-95 touch-manipulation relative ${
            activeTab === 'ai'
              ? 'bg-primary/10 text-primary'
              : (theme === 'dark' ? 'text-text-secondary hover:bg-bg-elevated hover:text-text-primary' : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900')
          }`}
          role="tab"
          aria-selected={activeTab === 'ai'}
          data-testid="ai-tab"
        >
          {activeTab === 'ai' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
          )}
          <Bot className="h-4 w-4 inline-block mr-1" /> AI 助手
        </button>
      </div>

      {/* 内容区域 */}
      <div style={{ flex: 1, overflowY: 'auto' }} className="custom-scrollbar">
        {activeTab === 'content' ? (
          isContentLoading ? (
            /* 加载中状态 */
            <div className="flex flex-col items-center justify-center h-full">
              <div className="animate-spin h-12 w-12 border-4 border-primary border-t-transparent rounded-full mb-4"></div>
              <p className={`text-sm ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}>加载课程内容中...</p>
            </div>
          ) : (
            /* 课程内容 */
            <div className={`p-6 prose prose-sm max-w-none ${theme === 'dark' ? 'prose-invert' : ''}`} data-testid="content-panel">
              <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
              components={{
                h1: ({ children }) => <h1 className={`text-2xl font-bold mb-4 mt-6 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>{children}</h1>,
                h2: ({ children }) => <h2 className={`text-xl font-semibold mb-3 mt-5 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>{children}</h2>,
                h3: ({ children }) => <h3 className={`text-lg font-semibold mb-2 mt-4 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>{children}</h3>,
                p: ({ children }) => <p className={`mb-3 leading-relaxed ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}`}>{children}</p>,
                ul: ({ children }) => <ul className={`list-disc list-inside space-y-1 mb-3 ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}`}>{children}</ul>,
                ol: ({ children }) => <ol className={`list-decimal list-inside space-y-1 mb-3 ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}`}>{children}</ol>,
                li: ({ children }) => <li className="ml-4">{children}</li>,
                code: (props: React.HTMLProps<HTMLElement> & { inline?: boolean }) => {
                  const { inline, children } = props;
                  return inline ? (
                    <code className={`px-1.5 py-0.5 rounded text-primary text-sm ${theme === 'dark' ? 'bg-bg-elevated' : 'bg-gray-100'}`}>{children}</code>
                  ) : (
                    <code className={`block p-3 rounded overflow-x-auto text-sm my-2 ${theme === 'dark' ? 'bg-bg-dark' : 'bg-gray-100'}`}>{children}</code>
                  );
                },
                pre: ({ children }) => <pre className={`p-4 rounded overflow-x-auto mb-4 ${theme === 'dark' ? 'bg-bg-dark' : 'bg-gray-100'}`}>{children}</pre>,
                blockquote: ({ children }) => (
                  <blockquote className={`border-l-4 border-primary pl-4 italic my-3 ${theme === 'dark' ? 'text-text-muted' : 'text-gray-600'}`}>{children}</blockquote>
                ),
                table: ({ children }) => <table className="w-full border-collapse my-4">{children}</table>,
                th: ({ children }) => <th className={`border px-3 py-2 text-left ${theme === 'dark' ? 'border-border bg-bg-elevated text-text-primary' : 'border-gray-300 bg-gray-100 text-gray-900'}`}>{children}</th>,
                td: ({ children }) => <td className={`border px-3 py-2 ${theme === 'dark' ? 'border-border text-text-secondary' : 'border-gray-300 text-gray-700'}`}>{children}</td>,
                strong: ({ children }) => <strong className={`font-semibold ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>{children}</strong>,
                a: ({ children, href }) => (
                  <a href={href} className="text-primary hover:underline" target="_blank" rel="noopener noreferrer">
                    {children}
                  </a>
                ),
              }}
            >
              {currentLesson.content || '# 加载中...\n\n正在加载课程内容...'}
            </ReactMarkdown>
            </div>
          )
        ) : (
          /* AI 助手 - 聊天界面 */
          <div className="h-full flex flex-col" data-testid="ai-chat">
            {/* 聊天消息列表 */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar" data-testid="chat-messages">
              {chatMessages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center p-8">
                  <div className="h-16 w-16 bg-ai/10 rounded-full flex items-center justify-center mb-4">
                    <Bot className="h-8 w-8 text-ai" />
                  </div>
                  <h3 className={`text-lg font-semibold mb-2 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>AI 学习助手</h3>
                  <p className={`text-sm mb-4 ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}>
                    我可以帮助你理解课程内容、解答疑问、分析代码
                  </p>
                  <div className={`text-xs space-y-1 ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
                    <p>💡 提示：你可以问我：</p>
                    <p>• "这章的核心概念是什么？"</p>
                    <p>• "这段代码有什么问题？"</p>
                    <p>• "如何实现 ReAct 循环？"</p>
                  </div>
                </div>
              ) : (
                chatMessages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    data-testid="chat-message"
                  >
                    {msg.role === 'assistant' && (
                      <div className="h-8 w-8 bg-ai/10 rounded-full flex items-center justify-center flex-shrink-0">
                        <Bot className="h-4 w-4 text-ai" />
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        msg.role === 'user'
                          ? 'bg-primary text-white'
                          : (theme === 'dark' ? 'bg-bg-elevated text-text-primary' : 'bg-gray-100 text-gray-900')
                      }`}
                      data-testid={msg.role === 'user' ? 'user-message' : 'ai-message'}
                    >
                      {msg.role === 'user' ? (
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      ) : (
                        <>
                          <div className={`prose prose-sm max-w-none ${theme === 'dark' ? 'prose-invert' : ''}`}>
                            <ReactMarkdown
                              remarkPlugins={[remarkGfm]}
                              rehypePlugins={[rehypeRaw]}
                              components={{
                                h1: ({ children }) => <h1 className={`text-lg font-bold mb-2 mt-3 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>{children}</h1>,
                                h2: ({ children }) => <h2 className={`text-base font-semibold mb-2 mt-2 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>{children}</h2>,
                                h3: ({ children }) => <h3 className={`text-sm font-semibold mb-1 mt-2 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>{children}</h3>,
                                p: ({ children }) => <p className={`mb-2 text-sm leading-relaxed ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}`}>{children}</p>,
                                ul: ({ children }) => <ul className={`list-disc list-inside space-y-1 mb-2 text-sm ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}`}>{children}</ul>,
                                ol: ({ children }) => <ol className={`list-decimal list-inside space-y-1 mb-2 text-sm ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}`}>{children}</ol>,
                                li: ({ children }) => <li className="ml-4">{children}</li>,
                                code: (props: React.HTMLProps<HTMLElement> & { inline?: boolean }) => {
                                  const { inline, children, className } = props;
                                  return (
                                    <CodeBlock inline={inline} className={className} theme={theme}>
                                      {children}
                                    </CodeBlock>
                                  );
                                },
                                pre: ({ children }) => <>{children}</>,
                                blockquote: ({ children }) => (
                                  <blockquote className={`border-l-2 border-primary pl-2 italic my-2 text-sm ${theme === 'dark' ? 'text-text-muted' : 'text-gray-600'}`}>{children}</blockquote>
                                ),
                                table: ({ children }) => <table className="w-full border-collapse my-2 text-sm">{children}</table>,
                                th: ({ children }) => <th className={`border px-2 py-1 text-left text-xs ${theme === 'dark' ? 'border-border bg-bg-dark text-text-primary' : 'border-gray-300 bg-gray-200 text-gray-900'}`}>{children}</th>,
                                td: ({ children }) => <td className={`border px-2 py-1 text-xs ${theme === 'dark' ? 'border-border text-text-secondary' : 'border-gray-300 text-gray-700'}`}>{children}</td>,
                                strong: ({ children }) => <strong className={`font-semibold ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>{children}</strong>,
                                a: ({ children, href }) => (
                                  <a href={href} className="text-primary hover:underline text-sm" target="_blank" rel="noopener noreferrer">
                                    {children}
                                  </a>
                                ),
                              }}
                            >
                              {msg.content}
                            </ReactMarkdown>
                          </div>
                          <MessageActions
                            content={msg.content}
                            onRegenerate={() => onRegenerateMessage(index)}
                            isRegenerating={isChatLoading}
                            theme={theme}
                          />
                        </>
                      )}
                    </div>
                    {msg.role === 'user' && (
                      <div className="h-8 w-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-sm">👤</span>
                      </div>
                    )}
                  </div>
                ))
              )}
              {isChatLoading && (
                <div className="flex gap-3" data-testid="ai-loading">
                  <div className="h-8 w-8 bg-ai/10 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="h-4 w-4 text-ai" />
                  </div>
                  <div className={`rounded-lg p-3 ${theme === 'dark' ? 'bg-bg-elevated' : 'bg-gray-100'}`}>
                    <div className="flex gap-1">
                      <div className={`h-2 w-2 rounded-full animate-bounce ${theme === 'dark' ? 'bg-text-muted' : 'bg-gray-400'}`} style={{ animationDelay: '0ms' }}></div>
                      <div className={`h-2 w-2 rounded-full animate-bounce ${theme === 'dark' ? 'bg-text-muted' : 'bg-gray-400'}`} style={{ animationDelay: '150ms' }}></div>
                      <div className={`h-2 w-2 rounded-full animate-bounce ${theme === 'dark' ? 'bg-text-muted' : 'bg-gray-400'}`} style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* 输入框 */}
            <div className={`p-4 border-t ${theme === 'dark' ? 'border-border' : 'border-gray-200'}`}>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => onChatInputChange(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      onSendMessage();
                    }
                  }}
                  placeholder="输入你的问题..."
                  className={`flex-1 px-3 py-2 border rounded text-sm focus:outline-none focus:border-primary ${
                    theme === 'dark'
                      ? 'bg-bg-elevated border-border text-text-primary placeholder-text-muted'
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400'
                  }`}
                  disabled={isChatLoading}
                />
                <Button
                  variant="primary"
                  size="sm"
                  onClick={onSendMessage}
                  disabled={!chatInput.trim() || isChatLoading}
                  data-testid="send-button"
                >
                  发送
                </Button>
              </div>
              <p className={`text-xs mt-2 ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
                按 Enter 发送，Shift + Enter 换行
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
