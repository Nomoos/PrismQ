import { describe, it, expect, beforeEach } from 'vitest'
import { useFormValidation, validationRules } from '@/composables/useFormValidation'

describe('useFormValidation Composable', () => {
  describe('field registration', () => {
    it('should register a field with initial value and rules', () => {
      const { registerField, fields } = useFormValidation()

      registerField('username', 'test', [validationRules.required()])

      expect(fields.value.username).toBeDefined()
      expect(fields.value.username.value).toBe('test')
      expect(fields.value.username.rules).toHaveLength(1)
      expect(fields.value.username.error).toBeNull()
      expect(fields.value.username.touched).toBe(false)
    })

    it('should use default empty string for initial value', () => {
      const { registerField, fields } = useFormValidation()

      registerField('email')

      expect(fields.value.email.value).toBe('')
    })

    it('should use empty array for rules when not provided', () => {
      const { registerField, fields } = useFormValidation()

      registerField('name', 'test')

      expect(fields.value.name.rules).toEqual([])
    })
  })

  describe('validateField', () => {
    it('should validate a single field successfully', () => {
      const { registerField, validateField, fields } = useFormValidation()

      registerField('username', 'test', [validationRules.required()])

      const isValid = validateField('username')

      expect(isValid).toBe(true)
      expect(fields.value.username.error).toBeNull()
      expect(fields.value.username.touched).toBe(true)
    })

    it('should fail validation and set error message', () => {
      const { registerField, validateField, fields } = useFormValidation()

      registerField('username', '', [validationRules.required('Username is required')])

      const isValid = validateField('username')

      expect(isValid).toBe(false)
      expect(fields.value.username.error).toBe('Username is required')
      expect(fields.value.username.touched).toBe(true)
    })

    it('should return true for non-existent field', () => {
      const { validateField } = useFormValidation()

      const isValid = validateField('nonexistent')

      expect(isValid).toBe(true)
    })

    it('should stop at first failing rule', () => {
      const { registerField, validateField, fields } = useFormValidation()

      registerField('password', '12', [
        validationRules.required('Required'),
        validationRules.minLength(8, 'Min 8 chars')
      ])

      validateField('password')

      expect(fields.value.password.error).toBe('Min 8 chars')
    })

    it('should clear error when validation passes', () => {
      const { registerField, validateField, fields } = useFormValidation()

      registerField('username', '', [validationRules.required()])
      
      validateField('username')
      expect(fields.value.username.error).not.toBeNull()

      fields.value.username.value = 'test'
      validateField('username')
      expect(fields.value.username.error).toBeNull()
    })
  })

  describe('validateAll', () => {
    it('should validate all fields', () => {
      const { registerField, validateAll } = useFormValidation()

      registerField('username', 'test', [validationRules.required()])
      registerField('email', 'test@example.com', [validationRules.email()])

      const isValid = validateAll()

      expect(isValid).toBe(true)
    })

    it('should return false if any field is invalid', () => {
      const { registerField, validateAll, fields } = useFormValidation()

      registerField('username', '', [validationRules.required()])
      registerField('email', 'test@example.com', [validationRules.email()])

      const isValid = validateAll()

      expect(isValid).toBe(false)
      expect(fields.value.username.error).not.toBeNull()
      expect(fields.value.email.error).toBeNull()
    })

    it('should mark all fields as touched', () => {
      const { registerField, validateAll, fields } = useFormValidation()

      registerField('field1', 'value')
      registerField('field2', 'value')

      validateAll()

      expect(fields.value.field1.touched).toBe(true)
      expect(fields.value.field2.touched).toBe(true)
    })
  })

  describe('setValue', () => {
    it('should update field value', () => {
      const { registerField, setValue, fields } = useFormValidation()

      registerField('username', 'old')

      setValue('username', 'new')

      expect(fields.value.username.value).toBe('new')
    })

    it('should validate field if already touched', () => {
      const { registerField, setValue, fields } = useFormValidation()

      registerField('username', 'test', [validationRules.minLength(5)])
      
      fields.value.username.touched = true
      setValue('username', 'hi')

      expect(fields.value.username.error).not.toBeNull()
    })

    it('should not validate field if not touched', () => {
      const { registerField, setValue, fields } = useFormValidation()

      registerField('username', 'test', [validationRules.minLength(5)])
      
      setValue('username', 'hi')

      expect(fields.value.username.error).toBeNull()
    })

    it('should handle non-existent field gracefully', () => {
      const { setValue } = useFormValidation()

      expect(() => setValue('nonexistent', 'value')).not.toThrow()
    })
  })

  describe('resetField', () => {
    it('should clear error and touched state', () => {
      const { registerField, validateField, resetField, fields } = useFormValidation()

      registerField('username', '', [validationRules.required()])
      
      validateField('username')
      expect(fields.value.username.error).not.toBeNull()
      expect(fields.value.username.touched).toBe(true)

      resetField('username')

      expect(fields.value.username.error).toBeNull()
      expect(fields.value.username.touched).toBe(false)
    })

    it('should handle non-existent field gracefully', () => {
      const { resetField } = useFormValidation()

      expect(() => resetField('nonexistent')).not.toThrow()
    })
  })

  describe('resetAll', () => {
    it('should reset all fields', () => {
      const { registerField, validateAll, resetAll, fields } = useFormValidation()

      registerField('field1', '', [validationRules.required()])
      registerField('field2', '', [validationRules.required()])
      
      validateAll()

      resetAll()

      expect(fields.value.field1.error).toBeNull()
      expect(fields.value.field1.touched).toBe(false)
      expect(fields.value.field2.error).toBeNull()
      expect(fields.value.field2.touched).toBe(false)
    })
  })

  describe('computed properties', () => {
    it('isValid should be true when no errors', () => {
      const { registerField, isValid } = useFormValidation()

      registerField('username', 'test')

      expect(isValid.value).toBe(true)
    })

    it('isValid should be false when errors exist', () => {
      const { registerField, validateField, isValid } = useFormValidation()

      registerField('username', '', [validationRules.required()])
      validateField('username')

      expect(isValid.value).toBe(false)
    })

    it('hasErrors should be false when no errors', () => {
      const { registerField, hasErrors } = useFormValidation()

      registerField('username', 'test')

      expect(hasErrors.value).toBe(false)
    })

    it('hasErrors should be true when errors exist', () => {
      const { registerField, validateField, hasErrors } = useFormValidation()

      registerField('username', '', [validationRules.required()])
      validateField('username')

      expect(hasErrors.value).toBe(true)
    })
  })
})

describe('Validation Rules', () => {
  describe('required', () => {
    it('should pass for non-empty string', () => {
      const rule = validationRules.required()
      expect(rule.validator('test')).toBe(true)
    })

    it('should fail for empty string', () => {
      const rule = validationRules.required()
      expect(rule.validator('')).toBe(false)
    })

    it('should fail for whitespace-only string', () => {
      const rule = validationRules.required()
      expect(rule.validator('   ')).toBe(false)
    })

    it('should pass for non-empty array', () => {
      const rule = validationRules.required()
      expect(rule.validator([1, 2])).toBe(true)
    })

    it('should fail for empty array', () => {
      const rule = validationRules.required()
      expect(rule.validator([])).toBe(false)
    })

    it('should fail for null or undefined', () => {
      const rule = validationRules.required()
      expect(rule.validator(null)).toBe(false)
      expect(rule.validator(undefined)).toBe(false)
    })

    it('should use custom message', () => {
      const rule = validationRules.required('Custom message')
      expect(rule.message).toBe('Custom message')
    })
  })

  describe('minLength', () => {
    it('should pass for string longer than minimum', () => {
      const rule = validationRules.minLength(5)
      expect(rule.validator('hello world')).toBe(true)
    })

    it('should pass for string equal to minimum', () => {
      const rule = validationRules.minLength(5)
      expect(rule.validator('hello')).toBe(true)
    })

    it('should fail for string shorter than minimum', () => {
      const rule = validationRules.minLength(5)
      expect(rule.validator('hi')).toBe(false)
    })

    it('should pass for non-string values', () => {
      const rule = validationRules.minLength(5)
      expect(rule.validator(123)).toBe(true)
      expect(rule.validator(null)).toBe(true)
    })
  })

  describe('maxLength', () => {
    it('should pass for string shorter than maximum', () => {
      const rule = validationRules.maxLength(10)
      expect(rule.validator('hello')).toBe(true)
    })

    it('should pass for string equal to maximum', () => {
      const rule = validationRules.maxLength(5)
      expect(rule.validator('hello')).toBe(true)
    })

    it('should fail for string longer than maximum', () => {
      const rule = validationRules.maxLength(5)
      expect(rule.validator('hello world')).toBe(false)
    })

    it('should pass for non-string values', () => {
      const rule = validationRules.maxLength(5)
      expect(rule.validator(123)).toBe(true)
    })
  })

  describe('email', () => {
    it('should pass for valid email', () => {
      const rule = validationRules.email()
      expect(rule.validator('test@example.com')).toBe(true)
      expect(rule.validator('user.name@domain.co.uk')).toBe(true)
    })

    it('should fail for invalid email', () => {
      const rule = validationRules.email()
      expect(rule.validator('invalid')).toBe(false)
      expect(rule.validator('test@')).toBe(false)
      expect(rule.validator('@example.com')).toBe(false)
      expect(rule.validator('test @example.com')).toBe(false)
    })

    it('should pass for non-string values', () => {
      const rule = validationRules.email()
      expect(rule.validator(123)).toBe(true)
    })
  })

  describe('numeric', () => {
    it('should pass for numbers', () => {
      const rule = validationRules.numeric()
      expect(rule.validator(123)).toBe(true)
      expect(rule.validator('456')).toBe(true)
      expect(rule.validator('3.14')).toBe(true)
    })

    it('should fail for non-numeric values', () => {
      const rule = validationRules.numeric()
      expect(rule.validator('abc')).toBe(false)
      expect(rule.validator('12abc')).toBe(false)
    })
  })

  describe('min', () => {
    it('should pass for values greater than minimum', () => {
      const rule = validationRules.min(5)
      expect(rule.validator(10)).toBe(true)
      expect(rule.validator('10')).toBe(true)
    })

    it('should pass for values equal to minimum', () => {
      const rule = validationRules.min(5)
      expect(rule.validator(5)).toBe(true)
    })

    it('should fail for values less than minimum', () => {
      const rule = validationRules.min(5)
      expect(rule.validator(3)).toBe(false)
    })
  })

  describe('max', () => {
    it('should pass for values less than maximum', () => {
      const rule = validationRules.max(10)
      expect(rule.validator(5)).toBe(true)
    })

    it('should pass for values equal to maximum', () => {
      const rule = validationRules.max(10)
      expect(rule.validator(10)).toBe(true)
    })

    it('should fail for values greater than maximum', () => {
      const rule = validationRules.max(10)
      expect(rule.validator(15)).toBe(false)
    })
  })

  describe('pattern', () => {
    it('should pass for matching pattern', () => {
      const rule = validationRules.pattern(/^[A-Z]+$/)
      expect(rule.validator('HELLO')).toBe(true)
    })

    it('should fail for non-matching pattern', () => {
      const rule = validationRules.pattern(/^[A-Z]+$/)
      expect(rule.validator('hello')).toBe(false)
    })

    it('should pass for non-string values', () => {
      const rule = validationRules.pattern(/^[A-Z]+$/)
      expect(rule.validator(123)).toBe(true)
    })
  })

  describe('custom', () => {
    it('should use custom validator function', () => {
      const rule = validationRules.custom(
        (value) => value === 'special',
        'Must be special'
      )
      
      expect(rule.validator('special')).toBe(true)
      expect(rule.validator('normal')).toBe(false)
      expect(rule.message).toBe('Must be special')
    })
  })

  describe('workerId', () => {
    it('should pass for valid worker IDs', () => {
      const rule = validationRules.workerId()
      expect(rule.validator('frontend-worker-1')).toBe(true)
      expect(rule.validator('worker_123')).toBe(true)
      expect(rule.validator('my.worker.01')).toBe(true)
    })

    it('should fail for too short worker ID', () => {
      const rule = validationRules.workerId()
      expect(rule.validator('ab')).toBe(false)
      expect(rule.validator('a')).toBe(false)
    })

    it('should fail for too long worker ID', () => {
      const rule = validationRules.workerId()
      const longId = 'a'.repeat(60)
      expect(rule.validator(longId)).toBe(false)
    })

    it('should fail for worker ID not starting with alphanumeric', () => {
      const rule = validationRules.workerId()
      expect(rule.validator('-worker')).toBe(false)
      expect(rule.validator('_worker')).toBe(false)
      expect(rule.validator('.worker')).toBe(false)
    })

    it('should fail for non-string values', () => {
      const rule = validationRules.workerId()
      expect(rule.validator(123)).toBe(false)
      expect(rule.validator(null)).toBe(false)
    })

    it('should sanitize and validate', () => {
      const rule = validationRules.workerId()
      // After sanitization, this becomes a valid worker ID
      expect(rule.validator('worker<test>123')).toBe(true)
    })
  })

  describe('safeContent', () => {
    it('should pass for safe content', () => {
      const rule = validationRules.safeContent()
      expect(rule.validator('Hello World')).toBe(true)
      expect(rule.validator('worker-123')).toBe(true)
    })

    it('should fail for script tags', () => {
      const rule = validationRules.safeContent()
      expect(rule.validator('<script>alert(1)</script>')).toBe(false)
    })

    it('should fail for javascript: protocol', () => {
      const rule = validationRules.safeContent()
      expect(rule.validator('javascript:alert(1)')).toBe(false)
    })

    it('should fail for event handlers', () => {
      const rule = validationRules.safeContent()
      expect(rule.validator('onclick="alert(1)"')).toBe(false)
    })

    it('should pass for non-string values', () => {
      const rule = validationRules.safeContent()
      expect(rule.validator(123)).toBe(true)
    })
  })
})
