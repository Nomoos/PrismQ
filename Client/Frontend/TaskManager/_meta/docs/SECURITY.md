# Security Guidelines

## Overview
This document describes the security measures implemented in the TaskManager frontend to protect against common web vulnerabilities, particularly Cross-Site Scripting (XSS) attacks.

The application uses a **defense-in-depth** approach with multiple layers of protection:
1. **DOMPurify** - Industry-standard HTML sanitization library
2. **Custom sanitization** - Application-specific input cleaning
3. **Input validation** - Client-side validation rules
4. **Vue.js built-in protection** - Framework-level XSS prevention

## Input Validation and Sanitization

### DOMPurify Integration

The application uses [DOMPurify](https://github.com/cure53/DOMPurify) as the primary defense against XSS attacks. DOMPurify is a battle-tested, industry-standard library that provides robust HTML sanitization.

**Key features:**
- Removes malicious scripts and event handlers
- Protects against mutation XSS (mXSS)
- Configurable allow-lists for safe HTML tags
- Regular security updates and maintenance
- Used by major companies and security professionals

### Sanitization Utilities
Located in `src/utils/sanitize.ts`, these utilities provide comprehensive protection against XSS attacks:

#### `sanitizeHtml(input: string): string`
Escapes HTML special characters to prevent XSS attacks.

**Use when:**
- Displaying user-generated content that might contain HTML
- Processing strings that will be rendered in HTML contexts

**Example:**
```typescript
import { sanitizeHtml } from '@/utils/sanitize'

const userInput = '<script>alert("xss")</script>'
const safe = sanitizeHtml(userInput)
// Result: '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'
```

**Characters escaped:**
- `&` → `&amp;`
- `<` → `&lt;`
- `>` → `&gt;`
- `"` → `&quot;`
- `'` → `&#x27;`
- `/` → `&#x2F;`

#### `sanitizeWorkerId(workerId: string): string`
Removes potentially dangerous characters from Worker IDs.

**Allowed characters:**
- Alphanumeric: `a-zA-Z0-9`
- Hyphens: `-`
- Underscores: `_`
- Dots: `.`

**Example:**
```typescript
import { sanitizeWorkerId } from '@/utils/sanitize'

const input = 'worker<script>alert(1)</script>'
const safe = sanitizeWorkerId(input)
// Result: 'workerscriptalert1script'
```

#### `sanitizeText(input: string, maxLength?: number): string`
General text sanitization with control character removal and length limiting.

**Features:**
- Trims whitespace
- Removes control characters (except newline, carriage return, tab)
- Limits to specified length (default: 1000 characters)

**Example:**
```typescript
import { sanitizeText } from '@/utils/sanitize'

const input = '  hello\x00world\x1F  '
const safe = sanitizeText(input, 50)
// Result: 'helloworld'
```

#### `isContentSafe(input: string): boolean`
Checks for potentially dangerous XSS patterns.

**Detects:**
- Script tags: `<script>`
- JavaScript protocol: `javascript:`
- Event handlers: `onclick=`, `onload=`, etc.
- IFrames: `<iframe>`
- Object/Embed tags: `<object>`, `<embed>`
- Eval calls: `eval(`
- CSS expressions: `expression(`

**Example:**
```typescript
import { isContentSafe } from '@/utils/sanitize'

isContentSafe('Hello World') // true
isContentSafe('<script>alert(1)</script>') // false
isContentSafe('onclick="hack()"') // false
```

#### `validateAndSanitizeWorkerId(workerId: string)`
Complete validation and sanitization for Worker IDs.

**Returns:**
```typescript
{
  value: string      // Sanitized value
  isValid: boolean   // Validation status
  error?: string     // Error message if invalid
}
```

**Validation rules:**
- Required (cannot be empty)
- Length: 3-50 characters
- Must start with alphanumeric character
- Allowed characters: `a-zA-Z0-9-_.`

**Example:**
```typescript
import { validateAndSanitizeWorkerId } from '@/utils/sanitize'

const result = validateAndSanitizeWorkerId('frontend-worker-1')
// { value: 'frontend-worker-1', isValid: true }

const result2 = validateAndSanitizeWorkerId('ab')
// { value: 'ab', isValid: false, error: 'Worker ID must be at least 3 characters' }
```

### DOMPurify-Based Functions

#### `sanitizeHtmlWithDOMPurify(dirty: string, allowedTags?: string[]): string`
Sanitizes HTML content using DOMPurify, allowing specified safe HTML tags.

**Use when:**
- Displaying rich user-generated content that may contain safe HTML
- Need to preserve formatting (bold, italic, etc.) while blocking XSS

**Default allowed tags:** `['b', 'i', 'em', 'strong', 'p', 'br', 'span']`

**Example:**
```typescript
import { sanitizeHtmlWithDOMPurify } from '@/utils/sanitize'

const userContent = '<p>Hello <strong>World</strong><script>alert(1)</script></p>'
const safe = sanitizeHtmlWithDOMPurify(userContent)
// Result: '<p>Hello <strong>World</strong></p>'
// Script tag removed, safe formatting preserved
```

**Custom allowed tags:**
```typescript
const safe = sanitizeHtmlWithDOMPurify(userContent, ['span', 'b'])
// Only span and b tags allowed
```

#### `sanitizeUserInput(input: string, maxLength?: number): string`
The most secure option for general user inputs - removes ALL HTML tags.

**Use when:**
- Processing form inputs (text fields, search queries)
- User-generated text where HTML should never be allowed
- Maximum security is required

**Features:**
- Removes all HTML tags using DOMPurify
- Removes control characters
- Trims whitespace
- Enforces length limits (default: 1000 chars)

**Example:**
```typescript
import { sanitizeUserInput } from '@/utils/sanitize'

const input = 'Hello <script>alert(1)</script> World'
const safe = sanitizeUserInput(input)
// Result: 'Hello  World'
// All HTML removed, plain text only

const limited = sanitizeUserInput(longText, 500)
// Enforces 500 character limit
```

#### `sanitizeRichText(dirty: string): string`
Sanitizes HTML for rich text contexts with a broader set of allowed tags.

**Use when:**
- Displaying task descriptions or comments
- Need to support headings, lists, links, and formatting
- Content should look good but remain secure

**Allowed tags:**
- Text formatting: `b`, `i`, `em`, `strong`, `u`, `s`, `strike`
- Structure: `p`, `br`, `span`, `div`
- Headings: `h1`, `h2`, `h3`, `h4`, `h5`, `h6`
- Lists: `ul`, `ol`, `li`
- Code: `code`, `pre`, `blockquote`
- Links: `a` (with `href` and `title` attributes)

**Allowed attributes:** Only `href` and `title` for links
**Allowed protocols:** `http`, `https`, `mailto`

**Example:**
```typescript
import { sanitizeRichText } from '@/utils/sanitize'

const taskDescription = `
  <h2>Task Overview</h2>
  <p>This task requires <strong>urgent</strong> attention.</p>
  <ul>
    <li>Step 1</li>
    <li>Step 2</li>
  </ul>
  <a href="https://docs.example.com">Documentation</a>
  <script>alert('XSS')</script>
`

const safe = sanitizeRichText(taskDescription)
// Safe formatting and structure preserved
// Script tag removed
// Only safe links allowed
```

#### `sanitizeUrl(url: string): string`
Sanitizes URLs to prevent `javascript:` and `data:` URI attacks.

**Use when:**
- Processing user-provided URLs
- Before using URLs in `href` or `src` attributes
- Link validation

**Allowed protocols:** `http`, `https`, `mailto`
**Blocked protocols:** `javascript`, `data`, `vbscript`

**Example:**
```typescript
import { sanitizeUrl } from '@/utils/sanitize'

sanitizeUrl('https://example.com/page')
// Result: 'https://example.com/page'

sanitizeUrl('javascript:alert(1)')
// Result: '' (blocked)

sanitizeUrl('data:text/html,<script>alert(1)</script>')
// Result: '' (blocked)
```

## Form Validation

### Enhanced Validation Rules
Located in `src/composables/useFormValidation.ts`, two new validation rules have been added:

#### `validationRules.workerId(message?: string)`
Validates Worker ID format.

**Example:**
```typescript
import { useFormValidation, validationRules } from '@/composables/useFormValidation'

const { registerField } = useFormValidation()

registerField('workerId', 'frontend-worker-1', [
  validationRules.required(),
  validationRules.workerId('Invalid worker ID format')
])
```

#### `validationRules.safeContent(message?: string)`
Validates content safety (XSS protection).

**Example:**
```typescript
registerField('comment', '', [
  validationRules.safeContent('Content contains potentially unsafe characters')
])
```

## Implementation in Components

### Settings View (Worker ID Input)
The Settings view (`src/views/Settings.vue`) implements comprehensive validation:

1. **Registration:** Field is registered with validation rules on mount
2. **Real-time validation:** Validates on blur event
3. **Visual feedback:** Red border and error message for invalid input
4. **Sanitization:** Input is sanitized before saving to localStorage
5. **Double validation:** Both client-side validation and sanitization before storage

**Code example:**
```vue
<template>
  <input
    v-model="workerIdInput"
    @blur="validateField('workerId')"
    :class="fields.workerId?.error ? 'border-red-500' : 'border-gray-300'"
  />
  <p v-if="fields.workerId?.error" class="text-red-600">
    {{ fields.workerId.error }}
  </p>
</template>

<script setup lang="ts">
import { useFormValidation, validationRules } from '../composables/useFormValidation'
import { validateAndSanitizeWorkerId } from '../utils/sanitize'

const { registerField, validateField, fields } = useFormValidation()

registerField('workerId', workerIdInput.value, [
  validationRules.required(),
  validationRules.workerId(),
  validationRules.safeContent()
])

function saveWorkerId() {
  if (!validateField('workerId')) return
  
  const result = validateAndSanitizeWorkerId(workerIdInput.value)
  if (!result.isValid) {
    // Show error
    return
  }
  
  localStorage.setItem('workerId', result.value)
}
</script>
```

## Vue's Built-in XSS Protection

Vue.js provides automatic XSS protection through:

1. **Text interpolation (`{{ }}`)**: Automatically escapes HTML
2. **Attribute binding (`:href`, `:src`)**: Safe by default
3. **No `v-html` usage**: We avoid using `v-html` directive which could introduce XSS vulnerabilities

**Safe (automatically escaped):**
```vue
<p>{{ userInput }}</p>
<div :title="userInput"></div>
```

**Unsafe (requires sanitization):**
```vue
<!-- ONLY use v-html with DOMPurify-sanitized content -->
<div v-html="sanitizedRichText"></div>
```

**Example with sanitization:**
```vue
<script setup lang="ts">
import { computed } from 'vue'
import { sanitizeRichText } from '@/utils/sanitize'

const props = defineProps<{ description: string }>()

const safeDescription = computed(() => sanitizeRichText(props.description))
</script>

<template>
  <!-- Safe: Content is sanitized with DOMPurify -->
  <div v-html="safeDescription"></div>
</template>
```

## Best Practices

### DO:
✅ Always validate user input before processing
✅ Sanitize data before storing in localStorage
✅ Use `sanitizeUserInput()` for form inputs where no HTML is needed
✅ Use `sanitizeRichText()` for rich text content (descriptions, comments)
✅ Use `sanitizeUrl()` before using user-provided URLs
✅ Use validation rules for all form inputs
✅ Display validation errors to users
✅ Use Vue's text interpolation (`{{ }}`) for displaying data
✅ Use DOMPurify-based functions when you need to allow some HTML
✅ Check for XSS patterns in user input

### DON'T:
❌ Never use `v-html` with unsanitized user input
❌ Never trust user input without validation
❌ Never store unsanitized data
❌ Never bypass validation rules
❌ Never use `eval()` or `Function()` with user input
❌ Never use `innerHTML` directly with user data
❌ Never allow `javascript:` or `data:` URLs
❌ Never disable DOMPurify or use unsafe configurations

## Testing

All security features are thoroughly tested with comprehensive XSS attack vector coverage:

### Sanitization Tests
- **`tests/unit/sanitize.spec.ts`** (57 tests)
  - Tests all sanitization functions
  - Verifies HTML escaping
  - Tests worker ID sanitization
  - Tests DOMPurify integration
  - Validates edge cases

### XSS Security Tests
- **`tests/security/xss.spec.ts`** (55 tests)
  - OWASP Top 10 XSS attack vectors
  - Script injection prevention
  - Event handler blocking
  - Protocol-based attacks (javascript:, data:)
  - Mutation XSS (mXSS) protection
  - SVG-based XSS attacks
  - Encoded script attacks
  - Form action injection
  - Style-based XSS

### Validation Tests
- **`tests/unit/useFormValidation.spec.ts`** (63 tests)
  - Tests all validation rules
  - Verifies worker ID validation
  - Tests safe content validation
  - Form validation composable

**Total Security Tests: 175 tests**

**Run all tests:**
```bash
npm run test
```

**Run only security tests:**
```bash
npm test -- tests/security/xss.spec.ts
npm test -- tests/unit/sanitize.spec.ts
```

## Security Checklist

Before deploying:
- [ ] All user inputs are validated
- [ ] Worker ID sanitization is applied
- [ ] DOMPurify is integrated and configured
- [ ] All v-html usage has DOMPurify sanitization
- [ ] Form validation is active
- [ ] Tests are passing (175 security tests)
- [ ] XSS patterns are detected and blocked
- [ ] URL sanitization is applied to user-provided links
- [ ] No dangerous protocols (javascript:, data:) are allowed
- [ ] Rich text content uses `sanitizeRichText()`
- [ ] Plain text inputs use `sanitizeUserInput()`

## Reporting Security Issues

If you discover a security vulnerability, please:
1. Do NOT open a public issue
2. Contact the security team directly
3. Provide detailed information about the vulnerability
4. Wait for confirmation before disclosing

## Additional Resources

- [DOMPurify Documentation](https://github.com/cure53/DOMPurify)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [Vue.js Security Best Practices](https://vuejs.org/guide/best-practices/security.html)
- [Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)

## Changelog

### 2025-11-10 - DOMPurify Integration (ISSUE-FRONTEND-014)
- ✅ Integrated DOMPurify library for industry-standard XSS protection
- ✅ Added `sanitizeHtmlWithDOMPurify()` for rich HTML sanitization
- ✅ Added `sanitizeUserInput()` for plain text input sanitization
- ✅ Added `sanitizeRichText()` for task descriptions and comments
- ✅ Added `sanitizeUrl()` for URL validation and sanitization
- ✅ Created comprehensive XSS security test suite (55 tests)
- ✅ Updated security documentation with DOMPurify usage
- ✅ Tested against OWASP Top 10 XSS attack vectors
- ✅ Total security tests: 175 (up from 103)

### Previous Updates
- ✅ Added comprehensive sanitization utilities
- ✅ Implemented Worker ID validation
- ✅ Enhanced form validation with XSS protection
- ✅ Added real-time validation feedback in Settings
- ✅ Created 51 new security-focused tests
