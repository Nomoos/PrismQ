import { describe, it, expect } from 'vitest'
import {
  getStatusColor,
  getStatusTextColor,
  getStatusLabel,
  getStatusIcon,
  getAllStatuses,
  isFinalStatus,
  isActiveStatus
} from '../../src/utils/statusHelpers'

describe('statusHelpers', () => {
  describe('getStatusColor', () => {
    it('returns yellow for pending status', () => {
      expect(getStatusColor('pending')).toContain('yellow')
    })
    
    it('returns blue for claimed status', () => {
      expect(getStatusColor('claimed')).toContain('blue')
    })
    
    it('returns green for completed status', () => {
      expect(getStatusColor('completed')).toContain('green')
    })
    
    it('returns red for failed status', () => {
      expect(getStatusColor('failed')).toContain('red')
    })
    
    it('returns gray for unknown status', () => {
      expect(getStatusColor('unknown')).toContain('gray')
    })
  })
  
  describe('getStatusTextColor', () => {
    it('returns text color classes', () => {
      expect(getStatusTextColor('pending')).toContain('text-')
      expect(getStatusTextColor('claimed')).toContain('text-')
      expect(getStatusTextColor('completed')).toContain('text-')
      expect(getStatusTextColor('failed')).toContain('text-')
    })
    
    it('handles dark mode classes', () => {
      expect(getStatusTextColor('pending')).toContain('dark:')
    })
  })
  
  describe('getStatusLabel', () => {
    it('capitalizes status', () => {
      expect(getStatusLabel('pending')).toBe('Pending')
      expect(getStatusLabel('claimed')).toBe('Claimed')
      expect(getStatusLabel('completed')).toBe('Completed')
      expect(getStatusLabel('failed')).toBe('Failed')
    })
    
    it('returns empty string for empty status', () => {
      expect(getStatusLabel('')).toBe('')
    })
  })
  
  describe('getStatusIcon', () => {
    it('returns icons for each status', () => {
      expect(getStatusIcon('pending')).toBe('⏳')
      expect(getStatusIcon('claimed')).toBe('🔄')
      expect(getStatusIcon('completed')).toBe('✅')
      expect(getStatusIcon('failed')).toBe('❌')
    })
    
    it('returns default icon for unknown status', () => {
      expect(getStatusIcon('unknown')).toBe('📋')
    })
  })
  
  describe('getAllStatuses', () => {
    it('returns array of all statuses', () => {
      const statuses = getAllStatuses()
      expect(statuses).toEqual(['pending', 'claimed', 'completed', 'failed'])
    })
  })
  
  describe('isFinalStatus', () => {
    it('returns true for completed status', () => {
      expect(isFinalStatus('completed')).toBe(true)
    })
    
    it('returns true for failed status', () => {
      expect(isFinalStatus('failed')).toBe(true)
    })
    
    it('returns false for pending status', () => {
      expect(isFinalStatus('pending')).toBe(false)
    })
    
    it('returns false for claimed status', () => {
      expect(isFinalStatus('claimed')).toBe(false)
    })
  })
  
  describe('isActiveStatus', () => {
    it('returns true for pending status', () => {
      expect(isActiveStatus('pending')).toBe(true)
    })
    
    it('returns true for claimed status', () => {
      expect(isActiveStatus('claimed')).toBe(true)
    })
    
    it('returns false for completed status', () => {
      expect(isActiveStatus('completed')).toBe(false)
    })
    
    it('returns false for failed status', () => {
      expect(isActiveStatus('failed')).toBe(false)
    })
  })
})
