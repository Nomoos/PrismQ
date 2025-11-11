/**
 * Sanitization utilities for XSS protection
 * 
 * SECURITY IMPLEMENTATION:
 * This module provides multiple layers of XSS protection:
 * 1. DOMPurify: Industry-standard sanitization for rich HTML content
 * 2. HTML escaping: Fallback for basic text that needs entity encoding
 * 3. Pattern-based validation: Detection of dangerous XSS patterns
 * 4. Input-specific sanitization: Specialized handling for different input types
 * 
 * USAGE GUIDELINES:
 * - Use sanitizeHtmlWithDOMPurify() for rich HTML content that needs to preserve safe tags
 * - Use sanitizeHtml() when displaying user-generated content (escapes all HTML)
 * - Use sanitizeUserInput() for general user inputs (combines DOMPurify + length limits)
 * - Use sanitizeWorkerId() for Worker ID inputs (Settings page)
 * - Use sanitizeText() for general text inputs that need length limits
 * - Use isContentSafe() to validate content before accepting it
 * - Use validateAndSanitizeWorkerId() for complete Worker ID validation
 * 
 * SECURITY NOTES:
 * - Vue's text interpolation {{ }} automatically escapes HTML
 * - Only use v-html with sanitized content (preferably with DOMPurify)
 * - Always sanitize user input before storing or processing
 * - Never trust client-side validation alone - always validate on server side too
 */

import DOMPurify from 'dompurify'

/**
 * Sanitize a string by escaping HTML special characters
 * This prevents XSS attacks by converting potentially dangerous characters to HTML entities
 * 
 * @param input - The input string to sanitize
 * @returns The sanitized string with HTML entities escaped
 */
export function sanitizeHtml(input: string): string {
  if (typeof input !== 'string') {
    return String(input)
  }
  
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;',
  }
  
  return input.replace(/[&<>"'/]/g, (char) => map[char])
}

/**
 * Sanitize a Worker ID by removing potentially dangerous characters
 * Allows only alphanumeric characters, hyphens, underscores, and dots
 * 
 * @param workerId - The worker ID to sanitize
 * @returns The sanitized worker ID
 */
export function sanitizeWorkerId(workerId: string): string {
  if (typeof workerId !== 'string') {
    return ''
  }
  
  // Remove any characters that aren't alphanumeric, hyphens, underscores, or dots
  return workerId.replace(/[^a-zA-Z0-9\-_.]/g, '')
}

/**
 * Sanitize a general text input by trimming and limiting length
 * Also removes any control characters that could be problematic
 * 
 * @param input - The input text to sanitize
 * @param maxLength - Maximum allowed length (default: 1000)
 * @returns The sanitized text
 */
export function sanitizeText(input: string, maxLength: number = 1000): string {
  if (typeof input !== 'string') {
    return String(input)
  }
  
  // Remove control characters except newline, carriage return, and tab
  let sanitized = input.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '')
  
  // Trim whitespace
  sanitized = sanitized.trim()
  
  // Limit length
  if (sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength)
  }
  
  return sanitized
}

/**
 * Check if a string contains potentially dangerous content
 * This is a basic check for common XSS patterns
 * 
 * @param input - The input to check
 * @returns true if the input appears safe, false if it contains suspicious content
 */
export function isContentSafe(input: string): boolean {
  if (typeof input !== 'string') {
    return true
  }
  
  // Check for common XSS patterns
  const dangerousPatterns = [
    /<script/i,
    /javascript:/i,
    /on\w+\s*=/i, // event handlers like onclick=, onload=, etc.
    /<iframe/i,
    /<object/i,
    /<embed/i,
    /eval\(/i,
    /expression\(/i,
  ]
  
  return !dangerousPatterns.some(pattern => pattern.test(input))
}

/**
 * Validate and sanitize Worker ID
 * Ensures the worker ID follows the expected format
 * 
 * @param workerId - The worker ID to validate and sanitize
 * @returns Object with sanitized value and validation status
 */
export function validateAndSanitizeWorkerId(workerId: string): { 
  value: string
  isValid: boolean
  error?: string 
} {
  if (!workerId || typeof workerId !== 'string') {
    return {
      value: '',
      isValid: false,
      error: 'Worker ID is required'
    }
  }
  
  const sanitized = sanitizeWorkerId(workerId.trim())
  
  if (sanitized.length === 0) {
    return {
      value: '',
      isValid: false,
      error: 'Worker ID cannot be empty'
    }
  }
  
  if (sanitized.length < 3) {
    return {
      value: sanitized,
      isValid: false,
      error: 'Worker ID must be at least 3 characters'
    }
  }
  
  if (sanitized.length > 50) {
    return {
      value: sanitized.substring(0, 50),
      isValid: false,
      error: 'Worker ID must be at most 50 characters'
    }
  }
  
  // Check if it starts with alphanumeric character
  if (!/^[a-zA-Z0-9]/.test(sanitized)) {
    return {
      value: sanitized,
      isValid: false,
      error: 'Worker ID must start with a letter or number'
    }
  }
  
  return {
    value: sanitized,
    isValid: true
  }
}

/**
 * Sanitize HTML content using DOMPurify with safe configuration
 * This allows limited safe HTML tags while removing dangerous content
 * 
 * USE CASE: When you need to display user-generated content that may contain
 * safe HTML formatting (e.g., bold, italic, links) but must block XSS attacks
 * 
 * @param dirty - The HTML content to sanitize
 * @param allowedTags - Optional array of allowed HTML tags (default: basic formatting tags)
 * @returns Sanitized HTML string safe for use with v-html
 */
export function sanitizeHtmlWithDOMPurify(
  dirty: string,
  allowedTags: string[] = ['b', 'i', 'em', 'strong', 'p', 'br', 'span']
): string {
  if (typeof dirty !== 'string') {
    return String(dirty)
  }

  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: allowedTags,
    ALLOWED_ATTR: [], // No attributes allowed by default for maximum security
    KEEP_CONTENT: true, // Keep text content even if tags are removed
    RETURN_DOM: false,
    RETURN_DOM_FRAGMENT: false,
  })
}

/**
 * Sanitize user input by removing all HTML tags using DOMPurify
 * This is the most secure option for general user inputs
 * 
 * USE CASE: Form inputs, search queries, and any user-generated text
 * where HTML should not be allowed
 * 
 * @param input - The user input to sanitize
 * @param maxLength - Maximum allowed length (default: 1000)
 * @returns Sanitized plain text with no HTML
 */
export function sanitizeUserInput(input: string, maxLength: number = 1000): string {
  if (typeof input !== 'string') {
    return String(input)
  }

  // First pass: Remove all HTML tags using DOMPurify
  let sanitized = DOMPurify.sanitize(input, {
    ALLOWED_TAGS: [], // No HTML tags allowed
    KEEP_CONTENT: true, // Keep the text content
  })

  // Remove control characters except newline, carriage return, and tab
  sanitized = sanitized.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '')

  // Trim whitespace
  sanitized = sanitized.trim()

  // Limit length
  if (sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength)
  }

  return sanitized
}

/**
 * Sanitize HTML for safe display in rich text contexts
 * Allows common formatting tags and safe attributes
 * 
 * USE CASE: Task descriptions, comments, or other rich text content
 * 
 * @param dirty - The HTML content to sanitize
 * @returns Sanitized HTML safe for display
 */
export function sanitizeRichText(dirty: string): string {
  if (typeof dirty !== 'string') {
    return String(dirty)
  }

  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: [
      'b', 'i', 'em', 'strong', 'u', 's', 'strike',
      'p', 'br', 'span', 'div',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li',
      'a', 'code', 'pre', 'blockquote'
    ],
    ALLOWED_ATTR: ['href', 'title'], // Only safe attributes for links
    ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto):)/i, // Only allow http, https, and mailto URLs
    KEEP_CONTENT: true,
    RETURN_DOM: false,
    RETURN_DOM_FRAGMENT: false,
  })
}

/**
 * Sanitize a URL to prevent javascript: and data: URI attacks
 * 
 * @param url - The URL to sanitize
 * @returns Safe URL or empty string if dangerous
 */
export function sanitizeUrl(url: string): string {
  if (typeof url !== 'string') {
    return ''
  }

  // Allow only http, https, and mailto protocols
  const allowedProtocols = /^(?:https?|mailto):/i
  
  // Remove whitespace
  const trimmed = url.trim()
  
  // Check for dangerous protocols
  if (/^(?:javascript|data|vbscript):/i.test(trimmed)) {
    return ''
  }

  // If it has a protocol, ensure it's allowed
  if (/:/.test(trimmed) && !allowedProtocols.test(trimmed)) {
    return ''
  }

  // Use DOMPurify to sanitize the URL
  const sanitized = DOMPurify.sanitize(trimmed, {
    ALLOWED_TAGS: [],
    KEEP_CONTENT: true,
  })

  return sanitized
}
