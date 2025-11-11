import { describe, it, expect } from 'vitest'
import {
  sanitizeHtmlWithDOMPurify,
  sanitizeUserInput,
  sanitizeRichText,
  sanitizeUrl,
  isContentSafe
} from '@/utils/sanitize'

/**
 * Comprehensive XSS Protection Tests
 * 
 * These tests verify protection against OWASP Top 10 XSS attack vectors
 * and ensure DOMPurify integration provides robust security.
 */

describe('XSS Protection with DOMPurify', () => {
  describe('sanitizeHtmlWithDOMPurify', () => {
    it('should block script tags', () => {
      const malicious = '<script>alert("XSS")</script>'
      const sanitized = sanitizeHtmlWithDOMPurify(malicious)
      expect(sanitized).not.toContain('<script>')
      expect(sanitized).not.toContain('alert')
    })

    it('should block event handlers in tags', () => {
      const malicious = '<img src="x" onerror="alert(\'XSS\')" />'
      const sanitized = sanitizeHtmlWithDOMPurify(malicious)
      expect(sanitized).not.toContain('onerror')
      expect(sanitized).not.toContain('alert')
    })

    it('should block javascript: protocol', () => {
      const malicious = '<a href="javascript:alert(\'XSS\')">Click</a>'
      const sanitized = sanitizeHtmlWithDOMPurify(malicious)
      expect(sanitized).not.toContain('javascript:')
    })

    it('should block data: URIs', () => {
      const malicious = '<a href="data:text/html,<script>alert(\'XSS\')</script>">Click</a>'
      const sanitized = sanitizeHtmlWithDOMPurify(malicious)
      expect(sanitized).not.toContain('data:')
    })

    it('should allow safe HTML tags', () => {
      const safe = '<p>This is <strong>safe</strong> and <em>formatted</em> text</p>'
      const sanitized = sanitizeHtmlWithDOMPurify(safe)
      expect(sanitized).toContain('<strong>')
      expect(sanitized).toContain('<em>')
      expect(sanitized).toContain('safe')
      expect(sanitized).toContain('formatted')
    })

    it('should remove disallowed tags but keep content', () => {
      const input = '<div><p>Hello</p><script>alert(1)</script></div>'
      const sanitized = sanitizeHtmlWithDOMPurify(input)
      expect(sanitized).toContain('Hello')
      expect(sanitized).not.toContain('<script>')
    })

    it('should block iframe injection', () => {
      const malicious = '<iframe src="evil.com"></iframe>'
      const sanitized = sanitizeHtmlWithDOMPurify(malicious)
      expect(sanitized).not.toContain('<iframe')
      expect(sanitized).not.toContain('evil.com')
    })

    it('should block object and embed tags', () => {
      const malicious1 = '<object data="evil.swf"></object>'
      const malicious2 = '<embed src="evil.swf" />'
      
      expect(sanitizeHtmlWithDOMPurify(malicious1)).not.toContain('<object')
      expect(sanitizeHtmlWithDOMPurify(malicious2)).not.toContain('<embed')
    })

    it('should block SVG XSS attacks', () => {
      const malicious = '<svg onload="alert(\'XSS\')"></svg>'
      const sanitized = sanitizeHtmlWithDOMPurify(malicious)
      expect(sanitized).not.toContain('onload')
      expect(sanitized).not.toContain('alert')
    })

    it('should block meta refresh attacks', () => {
      const malicious = '<meta http-equiv="refresh" content="0;url=evil.com">'
      const sanitized = sanitizeHtmlWithDOMPurify(malicious)
      expect(sanitized).not.toContain('<meta')
      expect(sanitized).not.toContain('evil.com')
    })

    it('should handle non-string input safely', () => {
      expect(sanitizeHtmlWithDOMPurify(123 as any)).toBe('123')
      expect(sanitizeHtmlWithDOMPurify(null as any)).toBe('null')
      expect(sanitizeHtmlWithDOMPurify(undefined as any)).toBe('undefined')
    })

    it('should handle empty string', () => {
      expect(sanitizeHtmlWithDOMPurify('')).toBe('')
    })

    it('should respect custom allowed tags', () => {
      const input = '<p>Paragraph</p><span>Span</span><div>Div</div>'
      const sanitized = sanitizeHtmlWithDOMPurify(input, ['span'])
      
      expect(sanitized).toContain('<span>')
      expect(sanitized).not.toContain('<p>')
      expect(sanitized).not.toContain('<div>')
      // Content should still be preserved
      expect(sanitized).toContain('Paragraph')
      expect(sanitized).toContain('Span')
      expect(sanitized).toContain('Div')
    })
  })

  describe('sanitizeUserInput', () => {
    it('should remove all HTML tags', () => {
      const input = '<p>Hello <strong>World</strong></p>'
      const sanitized = sanitizeUserInput(input)
      expect(sanitized).not.toContain('<p>')
      expect(sanitized).not.toContain('<strong>')
      expect(sanitized).toBe('Hello World')
    })

    it('should block script injection', () => {
      const malicious = 'Hello<script>alert(1)</script>World'
      const sanitized = sanitizeUserInput(malicious)
      expect(sanitized).not.toContain('<script>')
      expect(sanitized).not.toContain('alert')
      expect(sanitized).toContain('Hello')
      expect(sanitized).toContain('World')
    })

    it('should remove control characters', () => {
      const input = 'Hello\x00World\x1F'
      const sanitized = sanitizeUserInput(input)
      expect(sanitized).toBe('HelloWorld')
    })

    it('should preserve safe whitespace', () => {
      const input = 'Hello\nWorld\tTest'
      const sanitized = sanitizeUserInput(input)
      expect(sanitized).toBe('Hello\nWorld\tTest')
    })

    it('should trim whitespace', () => {
      const input = '  Hello World  '
      const sanitized = sanitizeUserInput(input)
      expect(sanitized).toBe('Hello World')
    })

    it('should enforce length limits', () => {
      const longText = 'a'.repeat(1500)
      const sanitized = sanitizeUserInput(longText)
      expect(sanitized.length).toBe(1000)
    })

    it('should respect custom max length', () => {
      const text = 'a'.repeat(100)
      const sanitized = sanitizeUserInput(text, 50)
      expect(sanitized.length).toBe(50)
    })

    it('should handle event handler text in plain text context', () => {
      // Note: When sanitizing plain text (not HTML), event handler text is harmless
      // because it won't be interpreted as HTML. This is safe for plain text display.
      const input = 'Hello onclick="alert(1)" World'
      const sanitized = sanitizeUserInput(input)
      // The text contains the word "onclick" but it's not in an HTML attribute context
      // so it's safe. What matters is that HTML tags are removed.
      expect(sanitized).toContain('Hello')
      expect(sanitized).toContain('World')
      // Verify no HTML tags are present
      expect(sanitized).not.toContain('<')
      expect(sanitized).not.toContain('>')
    })

    it('should handle non-string input', () => {
      expect(sanitizeUserInput(123 as any)).toBe('123')
      expect(sanitizeUserInput(null as any)).toBe('null')
    })
  })

  describe('sanitizeRichText', () => {
    it('should allow safe formatting tags', () => {
      const input = '<h1>Title</h1><p>Paragraph with <strong>bold</strong> and <em>italic</em></p>'
      const sanitized = sanitizeRichText(input)
      
      expect(sanitized).toContain('<h1>')
      expect(sanitized).toContain('<p>')
      expect(sanitized).toContain('<strong>')
      expect(sanitized).toContain('<em>')
    })

    it('should allow lists', () => {
      const input = '<ul><li>Item 1</li><li>Item 2</li></ul>'
      const sanitized = sanitizeRichText(input)
      
      expect(sanitized).toContain('<ul>')
      expect(sanitized).toContain('<li>')
      expect(sanitized).toContain('Item 1')
    })

    it('should allow safe links with href', () => {
      const input = '<a href="https://example.com" title="Example">Link</a>'
      const sanitized = sanitizeRichText(input)
      
      expect(sanitized).toContain('<a')
      expect(sanitized).toContain('href="https://example.com"')
      expect(sanitized).toContain('title="Example"')
    })

    it('should block javascript: in links', () => {
      const malicious = '<a href="javascript:alert(1)">Click</a>'
      const sanitized = sanitizeRichText(malicious)
      
      expect(sanitized).not.toContain('javascript:')
    })

    it('should block data: URIs in links', () => {
      const malicious = '<a href="data:text/html,<script>alert(1)</script>">Click</a>'
      const sanitized = sanitizeRichText(malicious)
      
      expect(sanitized).not.toContain('data:')
    })

    it('should block script tags', () => {
      const malicious = '<p>Text</p><script>alert(1)</script>'
      const sanitized = sanitizeRichText(malicious)
      
      expect(sanitized).not.toContain('<script>')
      expect(sanitized).toContain('<p>')
      expect(sanitized).toContain('Text')
    })

    it('should block event handlers', () => {
      const malicious = '<p onclick="alert(1)">Click me</p>'
      const sanitized = sanitizeRichText(malicious)
      
      expect(sanitized).not.toContain('onclick')
      expect(sanitized).toContain('Click me')
    })

    it('should block style attributes (XSS via CSS)', () => {
      const malicious = '<p style="background:url(javascript:alert(1))">Text</p>'
      const sanitized = sanitizeRichText(malicious)
      
      expect(sanitized).not.toContain('style=')
      expect(sanitized).toContain('Text')
    })

    it('should block dangerous tags like iframe', () => {
      const malicious = '<p>Text</p><iframe src="evil.com"></iframe>'
      const sanitized = sanitizeRichText(malicious)
      
      expect(sanitized).not.toContain('<iframe')
      expect(sanitized).toContain('Text')
    })
  })

  describe('sanitizeUrl', () => {
    it('should allow https URLs', () => {
      const url = 'https://example.com/path'
      const sanitized = sanitizeUrl(url)
      expect(sanitized).toBe(url)
    })

    it('should allow http URLs', () => {
      const url = 'http://example.com/path'
      const sanitized = sanitizeUrl(url)
      expect(sanitized).toBe(url)
    })

    it('should allow mailto URLs', () => {
      const url = 'mailto:test@example.com'
      const sanitized = sanitizeUrl(url)
      expect(sanitized).toBe(url)
    })

    it('should block javascript: protocol', () => {
      const malicious = 'javascript:alert(1)'
      const sanitized = sanitizeUrl(malicious)
      expect(sanitized).toBe('')
    })

    it('should block data: protocol', () => {
      const malicious = 'data:text/html,<script>alert(1)</script>'
      const sanitized = sanitizeUrl(malicious)
      expect(sanitized).toBe('')
    })

    it('should block vbscript: protocol', () => {
      const malicious = 'vbscript:msgbox(1)'
      const sanitized = sanitizeUrl(malicious)
      expect(sanitized).toBe('')
    })

    it('should handle relative URLs', () => {
      const url = '/path/to/page'
      const sanitized = sanitizeUrl(url)
      expect(sanitized).toBe(url)
    })

    it('should trim whitespace', () => {
      const url = '  https://example.com  '
      const sanitized = sanitizeUrl(url)
      expect(sanitized).toBe('https://example.com')
    })

    it('should handle non-string input', () => {
      expect(sanitizeUrl(123 as any)).toBe('')
      expect(sanitizeUrl(null as any)).toBe('')
    })

    it('should block URLs with embedded HTML', () => {
      const malicious = 'https://example.com/<script>alert(1)</script>'
      const sanitized = sanitizeUrl(malicious)
      expect(sanitized).not.toContain('<script>')
    })
  })

  describe('OWASP Top 10 XSS Attack Vectors', () => {
    it('should block stored XSS via script tags', () => {
      const attack = '<script>document.cookie</script>'
      expect(sanitizeUserInput(attack)).not.toContain('<script>')
    })

    it('should block reflected XSS via URL parameters', () => {
      const attack = 'search=<script>alert(document.domain)</script>'
      expect(sanitizeUserInput(attack)).not.toContain('<script>')
    })

    it('should block DOM-based XSS via innerHTML', () => {
      const attack = '<img src=x onerror=alert(1)>'
      const sanitized = sanitizeHtmlWithDOMPurify(attack)
      expect(sanitized).not.toContain('onerror')
    })

    it('should block XSS via event handlers', () => {
      const attacks = [
        '<body onload=alert(1)>',
        '<img onmouseover=alert(1)>',
        '<input onfocus=alert(1)>',
        '<select onchange=alert(1)>',
        '<textarea onkeypress=alert(1)>',
        '<div onclick=alert(1)>',
      ]

      attacks.forEach(attack => {
        const sanitized = sanitizeHtmlWithDOMPurify(attack)
        expect(sanitized).not.toMatch(/on\w+=/i)
      })
    })

    it('should block XSS via style attributes', () => {
      const attack = '<div style="background:url(javascript:alert(1))">XSS</div>'
      const sanitized = sanitizeRichText(attack)
      expect(sanitized).not.toContain('javascript:')
    })

    it('should block XSS via SVG', () => {
      const attacks = [
        '<svg onload=alert(1)>',
        '<svg><script>alert(1)</script></svg>',
        '<svg><animate onbegin=alert(1) attributeName=x dur=1s>',
      ]

      attacks.forEach(attack => {
        const sanitized = sanitizeHtmlWithDOMPurify(attack)
        expect(sanitized).not.toContain('alert')
      })
    })

    it('should block XSS via base tag', () => {
      const attack = '<base href="javascript:alert(1)//">'
      const sanitized = sanitizeHtmlWithDOMPurify(attack)
      expect(sanitized).not.toContain('<base')
    })

    it('should block XSS via form action', () => {
      const attack = '<form action="javascript:alert(1)"><input type="submit"></form>'
      const sanitized = sanitizeHtmlWithDOMPurify(attack)
      expect(sanitized).not.toContain('javascript:')
    })

    it('should block mutation XSS (mXSS)', () => {
      // DOMPurify specifically protects against mXSS
      const attack = '<noscript><p title="</noscript><img src=x onerror=alert(1)>">'
      const sanitized = sanitizeHtmlWithDOMPurify(attack)
      expect(sanitized).not.toContain('onerror')
    })

    it('should handle HTML entity encoded content safely', () => {
      // HTML entities in plain text are safe - they're just text characters
      // The important thing is that when rendered, they won't execute
      const attack = '&#60;script&#62;alert(1)&#60;/script&#62;'
      const sanitized = sanitizeUserInput(attack)
      // The entities themselves are harmless in plain text
      // What matters is no actual <script> tags are present
      expect(sanitized).not.toContain('<script')
      expect(sanitized).not.toContain('</script>')
    })
  })

  describe('Content Safety Validation (isContentSafe)', () => {
    it('should detect script tags', () => {
      expect(isContentSafe('<script>alert(1)</script>')).toBe(false)
      expect(isContentSafe('<SCRIPT>alert(1)</SCRIPT>')).toBe(false)
    })

    it('should detect javascript: protocol', () => {
      expect(isContentSafe('javascript:alert(1)')).toBe(false)
      expect(isContentSafe('JAVASCRIPT:alert(1)')).toBe(false)
    })

    it('should detect event handlers', () => {
      expect(isContentSafe('onclick="alert(1)"')).toBe(false)
      expect(isContentSafe('onload=alert(1)')).toBe(false)
      expect(isContentSafe('onerror="hack()"')).toBe(false)
    })

    it('should allow safe content', () => {
      expect(isContentSafe('Hello World')).toBe(true)
      expect(isContentSafe('frontend-worker-123')).toBe(true)
      expect(isContentSafe('Task #42 completed')).toBe(true)
    })
  })
})
