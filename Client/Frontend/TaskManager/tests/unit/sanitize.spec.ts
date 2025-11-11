import { describe, it, expect } from 'vitest'
import {
  sanitizeHtml,
  sanitizeWorkerId,
  sanitizeText,
  isContentSafe,
  validateAndSanitizeWorkerId,
  sanitizeHtmlWithDOMPurify,
  sanitizeUserInput,
  sanitizeRichText,
  sanitizeUrl
} from '@/utils/sanitize'

describe('Sanitization Utilities', () => {
  describe('sanitizeHtml', () => {
    it('should escape HTML special characters', () => {
      expect(sanitizeHtml('<script>alert("xss")</script>'))
        .toBe('&lt;script&gt;alert(&quot;xss&quot;)&lt;&#x2F;script&gt;')
    })

    it('should escape ampersands', () => {
      expect(sanitizeHtml('Tom & Jerry')).toBe('Tom &amp; Jerry')
    })

    it('should escape quotes', () => {
      expect(sanitizeHtml('Say "hello"')).toBe('Say &quot;hello&quot;')
      expect(sanitizeHtml("It's fine")).toBe('It&#x27;s fine')
    })

    it('should escape forward slashes', () => {
      expect(sanitizeHtml('a/b/c')).toBe('a&#x2F;b&#x2F;c')
    })

    it('should handle multiple special characters', () => {
      expect(sanitizeHtml('<div class="test" onclick=\'alert("xss")\'></div>'))
        .toBe('&lt;div class=&quot;test&quot; onclick=&#x27;alert(&quot;xss&quot;)&#x27;&gt;&lt;&#x2F;div&gt;')
    })

    it('should handle non-string values', () => {
      expect(sanitizeHtml(123 as any)).toBe('123')
      expect(sanitizeHtml(null as any)).toBe('null')
      expect(sanitizeHtml(undefined as any)).toBe('undefined')
    })

    it('should handle empty string', () => {
      expect(sanitizeHtml('')).toBe('')
    })

    it('should not modify safe text', () => {
      expect(sanitizeHtml('Hello World')).toBe('Hello World')
    })
  })

  describe('sanitizeWorkerId', () => {
    it('should allow valid worker IDs', () => {
      expect(sanitizeWorkerId('frontend-worker-1')).toBe('frontend-worker-1')
      expect(sanitizeWorkerId('worker_123')).toBe('worker_123')
      expect(sanitizeWorkerId('my.worker.01')).toBe('my.worker.01')
    })

    it('should remove special characters', () => {
      expect(sanitizeWorkerId('worker<script>alert(1)</script>'))
        .toBe('workerscriptalert1script')
    })

    it('should remove spaces', () => {
      expect(sanitizeWorkerId('worker 123')).toBe('worker123')
    })

    it('should remove XSS attempts', () => {
      expect(sanitizeWorkerId('worker\'" onclick="alert(1)"')).toBe('workeronclickalert1')
    })

    it('should preserve alphanumeric and allowed characters', () => {
      expect(sanitizeWorkerId('Worker-123_test.v2')).toBe('Worker-123_test.v2')
    })

    it('should handle non-string values', () => {
      expect(sanitizeWorkerId(123 as any)).toBe('')
      expect(sanitizeWorkerId(null as any)).toBe('')
    })

    it('should handle empty string', () => {
      expect(sanitizeWorkerId('')).toBe('')
    })
  })

  describe('sanitizeText', () => {
    it('should trim whitespace', () => {
      expect(sanitizeText('  hello  ')).toBe('hello')
    })

    it('should remove control characters', () => {
      expect(sanitizeText('hello\x00world\x1F')).toBe('helloworld')
    })

    it('should preserve newlines and tabs', () => {
      expect(sanitizeText('hello\nworld\ttest')).toBe('hello\nworld\ttest')
    })

    it('should limit length', () => {
      const longText = 'a'.repeat(1500)
      expect(sanitizeText(longText).length).toBe(1000)
    })

    it('should respect custom max length', () => {
      const text = 'a'.repeat(100)
      expect(sanitizeText(text, 50).length).toBe(50)
    })

    it('should handle non-string values', () => {
      expect(sanitizeText(123 as any)).toBe('123')
    })

    it('should handle empty string', () => {
      expect(sanitizeText('')).toBe('')
    })
  })

  describe('isContentSafe', () => {
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

    it('should detect iframe tags', () => {
      expect(isContentSafe('<iframe src="evil.com"></iframe>')).toBe(false)
    })

    it('should detect object and embed tags', () => {
      expect(isContentSafe('<object data="evil"></object>')).toBe(false)
      expect(isContentSafe('<embed src="evil"></embed>')).toBe(false)
    })

    it('should detect eval calls', () => {
      expect(isContentSafe('eval("alert(1)")')).toBe(false)
    })

    it('should allow safe content', () => {
      expect(isContentSafe('Hello World')).toBe(true)
      expect(isContentSafe('frontend-worker-123')).toBe(true)
      expect(isContentSafe('Task #42 completed')).toBe(true)
    })

    it('should handle non-string values', () => {
      expect(isContentSafe(123 as any)).toBe(true)
      expect(isContentSafe(null as any)).toBe(true)
    })
  })

  describe('validateAndSanitizeWorkerId', () => {
    it('should validate and return valid worker ID', () => {
      const result = validateAndSanitizeWorkerId('frontend-worker-1')
      expect(result.isValid).toBe(true)
      expect(result.value).toBe('frontend-worker-1')
      expect(result.error).toBeUndefined()
    })

    it('should reject empty worker ID', () => {
      const result = validateAndSanitizeWorkerId('')
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('Worker ID is required')
    })

    it('should reject null/undefined', () => {
      const result1 = validateAndSanitizeWorkerId(null as any)
      expect(result1.isValid).toBe(false)
      expect(result1.error).toBe('Worker ID is required')

      const result2 = validateAndSanitizeWorkerId(undefined as any)
      expect(result2.isValid).toBe(false)
      expect(result2.error).toBe('Worker ID is required')
    })

    it('should reject too short worker ID', () => {
      const result = validateAndSanitizeWorkerId('ab')
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('Worker ID must be at least 3 characters')
    })

    it('should reject too long worker ID', () => {
      const longId = 'a'.repeat(60)
      const result = validateAndSanitizeWorkerId(longId)
      expect(result.isValid).toBe(false)
      expect(result.value.length).toBe(50)
      expect(result.error).toBe('Worker ID must be at most 50 characters')
    })

    it('should sanitize and validate', () => {
      const result = validateAndSanitizeWorkerId('worker<script>test</script>123')
      expect(result.value).toBe('workerscripttestscript123')
      expect(result.isValid).toBe(true)
    })

    it('should reject worker ID not starting with alphanumeric', () => {
      const result = validateAndSanitizeWorkerId('-worker-123')
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('Worker ID must start with a letter or number')
    })

    it('should trim and validate', () => {
      const result = validateAndSanitizeWorkerId('  worker-123  ')
      expect(result.isValid).toBe(true)
      expect(result.value).toBe('worker-123')
    })

    it('should handle worker ID that becomes empty after sanitization', () => {
      const result = validateAndSanitizeWorkerId('<>')
      expect(result.isValid).toBe(false)
      expect(result.value).toBe('')
      expect(result.error).toBe('Worker ID cannot be empty')
    })

    it('should accept various valid formats', () => {
      const validIds = [
        'worker-1',
        'frontend_worker_123',
        'my.worker.01',
        'Worker123',
        'w123',
        'WORKER-ABC-123'
      ]

      validIds.forEach(id => {
        const result = validateAndSanitizeWorkerId(id)
        expect(result.isValid).toBe(true)
        expect(result.value).toBe(id)
      })
    })
  })

  describe('DOMPurify Integration', () => {
    describe('sanitizeHtmlWithDOMPurify', () => {
      it('should remove script tags but keep content', () => {
        const input = 'Safe text <script>alert(1)</script> more text'
        const sanitized = sanitizeHtmlWithDOMPurify(input)
        expect(sanitized).toContain('Safe text')
        expect(sanitized).toContain('more text')
        expect(sanitized).not.toContain('<script>')
      })

      it('should allow safe HTML tags by default', () => {
        const input = '<p>Text with <strong>bold</strong> and <em>italic</em></p>'
        const sanitized = sanitizeHtmlWithDOMPurify(input)
        expect(sanitized).toContain('<strong>')
        expect(sanitized).toContain('<em>')
      })

      it('should remove event handlers', () => {
        const input = '<p onclick="alert(1)">Click</p>'
        const sanitized = sanitizeHtmlWithDOMPurify(input)
        expect(sanitized).not.toContain('onclick')
        expect(sanitized).toContain('Click')
      })

      it('should respect custom allowed tags', () => {
        const input = '<p>Para</p><span>Span</span>'
        const sanitized = sanitizeHtmlWithDOMPurify(input, ['span'])
        expect(sanitized).toContain('<span>')
        expect(sanitized).not.toContain('<p>')
      })
    })

    describe('sanitizeUserInput', () => {
      it('should remove all HTML tags', () => {
        const input = '<p>Hello</p><b>World</b>'
        const sanitized = sanitizeUserInput(input)
        expect(sanitized).toBe('HelloWorld')
      })

      it('should enforce max length', () => {
        const input = 'a'.repeat(2000)
        const sanitized = sanitizeUserInput(input)
        expect(sanitized.length).toBe(1000)
      })

      it('should respect custom max length', () => {
        const input = 'a'.repeat(100)
        const sanitized = sanitizeUserInput(input, 50)
        expect(sanitized.length).toBe(50)
      })

      it('should trim whitespace', () => {
        const input = '  hello  '
        const sanitized = sanitizeUserInput(input)
        expect(sanitized).toBe('hello')
      })
    })

    describe('sanitizeRichText', () => {
      it('should allow headings and paragraphs', () => {
        const input = '<h1>Title</h1><p>Content</p>'
        const sanitized = sanitizeRichText(input)
        expect(sanitized).toContain('<h1>')
        expect(sanitized).toContain('<p>')
      })

      it('should allow links with safe protocols', () => {
        const input = '<a href="https://example.com">Link</a>'
        const sanitized = sanitizeRichText(input)
        expect(sanitized).toContain('<a')
        expect(sanitized).toContain('href=')
      })

      it('should block javascript protocol in links', () => {
        const input = '<a href="javascript:alert(1)">Bad</a>'
        const sanitized = sanitizeRichText(input)
        expect(sanitized).not.toContain('javascript:')
      })
    })

    describe('sanitizeUrl', () => {
      it('should allow https URLs', () => {
        const url = 'https://example.com'
        expect(sanitizeUrl(url)).toBe(url)
      })

      it('should allow http URLs', () => {
        const url = 'http://example.com'
        expect(sanitizeUrl(url)).toBe(url)
      })

      it('should allow mailto URLs', () => {
        const url = 'mailto:test@example.com'
        expect(sanitizeUrl(url)).toBe(url)
      })

      it('should block javascript protocol', () => {
        const url = 'javascript:alert(1)'
        expect(sanitizeUrl(url)).toBe('')
      })

      it('should block data protocol', () => {
        const url = 'data:text/html,<script>alert(1)</script>'
        expect(sanitizeUrl(url)).toBe('')
      })

      it('should trim whitespace', () => {
        const url = '  https://example.com  '
        expect(sanitizeUrl(url)).toBe('https://example.com')
      })
    })
  })
})
