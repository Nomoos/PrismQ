#!/usr/bin/env node

/**
 * Performance Baseline Analysis Script
 * 
 * This script captures and compares performance baselines to detect regressions
 * and improvements over time.
 * 
 * Commands:
 *   capture  - Capture current build metrics as baseline
 *   compare  - Compare current build against baseline
 *   report   - Generate detailed baseline report
 */

import { readdir, stat, readFile, writeFile, mkdir } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname, '..');

// Paths
const BASELINE_DIR = join(projectRoot, '.baselines');
const BASELINE_FILE = join(BASELINE_DIR, 'performance-baseline.json');
const HISTORY_FILE = join(BASELINE_DIR, 'baseline-history.json');

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  green: '\x1b[32m',
  cyan: '\x1b[36m',
  blue: '\x1b[34m',
  bold: '\x1b[1m',
  dim: '\x1b[2m'
};

function colorize(text, color) {
  return `${color}${text}${colors.reset}`;
}

function formatBytes(bytes) {
  return `${(bytes / 1024).toFixed(2)} KB`;
}

function formatDelta(current, baseline) {
  const delta = current - baseline;
  const percentage = baseline > 0 ? ((delta / baseline) * 100).toFixed(1) : '0.0';
  const sign = delta > 0 ? '+' : '';
  return {
    delta,
    percentage,
    display: `${sign}${formatBytes(delta)} (${sign}${percentage}%)`
  };
}

async function getGitInfo() {
  try {
    const { stdout: commit } = await execAsync('git rev-parse --short HEAD');
    const { stdout: branch } = await execAsync('git rev-parse --abbrev-ref HEAD');
    const { stdout: author } = await execAsync('git log -1 --pretty=format:"%an"');
    const { stdout: message } = await execAsync('git log -1 --pretty=format:"%s"');
    
    return {
      commit: commit.trim(),
      branch: branch.trim(),
      author: author.trim(),
      message: message.trim()
    };
  } catch (error) {
    return {
      commit: 'unknown',
      branch: 'unknown',
      author: 'unknown',
      message: 'unknown'
    };
  }
}

async function getFilesRecursive(dir) {
  const files = [];
  try {
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
  } catch (error) {
    // Directory doesn't exist or can't be read
  }
  
  return files;
}

async function analyzeBuild() {
  const distDir = join(projectRoot, 'dist');
  const files = await getFilesRecursive(distDir);
  
  const jsFiles = files.filter(f => f.path.endsWith('.js'));
  const cssFiles = files.filter(f => f.path.endsWith('.css'));
  const htmlFiles = files.filter(f => f.path.endsWith('.html'));
  const assetFiles = files.filter(f => 
    !f.path.endsWith('.js') && 
    !f.path.endsWith('.css') && 
    !f.path.endsWith('.html')
  );
  
  const jsSize = jsFiles.reduce((sum, f) => sum + f.size, 0);
  const cssSize = cssFiles.reduce((sum, f) => sum + f.size, 0);
  const htmlSize = htmlFiles.reduce((sum, f) => sum + f.size, 0);
  const assetSize = assetFiles.reduce((sum, f) => sum + f.size, 0);
  const totalSize = files.reduce((sum, f) => sum + f.size, 0);
  
  // Get largest chunks
  const sortedJs = [...jsFiles].sort((a, b) => b.size - a.size);
  const largestChunks = sortedJs.slice(0, 5).map(f => ({
    name: f.path.replace(distDir + '/', '').replace('assets/', ''),
    size: f.size
  }));
  
  return {
    totalSize,
    jsSize,
    cssSize,
    htmlSize,
    assetSize,
    fileCount: {
      total: files.length,
      js: jsFiles.length,
      css: cssFiles.length,
      html: htmlFiles.length,
      assets: assetFiles.length
    },
    largestChunks
  };
}

async function measureBuildTime() {
  const startTime = Date.now();
  
  try {
    await execAsync('npm run build', { cwd: projectRoot });
    const duration = Date.now() - startTime;
    return { success: true, duration };
  } catch (error) {
    const duration = Date.now() - startTime;
    return { success: false, duration, error: error.message };
  }
}

async function captureBaseline() {
  console.log(colorize('\n📸 Capturing Performance Baseline\n', colors.cyan + colors.bold));
  
  // Get git info
  console.log('Gathering git information...');
  const gitInfo = await getGitInfo();
  
  // Ensure build exists
  console.log('Analyzing build...');
  let buildMetrics;
  try {
    buildMetrics = await analyzeBuild();
  } catch (error) {
    console.log(colorize('⚠️  Build not found. Running build first...', colors.yellow));
    const buildResult = await measureBuildTime();
    if (!buildResult.success) {
      console.error(colorize(`\n❌ Build failed: ${buildResult.error}\n`, colors.red));
      process.exit(1);
    }
    buildMetrics = await analyzeBuild();
  }
  
  // Create baseline object
  const baseline = {
    timestamp: new Date().toISOString(),
    date: new Date().toLocaleString(),
    git: gitInfo,
    metrics: buildMetrics,
    budgets: {
      totalSize: 1048576, // 1MB
      jsSize: 512000,     // 500KB
      cssSize: 51200,     // 50KB
      chunkSize: 102400   // 100KB
    }
  };
  
  // Ensure baseline directory exists
  await mkdir(BASELINE_DIR, { recursive: true });
  
  // Save baseline
  await writeFile(BASELINE_FILE, JSON.stringify(baseline, null, 2));
  
  // Update history
  let history = [];
  try {
    const historyData = await readFile(HISTORY_FILE, 'utf8');
    history = JSON.parse(historyData);
  } catch (error) {
    // History file doesn't exist yet
  }
  
  history.push({
    timestamp: baseline.timestamp,
    commit: gitInfo.commit,
    totalSize: buildMetrics.totalSize,
    jsSize: buildMetrics.jsSize,
    cssSize: buildMetrics.cssSize
  });
  
  // Keep last 50 entries
  if (history.length > 50) {
    history = history.slice(-50);
  }
  
  await writeFile(HISTORY_FILE, JSON.stringify(history, null, 2));
  
  // Display captured baseline
  console.log(colorize('\n✅ Baseline Captured Successfully\n', colors.green + colors.bold));
  console.log(colorize('Git Information:', colors.bold));
  console.log(`  Commit:  ${gitInfo.commit}`);
  console.log(`  Branch:  ${gitInfo.branch}`);
  console.log(`  Author:  ${gitInfo.author}`);
  console.log(`  Message: ${gitInfo.message}`);
  
  console.log(colorize('\nBuild Metrics:', colors.bold));
  console.log(`  Total Size:  ${formatBytes(buildMetrics.totalSize)}`);
  console.log(`  JavaScript:  ${formatBytes(buildMetrics.jsSize)}`);
  console.log(`  CSS:         ${formatBytes(buildMetrics.cssSize)}`);
  console.log(`  HTML:        ${formatBytes(buildMetrics.htmlSize)}`);
  console.log(`  Assets:      ${formatBytes(buildMetrics.assetSize)}`);
  
  console.log(colorize('\nFile Counts:', colors.bold));
  console.log(`  Total:       ${buildMetrics.fileCount.total} files`);
  console.log(`  JavaScript:  ${buildMetrics.fileCount.js} files`);
  console.log(`  CSS:         ${buildMetrics.fileCount.css} files`);
  
  console.log(colorize('\nLargest Chunks:', colors.bold));
  buildMetrics.largestChunks.forEach((chunk, i) => {
    console.log(`  ${i + 1}. ${chunk.name}: ${formatBytes(chunk.size)}`);
  });
  
  console.log(colorize(`\n📁 Baseline saved to: ${BASELINE_FILE}\n`, colors.dim));
}

async function compareWithBaseline() {
  console.log(colorize('\n📊 Comparing Against Baseline\n', colors.cyan + colors.bold));
  
  // Load baseline
  let baseline;
  try {
    const baselineData = await readFile(BASELINE_FILE, 'utf8');
    baseline = JSON.parse(baselineData);
  } catch (error) {
    console.error(colorize('❌ No baseline found. Run "npm run baseline:capture" first.\n', colors.red));
    process.exit(1);
  }
  
  // Get current metrics
  console.log('Analyzing current build...');
  let currentMetrics;
  try {
    currentMetrics = await analyzeBuild();
  } catch (error) {
    console.error(colorize('❌ Current build not found. Run "npm run build" first.\n', colors.red));
    process.exit(1);
  }
  
  const gitInfo = await getGitInfo();
  
  // Compare metrics
  const totalDelta = formatDelta(currentMetrics.totalSize, baseline.metrics.totalSize);
  const jsDelta = formatDelta(currentMetrics.jsSize, baseline.metrics.jsSize);
  const cssDelta = formatDelta(currentMetrics.cssSize, baseline.metrics.cssSize);
  
  // Determine status
  const hasRegression = 
    currentMetrics.totalSize > baseline.metrics.totalSize ||
    currentMetrics.jsSize > baseline.metrics.jsSize ||
    currentMetrics.cssSize > baseline.metrics.cssSize;
  
  const significantChange = 
    Math.abs(totalDelta.delta) > 10240 || // 10KB
    Math.abs(jsDelta.delta) > 5120 ||     // 5KB
    Math.abs(cssDelta.delta) > 1024;      // 1KB
  
  // Display comparison
  console.log(colorize('Baseline Information:', colors.bold));
  console.log(`  Created:  ${baseline.date}`);
  console.log(`  Commit:   ${baseline.git.commit}`);
  console.log(`  Branch:   ${baseline.git.branch}`);
  
  console.log(colorize('\nCurrent Build:', colors.bold));
  console.log(`  Commit:   ${gitInfo.commit}`);
  console.log(`  Branch:   ${gitInfo.branch}`);
  
  console.log(colorize('\n📏 Size Comparison:\n', colors.cyan + colors.bold));
  
  // Total Size
  const totalColor = totalDelta.delta > 0 ? colors.red : colors.green;
  console.log(colorize('Total Size:', colors.bold));
  console.log(`  Baseline: ${formatBytes(baseline.metrics.totalSize)}`);
  console.log(`  Current:  ${formatBytes(currentMetrics.totalSize)}`);
  console.log(`  Delta:    ${colorize(totalDelta.display, totalColor)}`);
  
  // JavaScript
  const jsColor = jsDelta.delta > 0 ? colors.red : colors.green;
  console.log(colorize('\nJavaScript:', colors.bold));
  console.log(`  Baseline: ${formatBytes(baseline.metrics.jsSize)}`);
  console.log(`  Current:  ${formatBytes(currentMetrics.jsSize)}`);
  console.log(`  Delta:    ${colorize(jsDelta.display, jsColor)}`);
  
  // CSS
  const cssColor = cssDelta.delta > 0 ? colors.red : colors.green;
  console.log(colorize('\nCSS:', colors.bold));
  console.log(`  Baseline: ${formatBytes(baseline.metrics.cssSize)}`);
  console.log(`  Current:  ${formatBytes(currentMetrics.cssSize)}`);
  console.log(`  Delta:    ${colorize(cssDelta.display, cssColor)}`);
  
  // File counts
  console.log(colorize('\n📁 File Count Changes:\n', colors.cyan + colors.bold));
  console.log(`  JavaScript: ${baseline.metrics.fileCount.js} → ${currentMetrics.fileCount.js} (${currentMetrics.fileCount.js - baseline.metrics.fileCount.js > 0 ? '+' : ''}${currentMetrics.fileCount.js - baseline.metrics.fileCount.js})`);
  console.log(`  CSS:        ${baseline.metrics.fileCount.css} → ${currentMetrics.fileCount.css} (${currentMetrics.fileCount.css - baseline.metrics.fileCount.css > 0 ? '+' : ''}${currentMetrics.fileCount.css - baseline.metrics.fileCount.css})`);
  console.log(`  Total:      ${baseline.metrics.fileCount.total} → ${currentMetrics.fileCount.total} (${currentMetrics.fileCount.total - baseline.metrics.fileCount.total > 0 ? '+' : ''}${currentMetrics.fileCount.total - baseline.metrics.fileCount.total})`);
  
  // Budget Status
  console.log(colorize('\n🎯 Budget Status:\n', colors.cyan + colors.bold));
  
  const totalBudgetPercent = ((currentMetrics.totalSize / baseline.budgets.totalSize) * 100).toFixed(1);
  const totalBudgetColor = currentMetrics.totalSize <= baseline.budgets.totalSize ? colors.green : colors.red;
  console.log(`  Total:      ${formatBytes(currentMetrics.totalSize)} / ${formatBytes(baseline.budgets.totalSize)} ${colorize(`(${totalBudgetPercent}%)`, totalBudgetColor)}`);
  
  const jsBudgetPercent = ((currentMetrics.jsSize / baseline.budgets.jsSize) * 100).toFixed(1);
  const jsBudgetColor = currentMetrics.jsSize <= baseline.budgets.jsSize ? colors.green : colors.red;
  console.log(`  JavaScript: ${formatBytes(currentMetrics.jsSize)} / ${formatBytes(baseline.budgets.jsSize)} ${colorize(`(${jsBudgetPercent}%)`, jsBudgetColor)}`);
  
  const cssBudgetPercent = ((currentMetrics.cssSize / baseline.budgets.cssSize) * 100).toFixed(1);
  const cssBudgetColor = currentMetrics.cssSize <= baseline.budgets.cssSize ? colors.green : colors.red;
  console.log(`  CSS:        ${formatBytes(currentMetrics.cssSize)} / ${formatBytes(baseline.budgets.cssSize)} ${colorize(`(${cssBudgetPercent}%)`, cssBudgetColor)}`);
  
  // Summary
  console.log(colorize('\n📋 Summary:\n', colors.cyan + colors.bold));
  
  if (!significantChange) {
    console.log(colorize('  ✅ No significant changes detected', colors.green));
  } else if (hasRegression) {
    console.log(colorize('  ⚠️  Performance regression detected!', colors.yellow));
    console.log(colorize('  Consider investigating the size increase.', colors.yellow));
  } else {
    console.log(colorize('  ✅ Performance improved!', colors.green));
  }
  
  // Exit with appropriate code
  console.log('');
  if (hasRegression && significantChange) {
    process.exit(1);
  } else {
    process.exit(0);
  }
}

async function generateReport() {
  console.log(colorize('\n📄 Generating Performance Report\n', colors.cyan + colors.bold));
  
  // Load baseline
  let baseline;
  try {
    const baselineData = await readFile(BASELINE_FILE, 'utf8');
    baseline = JSON.parse(baselineData);
  } catch (error) {
    console.error(colorize('❌ No baseline found. Run "npm run baseline:capture" first.\n', colors.red));
    process.exit(1);
  }
  
  // Load history
  let history = [];
  try {
    const historyData = await readFile(HISTORY_FILE, 'utf8');
    history = JSON.parse(historyData);
  } catch (error) {
    console.warn(colorize('⚠️  No history found.\n', colors.yellow));
  }
  
  // Display baseline report
  console.log(colorize('Current Baseline:', colors.bold));
  console.log(`  Created:  ${baseline.date}`);
  console.log(`  Commit:   ${baseline.git.commit} (${baseline.git.branch})`);
  console.log(`  Author:   ${baseline.git.author}`);
  console.log(`  Message:  ${baseline.git.message}`);
  
  console.log(colorize('\nPerformance Metrics:', colors.bold));
  console.log(`  Total Size:  ${formatBytes(baseline.metrics.totalSize)}`);
  console.log(`  JavaScript:  ${formatBytes(baseline.metrics.jsSize)}`);
  console.log(`  CSS:         ${formatBytes(baseline.metrics.cssSize)}`);
  console.log(`  HTML:        ${formatBytes(baseline.metrics.htmlSize)}`);
  console.log(`  Assets:      ${formatBytes(baseline.metrics.assetSize)}`);
  
  console.log(colorize('\nFile Counts:', colors.bold));
  console.log(`  Total:       ${baseline.metrics.fileCount.total} files`);
  console.log(`  JavaScript:  ${baseline.metrics.fileCount.js} files`);
  console.log(`  CSS:         ${baseline.metrics.fileCount.css} files`);
  console.log(`  HTML:        ${baseline.metrics.fileCount.html} files`);
  console.log(`  Assets:      ${baseline.metrics.fileCount.assets} files`);
  
  console.log(colorize('\nLargest Chunks:', colors.bold));
  baseline.metrics.largestChunks.forEach((chunk, i) => {
    console.log(`  ${i + 1}. ${chunk.name}: ${formatBytes(chunk.size)}`);
  });
  
  // History trend
  if (history.length > 1) {
    console.log(colorize('\n📈 Historical Trend:\n', colors.cyan + colors.bold));
    console.log(colorize('  Last 10 builds:', colors.bold));
    
    const recentHistory = history.slice(-10);
    const oldest = recentHistory[0];
    const newest = recentHistory[recentHistory.length - 1];
    
    console.log(colorize('\n  Commit      Total        JS          CSS', colors.dim));
    console.log(colorize('  -------     -----        --          ---', colors.dim));
    
    recentHistory.forEach(entry => {
      const commit = entry.commit.substring(0, 7).padEnd(8);
      const total = formatBytes(entry.totalSize).padEnd(11);
      const js = formatBytes(entry.jsSize).padEnd(11);
      const css = formatBytes(entry.cssSize).padEnd(11);
      console.log(`  ${commit}  ${total}  ${js}  ${css}`);
    });
    
    // Overall trend
    const totalChange = newest.totalSize - oldest.totalSize;
    const trendColor = totalChange > 0 ? colors.red : colors.green;
    const trendSign = totalChange > 0 ? '+' : '';
    
    console.log(colorize('\n  Trend (oldest → newest):', colors.bold));
    console.log(`  Total: ${colorize(`${trendSign}${formatBytes(totalChange)}`, trendColor)}`);
  }
  
  console.log('');
}

// Main CLI
const command = process.argv[2];

switch (command) {
  case 'capture':
    captureBaseline();
    break;
  case 'compare':
    compareWithBaseline();
    break;
  case 'report':
    generateReport();
    break;
  default:
    console.log(colorize('\nPerformance Baseline Analysis Tool\n', colors.cyan + colors.bold));
    console.log('Usage:');
    console.log('  npm run baseline:capture  - Capture current build as baseline');
    console.log('  npm run baseline:compare  - Compare current build against baseline');
    console.log('  npm run baseline:report   - Generate detailed baseline report');
    console.log('');
    process.exit(1);
}
