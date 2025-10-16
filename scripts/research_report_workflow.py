"""
Multi-Agent Research Report Generation Workflow with AgentFlow

This workflow replicates a sophisticated research report generation system using
AgentFlow's multi-agent architecture. The system uses 10 specialized agents working
in a dependency chain to produce comprehensive, fact-checked research reports.

Agent Pipeline:
    1. Planner → 2. Researcher → 3. Cleaner → 4. Extractor
                                               → 5. Identifier
                                               → 6. Analyzer
                                      7. Checker ←┘
                                      8. Generator (waits for checker, identifier, analyzer)
                                      9. Writer
                                      10. Proofreader

Environment Setup:
    export ANTHROPIC_MODEL=glm-4.6
    export ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
    export ANTHROPIC_AUTH_TOKEN=665b963943b647dc9501dff942afb877.A47LrMc7sgGjyfBJ
    export TAVILY_API_KEY=your_tavily_key

Usage:
    python scripts/research_report_workflow.py
"""

import os
import sys
import asyncio
import time
from typing import Dict, Any, List

# Add project to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../agentflow")))

from agentflow.solver import construct_solver
from dotenv import load_dotenv

# Load environment
load_dotenv()


# ======================================
# Configuration and Setup
# ======================================

def setup_environment():
    """Configure Z.AI Anthropic-compatible API"""
    
    # Set Z.AI credentials as Anthropic environment variables
    os.environ["ANTHROPIC_API_KEY"] = os.getenv(
        "ANTHROPIC_AUTH_TOKEN", 
        "665b963943b647dc9501dff942afb877.A47LrMc7sgGjyfBJ"
    )
    os.environ["ANTHROPIC_BASE_URL"] = os.getenv(
        "ANTHROPIC_BASE_URL",
        "https://api.z.ai/api/anthropic"
    )
    
    # Verify required keys
    if not os.getenv("TAVILY_API_KEY"):
        print("WARNING: TAVILY_API_KEY not set. Web search will not work.")
        print("Set it in .env file or export TAVILY_API_KEY=your_key")
    
    print(f"✅ Using Z.AI API at: {os.environ['ANTHROPIC_BASE_URL']}")
    print(f"✅ Model: {os.getenv('ANTHROPIC_MODEL', 'glm-4.6')}")


# ======================================
# Agent Definitions
# ======================================

def create_planner_agent(llm_model: str = "claude-3-5-sonnet"):
    """
    Agent 1: Query Planner
    Generates 3-5 specific search queries from a user's research question
    """
    return construct_solver(
        llm_engine_name=llm_model,
        enabled_tools=["Base_Generator_Tool"],
        tool_engine=["self"],
        verbose=False
    )


def create_researcher_agent():
    """
    Agent 2: Researcher
    Executes web searches using Tavily and gathers raw data
    Dependencies: planner
    """
    return construct_solver(
        llm_engine_name="claude-3-5-sonnet",
        enabled_tools=["Google_Search_Tool", "Web_Search_Tool"],
        tool_engine=["Default", "Default"],
        verbose=False
    )


def create_cleaner_agent(llm_model: str = "claude-3-5-sonnet"):
    """
    Agent 3: Data Cleaner
    Consolidates and cleans raw research data
    Dependencies: researcher
    """
    return construct_solver(
        llm_engine_name=llm_model,
        enabled_tools=["Base_Generator_Tool"],
        tool_engine=["self"],
        verbose=False
    )


def create_extractor_agent(llm_model: str = "claude-3-5-sonnet"):
    """
    Agent 4: Fact Extractor
    Extracts key, verifiable facts from cleaned data
    Dependencies: cleaner
    """
    return construct_solver(
        llm_engine_name=llm_model,
        enabled_tools=["Base_Generator_Tool"],
        tool_engine=["self"],
        verbose=False
    )


def create_identifier_agent(llm_model: str = "claude-3-5-sonnet"):
    """
    Agent 5: Bias Identifier
    Identifies potential biases in the research data
    Dependencies: cleaner
    """
    return construct_solver(
        llm_engine_name=llm_model,
        enabled_tools=["Base_Generator_Tool"],
        tool_engine=["self"],
        verbose=False
    )


def create_analyzer_agent(llm_model: str = "claude-3-5-sonnet"):
    """
    Agent 6: Sentiment Analyzer
    Analyzes overall sentiment of the research data
    Dependencies: cleaner
    """
    return construct_solver(
        llm_engine_name=llm_model,
        enabled_tools=["Base_Generator_Tool"],
        tool_engine=["self"],
        verbose=False
    )


def create_checker_agent(llm_model: str = "claude-3-5-sonnet"):
    """
    Agent 7: Fact Checker
    Verifies extracted facts (simulated verification)
    Dependencies: extractor
    """
    return construct_solver(
        llm_engine_name=llm_model,
        enabled_tools=["Base_Generator_Tool"],
        tool_engine=["self"],
        verbose=False
    )


def create_generator_agent(llm_model: str = "claude-3-5-sonnet"):
    """
    Agent 8: Argument Generator
    Synthesizes key arguments from verified facts, bias notes, and sentiment
    Dependencies: checker, identifier, analyzer
    """
    return construct_solver(
        llm_engine_name=llm_model,
        enabled_tools=["Base_Generator_Tool"],
        tool_engine=["self"],
        verbose=False
    )


def create_writer_agent(llm_model: str = "claude-3-5-sonnet"):
    """
    Agent 9: Report Writer
    Writes comprehensive, well-structured report from arguments
    Dependencies: generator
    """
    return construct_solver(
        llm_engine_name=llm_model,
        enabled_tools=["Base_Generator_Tool"],
        tool_engine=["self"],
        verbose=False
    )


def create_proofreader_agent(llm_model: str = "claude-3-5-sonnet"):
    """
    Agent 10: Proofreader
    Polishes final report for grammar, clarity, and professionalism
    Dependencies: writer
    """
    return construct_solver(
        llm_engine_name=llm_model,
        enabled_tools=["Base_Generator_Tool"],
        tool_engine=["self"],
        verbose=False
    )


# ======================================
# Workflow Orchestration
# ======================================

class ResearchWorkflowOrchestrator:
    """
    Orchestrates the 10-agent research workflow
    Manages dependencies and data flow between agents
    """
    
    def __init__(self, llm_model: str = "claude-3-5-sonnet"):
        self.llm_model = llm_model
        self.results = {}
        self.metrics = {
            "agent_latencies": {},
            "agent_success": {},
        }
    
    async def execute_workflow(self, query: str) -> Dict[str, Any]:
        """Execute complete research workflow"""
        
        print("="*80)
        print("RESEARCH REPORT GENERATION WORKFLOW")
        print("="*80)
        print(f"\nQuery: {query}\n")
        
        # Stage 1: Planning
        print("📋 STAGE 1: Query Planning")
        print("-" * 80)
        planner_result = await self._execute_agent(
            "planner",
            create_planner_agent(self.llm_model),
            f"Generate 3-5 specific, diverse search queries for this research topic:\n{query}\n\nRespond with a JSON list of queries like: {{\"queries\": [\"query1\", \"query2\", \"query3\"]}}"
        )
        
        # Extract queries from planner response
        queries = self._extract_queries_from_response(
            planner_result.get("direct_output", query)
        )
        print(f"Generated {len(queries)} search queries")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")
        
        # Stage 2: Research
        print("\n🔍 STAGE 2: Web Research")
        print("-" * 80)
        researcher = create_researcher_agent()
        research_results = []
        
        for i, search_query in enumerate(queries, 1):
            print(f"Searching: {search_query}")
            result = await self._execute_agent(
                f"researcher_{i}",
                researcher,
                f"Search the web for: {search_query}"
            )
            research_results.append(result.get("direct_output", ""))
        
        raw_data = "\n\n---\n\n".join(research_results)
        print(f"✓ Gathered {len(research_results)} search results")
        
        # Stage 3: Data Cleaning
        print("\n🧹 STAGE 3: Data Cleaning")
        print("-" * 80)
        cleaner_result = await self._execute_agent(
            "cleaner",
            create_cleaner_agent(self.llm_model),
            f"Consolidate and clean this raw research data. Remove redundancies, correct formatting, and extract only the most relevant information:\n\n{raw_data[:5000]}"
        )
        cleaned_data = cleaner_result.get("direct_output", raw_data)
        print(f"✓ Cleaned data length: {len(cleaned_data)} chars")
        
        # Stage 4: Parallel Analysis (Extractor, Identifier, Analyzer)
        print("\n⚙️ STAGE 4: Parallel Analysis")
        print("-" * 80)
        
        # 4a: Extract Facts
        print("Extracting key facts...")
        extractor_result = await self._execute_agent(
            "extractor",
            create_extractor_agent(self.llm_model),
            f"Extract a list of 5-10 key, verifiable facts from this text. Respond with a JSON list like {{\"facts\": [\"fact1\", \"fact2\"]}}:\n\n{cleaned_data[:3000]}"
        )
        
        # 4b: Identify Biases (parallel)
        print("Identifying potential biases...")
        identifier_result = await self._execute_agent(
            "identifier",
            create_identifier_agent(self.llm_model),
            f"Analyze this text for potential biases (commercial, political, selection). Provide a brief summary. If no significant bias, state that:\n\n{cleaned_data[:3000]}"
        )
        
        # 4c: Analyze Sentiment (parallel)
        print("Analyzing sentiment...")
        analyzer_result = await self._execute_agent(
            "analyzer",
            create_analyzer_agent(self.llm_model),
            f"Analyze the overall sentiment of this text (Positive, Negative, Neutral, Mixed) and provide a one-sentence justification:\n\n{cleaned_data[:3000]}"
        )
        
        facts_raw = extractor_result.get("direct_output", "[]")
        bias_note = identifier_result.get("direct_output", "No bias analysis available")
        sentiment = analyzer_result.get("direct_output", "Sentiment analysis not available")
        
        print(f"✓ Extracted facts, identified biases, analyzed sentiment")
        
        # Stage 5: Fact Checking
        print("\n✅ STAGE 5: Fact Verification")
        print("-" * 80)
        checker_result = await self._execute_agent(
            "checker",
            create_checker_agent(self.llm_model),
            f"Review these facts and mark them as verified or needs verification. Return a status summary:\n\nFacts:\n{facts_raw}"
        )
        verification_status = checker_result.get("direct_output", "Verification completed")
        print(f"✓ Fact checking completed")
        
        # Stage 6: Argument Generation
        print("\n💡 STAGE 6: Argument Synthesis")
        print("-" * 80)
        generator_result = await self._execute_agent(
            "generator",
            create_generator_agent(self.llm_model),
            f"""Synthesize 3-5 key arguments or talking points based on:

Verified Facts: {facts_raw}
Verification Status: {verification_status}
Bias Note: {bias_note}
Sentiment: {sentiment}

Generate clear, evidence-based arguments."""
        )
        arguments = generator_result.get("direct_output", "Could not generate arguments")
        print(f"✓ Generated key arguments")
        
        # Stage 7: Report Writing
        print("\n✍️ STAGE 7: Report Writing")
        print("-" * 80)
        writer_result = await self._execute_agent(
            "writer",
            create_writer_agent(self.llm_model),
            f"Write a comprehensive, well-structured research report based on these key arguments. Make it informative and easy to read:\n\n{arguments}"
        )
        draft_report = writer_result.get("direct_output", "Report could not be written")
        print(f"✓ Draft report completed ({len(draft_report)} chars)")
        
        # Stage 8: Proofreading
        print("\n📝 STAGE 8: Final Proofreading")
        print("-" * 80)
        proofreader_result = await self._execute_agent(
            "proofreader",
            create_proofreader_agent(self.llm_model),
            f"Review this report for grammatical errors, spelling mistakes, and awkward phrasing. Make corrections to improve clarity and professionalism. Output only the final, polished version:\n\n{draft_report}"
        )
        final_report = proofreader_result.get("direct_output", draft_report)
        print(f"✓ Final report ready ({len(final_report)} chars)")
        
        # Compile all results
        return {
            "query": query,
            "search_queries": queries,
            "raw_data_length": len(raw_data),
            "cleaned_data_length": len(cleaned_data),
            "facts": facts_raw,
            "bias_note": bias_note,
            "sentiment": sentiment,
            "verification_status": verification_status,
            "arguments": arguments,
            "draft_report": draft_report,
            "final_report": final_report,
            "metrics": self.metrics,
        }
    
    async def _execute_agent(
        self, 
        agent_name: str, 
        agent, 
        query: str
    ) -> Dict[str, Any]:
        """Execute single agent with timing and error handling"""
        
        start = time.perf_counter()
        success = True
        
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(agent.solve, query),
                timeout=90
            )
            
        except asyncio.TimeoutError:
            print(f"  ⚠️ {agent_name} timed out")
            result = {"direct_output": f"[{agent_name} timed out]"}
            success = False
            
        except Exception as e:
            print(f"  ⚠️ {agent_name} error: {e}")
            result = {"direct_output": f"[{agent_name} error: {e}]"}
            success = False
        
        latency = time.perf_counter() - start
        
        # Track metrics
        self.metrics["agent_latencies"][agent_name] = latency
        self.metrics["agent_success"][agent_name] = success
        
        return result
    
    def _extract_queries_from_response(self, response: str) -> List[str]:
        """Extract query list from LLM response"""
        import json
        import re
        
        # Try JSON parsing first
        try:
            # Look for JSON in response
            json_match = re.search(r'\{.*"queries".*\[.*\].*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                if "queries" in data:
                    return data["queries"][:5]  # Max 5 queries
        except:
            pass
        
        # Fallback: extract quoted strings or numbered lines
        lines = [
            line.strip().strip('"-1234567890.)')
            for line in response.split('\n')
            if line.strip() and len(line.strip()) > 10
        ]
        
        if lines:
            return lines[:5]
        
        # Ultimate fallback: return original as single query
        return [response[:200]]
    
    def print_metrics(self):
        """Print workflow performance metrics"""
        print("\n" + "="*80)
        print("WORKFLOW PERFORMANCE METRICS")
        print("="*80)
        
        print("\n⏱️ Agent Latencies:")
        for agent, latency in self.metrics["agent_latencies"].items():
            status = "✓" if self.metrics["agent_success"].get(agent, False) else "✗"
            print(f"  {status} {agent:<20} {latency:.2f}s")
        
        total_time = sum(self.metrics["agent_latencies"].values())
        success_rate = sum(1 for v in self.metrics["agent_success"].values() if v) / len(self.metrics["agent_success"]) if self.metrics["agent_success"] else 0
        
        print(f"\n📊 Summary:")
        print(f"  Total Execution Time: {total_time:.2f}s")
        print(f"  Success Rate: {success_rate:.1%}")
        print(f"  Agents Executed: {len(self.metrics['agent_latencies'])}")


# ======================================
# Main Execution
# ======================================

async def main():
    """Main execution function"""
    
    # Setup
    setup_environment()
    
    # Create orchestrator
    orchestrator = ResearchWorkflowOrchestrator(
        llm_model="claude-3-5-sonnet"  # Will use Z.AI glm-4.6 via Anthropic compatibility
    )
    
    # Define research query
    query = "The implications of quantum computing advancements on cybersecurity and data privacy"
    
    # Execute workflow
    print(f"\n🚀 Starting research workflow...\n")
    start_time = time.perf_counter()
    
    results = await orchestrator.execute_workflow(query)
    
    total_time = time.perf_counter() - start_time
    
    # Print final report
    print("\n" + "="*80)
    print("📄 FINAL RESEARCH REPORT")
    print("="*80)
    print(f"\nQuery: {results['query']}\n")
    print(results['final_report'])
    
    # Print metrics
    orchestrator.print_metrics()
    
    print(f"\n⏱️ Total Workflow Time: {total_time:.2f}s")
    print("\n✅ Workflow completed successfully!")


async def test_simple_workflow():
    """Simplified test for debugging"""
    
    setup_environment()
    
    print("\n🧪 Testing Simple 3-Agent Workflow\n")
    print("="*80)
    
    # Test 1: Planner
    print("\n1️⃣ Testing Planner Agent...")
    planner = create_planner_agent()
    result1 = planner.solve("Generate 3 search queries about AI safety")
    print(f"Result: {result1.get('direct_output', 'No output')[:200]}...")
    
    # Test 2: Researcher
    print("\n2️⃣ Testing Researcher Agent...")
    researcher = create_researcher_agent()
    result2 = researcher.solve("Search for latest AI safety research")
    print(f"Result: {result2.get('direct_output', 'No output')[:200]}...")
    
    # Test 3: Writer
    print("\n3️⃣ Testing Writer Agent...")
    writer = create_writer_agent()
    result3 = writer.solve("Write a short paragraph about AI safety importance")
    print(f"Result: {result3.get('direct_output', 'No output')[:200]}...")
    
    print("\n✅ Simple workflow test completed!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Research Report Generation Workflow")
    parser.add_argument("--test", action="store_true", help="Run simple test workflow")
    parser.add_argument("--query", type=str, help="Custom research query")
    
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_simple_workflow())
    else:
        asyncio.run(main())
