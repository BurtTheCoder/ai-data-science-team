"""
Base Agent Class for Anthropic Agent SDK Implementation

This module provides the foundational BaseAgentSDK class that all agents
in the ai-data-science-team project will inherit from.
"""

from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import pandas as pd
from claude_agent_sdk import query, ClaudeAgentOptions
from abc import ABC, abstractmethod


class BaseAgentSDK(ABC):
    """
    Base class for all Agent SDK-based agents.
    
    This class provides common functionality for:
    - Working directory management
    - Agent configuration
    - Data I/O operations
    - Response tracking
    - Logging
    
    All agents should inherit from this class and implement the
    required abstract methods.
    """
    
    def __init__(
        self,
        working_dir: Optional[str] = None,
        max_turns: int = 10,
        allowed_tools: Optional[List[str]] = None,
        permission_mode: str = "acceptEdits",
        verbose: bool = True,
        log: bool = False,
        log_path: Optional[str] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            working_dir: Directory for agent operations. Defaults to temp directory.
            max_turns: Maximum number of agent turns before stopping.
            allowed_tools: List of tools the agent can use. Defaults to common tools.
            permission_mode: Permission mode for file operations.
            verbose: Whether to print progress messages.
            log: Whether to log agent operations.
            log_path: Path for log files.
        """
        self.working_dir = Path(working_dir) if working_dir else Path(f"/tmp/{self.__class__.__name__}")
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_turns = max_turns
        self.verbose = verbose
        self.log = log
        self.log_path = Path(log_path) if log_path else self.working_dir / "logs"
        
        if self.log:
            self.log_path.mkdir(parents=True, exist_ok=True)
        
        # Default tools for data science agents
        if allowed_tools is None:
            allowed_tools = [
                "Bash",      # Execute Python/pandas code
                "Read",      # Read files
                "Write",     # Create files
                "Edit",      # Edit files
                "Glob",      # Find files
                "Grep"       # Search content
            ]
        
        self.allowed_tools = allowed_tools
        self.permission_mode = permission_mode
        
        # Response tracking
        self.response = None
        self.messages = []
        
    def _get_base_options(self, system_prompt: Optional[str] = None) -> ClaudeAgentOptions:
        """
        Get base ClaudeAgentOptions with common settings.
        
        Args:
            system_prompt: Custom system prompt for this invocation.
            
        Returns:
            Configured ClaudeAgentOptions instance.
        """
        return ClaudeAgentOptions(
            system_prompt=system_prompt or self._get_default_system_prompt(),
            cwd=str(self.working_dir),
            allowed_tools=self.allowed_tools,
            max_turns=self.max_turns,
            permission_mode=self.permission_mode
        )
    
    @abstractmethod
    def _get_default_system_prompt(self) -> str:
        """
        Get the default system prompt for this agent.
        
        Each agent should implement this to define its role and capabilities.
        
        Returns:
            System prompt string.
        """
        pass
    
    def _save_dataframe(self, df: pd.DataFrame, filename: str) -> Path:
        """
        Save a DataFrame to the working directory.
        
        Args:
            df: DataFrame to save.
            filename: Name of the CSV file.
            
        Returns:
            Path to the saved file.
        """
        filepath = self.working_dir / filename
        df.to_csv(filepath, index=False)
        
        if self.verbose:
            print(f"💾 Saved DataFrame to {filepath}")
            print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        
        return filepath
    
    def _load_dataframe(self, filename: str) -> Optional[pd.DataFrame]:
        """
        Load a DataFrame from the working directory.
        
        Args:
            filename: Name of the CSV file.
            
        Returns:
            Loaded DataFrame or None if file doesn't exist.
        """
        filepath = self.working_dir / filename
        
        if not filepath.exists():
            if self.verbose:
                print(f"⚠️  File not found: {filepath}")
            return None
        
        df = pd.read_csv(filepath)
        
        if self.verbose:
            print(f"📂 Loaded DataFrame from {filepath}")
            print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        
        return df
    
    def _log_message(self, message: str, level: str = "INFO"):
        """
        Log a message to file if logging is enabled.
        
        Args:
            message: Message to log.
            level: Log level (INFO, WARNING, ERROR).
        """
        if self.log:
            log_file = self.log_path / f"{self.__class__.__name__}.log"
            with open(log_file, "a") as f:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] [{level}] {message}\n")
    
    async def _execute_query(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[ClaudeAgentOptions] = None
    ) -> List[Any]:
        """
        Execute a query using the Agent SDK.
        
        Args:
            prompt: User prompt for the agent.
            system_prompt: Optional custom system prompt.
            options: Optional custom ClaudeAgentOptions.
            
        Returns:
            List of messages from the agent.
        """
        if options is None:
            options = self._get_base_options(system_prompt)
        
        messages = []
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"🤖 {self.__class__.__name__}")
            print(f"{'='*70}\n")
        
        async for message in query(prompt=prompt, options=options):
            messages.append(message)
            
            if self.verbose:
                self._print_message(message)
        
        self.messages = messages
        
        if self.verbose:
            print(f"\n{'='*70}\n")
        
        return messages
    
    def _print_message(self, message: Any):
        """
        Print a message in a user-friendly format.
        
        Args:
            message: Message object from the agent.
        """
        if not hasattr(message, 'type'):
            return
        
        if message.type == "assistant" and hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'type') and block.type == "text":
                    text = block.text
                    # Truncate long messages
                    if len(text) > 200:
                        print(f"💭 {text[:200]}...")
                    else:
                        print(f"💭 {text}")
        
        elif message.type == "result":
            status = getattr(message, 'subtype', 'unknown')
            if status == "success":
                print(f"✅ Completed successfully")
            elif status == "error":
                print(f"❌ Error occurred")
            else:
                print(f"ℹ️  Status: {status}")
    
    def get_response(self) -> Optional[Dict[str, Any]]:
        """
        Get the last response from the agent.
        
        Returns:
            Response dictionary or None.
        """
        return self.response
    
    def get_messages(self) -> List[Any]:
        """
        Get all messages from the last agent execution.
        
        Returns:
            List of message objects.
        """
        return self.messages
