import os
import ast
from pathlib import Path
from typing import List, Dict
from crewai.tools import tool

@tool
def analyze_python_file(file_path: str) -> Dict:
    """Analyze a Python file and extract structure, functions, classes, and imports."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        analysis = {
            "file": file_path,
            "functions": [],
            "classes": [],
            "imports": [],
            "lines_of_code": len(content.split('\n')),
            "complexity_indicators": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis["functions"].append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, ast.ClassDef):
                analysis["classes"].append({
                    "name": node.name,
                    "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom):
                    analysis["imports"].append(f"from {node.module} import ...")
                else:
                    analysis["imports"].append(str(node.names))
        
        return analysis
    except Exception as e:
        return {"error": str(e), "file": file_path}


@tool
def get_file_dependencies(file_path: str) -> Dict:
    """Extract all imports and external dependencies from a Python file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        dependencies = {
            "internal": [],  # project imports
            "external": [],  # third-party
            "stdlib": []     # standard library
        }
        
        stdlib_modules = set(['os', 'sys', 'json', 'pathlib', 'typing', 'datetime', 
                             'collections', 'functools', 're', 'math', 'time'])
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith('.'):
                    dependencies["internal"].append(module)
                elif module.split('.')[0] in stdlib_modules:
                    dependencies["stdlib"].append(module)
                else:
                    dependencies["external"].append(module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split('.')[0]
                    if mod in stdlib_modules:
                        dependencies["stdlib"].append(alias.name)
                    else:
                        dependencies["external"].append(alias.name)
        
        return {
            "file": file_path,
            "dependencies": dependencies
        }
    except Exception as e:
        return {"error": str(e), "file": file_path}


@tool
def list_project_files(directory: str, extension: str = ".py") -> List[str]:
    """List only the root Python files and files in ai_development/src subdirectory."""
    files = []
    path = Path(directory)
    
    # Only include root .py files and ai_development/src files
    exclude_dirs = {'.venv', '__pycache__', 'node_modules', '.git', 'dist', 'build', '.pytest_cache', '.venv'}
    
    # Get root level python files
    for file in path.glob(f"*{extension}"):
        if file.is_file():
            files.append(str(file))
    
    # Get files from ai_development/src subdirectory only
    ai_dev_path = path / "ai_development" / "src"
    if ai_dev_path.exists():
        for file in ai_dev_path.rglob(f"*{extension}"):
            # Skip if in excluded directories
            if any(skip in file.parts for skip in exclude_dirs):
                continue
            files.append(str(file))
    
    return sorted(files)


@tool
def read_file_content(file_path: str) -> str:
    """Read and return the content of a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
