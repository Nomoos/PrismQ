# Input Validation Testing Scenarios

This document provides test scenarios to verify the input validation and XSS protection implementation.

## Worker ID Validation in Settings

### Test Scenario 1: Valid Worker IDs
These inputs should be accepted and save successfully:

1. **Input:** `frontend-worker-1`
   - **Expected:** ✅ Saved successfully
   - **Reason:** Valid format with alphanumeric, hyphen

2. **Input:** `worker_123`
   - **Expected:** ✅ Saved successfully
   - **Reason:** Valid format with alphanumeric, underscore

3. **Input:** `my.worker.01`
   - **Expected:** ✅ Saved successfully
   - **Reason:** Valid format with alphanumeric, dots

4. **Input:** `WORKER-ABC-123`
   - **Expected:** ✅ Saved successfully
   - **Reason:** Valid format with uppercase letters

### Test Scenario 2: Invalid Worker IDs - Too Short
These inputs should show validation error:

1. **Input:** `ab`
   - **Expected:** ❌ Error: "Worker ID must be at least 3 characters"
   - **UI:** Red border on input field

2. **Input:** `w1`
   - **Expected:** ❌ Error: "Worker ID must be at least 3 characters"
   - **UI:** Red border on input field

### Test Scenario 3: Invalid Worker IDs - Too Long
These inputs should show validation error:

1. **Input:** (60 character string)
   - **Expected:** ❌ Error: "Worker ID must be at most 50 characters"
   - **Action:** Truncates to 50 characters
   - **UI:** Red border on input field

### Test Scenario 4: Invalid Worker IDs - Wrong Start Character
These inputs should show validation error:

1. **Input:** `-worker-123`
   - **Expected:** ❌ Error: "Worker ID must start with a letter or number"
   - **UI:** Red border on input field

2. **Input:** `_worker`
   - **Expected:** ❌ Error: "Worker ID must start with a letter or number"
   - **UI:** Red border on input field

3. **Input:** `.worker`
   - **Expected:** ❌ Error: "Worker ID must start with a letter or number"
   - **UI:** Red border on input field

### Test Scenario 5: XSS Attack Prevention
These inputs should be sanitized and show appropriate errors:

1. **Input:** `<script>alert('xss')</script>`
   - **Expected:** Sanitized to: `scriptalertxssscript`
   - **Saved as:** `scriptalertxssscript` (sanitized)
   - **UI:** Accepts sanitized version

2. **Input:** `worker<test>123`
   - **Expected:** Sanitized to: `workertest123`
   - **Saved as:** `workertest123` (sanitized)
   - **UI:** ✅ Saved successfully after sanitization

3. **Input:** `worker" onclick="alert(1)"`
   - **Expected:** Sanitized to: `workeronclickalert1`
   - **Saved as:** `workeronclickalert1` (sanitized)
   - **UI:** ✅ Saved successfully after sanitization

4. **Input:** `javascript:alert(1)`
   - **Expected:** ❌ Error: "Content contains potentially unsafe characters"
   - **UI:** Red border on input field

### Test Scenario 6: Empty and Whitespace
These inputs should show validation error:

1. **Input:** (empty string)
   - **Expected:** ❌ Error: "Worker ID is required"
   - **UI:** Red border on input field

2. **Input:** `   ` (only spaces)
   - **Expected:** ❌ Error: "Worker ID is required"
   - **UI:** Red border on input field

3. **Input:** `  worker-123  ` (with leading/trailing spaces)
   - **Expected:** ✅ Trimmed and saved as `worker-123`
   - **UI:** Input value updated to trimmed version

### Test Scenario 7: Special Characters
These inputs should be sanitized:

1. **Input:** `worker@#$%123`
   - **Expected:** Sanitized to: `worker123`
   - **UI:** ✅ Saved successfully after sanitization

2. **Input:** `worker 123` (with space)
   - **Expected:** Sanitized to: `worker123`
   - **UI:** ✅ Saved successfully after sanitization

3. **Input:** `worker!@#123`
   - **Expected:** Sanitized to: `worker123`
   - **UI:** ✅ Saved successfully after sanitization

## Visual Feedback

### Normal State
- Input border: Gray (`border-gray-300`)
- Help text: "This ID will be used when claiming and completing tasks"
- No error message visible

### Error State
- Input border: Red (`border-red-500`)
- Error message: Displayed in red text below input
- Help text: Hidden (replaced by error message)

### Success State (after save)
- Green success message: "Worker ID saved successfully!"
- Message auto-dismisses after 3 seconds
- Input value updated to sanitized version if changed

## Testing Instructions

### Manual Testing
1. Open the application in development mode: `npm run dev`
2. Navigate to Settings page
3. Try each test scenario listed above
4. Verify the expected behavior and UI feedback

### Automated Testing
Run the test suite to verify all sanitization and validation:

```bash
# Run all tests
npm run test

# Run only sanitization tests
npm run test tests/unit/sanitize.spec.ts

# Run only validation tests
npm run test tests/unit/useFormValidation.spec.ts
```

### Expected Test Results
- ✅ All 293 tests should pass
- ✅ 40 sanitization tests
- ✅ 63 validation tests (including 11 new XSS protection tests)

## Security Verification

### XSS Pattern Detection
The `isContentSafe()` function detects these dangerous patterns:
- ✅ `<script>` tags (case-insensitive)
- ✅ `javascript:` protocol (case-insensitive)
- ✅ Event handlers: `onclick=`, `onload=`, `onerror=`, etc.
- ✅ `<iframe>` tags
- ✅ `<object>` and `<embed>` tags
- ✅ `eval(` function calls
- ✅ CSS `expression(` calls

### HTML Entity Escaping
The `sanitizeHtml()` function escapes:
- ✅ `&` → `&amp;`
- ✅ `<` → `&lt;`
- ✅ `>` → `&gt;`
- ✅ `"` → `&quot;`
- ✅ `'` → `&#x27;`
- ✅ `/` → `&#x2F;`

## Integration Points

### Where Validation is Applied
1. **Settings View** (`src/views/Settings.vue`):
   - Worker ID input field
   - Real-time validation on blur
   - Pre-save validation and sanitization

2. **Form Validation Composable** (`src/composables/useFormValidation.ts`):
   - Reusable validation rules
   - Can be applied to any form field

3. **Sanitization Utilities** (`src/utils/sanitize.ts`):
   - Standalone functions
   - Can be imported anywhere
   - Used for both validation and data processing

## Future Enhancements

Potential areas for extending validation:
- [ ] Add validation to other form fields (if added in future)
- [ ] Implement Content Security Policy (CSP) headers
- [ ] Add rate limiting for input validation
- [ ] Implement input history/autocomplete with sanitization
- [ ] Add validation for API responses (if user-generated content is returned)

## References

See `docs/SECURITY.md` for complete security documentation.
