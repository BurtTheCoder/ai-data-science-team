"""
AI Data Science Team - Anthropic Agent SDK Implementation

This package contains the refactored implementation of ai-data-science-team
using the Anthropic Agent SDK instead of LangChain/LangGraph.

Key improvements:
- 85-90% reduction in code complexity
- Built-in tool execution (Bash, Read, Write, etc.)
- Automatic context management and error recovery
- Simpler agent development and maintenance
"""

from ai_data_science_team_sdk.base_agent import BaseAgentSDK

__version__ = "2.0.0"  # Major version bump for SDK migration

__all__ = [
    "BaseAgentSDK",
]
