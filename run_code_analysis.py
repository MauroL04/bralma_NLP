#!/usr/bin/env python3
"""
Code Analysis Crew Runner
Analyzes the entire project structure with a multi-agent system
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add the ai_development package to the path
ai_dev_path = Path(__file__).parent / "ai_development" / "src"
sys.path.insert(0, str(ai_dev_path))

def main():
    """Run the code analysis crew"""
    try:
        from ai_development.crew import CodeAnalysisCrew
        
        project_path = str(Path(__file__).parent)
        inputs = {'project_path': project_path}
        
        print("\n" + "="*60)
        print("🚀 CODE ANALYSIS CREW - Multi-Agent System")
        print("="*60)
        print(f"📁 Analyzing: {project_path}")
        print("="*60 + "\n")
        
        crew = CodeAnalysisCrew()
        result = crew.crew().kickoff(inputs=inputs)
        
        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETE")
        print("="*60)
        print("📄 Output files generated:")
        print("   - codebase_documentation.md")
        print("   - project_analysis_report.md")
        print("="*60 + "\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
