"""
Data Cleaning Agent - Agent SDK Implementation

Handles data preparation including missing values, outliers, and data type conversions.
"""

from typing import Optional, Union
import pandas as pd

from ai_data_science_team_sdk.base_agent import BaseAgentSDK


class DataCleaningAgent(BaseAgentSDK):
    """
    Data Cleaning Agent for preparing and cleaning datasets.
    
    This agent can:
    - Handle missing values (imputation, deletion)
    - Detect and handle outliers
    - Convert data types
    - Remove duplicates
    - Standardize formats (dates, strings, etc.)
    - Validate data integrity
    
    Example:
        ```python
        import pandas as pd
        from ai_data_science_team_sdk.agents import DataCleaningAgent
        
        df = pd.read_csv("messy_data.csv")
        
        agent = DataCleaningAgent()
        
        result = await agent.clean_data(
            data_raw=df,
            user_instructions="Handle missing values and remove outliers"
        )
        
        clean_df = agent.get_data_cleaned()
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
        """Initialize the Data Cleaning Agent."""
        super().__init__(
            working_dir=working_dir or "/tmp/data_cleaning_agent",
            max_turns=max_turns,
            verbose=verbose,
            log=log,
            log_path=log_path
        )
        
        self.data_raw = None
        self.data_cleaned = None
    
    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for data cleaning."""
        return f"""You are an expert data cleaning agent specializing in data preparation and quality assurance.

Your role is to clean and prepare data for analysis or machine learning.

Working Directory: {self.working_dir}

Available Tools:
- Bash: Execute Python/pandas code for data cleaning
- Read: Read CSV files and examine data
- Write: Save cleaned data to CSV files

Process:
1. Read the input data file (input_data.csv)
2. Analyze data quality issues:
   - Missing values
   - Outliers
   - Incorrect data types
   - Duplicates
   - Format inconsistencies
3. Write Python code to clean the data
4. Execute the code using the Bash tool
5. Verify the cleaned data and save to output_data.csv
6. Report what cleaning operations were performed

Data Cleaning Best Practices:
- Document all cleaning decisions
- Handle missing values appropriately (impute, drop, or flag)
- Use statistical methods for outlier detection (IQR, Z-score)
- Convert data types correctly
- Preserve data integrity
- Report data quality metrics before and after

Code Template:
```python
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('input_data.csv')

# Analyze data quality
print("Missing values:", df.isnull().sum())
print("Duplicates:", df.duplicated().sum())

# Clean data
# ... cleaning operations ...

# Save cleaned data
df.to_csv('output_data.csv', index=False)

# Report changes
print(f"Original shape: {df.shape}")
print(f"Cleaned shape: {df.shape}")
```

Be thorough, document your decisions, and ensure data quality."""
    
    async def clean_data(
        self,
        data_raw: Union[pd.DataFrame, dict, list],
        user_instructions: str,
        input_filename: str = "input_data.csv",
        output_filename: str = "output_data.csv"
    ) -> dict:
        """
        Clean data according to user instructions.
        
        Args:
            data_raw: Input data (DataFrame, dict, or list of dicts).
            user_instructions: Natural language instructions for cleaning.
            input_filename: Name for the input CSV file.
            output_filename: Name for the output CSV file.
            
        Returns:
            Dictionary containing:
                - data_cleaned: Cleaned DataFrame
                - data_raw: Original DataFrame
                - cleaning_report: Summary of cleaning operations
                - success: Whether cleaning succeeded
                - messages: Agent messages
        """
        # Convert input to DataFrame
        if isinstance(data_raw, dict):
            df_input = pd.DataFrame(data_raw)
        elif isinstance(data_raw, list):
            df_input = pd.DataFrame(data_raw[0]) if len(data_raw) > 0 else pd.DataFrame()
        else:
            df_input = data_raw
        
        self.data_raw = df_input
        
        # Save input data
        input_path = self._save_dataframe(df_input, input_filename)
        
        # Analyze data quality
        missing_values = df_input.isnull().sum()
        duplicates = df_input.duplicated().sum()
        
        # Build the prompt
        prompt = f"""Clean the data in {input_filename} according to these instructions:

{user_instructions}

Input Data Summary:
- Shape: {df_input.shape[0]} rows × {df_input.shape[1]} columns
- Columns: {list(df_input.columns)}
- Data types: {df_input.dtypes.to_dict()}
- Missing values: {missing_values.to_dict()}
- Duplicates: {duplicates}

First few rows:
{df_input.head().to_string()}

Clean the data and save to {output_filename}.
Also create a file called cleaning_report.txt with details of all cleaning operations performed."""
        
        # Execute the agent
        if self.verbose:
            print(f"📊 Input: {df_input.shape[0]} rows × {df_input.shape[1]} columns")
            print(f"📝 Task: {user_instructions}\n")
        
        await self._execute_query(prompt)
        
        # Load the output
        df_output = self._load_dataframe(output_filename)
        
        # Load cleaning report if available
        report_path = self.working_dir / "cleaning_report.txt"
        cleaning_report = None
        if report_path.exists():
            with open(report_path, 'r') as f:
                cleaning_report = f.read()
        
        if df_output is not None:
            self.data_cleaned = df_output
            
            if self.verbose:
                print(f"📊 Output: {df_output.shape[0]} rows × {df_output.shape[1]} columns")
                print(f"   Rows changed: {df_input.shape[0]} → {df_output.shape[0]}")
                print(f"   Columns changed: {df_input.shape[1]} → {df_output.shape[1]}")
            
            self.response = {
                "data_cleaned": df_output,
                "data_raw": df_input,
                "cleaning_report": cleaning_report,
                "success": True,
                "messages": self.messages,
                "input_path": str(input_path),
                "output_path": str(self.working_dir / output_filename)
            }
        else:
            if self.verbose:
                print("⚠️  No output file generated")
            
            self.response = {
                "data_cleaned": None,
                "data_raw": df_input,
                "cleaning_report": cleaning_report,
                "success": False,
                "messages": self.messages,
                "input_path": str(input_path),
                "output_path": None
            }
        
        return self.response
    
    def get_data_cleaned(self) -> Optional[pd.DataFrame]:
        """Get the cleaned DataFrame."""
        return self.data_cleaned
    
    def get_data_raw(self) -> Optional[pd.DataFrame]:
        """Get the raw input DataFrame."""
        return self.data_raw
    
    def get_cleaning_report(self) -> Optional[str]:
        """Get the cleaning report."""
        if self.response:
            return self.response.get("cleaning_report")
        return None
