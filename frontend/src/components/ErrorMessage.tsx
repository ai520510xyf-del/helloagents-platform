import React from 'react';
import './ErrorMessage.css';

interface ErrorMessageProps {
  error: string | Error | null;
  onRetry?: () => void;
  showDetails?: boolean;
  className?: string;
}

/**
 * ErrorMessage 组件
 *
 * 可复用的错误提示组件，用于在页面中显示错误信息
 */
export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  error,
  onRetry,
  showDetails = false,
  className = '',
}) => {
  if (!error) return null;

  const errorMessage = typeof error === 'string' ? error : error.message;
  const errorStack = error instanceof Error ? error.stack : undefined;

  return (
    <div className={`error-message ${className}`} role="alert">
      <div className="error-message__container">
        <div className="error-message__icon">
          <svg
            className="error-message__icon-svg"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>

        <div className="error-message__content">
          <h3 className="error-message__title">出错了</h3>
          <p className="error-message__text">{errorMessage}</p>

          {showDetails && errorStack && (
            <details className="error-message__details">
              <summary className="error-message__details-summary">
                查看详情
              </summary>
              <pre className="error-message__details-pre">{errorStack}</pre>
            </details>
          )}
        </div>

        {onRetry && (
          <button
            className="error-message__retry-btn"
            onClick={onRetry}
            aria-label="重试"
          >
            <svg
              className="error-message__retry-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            重试
          </button>
        )}
      </div>
    </div>
  );
};
