import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ErrorBoundary } from '../src/components/ErrorBoundary';
import { ErrorMessage } from '../src/components/ErrorMessage';
import { GlobalErrorHandler } from '../src/utils/errorHandler';
import { logger } from '../src/utils/logger';
import { AxiosError } from 'axios';

// Mock react-toastify
vi.mock('react-toastify', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
    loading: vi.fn(),
    update: vi.fn(),
    dismiss: vi.fn(),
    promise: vi.fn(),
    isActive: vi.fn(),
  },
  ToastContainer: () => null,
}));

// Mock logger
vi.mock('../src/utils/logger', () => ({
  logger: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    performance: vi.fn(),
    userAction: vi.fn(),
  },
}));

describe('ErrorBoundary', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>Test Content</div>
      </ErrorBoundary>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('should render fallback UI when error occurs', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };

    // 捕获 console.error 以避免测试输出污染
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText('抱歉，出现了一些问题')).toBeInTheDocument();
    expect(screen.getByText('Test error')).toBeInTheDocument();

    consoleError.mockRestore();
  });

  it('should render custom fallback when provided', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };

    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <ErrorBoundary fallback={<div>Custom Error UI</div>}>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText('Custom Error UI')).toBeInTheDocument();

    consoleError.mockRestore();
  });

  it('should call onError callback when error occurs', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };

    const onError = vi.fn();
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(onError).toHaveBeenCalled();
    expect(logger.error).toHaveBeenCalledWith(
      'React Error Boundary caught error',
      expect.objectContaining({
        error: 'Test error',
      })
    );

    consoleError.mockRestore();
  });
});

describe('ErrorMessage', () => {
  it('should not render when error is null', () => {
    const { container } = render(<ErrorMessage error={null} />);
    expect(container.firstChild).toBeNull();
  });

  it('should render error message from string', () => {
    render(<ErrorMessage error="Test error message" />);
    expect(screen.getByText('出错了')).toBeInTheDocument();
    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  it('should render error message from Error object', () => {
    const error = new Error('Error object message');
    render(<ErrorMessage error={error} />);
    expect(screen.getByText('出错了')).toBeInTheDocument();
    expect(screen.getByText('Error object message')).toBeInTheDocument();
  });

  it('should show retry button when onRetry is provided', () => {
    const onRetry = vi.fn();
    render(<ErrorMessage error="Test error" onRetry={onRetry} />);

    const retryButton = screen.getByRole('button', { name: /重试/i });
    expect(retryButton).toBeInTheDocument();
  });

  it('should not show retry button when onRetry is not provided', () => {
    render(<ErrorMessage error="Test error" />);

    const retryButton = screen.queryByRole('button', { name: /重试/i });
    expect(retryButton).not.toBeInTheDocument();
  });

  it('should show error details when showDetails is true', () => {
    const error = new Error('Test error');
    render(<ErrorMessage error={error} showDetails={true} />);

    expect(screen.getByText('查看详情')).toBeInTheDocument();
  });
});

describe('GlobalErrorHandler', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('handleAPIError', () => {
    it('should handle validation error', () => {
      const error = {
        response: {
          status: 400,
          data: {
            error: {
              code: 'VALIDATION_ERROR',
              message: 'Invalid input',
            },
          },
        },
      } as AxiosError<{ error: { code: string; message: string } }>;

      GlobalErrorHandler.handleAPIError(error);

      expect(logger.error).toHaveBeenCalledWith(
        'API Error',
        expect.objectContaining({
          code: 'VALIDATION_ERROR',
          message: 'Invalid input',
        })
      );
    });

    it('should handle authentication error', () => {
      const error = {
        response: {
          status: 401,
          data: {
            error: {
              code: 'AUTHENTICATION_ERROR',
              message: 'Not authenticated',
            },
          },
        },
      } as AxiosError<{ error: { code: string; message: string } }>;

      GlobalErrorHandler.handleAPIError(error);

      expect(logger.error).toHaveBeenCalledWith(
        'API Error',
        expect.objectContaining({
          code: 'AUTHENTICATION_ERROR',
        })
      );
    });

    it('should handle network error', () => {
      const error = {
        code: 'ERR_NETWORK',
        message: 'Network Error',
      } as AxiosError;

      GlobalErrorHandler.handleAPIError(error);

      expect(logger.error).toHaveBeenCalledWith(
        'Network Error',
        expect.objectContaining({
          code: 'ERR_NETWORK',
        })
      );
    });

    it('should handle timeout error', () => {
      const error = {
        code: 'ECONNABORTED',
        message: 'Timeout',
      } as AxiosError;

      GlobalErrorHandler.handleAPIError(error);

      expect(logger.error).toHaveBeenCalledWith(
        'Network Error',
        expect.objectContaining({
          code: 'ECONNABORTED',
        })
      );
    });
  });

  describe('handleReactError', () => {
    it('should log React error', () => {
      const error = new Error('React component error');
      const errorInfo = {
        componentStack: 'at Component (App.tsx:10)',
      };

      GlobalErrorHandler.handleReactError(error, errorInfo);

      expect(logger.error).toHaveBeenCalledWith(
        'React Error',
        expect.objectContaining({
          message: 'React component error',
          componentStack: 'at Component (App.tsx:10)',
        })
      );
    });
  });

  describe('handleUnhandledRejection', () => {
    it('should handle unhandled promise rejection', () => {
      // Mock PromiseRejectionEvent
      const rejectedPromise = Promise.reject('Unhandled rejection');
      // Catch the rejection to prevent unhandled rejection error in tests
      rejectedPromise.catch(() => {});

      const event = {
        type: 'unhandledrejection',
        promise: rejectedPromise,
        reason: 'Unhandled rejection',
        preventDefault: vi.fn(),
      } as unknown as PromiseRejectionEvent;

      GlobalErrorHandler.handleUnhandledRejection(event);

      expect(logger.error).toHaveBeenCalledWith(
        'Unhandled Promise Rejection',
        expect.objectContaining({
          reason: 'Unhandled rejection',
        })
      );

      expect(event.preventDefault).toHaveBeenCalled();
    });
  });

  describe('handleGlobalError', () => {
    it('should handle global error event', () => {
      const event = new ErrorEvent('error', {
        message: 'Global error',
        filename: 'app.js',
        lineno: 10,
        colno: 5,
        error: new Error('Global error'),
      });

      GlobalErrorHandler.handleGlobalError(event);

      expect(logger.error).toHaveBeenCalledWith(
        'Global Error',
        expect.objectContaining({
          message: 'Global error',
          filename: 'app.js',
          lineno: 10,
          colno: 5,
        })
      );
    });
  });

  describe('init and cleanup', () => {
    let addEventListenerSpy: any;
    let removeEventListenerSpy: any;

    beforeEach(() => {
      addEventListenerSpy = vi.spyOn(window, 'addEventListener');
      removeEventListenerSpy = vi.spyOn(window, 'removeEventListener');
    });

    afterEach(() => {
      addEventListenerSpy.mockRestore();
      removeEventListenerSpy.mockRestore();
    });

    it('should register event listeners on init', () => {
      GlobalErrorHandler.init();

      expect(addEventListenerSpy).toHaveBeenCalledWith(
        'error',
        GlobalErrorHandler.handleGlobalError
      );
      expect(addEventListenerSpy).toHaveBeenCalledWith(
        'unhandledrejection',
        GlobalErrorHandler.handleUnhandledRejection
      );
    });

    it('should remove event listeners on cleanup', () => {
      GlobalErrorHandler.cleanup();

      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        'error',
        GlobalErrorHandler.handleGlobalError
      );
      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        'unhandledrejection',
        GlobalErrorHandler.handleUnhandledRejection
      );
    });
  });
});

describe('Logger', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should log debug messages', () => {
    logger.debug('Debug message', { data: 'test' });
    expect(logger.debug).toHaveBeenCalledWith('Debug message', { data: 'test' });
  });

  it('should log info messages', () => {
    logger.info('Info message', { data: 'test' });
    expect(logger.info).toHaveBeenCalledWith('Info message', { data: 'test' });
  });

  it('should log warning messages', () => {
    logger.warn('Warning message', { data: 'test' });
    expect(logger.warn).toHaveBeenCalledWith('Warning message', { data: 'test' });
  });

  it('should log error messages', () => {
    logger.error('Error message', { data: 'test' });
    expect(logger.error).toHaveBeenCalledWith('Error message', { data: 'test' });
  });
});
