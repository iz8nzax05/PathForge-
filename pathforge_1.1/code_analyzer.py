#!/usr/bin/env python3
"""
ADVANCED CODE ANALYZER
Comprehensive analysis tool for PathForge codebase
Scans for rule breaks, inconsistencies, and provides detailed reports
"""

import os
import ast
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class CodeIssue:
    """Represents a code issue found during analysis"""
    file: str
    line: int
    type: str
    severity: str
    message: str
    suggestion: str = ""

@dataclass
class AnalysisReport:
    """Comprehensive analysis report"""
    total_files: int
    total_lines: int
    issues: List[CodeIssue]
    statistics: Dict[str, Any]
    recommendations: List[str]

class CodeAnalyzer:
    """Advanced code analyzer for PathForge"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.issues: List[CodeIssue] = []
        self.statistics = defaultdict(int)
        self.file_analysis = {}
        
    def analyze_all(self) -> AnalysisReport:
        """Run comprehensive analysis on entire codebase"""
        print("🔍 Starting comprehensive code analysis...")
        
        # Find all Python files
        python_files = list(self.project_path.rglob("*.py"))
        self.statistics['total_files'] = len(python_files)
        
        total_lines = 0
        
        for file_path in python_files:
            print(f"📄 Analyzing: {file_path.relative_to(self.project_path)}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    total_lines += len(lines)
                    
                # Parse AST
                tree = ast.parse(content, filename=str(file_path))
                
                # Run all analysis checks
                self._analyze_imports(file_path, tree, content)
                self._analyze_naming_conventions(file_path, tree, content)
                self._analyze_code_structure(file_path, tree, content)
                self._analyze_duplication(file_path, content)
                self._analyze_complexity(file_path, tree)
                self._analyze_documentation(file_path, content)
                self._analyze_error_handling(file_path, tree, content)
                self._analyze_performance(file_path, tree, content)
                self._analyze_security(file_path, tree, content)
                
            except Exception as e:
                self.issues.append(CodeIssue(
                    file=str(file_path),
                    line=0,
                    type="PARSE_ERROR",
                    severity="ERROR",
                    message=f"Failed to parse file: {e}",
                    suggestion="Check for syntax errors"
                ))
        
        self.statistics['total_lines'] = total_lines
        self.statistics['total_issues'] = len(self.issues)
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        return AnalysisReport(
            total_files=len(python_files),
            total_lines=total_lines,
            issues=self.issues,
            statistics=dict(self.statistics),
            recommendations=recommendations
        )
    
    def _analyze_imports(self, file_path: Path, tree: ast.AST, content: str):
        """Analyze import organization and consistency"""
        imports = []
        from_imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    from_imports.append(node.module)
        
        # Check import order (standard library, third party, local)
        lines = content.split('\n')
        import_section = []
        in_imports = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                if not in_imports:
                    in_imports = True
                import_section.append((i + 1, stripped))
            elif in_imports and stripped and not stripped.startswith('#'):
                break
        
        # Check for mixed import styles
        has_import = any(line.startswith('import ') for _, line in import_section)
        has_from_import = any(line.startswith('from ') for _, line in import_section)
        
        if has_import and has_from_import:
            self.issues.append(CodeIssue(
                file=str(file_path),
                line=import_section[0][0] if import_section else 1,
                type="IMPORT_STYLE",
                severity="WARNING",
                message="Mixed import styles detected",
                suggestion="Use consistent import style (prefer 'from X import Y')"
            ))
        
        # Check for unused imports
        self._check_unused_imports(file_path, tree, imports, from_imports)
    
    def _check_unused_imports(self, file_path: Path, tree: ast.AST, imports: List[str], from_imports: List[str]):
        """Check for unused imports"""
        used_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                used_names.add(node.attr)
        
        # Check standard imports
        for imp in imports:
            if imp not in used_names:
                self.issues.append(CodeIssue(
                    file=str(file_path),
                    line=0,
                    type="UNUSED_IMPORT",
                    severity="WARNING",
                    message=f"Unused import: {imp}",
                    suggestion="Remove unused import"
                ))
    
    def _analyze_naming_conventions(self, file_path: Path, tree: ast.AST, content: str):
        """Analyze naming conventions"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Class names should be PascalCase
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    self.issues.append(CodeIssue(
                        file=str(file_path),
                        line=node.lineno,
                        type="NAMING_CONVENTION",
                        severity="ERROR",
                        message=f"Class name '{node.name}' should be PascalCase",
                        suggestion="Use PascalCase for class names (e.g., 'MyClass')"
                    ))
            
            elif isinstance(node, ast.FunctionDef):
                # Function names should be snake_case
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    self.issues.append(CodeIssue(
                        file=str(file_path),
                        line=node.lineno,
                        type="NAMING_CONVENTION",
                        severity="ERROR",
                        message=f"Function name '{node.name}' should be snake_case",
                        suggestion="Use snake_case for function names (e.g., 'my_function')"
                    ))
            
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                # Variable names should be snake_case
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.id) and not node.id.startswith('_'):
                    self.issues.append(CodeIssue(
                        file=str(file_path),
                        line=node.lineno,
                        type="NAMING_CONVENTION",
                        severity="WARNING",
                        message=f"Variable name '{node.id}' should be snake_case",
                        suggestion="Use snake_case for variable names (e.g., 'my_variable')"
                    ))
    
    def _analyze_code_structure(self, file_path: Path, tree: ast.AST, content: str):
        """Analyze code structure and organization"""
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node)
        
        # Check for classes without docstrings
        for cls in classes:
            if not ast.get_docstring(cls):
                self.issues.append(CodeIssue(
                    file=str(file_path),
                    line=cls.lineno,
                    type="MISSING_DOCSTRING",
                    severity="WARNING",
                    message=f"Class '{cls.name}' missing docstring",
                    suggestion="Add a docstring describing the class purpose"
                ))
        
        # Check for functions without docstrings (except private methods)
        for func in functions:
            if not func.name.startswith('_') and not ast.get_docstring(func):
                self.issues.append(CodeIssue(
                    file=str(file_path),
                    line=func.lineno,
                    type="MISSING_DOCSTRING",
                    severity="WARNING",
                    message=f"Function '{func.name}' missing docstring",
                    suggestion="Add a docstring describing the function purpose"
                ))
        
        # Check for overly long functions
        for func in functions:
            if len(func.body) > 50:  # More than 50 lines
                self.issues.append(CodeIssue(
                    file=str(file_path),
                    line=func.lineno,
                    type="FUNCTION_LENGTH",
                    severity="WARNING",
                    message=f"Function '{func.name}' is too long ({len(func.body)} lines)",
                    suggestion="Consider breaking into smaller functions"
                ))
    
    def _analyze_duplication(self, file_path: Path, content: str):
        """Analyze code duplication"""
        lines = content.split('\n')
        
        # Check for duplicate lines
        line_counts = defaultdict(int)
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                line_counts[stripped] += 1
        
        for line, count in line_counts.items():
            if count > 3:  # More than 3 occurrences
                self.issues.append(CodeIssue(
                    file=str(file_path),
                    line=0,
                    type="CODE_DUPLICATION",
                    severity="WARNING",
                    message=f"Duplicate code detected: '{line[:50]}...' appears {count} times",
                    suggestion="Consider extracting to a function or constant"
                ))
    
    def _analyze_complexity(self, file_path: Path, tree: ast.AST):
        """Analyze code complexity"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    self.issues.append(CodeIssue(
                        file=str(file_path),
                        line=node.lineno,
                        type="HIGH_COMPLEXITY",
                        severity="WARNING",
                        message=f"Function '{node.name}' has high complexity ({complexity})",
                        suggestion="Consider simplifying the logic or breaking into smaller functions"
                    ))
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _analyze_documentation(self, file_path: Path, content: str):
        """Analyze documentation quality"""
        lines = content.split('\n')
        
        # Check for TODO/FIXME comments
        for i, line in enumerate(lines):
            if re.search(r'\b(TODO|FIXME|XXX|HACK)\b', line, re.IGNORECASE):
                self.issues.append(CodeIssue(
                    file=str(file_path),
                    line=i + 1,
                    type="TECHNICAL_DEBT",
                    severity="INFO",
                    message=f"Technical debt marker: {line.strip()}",
                    suggestion="Address the TODO/FIXME item"
                ))
        
        # Check for missing module docstring
        if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
            self.issues.append(CodeIssue(
                file=str(file_path),
                line=1,
                type="MISSING_DOCSTRING",
                severity="INFO",
                message="Module missing docstring",
                suggestion="Add a module docstring at the top"
            ))
    
    def _analyze_error_handling(self, file_path: Path, tree: ast.AST, content: str):
        """Analyze error handling patterns"""
        has_try_except = False
        has_bare_except = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                has_try_except = True
                for handler in node.handlers:
                    if handler.type is None:  # Bare except
                        has_bare_except = True
                        self.issues.append(CodeIssue(
                            file=str(file_path),
                            line=handler.lineno,
                            type="BARE_EXCEPT",
                            severity="ERROR",
                            message="Bare except clause detected",
                            suggestion="Specify exception types (e.g., except ValueError:)"
                        ))
        
        # Check for print statements (should use logging)
        if 'print(' in content:
            self.issues.append(CodeIssue(
                file=str(file_path),
                line=0,
                type="PRINT_STATEMENT",
                severity="WARNING",
                message="Print statements found",
                suggestion="Consider using logging instead of print statements"
            ))
    
    def _analyze_performance(self, file_path: Path, tree: ast.AST, content: str):
        """Analyze performance issues"""
        # Check for inefficient patterns
        if 'for i in range(len(' in content:
            self.issues.append(CodeIssue(
                file=str(file_path),
                line=0,
                type="PERFORMANCE",
                severity="WARNING",
                message="Inefficient loop pattern detected",
                suggestion="Use enumerate() instead of range(len())"
            ))
        
        # Check for string concatenation in loops
        lines = content.split('\n')
        in_loop = False
        for i, line in enumerate(lines):
            if 'for ' in line and ' in ' in line:
                in_loop = True
            elif in_loop and ('+' in line and ('"' in line or "'" in line)):
                self.issues.append(CodeIssue(
                    file=str(file_path),
                    line=i + 1,
                    type="PERFORMANCE",
                    severity="WARNING",
                    message="String concatenation in loop detected",
                    suggestion="Use join() or f-strings for better performance"
                ))
            elif in_loop and line.strip() and not line.startswith(' '):
                in_loop = False
    
    def _analyze_security(self, file_path: Path, tree: ast.AST, content: str):
        """Analyze security issues"""
        # Check for eval usage
        if 'eval(' in content:
            self.issues.append(CodeIssue(
                file=str(file_path),
                line=0,
                type="SECURITY",
                severity="ERROR",
                message="eval() usage detected",
                suggestion="Avoid eval() as it can execute arbitrary code"
            ))
        
        # Check for exec usage
        if 'exec(' in content:
            self.issues.append(CodeIssue(
                file=str(file_path),
                line=0,
                type="SECURITY",
                severity="ERROR",
                message="exec() usage detected",
                suggestion="Avoid exec() as it can execute arbitrary code"
            ))
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Count issues by type
        issue_counts = defaultdict(int)
        for issue in self.issues:
            issue_counts[issue.type] += 1
        
        # Generate recommendations based on most common issues
        if issue_counts['NAMING_CONVENTION'] > 0:
            recommendations.append("🔧 Fix naming convention issues - use PascalCase for classes, snake_case for functions/variables")
        
        if issue_counts['MISSING_DOCSTRING'] > 0:
            recommendations.append("📝 Add missing docstrings to improve code documentation")
        
        if issue_counts['CODE_DUPLICATION'] > 0:
            recommendations.append("🔄 Refactor duplicate code into reusable functions")
        
        if issue_counts['HIGH_COMPLEXITY'] > 0:
            recommendations.append("🧩 Simplify complex functions by breaking them into smaller pieces")
        
        if issue_counts['PRINT_STATEMENT'] > 0:
            recommendations.append("📊 Replace print statements with proper logging")
        
        if issue_counts['BARE_EXCEPT'] > 0:
            recommendations.append("🛡️ Replace bare except clauses with specific exception handling")
        
        if issue_counts['SECURITY'] > 0:
            recommendations.append("🔒 Remove eval()/exec() usage for security")
        
        if not recommendations:
            recommendations.append("✅ Code quality looks good! No major issues found.")
        
        return recommendations
    
    def generate_report(self, report: AnalysisReport) -> str:
        """Generate a detailed report"""
        output = []
        output.append("=" * 80)
        output.append("🔍 PATHFORGE CODE ANALYSIS REPORT")
        output.append("=" * 80)
        output.append("")
        
        # Summary
        output.append("📊 SUMMARY")
        output.append("-" * 40)
        output.append(f"Total Files Analyzed: {report.total_files}")
        output.append(f"Total Lines of Code: {report.total_lines:,}")
        output.append(f"Total Issues Found: {report.statistics['total_issues']}")
        output.append("")
        
        # Issues by severity
        severity_counts = defaultdict(int)
        for issue in report.issues:
            severity_counts[issue.severity] += 1
        
        output.append("🚨 ISSUES BY SEVERITY")
        output.append("-" * 40)
        for severity in ['ERROR', 'WARNING', 'INFO']:
            count = severity_counts[severity]
            if count > 0:
                output.append(f"{severity}: {count}")
        output.append("")
        
        # Issues by type
        type_counts = defaultdict(int)
        for issue in report.issues:
            type_counts[issue.type] += 1
        
        output.append("📋 ISSUES BY TYPE")
        output.append("-" * 40)
        for issue_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            output.append(f"{issue_type}: {count}")
        output.append("")
        
        # Detailed issues
        if report.issues:
            output.append("🔍 DETAILED ISSUES")
            output.append("-" * 40)
            
            # Group by file
            issues_by_file = defaultdict(list)
            for issue in report.issues:
                issues_by_file[issue.file].append(issue)
            
            for file_path, file_issues in issues_by_file.items():
                output.append(f"\n📄 {file_path}")
                for issue in file_issues:
                    output.append(f"  Line {issue.line}: [{issue.severity}] {issue.type}")
                    output.append(f"    {issue.message}")
                    if issue.suggestion:
                        output.append(f"    💡 {issue.suggestion}")
                output.append("")
        
        # Recommendations
        output.append("💡 RECOMMENDATIONS")
        output.append("-" * 40)
        for i, rec in enumerate(report.recommendations, 1):
            output.append(f"{i}. {rec}")
        output.append("")
        
        # Code quality score
        total_issues = len(report.issues)
        error_count = severity_counts['ERROR']
        warning_count = severity_counts['WARNING']
        
        if total_issues == 0:
            score = 100
        else:
            score = max(0, 100 - (error_count * 10) - (warning_count * 5))
        
        output.append("📈 CODE QUALITY SCORE")
        output.append("-" * 40)
        output.append(f"Overall Score: {score}/100")
        
        if score >= 90:
            output.append("🌟 Excellent code quality!")
        elif score >= 80:
            output.append("👍 Good code quality with minor issues")
        elif score >= 70:
            output.append("⚠️ Fair code quality, needs improvement")
        else:
            output.append("🚨 Poor code quality, significant issues need attention")
        
        output.append("")
        output.append("=" * 80)
        
        return "\n".join(output)
    
    def save_report(self, report: AnalysisReport, output_file: str):
        """Save report to file"""
        report_text = self.generate_report(report)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        # Also save as JSON for programmatic access
        json_file = output_file.replace('.txt', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_files': report.total_files,
                    'total_lines': report.total_lines,
                    'total_issues': len(report.issues)
                },
                'issues': [
                    {
                        'file': issue.file,
                        'line': issue.line,
                        'type': issue.type,
                        'severity': issue.severity,
                        'message': issue.message,
                        'suggestion': issue.suggestion
                    }
                    for issue in report.issues
                ],
                'recommendations': report.recommendations
            }, indent=2)

def main():
    """Main function to run the analyzer"""
    analyzer = CodeAnalyzer(".")
    
    print("🚀 Starting PathForge Code Analysis...")
    print("This may take a few moments...")
    print()
    
    # Run analysis
    report = analyzer.analyze_all()
    
    # Generate and display report
    report_text = analyzer.generate_report(report)
    print(report_text)
    
    # Save report
    analyzer.save_report(report, "code_analysis_report.txt")
    print(f"\n💾 Report saved to: code_analysis_report.txt")
    print(f"💾 JSON report saved to: code_analysis_report.json")

if __name__ == "__main__":
    main()
