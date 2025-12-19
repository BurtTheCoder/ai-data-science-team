"""
Data Wrangling Agent - Agent SDK Implementation

Simplified implementation using Anthropic Agent SDK.
Replaces ~1038 lines of LangGraph code with ~150 lines.
"""

from typing import Optional, Union
import pandas as pd
from pathlib import Path

from ai_data_science_team.base_agent import BaseAgentSDK


class DataWranglingAgent(BaseAgentSDK):
    """
    Data Wrangling Agent for transforming and preparing data.
    
    This agent can:
    - Merge and join multiple datasets
    - Reshape data (pivot, melt, etc.)
    - Perform aggregations and groupby operations
    - Encode categorical variables
    - Create computed features
    - Handle data type conversions
    
    Example:
        ```python
        import pandas as pd
        from ai_data_science_team.agents import DataWranglingAgent
        
        df = pd.read_csv("data.csv")
        
        agent = DataWranglingAgent(
            working_dir="/tmp/wrangling",
            verbose=True
        )
        
        result = await agent.wrangle_data(
            data_raw=df,
            user_instructions="Group by 'category' and calculate mean of 'sales'"
        )
        
        wrangled_df = agent.get_data_wrangled()
        ```
    """
    
    def __init__(
        self,
        working_dir: Optional[str] = None,
        max_turns: int = 10,
        verbose: bool = True,
        log: bool = False,
        log_path: Optional[str] = None
    ):
        """
        Initialize the Data Wrangling Agent.
        
        Args:
            working_dir: Directory for agent operations.
            max_turns: Maximum number of agent turns.
            verbose: Whether to print progress messages.
            log: Whether to log operations.
            log_path: Path for log files.
        """
        super().__init__(
            working_dir=working_dir or "/tmp/data_wrangling_agent",
            max_turns=max_turns,
            verbose=verbose,
            log=log,
            log_path=log_path
        )
        
        self.data_raw = None
        self.data_wrangled = None
    
    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for data wrangling."""
        return f"""You are an expert data wrangling agent specializing in pandas data transformations.

Your role is to transform raw data according to user instructions using Python and pandas.

Working Directory: {self.working_dir}

Available Tools:
- Bash: Execute Python/pandas code for data transformations
- Read: Read CSV files and examine data
- Write: Save transformed data to CSV files
- Edit: Modify existing files if needed

Process:
1. Read the input data file (input_data.csv)
2. Analyze the data structure and content
3. Write Python code to perform the requested transformations
4. Execute the code using the Bash tool
5. Verify the output and save to output_data.csv
6. Report what transformations were applied

Best Practices:
- Always import pandas as pd at the start of your code
- Use descriptive variable names
- Handle missing values appropriately
- Verify data types after transformations
- Include error handling in your code
- Save the final result to output_data.csv

Be precise, handle edge cases, and ensure data integrity throughout the transformation."""
    
    async def wrangle_data(
        self,
        data_raw: Union[pd.DataFrame, dict, list],
        user_instructions: str,
        input_filename: str = "input_data.csv",
        output_filename: str = "output_data.csv"
    ) -> dict:
        """
        Wrangle data according to user instructions.
        
        Args:
            data_raw: Input data (DataFrame, dict, or list of dicts).
            user_instructions: Natural language instructions for wrangling.
            input_filename: Name for the input CSV file.
            output_filename: Name for the output CSV file.
            
        Returns:
            Dictionary containing:
                - data_wrangled: Transformed DataFrame
                - data_raw: Original DataFrame
                - success: Whether wrangling succeeded
                - messages: Agent messages
        """
        # Convert input to DataFrame if needed
        if isinstance(data_raw, dict):
            df_input = pd.DataFrame(data_raw)
        elif isinstance(data_raw, list):
            df_input = pd.DataFrame(data_raw[0]) if len(data_raw) > 0 else pd.DataFrame()
        else:
            df_input = data_raw
        
        self.data_raw = df_input
        
        # Save input data
        input_path = self._save_dataframe(df_input, input_filename)
        
        # Build the prompt
        prompt = f"""Transform the data in {input_filename} according to these instructions:

{user_instructions}

Input Data Summary:
- Shape: {df_input.shape[0]} rows × {df_input.shape[1]} columns
- Columns: {list(df_input.columns)}
- Data types: {df_input.dtypes.to_dict()}

First few rows:
{df_input.head().to_string()}

Save the transformed data to {output_filename}."""
        
        # Execute the agent
        if self.verbose:
            print(f"📊 Input: {df_input.shape[0]} rows × {df_input.shape[1]} columns")
            print(f"📝 Task: {user_instructions}\n")
        
        await self._execute_query(prompt)
        
        # Load the output
        df_output = self._load_dataframe(output_filename)
        
        if df_output is not None:
            self.data_wrangled = df_output
            
            if self.verbose:
                print(f"📊 Output: {df_output.shape[0]} rows × {df_output.shape[1]} columns")
            
            self.response = {
                "data_wrangled": df_output,
                "data_raw": df_input,
                "success": True,
                "messages": self.messages,
                "input_path": str(input_path),
                "output_path": str(self.working_dir / output_filename)
            }
        else:
            if self.verbose:
                print("⚠️  No output file generated")
            
            self.response = {
                "data_wrangled": None,
                "data_raw": df_input,
                "success": False,
                "messages": self.messages,
                "input_path": str(input_path),
                "output_path": None
            }
        
        return self.response
    
    def get_data_wrangled(self) -> Optional[pd.DataFrame]:
        """
        Get the wrangled DataFrame.
        
        Returns:
            Transformed DataFrame or None if wrangling failed.
        """
        return self.data_wrangled
    
    def get_data_raw(self) -> Optional[pd.DataFrame]:
        """
        Get the raw input DataFrame.
        
        Returns:
            Original DataFrame.
        """
        return self.data_raw
    
    def get_wrangling_summary(self) -> str:
        """
        Get a summary of the wrangling operation.
        
        Returns:
            Markdown-formatted summary string.
        """
        if not self.response:
            return "No wrangling operation has been performed yet."
        
        summary = "# Data Wrangling Summary\n\n"
        
        if self.data_raw is not None:
            summary += f"## Input Data\n"
            summary += f"- Shape: {self.data_raw.shape[0]} rows × {self.data_raw.shape[1]} columns\n"
            summary += f"- Columns: {', '.join(self.data_raw.columns)}\n\n"
        
        if self.data_wrangled is not None:
            summary += f"## Output Data\n"
            summary += f"- Shape: {self.data_wrangled.shape[0]} rows × {self.data_wrangled.shape[1]} columns\n"
            summary += f"- Columns: {', '.join(self.data_wrangled.columns)}\n\n"
            
            summary += f"## Changes\n"
            summary += f"- Rows: {self.data_raw.shape[0]} → {self.data_wrangled.shape[0]}\n"
            summary += f"- Columns: {self.data_raw.shape[1]} → {self.data_wrangled.shape[1]}\n"
        else:
            summary += "## Status\n⚠️ Wrangling failed - no output generated\n"
        
        return summary


# Synchronous wrapper for backwards compatibility
class DataWranglingAgentSync(DataWranglingAgent):
    """
    Synchronous wrapper for DataWranglingAgent.
    
    Provides a synchronous interface for use in non-async contexts.
    """
    
    def wrangle_data_sync(
        self,
        data_raw: Union[pd.DataFrame, dict, list],
        user_instructions: str,
        **kwargs
    ) -> dict:
        """
        Synchronous version of wrangle_data.
        
        Args:
            data_raw: Input data.
            user_instructions: Wrangling instructions.
            **kwargs: Additional arguments passed to wrangle_data.
            
        Returns:
            Wrangling result dictionary.
        """
        import asyncio
        return asyncio.run(self.wrangle_data(data_raw, user_instructions, **kwargs))
