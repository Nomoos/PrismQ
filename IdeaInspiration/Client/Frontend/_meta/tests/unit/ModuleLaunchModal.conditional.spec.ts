import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ModuleLaunchModal from '@/components/ModuleLaunchModal.vue'
import type { Module } from '@/types/module'

// Mock the moduleService
vi.mock('@/services/modules', () => ({
  moduleService: {
    getConfig: vi.fn().mockResolvedValue({
      module_id: 'youtube-shorts',
      parameters: { mode: 'trending' },
      updated_at: new Date().toISOString()
    }),
    deleteConfig: vi.fn().mockResolvedValue(true)
  }
}))

describe('ModuleLaunchModal Conditional Display', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  const youtubeModule: Module = {
    id: 'youtube-shorts',
    name: 'YouTube Shorts Source',
    description: 'Collect YouTube Shorts',
    category: 'Sources',
    version: '2.0.0',
    script_path: '/test/path',
    parameters: [
      {
        name: 'mode',
        type: 'select',
        default: 'trending',
        label: 'Scraping Mode',
        description: 'Choose how to collect YouTube Shorts',
        options: ['trending', 'channel', 'keyword'],
        required: true
      },
      {
        name: 'channel_url',
        type: 'text',
        default: '',
        label: 'Channel URL',
        description: 'YouTube channel URL',
        placeholder: 'https://www.youtube.com/@channelname',
        required: false,
        conditional_display: {
          field: 'mode',
          value: 'channel'
        },
        validation: {
          pattern: '^(https?://)?(www\\.)?youtube\\.com/([@\\w-]+|channel/[\\w-]+)|@[\\w-]+|UC[\\w-]+$',
          message: 'Must be a valid YouTube channel URL'
        }
      },
      {
        name: 'query',
        type: 'text',
        default: '',
        label: 'Search Query',
        description: 'Keyword to search for',
        placeholder: 'startup ideas',
        required: false,
        conditional_display: {
          field: 'mode',
          value: 'keyword'
        },
        warning: '⚠️ Keyword search is in development (Issue #300)'
      },
      {
        name: 'max_results',
        type: 'number',
        default: 50,
        min: 1,
        max: 100,
        label: 'Maximum Results',
        description: 'Number of Shorts to collect',
        required: false
      },
      {
        name: 'category',
        type: 'select',
        default: 'All',
        label: 'Category Filter',
        description: 'Filter trending Shorts',
        options: ['All', 'Gaming', 'Music', 'Entertainment'],
        required: false,
        conditional_display: {
          field: 'mode',
          value: 'trending'
        }
      }
    ],
    tags: ['youtube'],
    status: 'active',
    total_runs: 0,
    success_rate: 100,
    enabled: true
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should show only trending mode parameters initially', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: youtubeModule }
    })

    await flushPromises()

    // Should show mode selector
    expect(wrapper.text()).toContain('Scraping Mode')
    
    // Should show category (trending mode)
    expect(wrapper.text()).toContain('Category Filter')
    
    // Should show max_results (always visible)
    expect(wrapper.text()).toContain('Maximum Results')
    
    // Should NOT show channel_url (channel mode only)
    expect(wrapper.text()).not.toContain('Channel URL')
    
    // Should NOT show query (keyword mode only)
    expect(wrapper.text()).not.toContain('Search Query')
  })

  it('should show channel_url when mode is changed to channel', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: youtubeModule }
    })

    await flushPromises()

    // Initially no channel URL
    expect(wrapper.text()).not.toContain('Channel URL')

    // Change mode to channel
    const modeSelect = wrapper.find('select[id="mode"]')
    await modeSelect.setValue('channel')
    await wrapper.vm.$nextTick()

    // Now channel URL should be visible
    expect(wrapper.text()).toContain('Channel URL')
    
    // Category should be hidden
    expect(wrapper.text()).not.toContain('Category Filter')
    
    // Query should still be hidden
    expect(wrapper.text()).not.toContain('Search Query')
  })

  it('should show query when mode is changed to keyword', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: youtubeModule }
    })

    await flushPromises()

    // Change mode to keyword
    const modeSelect = wrapper.find('select[id="mode"]')
    await modeSelect.setValue('keyword')
    await wrapper.vm.$nextTick()

    // Now query should be visible
    expect(wrapper.text()).toContain('Search Query')
    
    // Should show warning
    expect(wrapper.text()).toContain('⚠️')
    expect(wrapper.text()).toContain('Issue #300')
    
    // Category should be hidden
    expect(wrapper.text()).not.toContain('Category Filter')
    
    // Channel URL should be hidden
    expect(wrapper.text()).not.toContain('Channel URL')
  })

  it('should display mode icons in select options', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: youtubeModule }
    })

    await flushPromises()

    const modeSelect = wrapper.find('select[id="mode"]')
    const options = modeSelect.findAll('option')
    
    // Check for emoji icons
    expect(options[0].text()).toContain('📈')  // trending
    expect(options[1].text()).toContain('👤')  // channel
    expect(options[2].text()).toContain('🔍')  // keyword
  })

  it('should validate channel URL with regex pattern', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: youtubeModule }
    })

    await flushPromises()

    // Change to channel mode
    const modeSelect = wrapper.find('select[id="mode"]')
    await modeSelect.setValue('channel')
    await wrapper.vm.$nextTick()

    // Enter invalid URL
    const channelInput = wrapper.find('input[id="channel_url"]')
    await channelInput.setValue('invalid-url')
    await channelInput.trigger('blur')
    
    // Submit form
    const form = wrapper.find('form')
    await form.trigger('submit.prevent')
    await wrapper.vm.$nextTick()

    // Should show validation error
    expect(wrapper.text()).toContain('Must be a valid YouTube channel URL')
  })

  it('should accept valid channel URL', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: youtubeModule }
    })

    await flushPromises()

    // Change to channel mode
    const modeSelect = wrapper.find('select[id="mode"]')
    await modeSelect.setValue('channel')
    await wrapper.vm.$nextTick()

    // Enter valid URL
    const channelInput = wrapper.find('input[id="channel_url"]')
    await channelInput.setValue('https://www.youtube.com/@testchannel')
    await wrapper.vm.$nextTick()

    // Should show validation success
    expect(wrapper.text()).toContain('✓ Valid')
  })

  it('should clear dependent fields when mode changes', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: youtubeModule }
    })

    await flushPromises()

    // Change to channel mode
    const modeSelect = wrapper.find('select[id="mode"]')
    await modeSelect.setValue('channel')
    await wrapper.vm.$nextTick()

    // Enter channel URL
    const channelInput = wrapper.find('input[id="channel_url"]')
    await channelInput.setValue('https://www.youtube.com/@test')
    
    // Change back to trending
    await modeSelect.setValue('trending')
    await wrapper.vm.$nextTick()

    // Change to channel again - field should be cleared
    await modeSelect.setValue('channel')
    await wrapper.vm.$nextTick()

    const channelInputAfter = wrapper.find('input[id="channel_url"]')
    expect(channelInputAfter.element.value).toBe('')
  })

  it('should only send visible parameters on submit', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: youtubeModule }
    })

    await flushPromises()

    // Fill in category (visible in trending mode)
    const categorySelect = wrapper.find('select[id="category"]')
    await categorySelect.setValue('Gaming')
    
    // Submit form
    const form = wrapper.find('form')
    await form.trigger('submit.prevent')
    await wrapper.vm.$nextTick()

    const launchEvent = wrapper.emitted('launch')
    expect(launchEvent).toBeTruthy()
    
    if (launchEvent) {
      const params = launchEvent[0][0]
      // Should include mode and category
      expect(params).toHaveProperty('mode', 'trending')
      expect(params).toHaveProperty('category', 'Gaming')
      // Should NOT include channel_url (not visible)
      expect(params).not.toHaveProperty('channel_url')
      // Should NOT include query (not visible)
      expect(params).not.toHaveProperty('query')
    }
  })

  it('should disable submit button when form is invalid', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: youtubeModule }
    })

    await flushPromises()

    // Change to channel mode (requires channel_url)
    const modeSelect = wrapper.find('select[id="mode"]')
    await modeSelect.setValue('channel')
    await wrapper.vm.$nextTick()

    // Enter invalid channel URL
    const channelInput = wrapper.find('input[id="channel_url"]')
    await channelInput.setValue('invalid')
    await wrapper.vm.$nextTick()

    // Submit button should be disabled
    const submitButton = wrapper.find('.btn-primary')
    expect(submitButton.attributes('disabled')).toBeDefined()
  })

  it('should show help icon when both label and description exist', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: youtubeModule }
    })

    await flushPromises()

    // Check for help icons
    const helpIcons = wrapper.findAll('.help-icon')
    expect(helpIcons.length).toBeGreaterThan(0)
  })

  it('should display warning message for keyword mode', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: youtubeModule }
    })

    await flushPromises()

    // Change to keyword mode
    const modeSelect = wrapper.find('select[id="mode"]')
    await modeSelect.setValue('keyword')
    await wrapper.vm.$nextTick()

    // Should find warning message
    const warning = wrapper.find('.warning-message')
    expect(warning.exists()).toBe(true)
    expect(warning.text()).toContain('⚠️')
    expect(warning.text()).toContain('Issue #300')
  })
})
