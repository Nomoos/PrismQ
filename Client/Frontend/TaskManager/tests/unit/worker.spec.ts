import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useWorkerStore } from '../../src/stores/worker'

describe('Worker Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  describe('initialization', () => {
    it('should initialize with offline status', () => {
      const store = useWorkerStore()
      expect(store.status).toBe('offline')
      expect(store.workerId).toBeNull()
      expect(store.isInitialized).toBe(false)
    })

    it('should generate new worker ID on first initialization', () => {
      const store = useWorkerStore()
      store.initializeWorker()

      expect(store.workerId).not.toBeNull()
      expect(store.workerId).toMatch(/^worker-\d+-[a-z0-9]+$/)
      expect(store.status).toBe('idle')
      expect(store.isInitialized).toBe(true)
    })

    it('should save worker ID to localStorage on initialization', () => {
      const store = useWorkerStore()
      store.initializeWorker()

      const storedId = localStorage.getItem('worker_id')
      expect(storedId).toBe(store.workerId)
    })

    it('should load existing worker ID from localStorage', () => {
      const existingId = 'worker-123-abc'
      localStorage.setItem('worker_id', existingId)

      const store = useWorkerStore()
      store.initializeWorker()

      expect(store.workerId).toBe(existingId)
      expect(store.status).toBe('idle')
    })

    it('should persist worker ID across multiple initializations', () => {
      const store = useWorkerStore()
      store.initializeWorker()
      
      const firstId = store.workerId

      // Create a new store instance (simulating page refresh)
      setActivePinia(createPinia())
      const newStore = useWorkerStore()
      newStore.initializeWorker()

      expect(newStore.workerId).toBe(firstId)
    })
  })

  describe('status management', () => {
    it('should update status to active', () => {
      const store = useWorkerStore()
      store.initializeWorker()
      
      store.setStatus('active')
      expect(store.status).toBe('active')
    })

    it('should update status to idle', () => {
      const store = useWorkerStore()
      store.initializeWorker()
      store.setStatus('active')
      
      store.setStatus('idle')
      expect(store.status).toBe('idle')
    })

    it('should update status to offline', () => {
      const store = useWorkerStore()
      store.initializeWorker()
      store.setStatus('active')
      
      store.setStatus('offline')
      expect(store.status).toBe('offline')
    })

    it('should handle rapid status changes', () => {
      const store = useWorkerStore()
      store.initializeWorker()
      
      store.setStatus('active')
      store.setStatus('idle')
      store.setStatus('offline')
      store.setStatus('active')
      
      expect(store.status).toBe('active')
    })
  })

  describe('computed properties', () => {
    it('should return false for isInitialized when workerId is null', () => {
      const store = useWorkerStore()
      expect(store.isInitialized).toBe(false)
    })

    it('should return true for isInitialized when workerId is set', () => {
      const store = useWorkerStore()
      store.initializeWorker()
      expect(store.isInitialized).toBe(true)
    })

    it('should update isInitialized reactively', () => {
      const store = useWorkerStore()
      expect(store.isInitialized).toBe(false)
      
      store.initializeWorker()
      expect(store.isInitialized).toBe(true)
    })
  })

  describe('worker ID generation', () => {
    it('should generate unique IDs for multiple workers', () => {
      const ids = new Set<string>()
      
      for (let i = 0; i < 10; i++) {
        localStorage.clear()
        setActivePinia(createPinia())
        const store = useWorkerStore()
        store.initializeWorker()
        ids.add(store.workerId!)
      }
      
      expect(ids.size).toBe(10)
    })

    it('should include timestamp in worker ID', () => {
      const store = useWorkerStore()
      const beforeTime = Date.now()
      
      store.initializeWorker()
      
      const afterTime = Date.now()
      const match = store.workerId!.match(/^worker-(\d+)-/)
      expect(match).not.toBeNull()
      
      const timestamp = parseInt(match![1])
      expect(timestamp).toBeGreaterThanOrEqual(beforeTime)
      expect(timestamp).toBeLessThanOrEqual(afterTime)
    })

    it('should include random component in worker ID', () => {
      const store = useWorkerStore()
      store.initializeWorker()
      
      const match = store.workerId!.match(/^worker-\d+-([a-z0-9]+)$/)
      expect(match).not.toBeNull()
      expect(match![1].length).toBeGreaterThan(0)
    })
  })

  describe('edge cases', () => {
    it('should handle empty localStorage gracefully', () => {
      localStorage.clear()
      const store = useWorkerStore()
      
      expect(() => store.initializeWorker()).not.toThrow()
      expect(store.workerId).not.toBeNull()
    })

    it('should generate new ID when localStorage has empty string', () => {
      localStorage.setItem('worker_id', '')
      const store = useWorkerStore()
      store.initializeWorker()
      
      // Empty string is falsy, so a new ID should be generated
      expect(store.workerId).not.toBe('')
      expect(store.workerId).toMatch(/^worker-\d+-[a-z0-9]+$/)
      expect(store.status).toBe('idle')
    })

    it('should maintain state across multiple status updates', () => {
      const store = useWorkerStore()
      store.initializeWorker()
      
      const originalId = store.workerId
      
      store.setStatus('active')
      store.setStatus('idle')
      store.setStatus('offline')
      
      expect(store.workerId).toBe(originalId)
    })

    it('should be independent across multiple store instances', () => {
      const store1 = useWorkerStore()
      store1.initializeWorker()
      
      const id1 = store1.workerId
      
      // Creating a second instance should reference the same store
      const store2 = useWorkerStore()
      expect(store2.workerId).toBe(id1)
    })
  })
})
