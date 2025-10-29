#!/usr/bin/env python3
"""
Test script for the enhanced Researcher agent with complex research task
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "agentflow"))
sys.path.insert(0, str(project_root))

from scripts.research_report_workflow import create_researcher_agent

# Complex research task
COMPLEX_RESEARCH_TASK = """
Research Topic: The Evolution and Future of Quantum Computing

Please conduct comprehensive research covering:

1. Historical Development (2010-2025)
   - Key breakthroughs and milestones
   - Major research institutions and companies involved
   - Evolution of qubit technologies (superconducting, trapped ion, topological)

2. Current State of Technology (2025)
   - Leading quantum computers and their qubit counts
   - Recent achievements in quantum error correction
   - Practical applications being tested or deployed
   - Performance comparisons (quantum advantage demonstrations)

3. Technical Challenges
   - Decoherence and error rates
   - Scalability issues
   - Temperature requirements and infrastructure costs
   - Integration with classical computing systems

4. Commercial Landscape
   - Major players (IBM, Google, Microsoft, Amazon, IonQ, Rigetti)
   - Investment trends and market size projections
   - Quantum-as-a-Service offerings
   - Strategic partnerships and collaborations

5. Future Outlook (2025-2030)
   - Predicted technological breakthroughs
   - Potential impact on cryptography and cybersecurity
   - Applications in drug discovery, materials science, optimization
   - Timeline predictions for quantum supremacy/advantage at scale

Please provide detailed findings with specific facts, numbers, and sources.
Compare different perspectives from industry, academia, and independent analysts.
"""


async def test_researcher_agent():
    """Test the researcher agent with a complex multi-faceted query"""
    
    print("=" * 80)
    print("🔬 TESTING ENHANCED RESEARCHER AGENT")
    print("=" * 80)
    print()
    print("📋 Complex Research Task:")
    print(COMPLEX_RESEARCH_TASK)
    print()
    print("=" * 80)
    print()
    
    # Verify environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    print("🔧 Environment Check:")
    print(f"✓ ANTHROPIC_API_KEY: {'Set' if api_key else '❌ NOT SET'}")
    print(f"✓ ANTHROPIC_BASE_URL: {base_url if base_url else '❌ NOT SET'}")
    print(f"✓ TAVILY_API_KEY: {'Set' if tavily_key else '❌ NOT SET'}")
    print()
    
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not set!")
        return
    
    # Create researcher agent
    print("🤖 Creating Enhanced Researcher Agent...")
    print("   Tools: Google_Search_Tool, Web_Search_Tool, Wikipedia_Search_Tool")
    print()
    
    researcher = create_researcher_agent()
    
    print("🚀 Starting Complex Research Task...")
    print("⏱️  This may take 2-5 minutes due to multiple search operations...")
    print()
    
    try:
        # Execute research
        result = await researcher.solve(query=COMPLEX_RESEARCH_TASK)
        
        print()
        print("=" * 80)
        print("✅ RESEARCH COMPLETED!")
        print("=" * 80)
        print()
        print("📊 Research Results:")
        print("-" * 80)
        print(result)
        print("-" * 80)
        print()
        
        # Save results to file
        output_file = "researcher_agent_results.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ENHANCED RESEARCHER AGENT - COMPLEX RESEARCH RESULTS\n")
            f.write("=" * 80 + "\n\n")
            f.write("Research Task:\n")
            f.write(COMPLEX_RESEARCH_TASK)
            f.write("\n\n" + "=" * 80 + "\n\n")
            f.write("Results:\n")
            f.write(result)
            f.write("\n\n" + "=" * 80 + "\n")
        
        print(f"💾 Results saved to: {output_file}")
        print()
        
        # Analysis
        result_length = len(result)
        word_count = len(result.split())
        
        print("📈 Analysis:")
        print(f"   - Total characters: {result_length:,}")
        print(f"   - Total words: {word_count:,}")
        print(f"   - Average words per character: {word_count/result_length:.2f}")
        print()
        
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERROR OCCURRED")
        print("=" * 80)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print()
        import traceback
        print("Traceback:")
        traceback.print_exc()


def main():
    """Main entry point"""
    # Set up environment if not already set
    if not os.getenv("ANTHROPIC_API_KEY"):
        # Try to load from .env file
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"').strip("'")
    
    # Run the test
    asyncio.run(test_researcher_agent())


if __name__ == "__main__":
    main()

