#!/usr/bin/env node

/**
 * Bundle Size Monitor
 * 
 * Checks the bundle size against performance budgets
 * and reports warnings/errors if budgets are exceeded.
 */

import { readdir, stat } from 'fs/promises';
import { join } from 'path';

// Performance budgets (in bytes)
const BUDGETS = {
  initial: 512000, // 500KB
  chunk: 102400,   // 100KB warning threshold
  css: 51200,      // 50KB
  total: 1048576   // 1MB
};

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  green: '\x1b[32m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m'
};

function formatBytes(bytes) {
  return `${(bytes / 1024).toFixed(2)} KB`;
}

function colorize(text, color) {
  return `${color}${text}${colors.reset}`;
}

async function getFilesRecursive(dir) {
  const files = [];
  const items = await readdir(dir);
  
  for (const item of items) {
    const fullPath = join(dir, item);
    const stats = await stat(fullPath);
    
    if (stats.isDirectory()) {
      files.push(...await getFilesRecursive(fullPath));
    } else {
      files.push({ path: fullPath, size: stats.size });
    }
  }
  
  return files;
}

async function analyzeBundleSize() {
  const distDir = 'dist';
  let totalSize = 0;
  let jsSize = 0;
  let cssSize = 0;
  let issues = [];
  
  console.log(colorize('\n📊 Bundle Size Analysis\n', colors.cyan + colors.bold));
  
  try {
    const files = await getFilesRecursive(distDir);
    
    // Categorize files
    const jsFiles = files.filter(f => f.path.endsWith('.js'));
    const cssFiles = files.filter(f => f.path.endsWith('.css'));
    const otherFiles = files.filter(f => !f.path.endsWith('.js') && !f.path.endsWith('.css'));
    
    // Calculate sizes
    jsSize = jsFiles.reduce((sum, f) => sum + f.size, 0);
    cssSize = cssFiles.reduce((sum, f) => sum + f.size, 0);
    totalSize = files.reduce((sum, f) => sum + f.size, 0);
    
    // Report JavaScript files
    console.log(colorize('JavaScript Files:', colors.bold));
    jsFiles.forEach(file => {
      const relativePath = file.path.replace('dist/', '');
      const sizeStr = formatBytes(file.size);
      
      let status = '✓';
      let statusColor = colors.green;
      
      if (file.size > BUDGETS.initial) {
        status = '✗';
        statusColor = colors.red;
        issues.push(`${relativePath} exceeds initial bundle budget (${sizeStr} > ${formatBytes(BUDGETS.initial)})`);
      } else if (file.size > BUDGETS.chunk) {
        status = '⚠';
        statusColor = colors.yellow;
        issues.push(`${relativePath} exceeds chunk warning threshold (${sizeStr} > ${formatBytes(BUDGETS.chunk)})`);
      }
      
      console.log(`  ${colorize(status, statusColor)} ${relativePath}: ${sizeStr}`);
    });
    
    console.log(`  ${colorize('Total JS:', colors.bold)} ${formatBytes(jsSize)}`);
    
    // Report CSS files
    console.log(colorize('\nCSS Files:', colors.bold));
    cssFiles.forEach(file => {
      const relativePath = file.path.replace('dist/', '');
      const sizeStr = formatBytes(file.size);
      
      let status = '✓';
      let statusColor = colors.green;
      
      if (file.size > BUDGETS.css) {
        status = '⚠';
        statusColor = colors.yellow;
        issues.push(`${relativePath} exceeds CSS budget (${sizeStr} > ${formatBytes(BUDGETS.css)})`);
      }
      
      console.log(`  ${colorize(status, statusColor)} ${relativePath}: ${sizeStr}`);
    });
    
    console.log(`  ${colorize('Total CSS:', colors.bold)} ${formatBytes(cssSize)}`);
    
    // Report other files
    if (otherFiles.length > 0) {
      console.log(colorize('\nOther Assets:', colors.bold));
      otherFiles.forEach(file => {
        const relativePath = file.path.replace('dist/', '');
        console.log(`  ${relativePath}: ${formatBytes(file.size)}`);
      });
    }
    
    // Summary
    console.log(colorize('\n📋 Summary:', colors.cyan + colors.bold));
    console.log(`  Total Size: ${formatBytes(totalSize)}`);
    console.log(`  JavaScript: ${formatBytes(jsSize)}`);
    console.log(`  CSS: ${formatBytes(cssSize)}`);
    console.log(`  Other: ${formatBytes(totalSize - jsSize - cssSize)}`);
    
    // Budget check
    console.log(colorize('\n🎯 Budget Status:', colors.cyan + colors.bold));
    
    const totalStatus = totalSize <= BUDGETS.total ? '✓' : '✗';
    const totalColor = totalSize <= BUDGETS.total ? colors.green : colors.red;
    console.log(`  ${colorize(totalStatus, totalColor)} Total: ${formatBytes(totalSize)} / ${formatBytes(BUDGETS.total)}`);
    
    const jsStatus = jsSize <= BUDGETS.initial ? '✓' : '✗';
    const jsColor = jsSize <= BUDGETS.initial ? colors.green : colors.red;
    console.log(`  ${colorize(jsStatus, jsColor)} JavaScript: ${formatBytes(jsSize)} / ${formatBytes(BUDGETS.initial)}`);
    
    const cssStatus = cssSize <= BUDGETS.css ? '✓' : '✗';
    const cssColor = cssSize <= BUDGETS.css ? colors.green : colors.red;
    console.log(`  ${colorize(cssStatus, cssColor)} CSS: ${formatBytes(cssSize)} / ${formatBytes(BUDGETS.css)}`);
    
    // Issues
    if (issues.length > 0) {
      console.log(colorize('\n⚠️  Issues Found:', colors.yellow + colors.bold));
      issues.forEach(issue => {
        console.log(`  - ${issue}`);
      });
      console.log('');
      process.exit(1);
    } else {
      console.log(colorize('\n✅ All budgets passed!\n', colors.green + colors.bold));
      process.exit(0);
    }
    
  } catch (error) {
    console.error(colorize(`\n❌ Error analyzing bundle: ${error.message}\n`, colors.red));
    process.exit(1);
  }
}

analyzeBundleSize();
