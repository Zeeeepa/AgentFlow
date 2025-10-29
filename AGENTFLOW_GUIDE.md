# AgentFlow Customization Guide

## 🎯 Overview

AgentFlow is a multi-agent orchestration framework that uses specialized agents to plan, execute, and manage complex tasks. This guide explains how to customize AgentFlow for your needs.

## 📋 Architecture

```
User Query → Planner → Memory → Executor → Tools → Result
```

### Core Components

1. **Planner Agent** - Strategizes and plans task execution
2. **Executor Agent** - Executes specific tools and actions
3. **Memory System** - Maintains conversation context
4. **Tool System** - Extensible tool framework

## 🔧 Key Fixes for Z.AI Integration

The following fixes were made to enable AgentFlow to work with Z.AI:

### 1. Fixed Hardcoded Model References

**File**: `agentflow/agentflow/models/planner.py`
```python
# Before:
self.llm_engine_fixed = create_llm_engine(model_string="dashscope", ...)

# After:
self.llm_engine_fixed = create_llm_engine(model_string=llm_engine_name, ...)
```

**File**: `agentflow/agentflow/solver.py`
```python
# Before:
executor = Executor(llm_engine_name="dashscope", ...)

# After:
executor = Executor(llm_engine_name=llm_engine_name, base_url=base_url, ...)
```

### 2. Added Custom Base URL Support

**File**: `agentflow/agentflow/engine/anthropic.py`
```python
# Support custom base URLs (e.g., for Z.AI)
client_kwargs = {"api_key": os.getenv("ANTHROPIC_API_KEY")}
if os.getenv("ANTHROPIC_BASE_URL"):
    client_kwargs["base_url"] = os.getenv("ANTHROPIC_BASE_URL")

self.client = Anthropic(**client_kwargs)
```

### 3. Fixed Factory Initialization

**File**: `agentflow/agentflow/engine/factory.py`
```python
# Anthropic: temperature/top_p/top_k are passed to generate(), not __init__()
config = {
    "model_string": model_string,
    "use_cache": use_cache,
    "is_multimodal": is_multimodal,
}
return ChatAnthropic(**config)
```

## 🛠️ How to Add Custom Tools

### Step 1: Create Tool Directory

```bash
cd agentflow/agentflow/tools/
mkdir my_custom_tool
cd my_custom_tool
touch tool.py __init__.py
```

### Step 2: Implement Tool Class

Create `tool.py`:

```python
from agentflow.engine.factory import create_llm_engine
from typing import Dict, Any

class My_Custom_Tool:
    """
    Custom tool for specific task processing
    """
    
    def __init__(self, model_string: str = "claude-3-5-sonnet"):
        """
        Initialize the tool with specified model
        
        Args:
            model_string: Name of the LLM model to use
        """
        self.model_string = model_string
        self.llm_engine = create_llm_engine(
            model_string=self.model_string,
            is_multimodal=False,
            temperature=0.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
    
    def execute(self, query: str, **kwargs) -> str:
        """
        Execute the tool with given query
        
        Args:
            query: Input query to process
            **kwargs: Additional parameters
            
        Returns:
            str: Processed result
        """
        # Your custom logic here
        prompt = self._build_prompt(query)
        response = self.llm_engine.generate(prompt)
        return response
    
    def _build_prompt(self, query: str) -> str:
        """
        Build the prompt for the LLM
        
        Args:
            query: User query
            
        Returns:
            str: Formatted prompt
        """
        return f"""Process the following query:

Query: {query}

Provide a detailed response."""
    
    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """
        Return tool metadata for AgentFlow
        
        Returns:
            dict: Tool metadata
        """
        return {
            "tool_name": "My_Custom_Tool",
            "tool_description": "Processes specific types of queries with custom logic",
            "tool_version": "1.0.0",
            "input_types": {
                "query": "str - The input query to process"
            },
            "output_type": "str - The processed result",
            "demo_commands": [{
                "command": "tool.execute(query='Sample query')",
                "description": "Example usage of the custom tool"
            }],
            "user_metadata": {
                "limitation": "May not handle complex multi-step reasoning",
                "best_practice": "Use for specific domain tasks where custom logic is needed"
            },
            "require_llm_engine": True
        }
```

### Step 3: Register Tool in Workflow

```python
from agentflow.solver import construct_solver

# Create agent with custom tool
agent = construct_solver(
    llm_engine_name="claude-3-5-sonnet",
    enabled_tools=["My_Custom_Tool"],  # Add your tool here
    tool_engine=["self"],
    verbose=True
)

# Use the agent
result = await agent.solve(query="Your query here")
```

## 🤖 How to Define Specialized Agents

### Method 1: Functional Approach

```python
from agentflow.solver import construct_solver

def create_research_agent(model: str = "claude-3-5-sonnet"):
    """
    Agent specialized for research and information gathering
    """
    return construct_solver(
        llm_engine_name=model,
        enabled_tools=["Web_Search_Tool", "Wikipedia_Search_Tool"],
        tool_engine=["self"],
        verbose=False
    )

def create_coding_agent(model: str = "claude-3-5-sonnet"):
    """
    Agent specialized for code generation and analysis
    """
    return construct_solver(
        llm_engine_name=model,
        enabled_tools=["Python_Coder_Tool"],
        tool_engine=["self"],
        verbose=False
    )

def create_writer_agent(model: str = "claude-3-5-sonnet"):
    """
    Agent specialized for content creation
    """
    return construct_solver(
        llm_engine_name=model,
        enabled_tools=["Base_Generator_Tool"],
        tool_engine=["self"],
        verbose=False
    )
```

### Method 2: Configuration-Based Approach

Create `agents/config.py`:

```python
from agentflow.solver import construct_solver
from typing import Dict, Any

AGENT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "researcher": {
        "model": "claude-3-5-sonnet",
        "tools": ["Web_Search_Tool", "Wikipedia_Search_Tool"],
        "description": "Research and information gathering specialist",
        "verbose": False
    },
    "coder": {
        "model": "claude-3-5-sonnet",
        "tools": ["Python_Coder_Tool"],
        "description": "Code generation and analysis specialist",
        "verbose": False
    },
    "writer": {
        "model": "claude-3-5-sonnet",
        "tools": ["Base_Generator_Tool"],
        "description": "Content creation and summarization specialist",
        "verbose": False
    },
    "analyst": {
        "model": "claude-3-5-sonnet",
        "tools": ["Base_Generator_Tool", "Python_Coder_Tool"],
        "description": "Data analysis and insights specialist",
        "verbose": True
    }
}

def create_agent(agent_type: str, override_model: str = None):
    """
    Create an agent based on predefined configuration
    
    Args:
        agent_type: Type of agent to create (researcher, coder, writer, analyst)
        override_model: Optional model to use instead of default
        
    Returns:
        Configured agent instance
    """
    if agent_type not in AGENT_CONFIGS:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    config = AGENT_CONFIGS[agent_type]
    model = override_model or config["model"]
    
    return construct_solver(
        llm_engine_name=model,
        enabled_tools=config["tools"],
        tool_engine=["self"],
        verbose=config["verbose"]
    )

def list_agent_types():
    """List all available agent types"""
    return list(AGENT_CONFIGS.keys())

def get_agent_description(agent_type: str) -> str:
    """Get description of an agent type"""
    return AGENT_CONFIGS.get(agent_type, {}).get("description", "")
```

## 🔄 Multi-Agent Workflows

### Example: Sequential Workflow

```python
import asyncio
from typing import Dict, Any

async def sequential_workflow(topic: str) -> Dict[str, Any]:
    """
    Execute a sequential multi-agent workflow
    
    Args:
        topic: Research topic
        
    Returns:
        dict: Results from each agent
    """
    # Step 1: Research
    researcher = create_research_agent()
    research_results = await researcher.solve(
        query=f"Research comprehensive information about {topic}"
    )
    
    # Step 2: Analyze
    analyzer = create_agent("analyst")
    analysis = await analyzer.solve(
        query=f"Analyze this research and identify key insights: {research_results}"
    )
    
    # Step 3: Generate Report
    writer = create_writer_agent()
    report = await writer.solve(
        query=f"Write a comprehensive report based on: {analysis}"
    )
    
    return {
        "research": research_results,
        "analysis": analysis,
        "report": report
    }

# Execute workflow
results = asyncio.run(sequential_workflow("Quantum Computing"))
```

### Example: Parallel Workflow

```python
import asyncio
from typing import List, Dict, Any

async def parallel_workflow(topics: List[str]) -> List[Dict[str, Any]]:
    """
    Execute parallel research on multiple topics
    
    Args:
        topics: List of topics to research
        
    Returns:
        list: Results for each topic
    """
    # Create multiple researcher agents
    researchers = [create_research_agent() for _ in topics]
    
    # Execute research in parallel
    tasks = [
        agent.solve(query=f"Research about {topic}")
        for agent, topic in zip(researchers, topics)
    ]
    
    results = await asyncio.gather(*tasks)
    
    return [
        {"topic": topic, "research": result}
        for topic, result in zip(topics, results)
    ]

# Execute parallel workflow
topics = ["AI Safety", "Quantum Computing", "Climate Change"]
results = asyncio.run(parallel_workflow(topics))
```

### Example: Hierarchical Workflow

```python
async def hierarchical_workflow(main_query: str) -> Dict[str, Any]:
    """
    Execute hierarchical workflow with orchestrator
    
    Args:
        main_query: Main user query
        
    Returns:
        dict: Final synthesized result
    """
    # Orchestrator: Break down query
    planner = create_agent("researcher")
    sub_queries = await planner.solve(
        query=f"Break down this query into 3 specific sub-queries: {main_query}"
    )
    
    # Specialist agents: Handle sub-queries
    specialists = {
        "tech": create_agent("coder"),
        "analysis": create_agent("analyst"),
        "writing": create_agent("writer")
    }
    
    sub_results = {}
    for agent_type, agent in specialists.items():
        result = await agent.solve(
            query=f"Address your specialty for: {sub_queries}"
        )
        sub_results[agent_type] = result
    
    # Synthesizer: Combine results
    synthesizer = create_agent("writer")
    final_report = await synthesizer.solve(
        query=f"Synthesize these results into a cohesive answer: {sub_results}"
    )
    
    return {
        "original_query": main_query,
        "sub_queries": sub_queries,
        "specialist_results": sub_results,
        "final_report": final_report
    }

# Execute hierarchical workflow
result = asyncio.run(
    hierarchical_workflow("How can we build safe and beneficial AGI?")
)
```

## 🌐 Built-in Tools

AgentFlow provides several built-in tools:

| Tool Name | Description | Use Case |
|-----------|-------------|----------|
| `Wikipedia_Search_Tool` | Wikipedia RAG search | Factual information retrieval |
| `Google_Search_Tool` | Google web search | Current information |
| `Web_Search_Tool` | Web RAG search | Comprehensive web research |
| `Python_Coder_Tool` | Python code generation | Code creation and analysis |
| `Base_Generator_Tool` | General-purpose reasoning | General queries and reasoning |

### Using Built-in Tools

```python
# Single tool
agent = construct_solver(
    llm_engine_name="claude-3-5-sonnet",
    enabled_tools=["Web_Search_Tool"],
    tool_engine=["self"]
)

# Multiple tools
agent = construct_solver(
    llm_engine_name="claude-3-5-sonnet",
    enabled_tools=["Web_Search_Tool", "Wikipedia_Search_Tool", "Python_Coder_Tool"],
    tool_engine=["self"]
)
```

## 📦 Environment Configuration

### Required Environment Variables

Create `.env` file in the project root:

```bash
# Z.AI Configuration
ANTHROPIC_API_KEY="your-zai-api-key-here"
ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
ANTHROPIC_MODEL="glm-4.6"

# Optional: Search Tools
TAVILY_API_KEY="your-tavily-key"  # For web search tools

# Optional: Other LLM Providers
OPENAI_API_KEY="your-openai-key"  # If using OpenAI models
DASHSCOPE_API_KEY="your-dashscope-key"  # If using DashScope models
```

### Loading Environment Variables

```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Verify configuration
print(f"✅ API Key configured: {bool(os.getenv('ANTHROPIC_API_KEY'))}")
print(f"✅ Base URL: {os.getenv('ANTHROPIC_BASE_URL')}")
print(f"✅ Model: {os.getenv('ANTHROPIC_MODEL', 'glm-4.5V')}")
```

## 🚀 Quick Start Examples

### Example 1: Simple Query

```python
from agentflow.solver import construct_solver

# Create simple agent
agent = construct_solver(
    llm_engine_name="claude-3-5-sonnet",
    enabled_tools=["Base_Generator_Tool"],
    tool_engine=["self"]
)

# Execute query
result = await agent.solve(
    query="Explain quantum entanglement in simple terms"
)
print(result)
```

### Example 2: Research Agent

```python
# Create research-focused agent
researcher = construct_solver(
    llm_engine_name="claude-3-5-sonnet",
    enabled_tools=["Web_Search_Tool", "Wikipedia_Search_Tool"],
    tool_engine=["self"]
)

# Conduct research
research = await researcher.solve(
    query="What are the latest developments in AI safety?"
)
```

### Example 3: Coding Agent

```python
# Create coding agent
coder = construct_solver(
    llm_engine_name="claude-3-5-sonnet",
    enabled_tools=["Python_Coder_Tool"],
    tool_engine=["self"]
)

# Generate code
code = await coder.solve(
    query="Write a Python function to calculate Fibonacci numbers"
)
```

## 🔍 Debugging Tips

### Enable Verbose Mode

```python
agent = construct_solver(
    llm_engine_name="claude-3-5-sonnet",
    enabled_tools=["Base_Generator_Tool"],
    tool_engine=["self"],
    verbose=True  # Enable detailed logging
)
```

### Check Tool Availability

```python
from agentflow.models.initializer import Initializer

# Initialize and check tools
initializer = Initializer(
    llm_engine_name="claude-3-5-sonnet",
    enabled_tools=["Web_Search_Tool"],
    tool_engine=["self"]
)

print("Available tools:", initializer.get_available_tools())
```

## 📝 Best Practices

1. **Tool Selection**
   - Use specific tools for specialized tasks
   - Combine complementary tools for complex workflows
   - Start with simple tools before adding complexity

2. **Model Selection**
   - Use "claude-3-5-sonnet" for general tasks
   - Consider model capabilities vs. cost tradeoffs
   - Test with different models for optimal results

3. **Error Handling**
   - Always wrap agent calls in try-except blocks
   - Log errors for debugging
   - Implement retry logic for transient failures

4. **Performance**
   - Use parallel workflows when tasks are independent
   - Cache frequently used results
   - Optimize prompts to reduce token usage

## 🐛 Common Issues

### Issue: "No module named 'agentflow'"

**Solution**: Add project to Python path
```python
import sys
sys.path.insert(0, "/path/to/AgentFlow")
sys.path.insert(0, "/path/to/AgentFlow/agentflow")
```

### Issue: "ANTHROPIC_API_KEY not set"

**Solution**: Set environment variable
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Issue: Tools not loading

**Solution**: Check tool directory structure
```bash
agentflow/agentflow/tools/
├── my_tool/
│   ├── __init__.py
│   └── tool.py  # Must contain Tool class with get_metadata()
```

## 📚 Additional Resources

- [AgentFlow Repository](https://github.com/lupantech/AgentFlow)
- [Z.AI Documentation](https://api.z.ai/docs)
- [Anthropic API Reference](https://docs.anthropic.com/)

## 🤝 Contributing

When contributing custom tools:
1. Follow the tool template structure
2. Include comprehensive metadata
3. Add demo commands for testing
4. Document limitations and best practices
5. Test with multiple models

---

**Last Updated**: 2025-10-16  
**Version**: 2.0  
**Maintained by**: AgentFlow Community

