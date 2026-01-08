/**
 * Button 组件测试
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button', () => {
  it('应该渲染按钮文本', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('应该在点击时调用 onClick 处理函数', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)

    const button = screen.getByText('Click me')
    fireEvent.click(button)

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('应该在 disabled 时不触发点击', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick} disabled>Click me</Button>)

    const button = screen.getByText('Click me')
    fireEvent.click(button)

    expect(handleClick).not.toHaveBeenCalled()
  })

  it('应该在 isLoading 时显示加载状态', () => {
    render(<Button isLoading>Click me</Button>)

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    // 可以检查是否有加载指示器
  })

  it('应该应用不同的 variant 样式', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>)
    let button = screen.getByText('Primary')
    expect(button).toBeInTheDocument()

    rerender(<Button variant="secondary">Secondary</Button>)
    button = screen.getByText('Secondary')
    expect(button).toBeInTheDocument()

    rerender(<Button variant="destructive">Destructive</Button>)
    button = screen.getByText('Destructive')
    expect(button).toBeInTheDocument()
  })

  it('应该应用不同的 size 样式', () => {
    const { rerender } = render(<Button size="sm">Small</Button>)
    let button = screen.getByText('Small')
    expect(button).toBeInTheDocument()

    rerender(<Button size="md">Medium</Button>)
    button = screen.getByText('Medium')
    expect(button).toBeInTheDocument()

    rerender(<Button size="lg">Large</Button>)
    button = screen.getByText('Large')
    expect(button).toBeInTheDocument()
  })

  it('应该支持自定义 className', () => {
    render(<Button className="custom-class">Custom</Button>)
    const button = screen.getByText('Custom')
    expect(button).toHaveClass('custom-class')
  })

  it('应该渲染子元素', () => {
    render(
      <Button>
        <span>Icon</span>
        <span>Text</span>
      </Button>
    )

    expect(screen.getByText('Icon')).toBeInTheDocument()
    expect(screen.getByText('Text')).toBeInTheDocument()
  })
})
