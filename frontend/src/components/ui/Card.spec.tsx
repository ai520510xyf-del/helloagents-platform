/**
 * Card 组件测试
 */
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from './Card'

describe('Card', () => {
  describe('Card component', () => {
    it('应该渲染子元素', () => {
      render(<Card>Card content</Card>)
      expect(screen.getByText('Card content')).toBeInTheDocument()
    })

    it('应该应用默认变体样式', () => {
      const { container } = render(<Card>Default card</Card>)
      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('bg-bg-surface', 'border-border')
    })

    it('应该应用 elevated 变体样式', () => {
      const { container } = render(<Card variant="elevated">Elevated card</Card>)
      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('bg-bg-elevated', 'shadow-lg')
    })

    it('应该应用 ghost 变体样式', () => {
      const { container } = render(<Card variant="ghost">Ghost card</Card>)
      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('bg-transparent', 'border-transparent')
    })

    it('应该应用不同的 padding 大小', () => {
      const { container, rerender } = render(<Card padding="none">No padding</Card>)
      let card = container.firstChild as HTMLElement
      expect(card).toHaveClass('p-0')

      rerender(<Card padding="sm">Small padding</Card>)
      card = container.firstChild as HTMLElement
      expect(card).toHaveClass('p-4')

      rerender(<Card padding="md">Medium padding</Card>)
      card = container.firstChild as HTMLElement
      expect(card).toHaveClass('p-6')

      rerender(<Card padding="lg">Large padding</Card>)
      card = container.firstChild as HTMLElement
      expect(card).toHaveClass('p-8')
    })

    it('应该在 hover 为 true 时添加悬停样式', () => {
      const { container } = render(<Card hover>Hoverable card</Card>)
      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('hover:border-border-light', 'cursor-pointer')
    })

    it('应该支持自定义 className', () => {
      const { container } = render(<Card className="custom-class">Custom</Card>)
      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('custom-class')
    })

    it('应该传递额外的 HTML 属性', () => {
      render(<Card data-testid="test-card">Test</Card>)
      expect(screen.getByTestId('test-card')).toBeInTheDocument()
    })

    it('应该渲染复杂的子元素结构', () => {
      render(
        <Card>
          <div>
            <span>Child 1</span>
            <span>Child 2</span>
          </div>
        </Card>
      )
      expect(screen.getByText('Child 1')).toBeInTheDocument()
      expect(screen.getByText('Child 2')).toBeInTheDocument()
    })
  })

  describe('CardHeader', () => {
    it('应该渲染子元素', () => {
      render(<CardHeader>Header content</CardHeader>)
      expect(screen.getByText('Header content')).toBeInTheDocument()
    })

    it('应该应用默认样式', () => {
      const { container } = render(<CardHeader>Header</CardHeader>)
      const header = container.firstChild as HTMLElement
      expect(header).toHaveClass('flex', 'flex-col', 'space-y-1.5')
    })

    it('应该支持自定义 className', () => {
      const { container } = render(
        <CardHeader className="custom-header">Header</CardHeader>
      )
      const header = container.firstChild as HTMLElement
      expect(header).toHaveClass('custom-header')
    })
  })

  describe('CardTitle', () => {
    it('应该渲染标题文本', () => {
      render(<CardTitle>Card Title</CardTitle>)
      expect(screen.getByText('Card Title')).toBeInTheDocument()
    })

    it('应该使用 h3 标签', () => {
      const { container } = render(<CardTitle>Title</CardTitle>)
      const title = container.querySelector('h3')
      expect(title).toBeInTheDocument()
    })

    it('应该应用标题样式', () => {
      const { container } = render(<CardTitle>Title</CardTitle>)
      const title = container.firstChild as HTMLElement
      expect(title).toHaveClass('text-xl', 'font-semibold', 'text-text-primary')
    })

    it('应该支持自定义 className', () => {
      const { container } = render(
        <CardTitle className="custom-title">Title</CardTitle>
      )
      const title = container.firstChild as HTMLElement
      expect(title).toHaveClass('custom-title')
    })
  })

  describe('CardDescription', () => {
    it('应该渲染描述文本', () => {
      render(<CardDescription>Card description</CardDescription>)
      expect(screen.getByText('Card description')).toBeInTheDocument()
    })

    it('应该使用 p 标签', () => {
      const { container } = render(<CardDescription>Description</CardDescription>)
      const description = container.querySelector('p')
      expect(description).toBeInTheDocument()
    })

    it('应该应用描述样式', () => {
      const { container } = render(<CardDescription>Description</CardDescription>)
      const description = container.firstChild as HTMLElement
      expect(description).toHaveClass('text-sm', 'text-text-secondary')
    })

    it('应该支持自定义 className', () => {
      const { container } = render(
        <CardDescription className="custom-description">Description</CardDescription>
      )
      const description = container.firstChild as HTMLElement
      expect(description).toHaveClass('custom-description')
    })
  })

  describe('CardContent', () => {
    it('应该渲染内容', () => {
      render(<CardContent>Content area</CardContent>)
      expect(screen.getByText('Content area')).toBeInTheDocument()
    })

    it('应该应用内容样式', () => {
      const { container } = render(<CardContent>Content</CardContent>)
      const content = container.firstChild as HTMLElement
      expect(content).toHaveClass('pt-4')
    })

    it('应该支持自定义 className', () => {
      const { container } = render(
        <CardContent className="custom-content">Content</CardContent>
      )
      const content = container.firstChild as HTMLElement
      expect(content).toHaveClass('custom-content')
    })
  })

  describe('CardFooter', () => {
    it('应该渲染页脚内容', () => {
      render(<CardFooter>Footer content</CardFooter>)
      expect(screen.getByText('Footer content')).toBeInTheDocument()
    })

    it('应该应用页脚样式', () => {
      const { container } = render(<CardFooter>Footer</CardFooter>)
      const footer = container.firstChild as HTMLElement
      expect(footer).toHaveClass('flex', 'items-center', 'pt-4')
    })

    it('应该支持自定义 className', () => {
      const { container } = render(
        <CardFooter className="custom-footer">Footer</CardFooter>
      )
      const footer = container.firstChild as HTMLElement
      expect(footer).toHaveClass('custom-footer')
    })
  })

  describe('Card 组合使用', () => {
    it('应该正确渲染完整的卡片结构', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Card</CardTitle>
            <CardDescription>This is a test card description</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Main content goes here</p>
          </CardContent>
          <CardFooter>
            <button>Action</button>
          </CardFooter>
        </Card>
      )

      expect(screen.getByText('Test Card')).toBeInTheDocument()
      expect(screen.getByText('This is a test card description')).toBeInTheDocument()
      expect(screen.getByText('Main content goes here')).toBeInTheDocument()
      expect(screen.getByText('Action')).toBeInTheDocument()
    })

    it('应该支持嵌套的复杂内容', () => {
      render(
        <Card variant="elevated" padding="lg">
          <CardHeader>
            <CardTitle>Complex Card</CardTitle>
          </CardHeader>
          <CardContent>
            <div>
              <ul>
                <li>Item 1</li>
                <li>Item 2</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )

      expect(screen.getByText('Complex Card')).toBeInTheDocument()
      expect(screen.getByText('Item 1')).toBeInTheDocument()
      expect(screen.getByText('Item 2')).toBeInTheDocument()
    })
  })
})
