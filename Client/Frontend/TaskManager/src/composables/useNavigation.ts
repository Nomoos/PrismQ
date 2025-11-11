import { ref, computed } from 'vue'

// Navigation hierarchy: Tree structure with PrismQ as root
export type NavigationLevel = 
  | 'PrismQ' 
  | 'PrismQ.Idea' 
  | 'PrismQ.IdeaInspiration' 
  | 'PrismQ.Draft'
  | 'PrismQ.Script'
  | 'PrismQ.Proofreading'
  | 'PrismQ.Voiceover'

const STORAGE_KEY = 'prismq_navigation_position'
const STORAGE_KEY_HISTORY = 'prismq_navigation_history'

function loadPosition(): NavigationLevel {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved && isValidLevel(saved)) {
    return saved as NavigationLevel
  }
  return 'PrismQ' // Default starting position (root)
}

function loadHistory(): NavigationLevel[] {
  const saved = localStorage.getItem(STORAGE_KEY_HISTORY)
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed) && parsed.every(isValidLevel)) {
        return parsed as NavigationLevel[]
      }
    } catch {
      // Invalid history, return default
    }
  }
  return ['PrismQ'] // Start with root
}

// Persistent state - initialize lazily in useNavigation
let currentPosition = ref<NavigationLevel>(loadPosition())
let navigationHistory = ref<NavigationLevel[]>(loadHistory())
let isInitialized = false

// Initialize state
function initializeState() {
  if (!isInitialized) {
    currentPosition = ref<NavigationLevel>(loadPosition())
    navigationHistory = ref<NavigationLevel[]>(loadHistory())
    isInitialized = true
  }
}

// For testing purposes - reset the singleton state
export function __resetNavigationState() {
  isInitialized = false
  currentPosition = ref<NavigationLevel>('PrismQ')
  navigationHistory = ref<NavigationLevel[]>(['PrismQ'])
  localStorage.removeItem(STORAGE_KEY)
  localStorage.removeItem(STORAGE_KEY_HISTORY)
}

function isValidLevel(level: string): boolean {
  return [
    'PrismQ',
    'PrismQ.Idea',
    'PrismQ.IdeaInspiration',
    'PrismQ.Draft',
    'PrismQ.Script',
    'PrismQ.Proofreading',
    'PrismQ.Voiceover'
  ].includes(level)
}

function savePosition(level: NavigationLevel) {
  initializeState()
  localStorage.setItem(STORAGE_KEY, level)
  currentPosition.value = level
  
  // Update history
  const newHistory = [...navigationHistory.value]
  const currentIndex = newHistory.indexOf(level)
  
  if (currentIndex >= 0) {
    // Remove everything after this position
    navigationHistory.value = newHistory.slice(0, currentIndex + 1)
  } else {
    // Add to history
    navigationHistory.value = [...newHistory, level]
  }
  
  localStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify(navigationHistory.value))
}

export function useNavigation() {
  initializeState()
  
  // Define the tree structure
  const childNodes: Record<string, NavigationLevel[]> = {
    'PrismQ': [
      'PrismQ.Idea',
      'PrismQ.IdeaInspiration',
      'PrismQ.Draft',
      'PrismQ.Script',
      'PrismQ.Proofreading',
      'PrismQ.Voiceover'
    ]
  }
  
  // Get available child nodes for current position
  const availableChildren = computed(() => {
    return childNodes[currentPosition.value] || []
  })
  
  // Get parent node
  const parentNode = computed(() => {
    const current = currentPosition.value
    if (current.startsWith('PrismQ.')) {
      return 'PrismQ' as NavigationLevel
    }
    return null
  })
  
  // Navigation history for back/forward
  const historyIndex = computed(() => {
    return navigationHistory.value.indexOf(currentPosition.value)
  })
  
  const canGoBack = computed(() => historyIndex.value > 0)
  const canGoForward = computed(() => historyIndex.value < navigationHistory.value.length - 1)
  
  // Build breadcrumbs based on hierarchy
  const breadcrumbs = computed(() => {
    const current = currentPosition.value
    const crumbs: Array<{ level: NavigationLevel; label: string; isActive: boolean }> = []
    
    // Always start with root
    crumbs.push({
      level: 'PrismQ',
      label: 'PrismQ',
      isActive: current === 'PrismQ'
    })
    
    // Add current if it's a child node
    if (current.startsWith('PrismQ.')) {
      const label = current.split('.')[1] // Extract the part after 'PrismQ.'
      crumbs.push({
        level: current,
        label: label,
        isActive: true
      })
    }
    
    return crumbs
  })
  
  function navigateTo(level: NavigationLevel) {
    if (isValidLevel(level)) {
      savePosition(level)
    }
  }
  
  function goBack() {
    if (canGoBack.value) {
      const newPosition = navigationHistory.value[historyIndex.value - 1]
      currentPosition.value = newPosition
      localStorage.setItem(STORAGE_KEY, newPosition)
    }
  }
  
  function goForward() {
    if (canGoForward.value) {
      const newPosition = navigationHistory.value[historyIndex.value + 1]
      currentPosition.value = newPosition
      localStorage.setItem(STORAGE_KEY, newPosition)
    }
  }
  
  function goToParent() {
    if (parentNode.value) {
      savePosition(parentNode.value)
    }
  }
  
  function reset() {
    navigationHistory.value = ['PrismQ']
    savePosition('PrismQ')
  }
  
  return {
    currentPosition: computed(() => currentPosition.value),
    availableChildren,
    parentNode,
    canGoBack,
    canGoForward,
    breadcrumbs,
    navigateTo,
    goBack,
    goForward,
    goToParent,
    reset
  }
}
