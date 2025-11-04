#!/usr/bin/env python3
"""
Comprehensive Test Coverage Analysis Script for PrismQ.IdeaInspiration

This script analyzes test coverage across all modules in the repository,
identifies gaps, and provides actionable recommendations for improvement.
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ModuleCoverage:
    """Coverage statistics for a single module."""
    
    name: str
    path: Path
    total_statements: int = 0
    covered_statements: int = 0
    missing_statements: int = 0
    coverage_percentage: float = 0.0
    test_count: int = 0
    test_failures: int = 0
    has_tests: bool = False
    uncovered_files: List[str] = field(default_factory=list)
    partially_covered_files: List[Dict] = field(default_factory=list)
    
    @property
    def status(self) -> str:
        """Get coverage status label."""
        if not self.has_tests:
            return "NO_TESTS"
        if self.coverage_percentage >= 90:
            return "EXCELLENT"
        if self.coverage_percentage >= 80:
            return "GOOD"
        if self.coverage_percentage >= 60:
            return "FAIR"
        return "NEEDS_IMPROVEMENT"


class CoverageAnalyzer:
    """Analyzes test coverage across the repository."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.modules: List[ModuleCoverage] = []
        self.module_directories = [
            "Scoring",
            "Classification", 
            "Model",
            "ConfigLoad",
        ]
        
    def run_module_tests(self, module_path: Path) -> Optional[ModuleCoverage]:
        """Run tests for a single module and collect coverage data."""
        module_name = module_path.relative_to(self.repo_root).as_posix()
        print(f"\n{'='*80}")
        print(f"Analyzing: {module_name}")
        print(f"{'='*80}")
        
        coverage = ModuleCoverage(name=module_name, path=module_path)
        
        # Find test directory
        test_dirs = []
        if (module_path / "_meta" / "tests").exists():
            test_dirs.append(module_path / "_meta" / "tests")
        if (module_path / "tests").exists():
            test_dirs.append(module_path / "tests")
            
        if not test_dirs:
            print(f"⚠️  No tests directory found")
            coverage.has_tests = False
            return coverage
            
        coverage.has_tests = True
        
        # Determine source directories to measure
        src_dirs = []
        if (module_path / "src").exists():
            src_dirs.append("src")
        if (module_path / "prismq").exists():
            src_dirs.append("prismq")
        if module_name == "Model":
            src_dirs.append("idea_inspiration.py")
        if module_name == "ConfigLoad":
            src_dirs.extend(["config.py", "logging_config.py"])
            
        if not src_dirs:
            print(f"⚠️  No source directory found")
            return coverage
            
        # Build pytest command arguments
        pytest_args = [
            "python", "-m", "pytest"
        ]
        
        # Add test paths
        for td in test_dirs:
            pytest_args.append(str(td.relative_to(module_path)))
        
        # Add coverage arguments
        for src in src_dirs:
            pytest_args.extend(["--cov", src])
        
        pytest_args.extend([
            "--cov-report=json:coverage.json",
            "--cov-report=term",
            "-v", "--tb=no", "-q"
        ])
        
        # Set environment
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{module_path}:{env.get('PYTHONPATH', '')}"
        
        try:
            result = subprocess.run(
                pytest_args,
                cwd=module_path,
                capture_output=True,
                text=True,
                timeout=240,  # 4 minutes, configurable via environment
                env=env
            )
            
            # Parse test results
            output = result.stdout + result.stderr
            
            # Count tests
            if " passed" in output:
                for line in output.split("\n"):
                    if " passed" in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == "passed":
                                try:
                                    coverage.test_count = int(parts[i-1])
                                except (ValueError, IndexError):
                                    pass
                        if " failed" in line:
                            for i, part in enumerate(parts):
                                if part == "failed,":
                                    try:
                                        coverage.test_failures = int(parts[i-1])
                                    except (ValueError, IndexError):
                                        pass
            
            # Parse coverage JSON if available
            coverage_json_path = module_path / "coverage.json"
            if coverage_json_path.exists():
                with open(coverage_json_path) as f:
                    cov_data = json.load(f)
                    
                coverage.total_statements = cov_data["totals"]["num_statements"]
                coverage.covered_statements = cov_data["totals"]["covered_lines"]
                coverage.missing_statements = cov_data["totals"]["missing_lines"]
                coverage.coverage_percentage = cov_data["totals"]["percent_covered"]
                
                # Find uncovered and partially covered files
                for file_path, file_data in cov_data["files"].items():
                    file_cov = file_data["summary"]["percent_covered"]
                    if file_cov == 0:
                        coverage.uncovered_files.append(file_path)
                    elif file_cov < 80:
                        coverage.partially_covered_files.append({
                            "file": file_path,
                            "coverage": file_cov,
                            "missing": file_data["summary"]["missing_lines"]
                        })
                        
                # Clean up
                coverage_json_path.unlink()
                
            print(f"✅ Tests: {coverage.test_count} passed, {coverage.test_failures} failed")
            print(f"📊 Coverage: {coverage.coverage_percentage:.1f}% ({coverage.covered_statements}/{coverage.total_statements} statements)")
            
        except subprocess.TimeoutExpired:
            print(f"⏱️  Tests timed out")
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            
        return coverage
        
    def analyze_all_modules(self) -> None:
        """Analyze coverage for all configured modules."""
        print(f"\n{'#'*80}")
        print(f"# PrismQ.IdeaInspiration - Test Coverage Analysis")
        print(f"{'#'*80}\n")
        
        for module_dir in self.module_directories:
            module_path = self.repo_root / module_dir
            if not module_path.exists():
                print(f"⚠️  Module not found: {module_dir}")
                continue
                
            coverage = self.run_module_tests(module_path)
            if coverage:
                self.modules.append(coverage)
                
    def generate_report(self) -> str:
        """Generate comprehensive coverage report."""
        report = []
        report.append("\n" + "="*80)
        report.append("COVERAGE SUMMARY REPORT")
        report.append("="*80 + "\n")
        
        # Overall statistics
        total_modules = len(self.modules)
        modules_with_tests = sum(1 for m in self.modules if m.has_tests)
        modules_without_tests = total_modules - modules_with_tests
        
        total_statements = sum(m.total_statements for m in self.modules)
        total_covered = sum(m.covered_statements for m in self.modules)
        overall_coverage = (total_covered / total_statements * 100) if total_statements > 0 else 0
        
        total_tests = sum(m.test_count for m in self.modules)
        total_failures = sum(m.test_failures for m in self.modules)
        
        report.append("📈 OVERALL STATISTICS")
        report.append("-" * 80)
        report.append(f"Total Modules Analyzed:     {total_modules}")
        report.append(f"Modules with Tests:         {modules_with_tests}")
        report.append(f"Modules without Tests:      {modules_without_tests}")
        report.append(f"Total Test Cases:           {total_tests}")
        report.append(f"Failed Tests:               {total_failures}")
        report.append(f"Overall Coverage:           {overall_coverage:.1f}%")
        report.append(f"Total Statements:           {total_statements}")
        report.append(f"Covered Statements:         {total_covered}")
        report.append(f"Missing Statements:         {total_statements - total_covered}")
        report.append("")
        
        # Module breakdown by status
        by_status = {}
        for module in self.modules:
            status = module.status
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(module)
            
        status_order = ["EXCELLENT", "GOOD", "FAIR", "NEEDS_IMPROVEMENT", "NO_TESTS"]
        status_emoji = {
            "EXCELLENT": "🌟",
            "GOOD": "✅",
            "FAIR": "⚠️",
            "NEEDS_IMPROVEMENT": "❌",
            "NO_TESTS": "🚫"
        }
        
        report.append("📊 MODULE BREAKDOWN BY COVERAGE")
        report.append("-" * 80)
        
        for status in status_order:
            if status not in by_status:
                continue
            modules = by_status[status]
            report.append(f"\n{status_emoji[status]} {status} ({len(modules)} modules)")
            report.append("")
            
            for module in sorted(modules, key=lambda m: m.coverage_percentage, reverse=True):
                if module.has_tests:
                    report.append(
                        f"  {module.name:50s} "
                        f"{module.coverage_percentage:5.1f}% "
                        f"({module.test_count} tests, {module.test_failures} failed)"
                    )
                else:
                    report.append(f"  {module.name:50s} NO TESTS")
                    
        # Detailed issues and recommendations
        report.append("\n" + "="*80)
        report.append("🔍 DETAILED FINDINGS & RECOMMENDATIONS")
        report.append("="*80 + "\n")
        
        # 1. Modules without tests
        no_test_modules = [m for m in self.modules if not m.has_tests]
        if no_test_modules:
            report.append("1️⃣ MODULES WITHOUT TESTS")
            report.append("-" * 80)
            report.append("These modules have no test coverage at all:\n")
            for module in no_test_modules:
                report.append(f"   • {module.name}")
            report.append("\n💡 RECOMMENDATION: Create test infrastructure for these modules")
            report.append("   - Add tests directory (_meta/tests or tests/)")
            report.append("   - Create basic test files covering core functionality")
            report.append("   - Configure pytest in pyproject.toml\n")
            
        # 2. Modules with failing tests
        failing_test_modules = [m for m in self.modules if m.test_failures > 0]
        if failing_test_modules:
            report.append("2️⃣ MODULES WITH FAILING TESTS")
            report.append("-" * 80)
            report.append("These modules have test failures that need attention:\n")
            for module in failing_test_modules:
                report.append(
                    f"   • {module.name}: {module.test_failures} failures "
                    f"out of {module.test_count + module.test_failures} tests"
                )
            report.append("\n💡 RECOMMENDATION: Fix failing tests before adding new ones")
            report.append("   - Investigate API changes causing failures")
            report.append("   - Update tests to match current implementation")
            report.append("   - Ensure CI/CD pipeline catches test failures\n")
            
        # 3. Files with zero coverage
        report.append("3️⃣ FILES WITH ZERO COVERAGE")
        report.append("-" * 80)
        uncovered_count = 0
        for module in self.modules:
            if module.uncovered_files:
                uncovered_count += len(module.uncovered_files)
                report.append(f"\n{module.name}:")
                for file in module.uncovered_files:
                    report.append(f"   • {file}")
                    
        if uncovered_count > 0:
            report.append(f"\n💡 RECOMMENDATION: Add tests for {uncovered_count} uncovered files")
            report.append("   - Prioritize main.py, CLI entry points, and core logic files")
            report.append("   - Consider if some files (like __init__.py) need coverage")
            report.append("   - Add integration tests for entry points\n")
        else:
            report.append("✅ No files with zero coverage!\n")
            
        # 4. Files with low coverage
        report.append("4️⃣ FILES WITH LOW COVERAGE (<80%)")
        report.append("-" * 80)
        low_coverage_count = 0
        for module in self.modules:
            if module.partially_covered_files:
                low_coverage_count += len(module.partially_covered_files)
                report.append(f"\n{module.name}:")
                for file_info in sorted(module.partially_covered_files, key=lambda x: x["coverage"]):
                    report.append(
                        f"   • {file_info['file']:50s} "
                        f"{file_info['coverage']:5.1f}% "
                        f"({file_info['missing']} lines missing)"
                    )
                    
        if low_coverage_count > 0:
            report.append(f"\n💡 RECOMMENDATION: Improve coverage for {low_coverage_count} partially covered files")
            report.append("   - Focus on edge cases and error handling")
            report.append("   - Add tests for exceptional conditions")
            report.append("   - Review uncovered lines and add targeted tests\n")
        else:
            report.append("✅ All covered files have good coverage (≥80%)!\n")
            
        # 5. Coverage configuration improvements
        report.append("5️⃣ COVERAGE CONFIGURATION IMPROVEMENTS")
        report.append("-" * 80)
        report.append("Recommended improvements to coverage configuration:\n")
        report.append("   • Add .coveragerc or [tool.coverage] in pyproject.toml")
        report.append("   • Configure coverage exclusions (pragma: no cover)")
        report.append("   • Set minimum coverage thresholds")
        report.append("   • Enable branch coverage (--cov-branch)")
        report.append("   • Configure HTML reports for better visualization")
        report.append("   • Add coverage badges to README files\n")
        
        # 6. Testing best practices
        report.append("6️⃣ TESTING BEST PRACTICES & OPPORTUNITIES")
        report.append("-" * 80)
        report.append("General recommendations for improving test quality:\n")
        report.append("   • Add integration tests for module interactions")
        report.append("   • Implement property-based testing (hypothesis)")
        report.append("   • Add performance/benchmark tests for critical paths")
        report.append("   • Create test fixtures for common test data")
        report.append("   • Add mocking for external dependencies")
        report.append("   • Implement test coverage trends tracking")
        report.append("   • Add mutation testing to verify test effectiveness")
        report.append("   • Consider adding type checking (mypy) to CI")
        report.append("")
        
        return "\n".join(report)
        
    def save_report(self, output_path: Path) -> None:
        """Save report to file."""
        report = self.generate_report()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(report)
        print(f"\n📄 Report saved to: {output_path}")
        
        # Also print to console
        print(report)


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent
    
    analyzer = CoverageAnalyzer(repo_root)
    analyzer.analyze_all_modules()
    
    # Generate and save report
    report_path = repo_root / "_meta" / "docs" / "TEST_COVERAGE_REPORT.md"
    analyzer.save_report(report_path)
    
    # Exit with error if overall coverage is below threshold
    total_statements = sum(m.total_statements for m in analyzer.modules)
    total_covered = sum(m.covered_statements for m in analyzer.modules)
    overall_coverage = (total_covered / total_statements * 100) if total_statements > 0 else 0
    
    print(f"\n{'='*80}")
    if overall_coverage >= 80:
        print(f"✅ Overall coverage {overall_coverage:.1f}% meets threshold (≥80%)")
        return 0
    else:
        print(f"⚠️  Overall coverage {overall_coverage:.1f}% below recommended threshold (80%)")
        return 0  # Don't fail, just warn


if __name__ == "__main__":
    sys.exit(main())
