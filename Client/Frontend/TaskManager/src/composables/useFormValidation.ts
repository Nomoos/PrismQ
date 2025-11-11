import { ref, computed } from 'vue'
import { sanitizeWorkerId, isContentSafe } from '../utils/sanitize'

export interface ValidationRule {
  message: string
  validator: (value: any) => boolean
}

export interface FieldValidation {
  value: any
  rules: ValidationRule[]
  error: string | null
  touched: boolean
}

export function useFormValidation() {
  const fields = ref<Record<string, FieldValidation>>({})

  function registerField(
    name: string,
    initialValue: any = '',
    rules: ValidationRule[] = []
  ) {
    fields.value[name] = {
      value: initialValue,
      rules,
      error: null,
      touched: false
    }
  }

  function validateField(name: string): boolean {
    const field = fields.value[name]
    if (!field) return true

    field.touched = true
    
    for (const rule of field.rules) {
      if (!rule.validator(field.value)) {
        field.error = rule.message
        return false
      }
    }
    
    field.error = null
    return true
  }

  function validateAll(): boolean {
    let isValid = true
    
    for (const name in fields.value) {
      if (!validateField(name)) {
        isValid = false
      }
    }
    
    return isValid
  }

  function setValue(name: string, value: any) {
    if (fields.value[name]) {
      fields.value[name].value = value
      if (fields.value[name].touched) {
        validateField(name)
      }
    }
  }

  function resetField(name: string) {
    if (fields.value[name]) {
      fields.value[name].error = null
      fields.value[name].touched = false
    }
  }

  function resetAll() {
    for (const name in fields.value) {
      resetField(name)
    }
  }

  const isValid = computed(() => {
    return Object.values(fields.value).every(field => field.error === null)
  })

  const hasErrors = computed(() => {
    return Object.values(fields.value).some(field => field.error !== null)
  })

  return {
    fields,
    registerField,
    validateField,
    validateAll,
    setValue,
    resetField,
    resetAll,
    isValid,
    hasErrors
  }
}

// Common validation rules
export const validationRules = {
  required: (message = 'This field is required'): ValidationRule => ({
    message,
    validator: (value) => {
      if (typeof value === 'string') return value.trim().length > 0
      if (Array.isArray(value)) return value.length > 0
      return value !== null && value !== undefined
    }
  }),

  minLength: (min: number, message?: string): ValidationRule => ({
    message: message || `Minimum length is ${min} characters`,
    validator: (value) => {
      if (typeof value !== 'string') return true
      return value.length >= min
    }
  }),

  maxLength: (max: number, message?: string): ValidationRule => ({
    message: message || `Maximum length is ${max} characters`,
    validator: (value) => {
      if (typeof value !== 'string') return true
      return value.length <= max
    }
  }),

  email: (message = 'Invalid email format'): ValidationRule => ({
    message,
    validator: (value) => {
      if (typeof value !== 'string') return true
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(value)
    }
  }),

  numeric: (message = 'Must be a number'): ValidationRule => ({
    message,
    validator: (value) => {
      return !isNaN(Number(value))
    }
  }),

  min: (min: number, message?: string): ValidationRule => ({
    message: message || `Minimum value is ${min}`,
    validator: (value) => {
      const num = Number(value)
      return !isNaN(num) && num >= min
    }
  }),

  max: (max: number, message?: string): ValidationRule => ({
    message: message || `Maximum value is ${max}`,
    validator: (value) => {
      const num = Number(value)
      return !isNaN(num) && num <= max
    }
  }),

  pattern: (pattern: RegExp, message = 'Invalid format'): ValidationRule => ({
    message,
    validator: (value) => {
      if (typeof value !== 'string') return true
      return pattern.test(value)
    }
  }),

  custom: (validator: (value: any) => boolean, message: string): ValidationRule => ({
    message,
    validator
  }),

  // Worker ID validation
  workerId: (message = 'Invalid worker ID format'): ValidationRule => ({
    message,
    validator: (value) => {
      if (typeof value !== 'string') return false
      const sanitized = sanitizeWorkerId(value.trim())
      
      // Must be at least 3 characters after sanitization
      if (sanitized.length < 3) return false
      
      // Must not exceed 50 characters
      if (sanitized.length > 50) return false
      
      // Must start with alphanumeric
      if (!/^[a-zA-Z0-9]/.test(sanitized)) return false
      
      return true
    }
  }),

  // XSS safety check
  safeContent: (message = 'Content contains potentially unsafe characters'): ValidationRule => ({
    message,
    validator: (value) => {
      if (typeof value !== 'string') return true
      return isContentSafe(value)
    }
  })
}
