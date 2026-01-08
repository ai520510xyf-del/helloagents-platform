import { lazy, Suspense } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ToastProvider } from './components/Toast';
import { PageLoading } from './components/Loading';
import { GlobalErrorHandler } from './utils/errorHandler';

// 使用 React.lazy 进行路由级别的代码分割
const LearnPage = lazy(() =>
  import(/* webpackChunkName: "learn-page" */ './pages/LearnPage').then(module => ({
    default: module.LearnPage,
  }))
);

// 可选：TestPanels 也可以懒加载
// const TestPanels = lazy(() => import(/* webpackChunkName: "test-panels" */ './pages/TestPanels'));

function App() {
  return (
    <ErrorBoundary
      onError={GlobalErrorHandler.handleReactError}
      fallback={
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-8">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mx-auto mb-4">
              <svg
                className="w-8 h-8 text-red-600"
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
            <h1 className="text-2xl font-bold text-gray-900 mb-2">应用出错</h1>
            <p className="text-gray-600 mb-6">我们正在修复这个问题</p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              刷新页面
            </button>
          </div>
        </div>
      }
    >
      <ToastProvider />

      {/* Suspense 包裹懒加载组件，提供加载状态 */}
      <Suspense fallback={<PageLoading theme="dark" />}>
        <LearnPage />
      </Suspense>
    </ErrorBoundary>
  );
}

export default App;
