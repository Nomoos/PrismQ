# Implementation Plan: Client-Database Integration

**Issue**: Client lacks IdeaInspiration results display and database integration  
**Priority**: 🔴 Critical  
**Estimated Effort**: 4-5 weeks  
**Status**: 📋 Planned

---

## Overview

This document outlines the implementation plan for integrating the IdeaInspiration database with the Client, enabling users to view, filter, sort, and analyze collected content ideas.

---

## Phase 1: Backend Database Integration (Week 1-2)

### 1.1 Database Connection Setup

**File**: `Client/Backend/src/core/idea_inspiration_service.py` (NEW)

**Tasks**:
- [ ] Import Model module's database layer
- [ ] Create database service class
- [ ] Handle database path configuration
- [ ] Add connection pooling (if needed)
- [ ] Error handling for missing database

**Code Structure**:
```python
# Client/Backend/src/core/idea_inspiration_service.py
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

# Import Model module
model_path = Path(__file__).resolve().parents[4] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration import IdeaInspiration
from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path

class IdeaInspirationService:
    """Service for querying IdeaInspiration database."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = get_central_database_path()
        self.db = IdeaInspirationDatabase(db_path)
    
    def get_all(self, limit: int = 50, offset: int = 0) -> List[IdeaInspiration]:
        """Get all inspirations with pagination."""
        pass
    
    def filter(self, **filters) -> List[IdeaInspiration]:
        """Filter inspirations by various criteria."""
        pass
    
    def get_by_id(self, id: int) -> Optional[IdeaInspiration]:
        """Get inspiration by ID."""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        pass
```

**Dependencies**:
- Model module (already available)
- No new Python packages needed

### 1.2 Pydantic Models

**File**: `Client/Backend/src/models/idea_inspiration.py` (NEW)

**Tasks**:
- [ ] Create Pydantic models for API responses
- [ ] Match IdeaInspiration structure
- [ ] Add validation
- [ ] Add serialization helpers

**Models**:
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class IdeaInspirationResponse(BaseModel):
    """Response model for IdeaInspiration."""
    id: int
    title: str
    description: str
    content: str
    keywords: List[str]
    source_type: str
    source_id: Optional[str]
    source_url: Optional[str]
    source_created_by: Optional[str]
    source_created_at: Optional[str]
    score: Optional[int]
    category: Optional[str]
    subcategory_relevance: Dict[str, int] = Field(default_factory=dict)
    contextual_category_scores: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, str] = Field(default_factory=dict)
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class IdeaInspirationListResponse(BaseModel):
    """Paginated list response."""
    items: List[IdeaInspirationResponse]
    total: int
    page: int
    page_size: int
    pages: int

class IdeaInspirationStatsResponse(BaseModel):
    """Statistics response."""
    total_count: int
    avg_score: Optional[float]
    categories: Dict[str, int]
    sources: Dict[str, int]
    recent_count: int  # Last 7 days
```

### 1.3 API Endpoints

**File**: `Client/Backend/src/api/inspirations.py` (NEW)

**Tasks**:
- [ ] Create router for inspirations endpoints
- [ ] Implement GET /api/inspirations (list with pagination)
- [ ] Implement GET /api/inspirations/{id} (get by ID)
- [ ] Implement GET /api/inspirations/search (advanced search)
- [ ] Implement GET /api/inspirations/stats (statistics)
- [ ] Add query parameter validation
- [ ] Add error handling
- [ ] Add documentation/OpenAPI schemas

**Endpoints**:
```python
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from ..core.idea_inspiration_service import IdeaInspirationService
from ..models.idea_inspiration import (
    IdeaInspirationResponse,
    IdeaInspirationListResponse,
    IdeaInspirationStatsResponse
)

router = APIRouter(prefix="/api/inspirations", tags=["inspirations"])
service = IdeaInspirationService()

@router.get("/", response_model=IdeaInspirationListResponse)
async def list_inspirations(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(score|created_at|title)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    score_min: Optional[int] = Query(None, ge=0, le=100),
    score_max: Optional[int] = Query(None, ge=0, le=100),
    category: Optional[str] = None,
    source_type: Optional[str] = None,
):
    """List inspirations with filtering and pagination."""
    pass

@router.get("/search", response_model=IdeaInspirationListResponse)
async def search_inspirations(
    q: Optional[str] = Query(None),
    keywords: Optional[List[str]] = Query(None),
    days_back: Optional[int] = Query(None, ge=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """Advanced search with keywords and date filtering."""
    pass

@router.get("/stats", response_model=IdeaInspirationStatsResponse)
async def get_stats():
    """Get database statistics."""
    pass

@router.get("/{id}", response_model=IdeaInspirationResponse)
async def get_inspiration(id: int):
    """Get inspiration by ID."""
    pass
```

### 1.4 Router Registration

**File**: `Client/Backend/src/main.py` (UPDATE)

**Tasks**:
- [ ] Import inspirations router
- [ ] Register router with app
- [ ] Update CORS if needed
- [ ] Update OpenAPI metadata

**Code**:
```python
from .api import inspirations

# Register routers
app.include_router(modules.router)
app.include_router(runs.router)
app.include_router(system.router)
app.include_router(inspirations.router)  # NEW
```

### 1.5 Testing

**File**: `Client/Backend/tests/test_api/test_inspirations.py` (NEW)

**Tasks**:
- [ ] Test list endpoint with pagination
- [ ] Test filtering (score, category, date)
- [ ] Test sorting (asc/desc, different fields)
- [ ] Test search endpoint
- [ ] Test stats endpoint
- [ ] Test get by ID
- [ ] Test error cases (invalid ID, etc.)
- [ ] Test with empty database
- [ ] Test with populated database

---

## Phase 2: Frontend Display Components (Week 3-4)

### 2.1 TypeScript Types

**File**: `Client/Frontend/src/types/inspiration.ts` (NEW)

**Tasks**:
- [ ] Define IdeaInspiration interface
- [ ] Define filter/search interfaces
- [ ] Define stats interface
- [ ] Export types

**Types**:
```typescript
export interface IdeaInspiration {
  id: number
  title: string
  description: string
  content: string
  keywords: string[]
  source_type: string
  source_id?: string
  source_url?: string
  source_created_by?: string
  source_created_at?: string
  score?: number
  category?: string
  subcategory_relevance: Record<string, number>
  contextual_category_scores: Record<string, number>
  metadata: Record<string, string>
  created_at?: string
  updated_at?: string
}

export interface IdeaInspirationFilters {
  page?: number
  page_size?: number
  sort_by?: 'score' | 'created_at' | 'title'
  sort_order?: 'asc' | 'desc'
  score_min?: number
  score_max?: number
  category?: string
  source_type?: string
  keywords?: string[]
  days_back?: number
}

export interface IdeaInspirationStats {
  total_count: number
  avg_score?: number
  categories: Record<string, number>
  sources: Record<string, number>
  recent_count: number
}
```

### 2.2 API Service

**File**: `Client/Frontend/src/services/inspirations.ts` (NEW)

**Tasks**:
- [ ] Create service for API calls
- [ ] Implement list method
- [ ] Implement search method
- [ ] Implement getById method
- [ ] Implement getStats method
- [ ] Add error handling
- [ ] Add request cancellation

**Service**:
```typescript
import api from './api'
import type { IdeaInspiration, IdeaInspirationFilters, IdeaInspirationStats } from '@/types/inspiration'

export const inspirationService = {
  async list(filters: IdeaInspirationFilters = {}) {
    const response = await api.get('/api/inspirations', { params: filters })
    return response.data
  },

  async search(query: string, filters: IdeaInspirationFilters = {}) {
    const response = await api.get('/api/inspirations/search', {
      params: { q: query, ...filters }
    })
    return response.data
  },

  async getById(id: number) {
    const response = await api.get(`/api/inspirations/${id}`)
    return response.data
  },

  async getStats() {
    const response = await api.get('/api/inspirations/stats')
    return response.data
  }
}
```

### 2.3 Main View Component

**File**: `Client/Frontend/src/views/Inspirations.vue` (NEW)

**Tasks**:
- [ ] Create main inspirations view
- [ ] Add search/filter UI
- [ ] Add sorting controls
- [ ] Add pagination
- [ ] Display loading state
- [ ] Display error state
- [ ] Display empty state
- [ ] Integrate with API service

**Component Structure**:
```vue
<template>
  <div class="inspirations-view">
    <header class="header">
      <h1>Content Inspirations</h1>
      <div class="stats-bar">
        <StatCard v-if="stats" :icon="'database'" :label="'Total'" :value="stats.total_count" />
        <StatCard v-if="stats && stats.avg_score" :icon="'star'" :label="'Avg Score'" :value="stats.avg_score.toFixed(1)" />
        <StatCard v-if="stats" :icon="'clock'" :label="'Recent'" :value="stats.recent_count" />
      </div>
    </header>

    <!-- Filters and Search -->
    <IdeaInspirationFilters
      v-model:filters="filters"
      @update:filters="loadInspirations"
      @reset="resetFilters"
    />

    <!-- Results Grid -->
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="inspirations.length === 0" class="empty">No inspirations found</div>
    <div v-else class="grid">
      <IdeaInspirationCard
        v-for="inspiration in inspirations"
        :key="inspiration.id"
        :inspiration="inspiration"
        @click="viewDetails(inspiration.id)"
      />
    </div>

    <!-- Pagination -->
    <PaginationControls
      v-if="totalPages > 1"
      v-model:page="currentPage"
      :total-pages="totalPages"
      @update:page="loadInspirations"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { inspirationService } from '@/services/inspirations'
import IdeaInspirationCard from '@/components/IdeaInspirationCard.vue'
import IdeaInspirationFilters from '@/components/IdeaInspirationFilters.vue'
import StatCard from '@/components/StatCard.vue'
import PaginationControls from '@/components/PaginationControls.vue'
import type { IdeaInspiration, IdeaInspirationFilters as Filters } from '@/types/inspiration'

const router = useRouter()
const inspirations = ref<IdeaInspiration[]>([])
const stats = ref(null)
const loading = ref(false)
const error = ref<string | null>(null)
const filters = ref<Filters>({
  page: 1,
  page_size: 50,
  sort_by: 'created_at',
  sort_order: 'desc'
})
const totalCount = ref(0)

const currentPage = computed({
  get: () => filters.value.page || 1,
  set: (value) => { filters.value.page = value }
})

const totalPages = computed(() => {
  return Math.ceil(totalCount.value / (filters.value.page_size || 50))
})

async function loadInspirations() {
  loading.value = true
  error.value = null
  try {
    const result = await inspirationService.list(filters.value)
    inspirations.value = result.items
    totalCount.value = result.total
  } catch (err: any) {
    error.value = err.message || 'Failed to load inspirations'
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    stats.value = await inspirationService.getStats()
  } catch (err) {
    console.error('Failed to load stats:', err)
  }
}

function resetFilters() {
  filters.value = {
    page: 1,
    page_size: 50,
    sort_by: 'created_at',
    sort_order: 'desc'
  }
  loadInspirations()
}

function viewDetails(id: number) {
  router.push(`/inspirations/${id}`)
}

onMounted(() => {
  loadInspirations()
  loadStats()
})
</script>
```

### 2.4 Card Component

**File**: `Client/Frontend/src/components/IdeaInspirationCard.vue` (NEW)

**Tasks**:
- [ ] Create card component for grid display
- [ ] Display title, description, score
- [ ] Show category badge
- [ ] Show source type icon
- [ ] Show keywords
- [ ] Add hover effects
- [ ] Make clickable

### 2.5 Filters Component

**File**: `Client/Frontend/src/components/IdeaInspirationFilters.vue` (NEW)

**Tasks**:
- [ ] Create filter/search UI
- [ ] Search input
- [ ] Score range sliders
- [ ] Category dropdown
- [ ] Source type dropdown
- [ ] Date range picker
- [ ] Sort by dropdown
- [ ] Sort order toggle
- [ ] Reset button
- [ ] Emit filter changes

### 2.6 Details View

**File**: `Client/Frontend/src/views/InspirationDetails.vue` (NEW)

**Tasks**:
- [ ] Create detailed view for single inspiration
- [ ] Display all fields
- [ ] Show metadata table
- [ ] Show subcategory relevance chart
- [ ] Show contextual scores
- [ ] Back button
- [ ] Edit button (future)
- [ ] Delete button (future)

### 2.7 Router Updates

**File**: `Client/Frontend/src/router/index.ts` (UPDATE)

**Tasks**:
- [ ] Add /inspirations route
- [ ] Add /inspirations/:id route
- [ ] Update navigation

**Routes**:
```typescript
{
  path: '/inspirations',
  name: 'Inspirations',
  component: () => import('@/views/Inspirations.vue')
},
{
  path: '/inspirations/:id',
  name: 'InspirationDetails',
  component: () => import('@/views/InspirationDetails.vue')
}
```

### 2.8 Navigation Updates

**File**: `Client/Frontend/src/App.vue` or Navigation Component (UPDATE)

**Tasks**:
- [ ] Add "Inspirations" link to main navigation
- [ ] Add icon
- [ ] Make active when on inspirations routes

---

## Phase 3: Module Registration (Week 5)

### 3.1 Update Module Configuration

**File**: `Client/Backend/configs/modules.json` (UPDATE)

**Tasks**:
- [ ] Add Classification module
- [ ] Add Scoring module
- [ ] Add all Sources modules
- [ ] Define parameters for each
- [ ] Add proper descriptions
- [ ] Add categories
- [ ] Test script paths

**Example Additions**:
```json
{
  "modules": [
    {
      "id": "classification",
      "name": "Content Classification",
      "description": "Classify content into categories and detect stories",
      "category": "Processing",
      "version": "2.1.0",
      "script_path": "../../Classification/src/main.py",
      "parameters": [
        {
          "name": "input_db",
          "type": "text",
          "default": "../../Model/db.s3db",
          "description": "Path to IdeaInspiration database",
          "required": true
        },
        {
          "name": "classify_mode",
          "type": "select",
          "options": ["category", "story", "both"],
          "default": "both",
          "description": "Classification mode",
          "required": true
        }
      ],
      "tags": ["classification", "processing"],
      "status": "active",
      "enabled": true
    },
    {
      "id": "scoring",
      "name": "Content Scoring",
      "description": "Score content quality and engagement",
      "category": "Processing",
      "version": "1.0.0",
      "script_path": "../../Scoring/src/main.py",
      "parameters": [
        {
          "name": "input_db",
          "type": "text",
          "default": "../../Model/db.s3db",
          "description": "Path to IdeaInspiration database",
          "required": true
        },
        {
          "name": "score_mode",
          "type": "select",
          "options": ["engagement", "text_quality", "universal"],
          "default": "universal",
          "description": "Scoring mode",
          "required": true
        }
      ],
      "tags": ["scoring", "processing"],
      "status": "active",
      "enabled": true
    }
  ]
}
```

### 3.2 Module CLI Adapters

**Tasks**:
- [ ] Ensure Classification has CLI entry point
- [ ] Ensure Scoring has CLI entry point
- [ ] Ensure all Sources have CLI entry points
- [ ] Test module execution from Client
- [ ] Verify output reporting

---

## Phase 4: Testing & Documentation (Week 5)

### 4.1 End-to-End Testing

**Tasks**:
- [ ] Test complete workflow:
  - Launch Source module
  - Verify data saved to database
  - View data in Inspirations view
  - Filter and sort
  - View details
- [ ] Test with empty database
- [ ] Test with large dataset
- [ ] Test pagination
- [ ] Test error scenarios

### 4.2 Documentation Updates

**Files to Update**:
- [ ] `Client/README.md` - Add Inspirations feature
- [ ] `Client/docs/USER_GUIDE.md` - Usage instructions
- [ ] `Client/docs/API.md` - New endpoints
- [ ] `_meta/issues/wip/CURRENT_FUNCTIONALITY_EVALUATION.md` - Mark as completed

**New Documentation**:
- [ ] `Client/docs/INSPIRATIONS_GUIDE.md` - Complete guide
- [ ] `Client/docs/DATABASE_INTEGRATION.md` - Technical details

### 4.3 Screenshots

**Tasks**:
- [ ] Capture Inspirations list view
- [ ] Capture filters in action
- [ ] Capture details view
- [ ] Capture statistics
- [ ] Update README with screenshots

---

## Success Criteria

### Phase 1 Complete When:
- ✅ Backend API endpoints working
- ✅ Database queries functional
- ✅ Tests passing (>90% coverage)

### Phase 2 Complete When:
- ✅ Frontend displays inspirations
- ✅ Filtering works (score, category, date)
- ✅ Sorting works (score, date, title)
- ✅ Pagination works
- ✅ Details view works

### Phase 3 Complete When:
- ✅ All modules registered
- ✅ Can launch Classification
- ✅ Can launch Scoring
- ✅ Can launch all Sources

### Phase 4 Complete When:
- ✅ End-to-end tests passing
- ✅ Documentation updated
- ✅ Screenshots captured
- ✅ User guide complete

---

## Dependencies

### Python Packages (Backend)
- No new packages needed (Model module already has everything)

### NPM Packages (Frontend)
- May need charting library (e.g., Chart.js or Recharts) for statistics visualization
- Consider date picker library (e.g., VueDatePicker)

---

## Risks & Mitigation

### Risk 1: Database Location
**Issue**: Different users may have database in different locations  
**Mitigation**: Use Model's `get_central_database_path()` function

### Risk 2: Large Datasets
**Issue**: Performance with 10,000+ inspirations  
**Mitigation**: Implement pagination, add database indexes if needed

### Risk 3: Concurrent Access
**Issue**: Client and modules accessing database simultaneously  
**Mitigation**: SQLite handles this, but test thoroughly

---

## Timeline

**Week 1**: Backend service & models  
**Week 2**: Backend API endpoints & tests  
**Week 3**: Frontend types & services  
**Week 4**: Frontend components & views  
**Week 5**: Module registration & testing

**Total**: 5 weeks

---

## Next Steps

1. Review this plan
2. Get approval
3. Create GitHub issues for each phase
4. Start implementation
5. Report progress weekly

---

**Plan Status**: ✅ Ready for Implementation  
**Created**: 2025-11-01  
**Owner**: Development Team
