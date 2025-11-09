# Frontend/TaskManager - Contributing Guide

**Version**: 1.0  
**Last Updated**: 2025-11-09  
**Audience**: Contributors

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Code Standards](#code-standards)
4. [Testing Requirements](#testing-requirements)
5. [Pull Request Process](#pull-request-process)
6. [Issue Reporting](#issue-reporting)

---

## Getting Started

### Prerequisites

- Node.js 18+
- npm 9+
- Git
- Code editor (VS Code recommended)

### Setup

1. **Fork the repository**

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/PrismQ.Client.git
   cd PrismQ.Client/Frontend/TaskManager
   ```

3. **Install dependencies**:
   ```bash
   npm install
   ```

4. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. **Start development server**:
   ```bash
   npm run dev
   ```

---

## Development Workflow

### Branch Naming

- **Features**: `feature/feature-name`
- **Bug fixes**: `fix/bug-description`
- **Documentation**: `docs/what-changed`
- **Refactoring**: `refactor/what-changed`

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests
- `chore`: Updating build tasks, package manager configs, etc.

**Examples**:
```
feat(tasks): add task filtering by priority

fix(api): handle network timeout errors

docs(readme): update deployment instructions

refactor(stores): simplify task store logic
```

---

## Code Standards

### TypeScript

- **Use strict mode**: Enabled in tsconfig.json
- **Type everything**: No `any` types
- **Use interfaces**: For object shapes

```typescript
// ✅ Good
interface Task {
  id: number
  status: TaskStatus
}

// ❌ Bad
const task: any = { id: 1, status: 'pending' }
```

### Vue Components

- **Use Composition API**: With `<script setup>`
- **Type props and emits**: Use TypeScript interfaces
- **Single responsibility**: One concern per component

```vue
<template>
  <div class="task-card">
    <!-- Template -->
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  task: Task
}

const props = defineProps<Props>()

const statusClass = computed(() => {
  return `status-${props.task.status}`
})
</script>

<style scoped>
/* Prefer Tailwind, use scoped styles sparingly */
</style>
```

### Styling

- **Mobile-first**: Design for mobile, enhance for desktop
- **Use Tailwind utilities**: Avoid custom CSS when possible
- **Consistent spacing**: Use Tailwind spacing scale (4px base)

```vue
<!-- ✅ Good - Mobile first -->
<div class="p-4 md:p-6 lg:p-8">

<!-- ❌ Bad - Desktop first -->
<div class="p-8 md:p-6 sm:p-4">
```

### File Organization

```
src/
├── components/     # Reusable components
│   ├── base/       # Base UI components
│   └── tasks/      # Domain-specific components
├── views/          # Page components
├── stores/         # Pinia stores
├── services/       # API services
├── types/          # TypeScript types
├── composables/    # Composition functions
└── assets/         # Static assets
```

---

## Testing Requirements

### Unit Tests

Required for:
- All stores
- All services
- Complex composables
- Utility functions

```typescript
// tests/unit/taskService.spec.ts
import { describe, it, expect, vi } from 'vitest'
import { taskService } from '@/services/taskService'

describe('taskService', () => {
  it('fetches tasks successfully', async () => {
    const tasks = await taskService.list()
    expect(tasks).toBeDefined()
  })
})
```

### Component Tests

Required for:
- All views
- Complex components
- Components with business logic

```typescript
// tests/unit/TaskCard.spec.ts
import { mount } from '@vue/test-utils'
import TaskCard from '@/components/tasks/TaskCard.vue'

describe('TaskCard', () => {
  it('renders task information', () => {
    const wrapper = mount(TaskCard, {
      props: { task: mockTask }
    })
    expect(wrapper.text()).toContain('pending')
  })
})
```

### E2E Tests

Required for:
- Critical user flows
- Task claiming flow
- Task completion flow

```typescript
// tests/e2e/task-flow.spec.ts
import { test, expect } from '@playwright/test'

test('user can claim and complete task', async ({ page }) => {
  await page.goto('/')
  await page.click('.task-card:first-child')
  await page.click('button:has-text("Claim Task")')
  await expect(page.locator('.status-badge')).toHaveText('Claimed')
})
```

### Running Tests

```bash
# Unit tests
npm test

# Unit tests with coverage
npm run test:coverage

# E2E tests
npm run test:e2e

# All tests
npm run test:all
```

**Coverage Requirements**:
- Minimum 80% line coverage
- Minimum 70% branch coverage

---

## Pull Request Process

### Before Submitting

1. **Run tests**: `npm test`
2. **Run linter**: `npm run lint`
3. **Type check**: `npm run type-check`
4. **Build**: `npm run build`
5. **Update documentation**: If needed

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] E2E tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
- [ ] Dependent changes merged
```

### Review Process

1. **Automated checks**: All must pass
   - Tests
   - Linter
   - Type checking
   - Build

2. **Code review**: Minimum 1 approval required

3. **Testing**: Reviewer tests changes manually

4. **Merge**: Squash and merge to main

---

## Issue Reporting

### Bug Reports

Use this template:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment**
- Browser: [e.g. Chrome 120]
- Device: [e.g. iPhone 12]
- OS: [e.g. iOS 15]

**Additional context**
Any other context about the problem.
```

### Feature Requests

Use this template:

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution**
What you want to happen.

**Describe alternatives**
Alternative solutions you've considered.

**Additional context**
Any other context, mockups, or screenshots.
```

---

## Code Review Guidelines

### As a Reviewer

- **Be constructive**: Suggest improvements, don't just criticize
- **Ask questions**: Understand the why
- **Test thoroughly**: Don't just read code
- **Check documentation**: Ensure docs are updated
- **Approve only if**: All checks pass and code is production-ready

### As an Author

- **Respond promptly**: Address feedback quickly
- **Explain decisions**: Why you chose this approach
- **Accept feedback**: Be open to suggestions
- **Keep PRs small**: Easier to review
- **Update documentation**: Don't forget the docs

---

## Community Guidelines

### Be Respectful

- Respect all contributors
- Welcome newcomers
- Be patient with questions
- Give constructive feedback

### Collaborate

- Discuss big changes first
- Help others
- Share knowledge
- Celebrate successes

---

## Resources

### Documentation

- [Vue 3 Docs](https://vuejs.org/)
- [TypeScript Docs](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Pinia Docs](https://pinia.vuejs.org/)
- [Vitest Docs](https://vitest.dev/)
- [Playwright Docs](https://playwright.dev/)

### Project Docs

- [User Guide](USER_GUIDE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [API Integration](API_INTEGRATION.md)
- [Troubleshooting](TROUBLESHOOTING.md)

---

## Questions?

If you have questions:

1. Check existing documentation
2. Search closed issues
3. Ask in discussions
4. Open a new issue

---

**Thank you for contributing!** 🎉

**Document Owner**: Worker06 (Documentation Specialist)  
**Last Updated**: 2025-11-09  
**Version**: 1.0  
**Status**: ✅ Complete
