import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import TaskCard from '../../src/components/TaskCard.vue'
import StatusBadge from '../../src/components/base/StatusBadge.vue'
import type { Task } from '../../src/types'

describe('TaskCard.vue', () => {
  const mockTask: Task = {
    id: 1,
    type: 'test-task',
    type_id: 1,
    status: 'pending',
    priority: 1,
    attempts: 0,
    max_attempts: 3,
    progress: 0,
    created_at: '2025-11-10T12:00:00Z',
    updated_at: '2025-11-10T12:00:00Z',
    claimed_at: null,
    completed_at: null,
    worker_id: null,
    params: {},
    result: null,
    error: null
  }
  
  it('renders task information', () => {
    const wrapper = mount(TaskCard, {
      props: {
        task: mockTask
      },
      global: {
        components: {
          StatusBadge
        }
      }
    })
    
    expect(wrapper.text()).toContain('test-task')
    expect(wrapper.text()).toContain('ID: 1')
    expect(wrapper.text()).toContain('Priority: 1')
    expect(wrapper.text()).toContain('Attempts: 0/3')
  })
  
  it('renders StatusBadge component', () => {
    const wrapper = mount(TaskCard, {
      props: {
        task: mockTask
      },
      global: {
        components: {
          StatusBadge
        }
      }
    })
    
    const badge = wrapper.findComponent(StatusBadge)
    expect(badge.exists()).toBe(true)
    expect(badge.props('status')).toBe('pending')
  })
  
  it('shows progress bar when task is claimed with progress', () => {
    const claimedTask = { ...mockTask, status: 'claimed', progress: 50 }
    const wrapper = mount(TaskCard, {
      props: {
        task: claimedTask
      },
      global: {
        components: {
          StatusBadge
        }
      }
    })
    
    const progressBar = wrapper.find('[role="progressbar"]')
    expect(progressBar.exists()).toBe(true)
    expect(progressBar.attributes('aria-valuenow')).toBe('50')
    expect(wrapper.text()).toContain('50% complete')
  })
  
  it('hides progress bar when showProgress is false', () => {
    const claimedTask = { ...mockTask, status: 'claimed', progress: 50 }
    const wrapper = mount(TaskCard, {
      props: {
        task: claimedTask,
        showProgress: false
      },
      global: {
        components: {
          StatusBadge
        }
      }
    })
    
    const progressBar = wrapper.find('[role="progressbar"]')
    expect(progressBar.exists()).toBe(false)
  })
  
  it('hides date when showDate is false', () => {
    const wrapper = mount(TaskCard, {
      props: {
        task: mockTask,
        showDate: false
      },
      global: {
        components: {
          StatusBadge
        }
      }
    })
    
    expect(wrapper.text()).not.toMatch(/ago/)
  })
  
  it('emits click event with task id when clicked', async () => {
    const wrapper = mount(TaskCard, {
      props: {
        task: mockTask
      },
      global: {
        components: {
          StatusBadge
        }
      }
    })
    
    await wrapper.trigger('click')
    
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')?.[0]).toEqual([1])
  })
  
  it('emits click event on Enter key', async () => {
    const wrapper = mount(TaskCard, {
      props: {
        task: mockTask
      },
      global: {
        components: {
          StatusBadge
        }
      }
    })
    
    await wrapper.trigger('keydown.enter')
    
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')?.[0]).toEqual([1])
  })
  
  it('emits click event on Space key', async () => {
    const wrapper = mount(TaskCard, {
      props: {
        task: mockTask
      },
      global: {
        components: {
          StatusBadge
        }
      }
    })
    
    await wrapper.trigger('keydown.space')
    
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')?.[0]).toEqual([1])
  })
  
  it('has correct ARIA attributes', () => {
    const wrapper = mount(TaskCard, {
      props: {
        task: mockTask
      },
      global: {
        components: {
          StatusBadge
        }
      }
    })
    
    const article = wrapper.find('article')
    expect(article.attributes('role')).toBe('listitem')
    expect(article.attributes('tabindex')).toBe('0')
    expect(article.attributes('aria-label')).toContain('test-task')
    expect(article.attributes('aria-label')).toContain('ID 1')
    expect(article.attributes('aria-label')).toContain('status pending')
    expect(article.attributes('aria-label')).toContain('priority 1')
  })
  
  it('applies correct status color', () => {
    const wrapper = mount(TaskCard, {
      props: {
        task: mockTask
      },
      global: {
        components: {
          StatusBadge
        }
      }
    })
    
    const statusDot = wrapper.find('[role="img"]')
    expect(statusDot.classes()).toContain('bg-yellow-500')
  })
})
