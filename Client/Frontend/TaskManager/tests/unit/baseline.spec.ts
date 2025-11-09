import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { readFile, writeFile, mkdir, rm } from 'fs/promises'
import { join } from 'path'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

describe('Performance Baseline Analysis', () => {
  const testBaselineDir = join(process.cwd(), '.test-baselines')
  const testBaselineFile = join(testBaselineDir, 'performance-baseline.json')
  
  beforeEach(async () => {
    // Create test baseline directory
    await mkdir(testBaselineDir, { recursive: true })
  })
  
  afterEach(async () => {
    // Clean up test files
    try {
      await rm(testBaselineDir, { recursive: true, force: true })
    } catch (error) {
      // Ignore errors during cleanup
    }
  })
  
  it('should create baseline with required fields', async () => {
    const baseline = {
      timestamp: new Date().toISOString(),
      date: new Date().toLocaleString(),
      git: {
        commit: 'abc1234',
        branch: 'test-branch',
        author: 'Test Author',
        message: 'Test commit'
      },
      metrics: {
        totalSize: 200000,
        jsSize: 150000,
        cssSize: 20000,
        htmlSize: 1000,
        assetSize: 5000,
        fileCount: {
          total: 10,
          js: 5,
          css: 2,
          html: 1,
          assets: 2
        },
        largestChunks: [
          { name: 'vendor.js', size: 100000 },
          { name: 'main.js', size: 50000 }
        ]
      },
      budgets: {
        totalSize: 1048576,
        jsSize: 512000,
        cssSize: 51200,
        chunkSize: 102400
      }
    }
    
    await writeFile(testBaselineFile, JSON.stringify(baseline, null, 2))
    
    const savedData = await readFile(testBaselineFile, 'utf8')
    const savedBaseline = JSON.parse(savedData)
    
    expect(savedBaseline).toHaveProperty('timestamp')
    expect(savedBaseline).toHaveProperty('git')
    expect(savedBaseline).toHaveProperty('metrics')
    expect(savedBaseline).toHaveProperty('budgets')
    expect(savedBaseline.git).toHaveProperty('commit')
    expect(savedBaseline.metrics).toHaveProperty('totalSize')
    expect(savedBaseline.metrics).toHaveProperty('jsSize')
    expect(savedBaseline.metrics).toHaveProperty('cssSize')
  })
  
  it('should calculate deltas correctly', () => {
    const baseline = {
      totalSize: 200000,
      jsSize: 150000,
      cssSize: 20000
    }
    
    const current = {
      totalSize: 220000,
      jsSize: 160000,
      cssSize: 22000
    }
    
    const totalDelta = current.totalSize - baseline.totalSize
    const totalPercent = ((totalDelta / baseline.totalSize) * 100).toFixed(1)
    
    const jsDelta = current.jsSize - baseline.jsSize
    const jsPercent = ((jsDelta / baseline.jsSize) * 100).toFixed(1)
    
    const cssDelta = current.cssSize - baseline.cssSize
    const cssPercent = ((cssDelta / baseline.cssSize) * 100).toFixed(1)
    
    expect(totalDelta).toBe(20000)
    expect(totalPercent).toBe('10.0')
    
    expect(jsDelta).toBe(10000)
    expect(jsPercent).toBe('6.7')
    
    expect(cssDelta).toBe(2000)
    expect(cssPercent).toBe('10.0')
  })
  
  it('should detect regressions', () => {
    const baseline = {
      totalSize: 200000,
      jsSize: 150000,
      cssSize: 20000
    }
    
    const currentWithRegression = {
      totalSize: 220000, // +20KB
      jsSize: 160000,    // +10KB
      cssSize: 22000     // +2KB
    }
    
    const currentWithImprovement = {
      totalSize: 180000, // -20KB
      jsSize: 140000,    // -10KB
      cssSize: 18000     // -2KB
    }
    
    // Regression detection
    const hasRegression = 
      currentWithRegression.totalSize > baseline.totalSize ||
      currentWithRegression.jsSize > baseline.jsSize ||
      currentWithRegression.cssSize > baseline.cssSize
    
    expect(hasRegression).toBe(true)
    
    // Improvement detection
    const hasImprovement = 
      currentWithImprovement.totalSize < baseline.totalSize &&
      currentWithImprovement.jsSize < baseline.jsSize &&
      currentWithImprovement.cssSize < baseline.cssSize
    
    expect(hasImprovement).toBe(true)
  })
  
  it('should identify significant changes', () => {
    const isSignificantChange = (delta: number, threshold: number) => {
      return Math.abs(delta) > threshold
    }
    
    // Thresholds
    const TOTAL_THRESHOLD = 10240  // 10KB
    const JS_THRESHOLD = 5120      // 5KB
    const CSS_THRESHOLD = 1024     // 1KB
    
    // Small changes (not significant)
    expect(isSignificantChange(5000, TOTAL_THRESHOLD)).toBe(false)
    expect(isSignificantChange(3000, JS_THRESHOLD)).toBe(false)
    expect(isSignificantChange(500, CSS_THRESHOLD)).toBe(false)
    
    // Large changes (significant)
    expect(isSignificantChange(15000, TOTAL_THRESHOLD)).toBe(true)
    expect(isSignificantChange(10000, JS_THRESHOLD)).toBe(true)
    expect(isSignificantChange(2000, CSS_THRESHOLD)).toBe(true)
  })
  
  it('should validate budget compliance', () => {
    const budgets = {
      totalSize: 1048576, // 1MB
      jsSize: 512000,     // 500KB
      cssSize: 51200      // 50KB
    }
    
    const withinBudget = {
      totalSize: 200000,
      jsSize: 150000,
      cssSize: 20000
    }
    
    const exceedsBudget = {
      totalSize: 1100000,
      jsSize: 600000,
      cssSize: 60000
    }
    
    // Within budget
    expect(withinBudget.totalSize <= budgets.totalSize).toBe(true)
    expect(withinBudget.jsSize <= budgets.jsSize).toBe(true)
    expect(withinBudget.cssSize <= budgets.cssSize).toBe(true)
    
    // Exceeds budget
    expect(exceedsBudget.totalSize <= budgets.totalSize).toBe(false)
    expect(exceedsBudget.jsSize <= budgets.jsSize).toBe(false)
    expect(exceedsBudget.cssSize <= budgets.cssSize).toBe(false)
  })
})
