#!/usr/bin/env python3
"""
Simple test for Researcher agent - demonstrates it works even without search tools
Shows the agent's reasoning and planning capabilities
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "agentflow"))
sys.path.insert(0, str(project_root))

from agentflow.solver import construct_solver

# Complex research task
RESEARCH_TASK = """
Research Task: Analyze the future of quantum computing

Please provide a structured analysis covering:

1. What are the key technological breakthroughs needed for practical quantum computers?
2. What industries will be most impacted by quantum computing?
3. What are the main challenges preventing widespread adoption?
4. What timeline predictions exist for quantum advantage at scale?
5. How will quantum computing impact cryptography and cybersecurity?

Provide a well-structured, comprehensive analysis with logical reasoning.
"""


async def test_researcher():
    """Test the researcher agent"""
    
    print("=" * 80)
    print("🔬 TESTING RESEARCHER AGENT")
    print("=" * 80)
    print()
    
    # Verify environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.z.ai/api/anthropic")
    
    print("🔧 Configuration:")
    print(f"   API Key: {'✓ Set' if api_key else '❌ NOT SET'}")
    print(f"   Base URL: {base_url}")
    print()
    
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not set!")
        return
    
    print("📋 Research Task:")
    print(RESEARCH_TASK)
    print()
    print("=" * 80)
    print()
    
    # Create simple researcher agent (without search tools for this demo)
    print("🤖 Creating Researcher Agent...")
    print("   Note: Using Base_Generator for reasoning (search tools require OpenAI API)")
    print()
    
    researcher = construct_solver(
        llm_engine_name="claude-3-5-sonnet",
        enabled_tools=["Base_Generator_Tool"],
        tool_engine=["self"],
        verbose=False
    )
    
    print("🚀 Starting Research Task...")
    print()
    
    try:
        # Execute research using correct parameter name
        result = researcher.solve(question=RESEARCH_TASK)
        
        print()
        print("=" * 80)
        print("✅ RESEARCH COMPLETED!")
        print("=" * 80)
        print()
        print("📊 Analysis Results:")
        print("-" * 80)
        print(result)
        print("-" * 80)
        print()
        
        # Save results
        output_file = "researcher_results.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("RESEARCHER AGENT - ANALYSIS RESULTS\n")
            f.write("=" * 80 + "\n\n")
            f.write("Task:\n")
            f.write(RESEARCH_TASK)
            f.write("\n\n" + "=" * 80 + "\n\n")
            f.write("Results:\n")
            f.write(result)
        
        print(f"💾 Results saved to: {output_file}")
        print()
        
        # Stats
        result_str = str(result)
        word_count = len(result_str.split())
        
        print("📈 Statistics:")
        print(f"   - Characters: {len(result_str):,}")
        print(f"   - Words: {word_count:,}")
        print()
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERROR")
        print("=" * 80)
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print()
        import traceback
        traceback.print_exc()


def main():
    """Main entry point"""
    # Load env if available
    env_file = Path(__file__).parent / ".env"
    if env_file.exists() and not os.getenv("ANTHROPIC_API_KEY"):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")
    
    asyncio.run(test_researcher())


if __name__ == "__main__":
    main()

