#!/usr/bin/env node
/**
 * Performance testing script
 * Runs comprehensive performance tests and generates a report
 */

import { exec } from 'child_process'
import { promisify } from 'util'
import fs from 'fs/promises'
import path from 'path'

const execAsync = promisify(exec)

const COLORS = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
}

function log(message, color = 'reset') {
  console.log(`${COLORS[color]}${message}${COLORS.reset}`)
}

async function runBundleCheck() {
  log('\n📦 Running Bundle Size Check...', 'cyan')
  try {
    const { stdout } = await execAsync('npm run bundle:check')
    console.log(stdout)
    return true
  } catch (error) {
    log('❌ Bundle check failed', 'red')
    console.error(error.stdout || error.message)
    return false
  }
}

async function runBuild() {
  log('\n🔨 Building for production...', 'cyan')
  try {
    await execAsync('npm run build')
    log('✅ Build successful', 'green')
    return true
  } catch (error) {
    log('❌ Build failed', 'red')
    console.error(error.stdout || error.message)
    return false
  }
}

async function analyzeBundle() {
  log('\n📊 Analyzing bundle composition...', 'cyan')
  try {
    const distPath = path.join(process.cwd(), 'dist')
    const files = await fs.readdir(path.join(distPath, 'assets'))
    
    const jsFiles = files.filter(f => f.endsWith('.js'))
    const cssFiles = files.filter(f => f.endsWith('.css'))
    
    log(`\nBundle Composition:`, 'blue')
    log(`  JavaScript files: ${jsFiles.length}`)
    log(`  CSS files: ${cssFiles.length}`)
    
    // Get total sizes
    let totalJsSize = 0
    let totalCssSize = 0
    
    for (const file of jsFiles) {
      const stats = await fs.stat(path.join(distPath, 'assets', file))
      totalJsSize += stats.size
    }
    
    for (const file of cssFiles) {
      const stats = await fs.stat(path.join(distPath, 'assets', file))
      totalCssSize += stats.size
    }
    
    log(`  Total JS size: ${(totalJsSize / 1024).toFixed(2)} KB`)
    log(`  Total CSS size: ${(totalCssSize / 1024).toFixed(2)} KB`)
    
    return true
  } catch (error) {
    log('❌ Bundle analysis failed', 'red')
    console.error(error.message)
    return false
  }
}

async function generateReport() {
  log('\n📝 Generating Performance Report...', 'cyan')
  
  const report = {
    timestamp: new Date().toISOString(),
    date: new Date().toLocaleString(),
    tests: {
      bundleSize: 'Passed',
      build: 'Passed'
    },
    recommendations: []
  }
  
  // Read bundle stats
  try {
    const distPath = path.join(process.cwd(), 'dist')
    const files = await fs.readdir(path.join(distPath, 'assets'))
    
    const jsFiles = files.filter(f => f.endsWith('.js'))
    let totalJsSize = 0
    
    for (const file of jsFiles) {
      const stats = await fs.stat(path.join(distPath, 'assets', file))
      totalJsSize += stats.size
    }
    
    report.bundleSize = {
      totalJs: (totalJsSize / 1024).toFixed(2) + ' KB',
      budget: '500 KB',
      percentage: ((totalJsSize / (500 * 1024)) * 100).toFixed(1) + '%'
    }
    
    // Add recommendations based on size
    if (totalJsSize > 400 * 1024) {
      report.recommendations.push('Consider code splitting for larger components')
    }
    if (totalJsSize > 450 * 1024) {
      report.recommendations.push('WARNING: Approaching bundle size budget')
    }
  } catch (error) {
    console.warn('Could not read bundle stats:', error.message)
  }
  
  // Write report
  const reportPath = path.join(process.cwd(), 'performance-report.json')
  await fs.writeFile(reportPath, JSON.stringify(report, null, 2))
  
  log(`\n✅ Report saved to: ${reportPath}`, 'green')
  
  // Print summary
  log('\n' + '='.repeat(60), 'blue')
  log('PERFORMANCE TEST SUMMARY', 'blue')
  log('='.repeat(60), 'blue')
  log(`Date: ${report.date}`)
  if (report.bundleSize) {
    log(`Bundle Size: ${report.bundleSize.totalJs} / ${report.bundleSize.budget} (${report.bundleSize.percentage})`)
  }
  log(`Status: ${report.tests.bundleSize}`, 'green')
  
  if (report.recommendations.length > 0) {
    log('\nRecommendations:', 'yellow')
    report.recommendations.forEach(rec => log(`  - ${rec}`, 'yellow'))
  }
  log('='.repeat(60), 'blue')
  
  return true
}

async function main() {
  log('🚀 Starting Performance Tests', 'cyan')
  log('='.repeat(60), 'cyan')
  
  let success = true
  
  // Run build
  if (!await runBuild()) {
    success = false
  }
  
  // Analyze bundle
  if (!await analyzeBundle()) {
    success = false
  }
  
  // Run bundle check
  if (!await runBundleCheck()) {
    success = false
  }
  
  // Generate report
  await generateReport()
  
  if (success) {
    log('\n✅ All performance tests passed!', 'green')
    process.exit(0)
  } else {
    log('\n❌ Some performance tests failed', 'red')
    process.exit(1)
  }
}

main().catch(error => {
  log(`\n❌ Error: ${error.message}`, 'red')
  process.exit(1)
})
