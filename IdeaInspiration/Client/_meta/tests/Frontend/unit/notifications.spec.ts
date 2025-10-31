import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useNotificationStore } from '@/stores/notifications'

describe('Notification Store', () => {
  beforeEach(() => {
    // Create a fresh pinia instance for each test
    setActivePinia(createPinia())
    
    // Clear any existing timers
    vi.clearAllTimers()
  })

  it('should initialize with empty notifications', () => {
    const store = useNotificationStore()
    expect(store.notifications).toEqual([])
  })

  it('should add a notification with success type', () => {
    const store = useNotificationStore()
    
    store.success({
      title: 'Success',
      message: 'Operation completed successfully',
    })

    expect(store.notifications).toHaveLength(1)
    expect(store.notifications[0].type).toBe('success')
    expect(store.notifications[0].title).toBe('Success')
    expect(store.notifications[0].message).toBe('Operation completed successfully')
    expect(store.notifications[0].id).toBeDefined()
  })

  it('should add a notification with error type', () => {
    const store = useNotificationStore()
    
    store.error({
      title: 'Error',
      message: 'Something went wrong',
      errorCode: 'ERR_001',
    })

    expect(store.notifications).toHaveLength(1)
    expect(store.notifications[0].type).toBe('error')
    expect(store.notifications[0].errorCode).toBe('ERR_001')
    expect(store.notifications[0].duration).toBe(10000) // Errors have 10s duration
  })

  it('should add a notification with warning type', () => {
    const store = useNotificationStore()
    
    store.warning({
      title: 'Warning',
      message: 'This is a warning',
    })

    expect(store.notifications).toHaveLength(1)
    expect(store.notifications[0].type).toBe('warning')
  })

  it('should add a notification with info type', () => {
    const store = useNotificationStore()
    
    store.info({
      title: 'Info',
      message: 'This is informational',
    })

    expect(store.notifications).toHaveLength(1)
    expect(store.notifications[0].type).toBe('info')
  })

  it('should remove notification by id', () => {
    const store = useNotificationStore()
    
    store.success({ title: 'Test', message: 'Message 1' })
    store.success({ title: 'Test', message: 'Message 2' })

    expect(store.notifications).toHaveLength(2)

    const firstId = store.notifications[0].id
    store.remove(firstId)

    expect(store.notifications).toHaveLength(1)
    expect(store.notifications[0].message).toBe('Message 2')
  })

  it('should clear all notifications', () => {
    const store = useNotificationStore()
    
    store.success({ title: 'Test', message: 'Message 1' })
    store.error({ title: 'Test', message: 'Message 2' })
    store.warning({ title: 'Test', message: 'Message 3' })

    expect(store.notifications).toHaveLength(3)

    store.clear()

    expect(store.notifications).toHaveLength(0)
  })

  it('should auto-remove notification after duration', async () => {
    vi.useFakeTimers()
    const store = useNotificationStore()
    
    store.success({
      title: 'Test',
      message: 'Auto-remove test',
      duration: 1000,
    })

    expect(store.notifications).toHaveLength(1)

    // Fast-forward time
    vi.advanceTimersByTime(1000)

    expect(store.notifications).toHaveLength(0)

    vi.useRealTimers()
  })

  it('should use default duration for success notifications', () => {
    const store = useNotificationStore()
    
    store.success({ title: 'Test', message: 'Test' })

    expect(store.notifications[0].duration).toBe(5000)
  })

  it('should use longer duration for error notifications', () => {
    const store = useNotificationStore()
    
    store.error({ title: 'Test', message: 'Test' })

    expect(store.notifications[0].duration).toBe(10000)
  })

  it('should respect custom duration', () => {
    const store = useNotificationStore()
    
    store.success({ 
      title: 'Test', 
      message: 'Test',
      duration: 15000,
    })

    expect(store.notifications[0].duration).toBe(15000)
  })

  it('should generate unique IDs for notifications', () => {
    const store = useNotificationStore()
    
    store.success({ title: 'Test', message: 'Message 1' })
    store.success({ title: 'Test', message: 'Message 2' })

    const id1 = store.notifications[0].id
    const id2 = store.notifications[1].id

    expect(id1).not.toBe(id2)
  })

  it('should handle removing non-existent notification gracefully', () => {
    const store = useNotificationStore()
    
    store.success({ title: 'Test', message: 'Test' })
    expect(store.notifications).toHaveLength(1)

    store.remove('non-existent-id')
    expect(store.notifications).toHaveLength(1)
  })
})
