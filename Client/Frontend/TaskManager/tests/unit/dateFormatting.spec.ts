import { describe, it, expect } from 'vitest'
import {
  formatDate,
  formatDateShort,
  formatRelativeTime,
  formatDateTimeAttribute
} from '../../src/utils/dateFormatting'

describe('dateFormatting', () => {
  describe('formatDate', () => {
    it('formats a date string to localized string', () => {
      const date = '2025-11-10T12:00:00Z'
      const result = formatDate(date)
      expect(result).toBeTruthy()
      expect(result).toContain('2025') // Should contain the year
    })
    
    it('formats a Date object', () => {
      const date = new Date('2025-11-10T12:00:00Z')
      const result = formatDate(date)
      expect(result).toBeTruthy()
      expect(result).toContain('2025')
    })
    
    it('returns empty string for empty input', () => {
      const result = formatDate('')
      expect(result).toBe('')
    })
  })
  
  describe('formatDateShort', () => {
    it('formats a date string to short format', () => {
      const date = '2025-11-10T12:00:00Z'
      const result = formatDateShort(date)
      expect(result).toBeTruthy()
      expect(result).toContain('Nov')
      expect(result).toContain('10')
      expect(result).toContain('2025')
    })
    
    it('returns empty string for empty input', () => {
      const result = formatDateShort('')
      expect(result).toBe('')
    })
  })
  
  describe('formatRelativeTime', () => {
    it('returns "just now" for very recent dates', () => {
      const date = new Date()
      const result = formatRelativeTime(date)
      expect(result).toBe('just now')
    })
    
    it('returns minutes ago for recent dates', () => {
      const date = new Date(Date.now() - 5 * 60 * 1000) // 5 minutes ago
      const result = formatRelativeTime(date)
      expect(result).toBe('5 minutes ago')
    })
    
    it('returns singular minute for 1 minute ago', () => {
      const date = new Date(Date.now() - 1 * 60 * 1000) // 1 minute ago
      const result = formatRelativeTime(date)
      expect(result).toBe('1 minute ago')
    })
    
    it('returns hours ago for dates within 24 hours', () => {
      const date = new Date(Date.now() - 3 * 60 * 60 * 1000) // 3 hours ago
      const result = formatRelativeTime(date)
      expect(result).toBe('3 hours ago')
    })
    
    it('returns "yesterday" for 1 day ago', () => {
      const date = new Date(Date.now() - 24 * 60 * 60 * 1000) // 1 day ago
      const result = formatRelativeTime(date)
      expect(result).toBe('yesterday')
    })
    
    it('returns days ago for dates within a week', () => {
      const date = new Date(Date.now() - 3 * 24 * 60 * 60 * 1000) // 3 days ago
      const result = formatRelativeTime(date)
      expect(result).toBe('3 days ago')
    })
    
    it('returns weeks ago for dates within a month', () => {
      const date = new Date(Date.now() - 14 * 24 * 60 * 60 * 1000) // 2 weeks ago
      const result = formatRelativeTime(date)
      expect(result).toBe('2 weeks ago')
    })
    
    it('returns short format for older dates', () => {
      const date = new Date(Date.now() - 60 * 24 * 60 * 60 * 1000) // 2 months ago
      const result = formatRelativeTime(date)
      expect(result).toBeTruthy()
      // Should be a date format, not relative time
      expect(result).not.toContain('ago')
    })
    
    it('returns empty string for empty input', () => {
      const result = formatRelativeTime('')
      expect(result).toBe('')
    })
  })
  
  describe('formatDateTimeAttribute', () => {
    it('formats a date to ISO string', () => {
      const date = '2025-11-10T12:00:00Z'
      const result = formatDateTimeAttribute(date)
      expect(result).toBe('2025-11-10T12:00:00.000Z')
    })
    
    it('formats a Date object to ISO string', () => {
      const date = new Date('2025-11-10T12:00:00Z')
      const result = formatDateTimeAttribute(date)
      expect(result).toBe('2025-11-10T12:00:00.000Z')
    })
    
    it('returns empty string for empty input', () => {
      const result = formatDateTimeAttribute('')
      expect(result).toBe('')
    })
  })
})
