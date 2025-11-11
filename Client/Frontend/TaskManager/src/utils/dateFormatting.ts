/**
 * Date formatting utilities
 * 
 * Provides consistent date formatting across the application.
 */

/**
 * Format a date as a localized string
 * @param date - The date to format
 * @returns Formatted date string (e.g., "11/10/2025, 10:30:00 AM")
 */
export function formatDate(date: string | Date): string {
  if (!date) return ''
  return new Date(date).toLocaleString()
}

/**
 * Format a date as a short localized string
 * @param date - The date to format
 * @returns Short formatted date string (e.g., "Nov 10, 2025")
 */
export function formatDateShort(date: string | Date): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

/**
 * Format a date as relative time
 * @param date - The date to format
 * @returns Relative time string (e.g., "2 hours ago", "yesterday")
 */
export function formatRelativeTime(date: string | Date): string {
  if (!date) return ''
  
  const now = new Date()
  const target = new Date(date)
  const diffInSeconds = Math.floor((now.getTime() - target.getTime()) / 1000)
  
  if (diffInSeconds < 60) {
    return 'just now'
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60)
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes === 1 ? '' : 's'} ago`
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours === 1 ? '' : 's'} ago`
  }
  
  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays === 1) {
    return 'yesterday'
  }
  if (diffInDays < 7) {
    return `${diffInDays} days ago`
  }
  
  const diffInWeeks = Math.floor(diffInDays / 7)
  if (diffInWeeks < 4) {
    return `${diffInWeeks} week${diffInWeeks === 1 ? '' : 's'} ago`
  }
  
  // For older dates, return short format
  return formatDateShort(date)
}

/**
 * Format a date for display in a time element
 * @param date - The date to format
 * @returns ISO string for datetime attribute
 */
export function formatDateTimeAttribute(date: string | Date): string {
  if (!date) return ''
  return new Date(date).toISOString()
}
