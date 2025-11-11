/**
 * Status helper utilities
 * 
 * Provides consistent status-related functionality across the application.
 */

/**
 * Get the color class for a task status
 * @param status - The task status
 * @returns Tailwind CSS color class
 */
export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    pending: 'bg-yellow-500 dark:bg-yellow-600',
    claimed: 'bg-blue-500 dark:bg-blue-600',
    completed: 'bg-green-500 dark:bg-green-600',
    failed: 'bg-red-500 dark:bg-red-600'
  }
  return colors[status] || 'bg-gray-500 dark:bg-gray-600'
}

/**
 * Get the text color class for a task status
 * @param status - The task status
 * @returns Tailwind CSS text color class
 */
export function getStatusTextColor(status: string): string {
  const colors: Record<string, string> = {
    pending: 'text-yellow-700 dark:text-yellow-400',
    claimed: 'text-blue-700 dark:text-blue-400',
    completed: 'text-green-700 dark:text-green-400',
    failed: 'text-red-700 dark:text-red-400'
  }
  return colors[status] || 'text-gray-700 dark:text-gray-400'
}

/**
 * Get a human-readable label for a status
 * @param status - The task status
 * @returns Capitalized status label
 */
export function getStatusLabel(status: string): string {
  if (!status) return ''
  return status.charAt(0).toUpperCase() + status.slice(1)
}

/**
 * Get an icon/emoji for a task status
 * @param status - The task status
 * @returns Icon or emoji representing the status
 */
export function getStatusIcon(status: string): string {
  const icons: Record<string, string> = {
    pending: '⏳',
    claimed: '🔄',
    completed: '✅',
    failed: '❌'
  }
  return icons[status] || '📋'
}

/**
 * Get all available task statuses
 * @returns Array of status values
 */
export function getAllStatuses(): string[] {
  return ['pending', 'claimed', 'completed', 'failed']
}

/**
 * Check if a status is a final state (completed or failed)
 * @param status - The task status
 * @returns True if the status is final
 */
export function isFinalStatus(status: string): boolean {
  return status === 'completed' || status === 'failed'
}

/**
 * Check if a status is an active state (pending or claimed)
 * @param status - The task status
 * @returns True if the status is active
 */
export function isActiveStatus(status: string): boolean {
  return status === 'pending' || status === 'claimed'
}
