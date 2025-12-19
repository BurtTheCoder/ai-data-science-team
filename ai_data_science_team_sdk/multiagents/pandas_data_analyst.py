"""
Pandas Data Analyst - Agent SDK Implementation

A comprehensive multi-agent system for end-to-end pandas data analysis.
Uses Agent SDK's sub-agent capabilities for orchestration.
"""

from typing import Optional, Union, Dict, Any
import pandas as pd
from pathlib import Path

from ai_data_science_team_sdk.base_agent import BaseAgentSDK


class PandasDataAnalyst(BaseAgentSDK):
    """
    Pandas Data Analyst - A comprehensive data analysis agent.
    
    This multi-agent system can perform complete data analysis workflows:
    - Data loading and exploration
    - Data cleaning and preparation
    - Feature engineering
    - Visualization
    - Statistical analysis
    - Report generation
    
    The agent uses the Agent SDK's built-in capabilities to orchestrate
    multiple analysis tasks in a single conversation.
    
    Example:
        ```python
        import pandas as pd
        from ai_data_science_team_sdk.multiagents import PandasDataAnalyst
        
        df = pd.read_csv("data.csv")
        
        analyst = PandasDataAnalyst()
        
        result = await analyst.analyze(
            data=df,
            analysis_goal="Analyze sales trends and create visualizations"
        )
        
        report = analyst.get_report()
        ```
    """
    
    def __init__(
        self,
        working_dir: Optional[str] = None,
        max_turns: int = 20,
        verbose: bool = True,
        log: bool = False,
        log_path: Optional[str] = None
    ):
        """
        Initialize the Pandas Data Analyst.
        
        Args:
            working_dir: Directory for analysis operations.
            max_turns: Maximum number of agent turns.
            verbose: Whether to print progress messages.
            log: Whether to log operations.
            log_path: Path for log files.
        """
        # Add web tools for research and data gathering
        allowed_tools = [
            "Bash",       # Execute Python/pandas code
            "Read",       # Read files
            "Write",      # Create files
            "Edit",       # Edit files
            "Glob",       # Find files
            "Grep",       # Search content
            "WebSearch",  # Search the web
            "WebFetch"    # Fetch web content
        ]
        
        super().__init__(
            working_dir=working_dir or "/tmp/pandas_data_analyst",
            max_turns=max_turns,
            allowed_tools=allowed_tools,
            verbose=verbose,
            log=log,
            log_path=log_path
        )
        
        self.analysis_report = None
    
    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for the Pandas Data Analyst."""
        return f"""You are an expert Pandas Data Analyst with comprehensive data analysis capabilities.

Your role is to perform end-to-end data analysis workflows using pandas, including:
- Data exploration and profiling
- Data cleaning and preparation
- Feature engineering
- Statistical analysis
- Visualization with Plotly
- Insight generation
- Report writing

Working Directory: {self.working_dir}

Available Tools:
- Bash: Execute Python/pandas code
- Read: Read CSV and other data files
- Write: Create analysis outputs and reports
- Edit: Modify existing files
- Glob: Find files by pattern
- Grep: Search file contents
- WebSearch: Search for information online
- WebFetch: Fetch content from URLs

Analysis Workflow:
1. Load and explore the data
2. Assess data quality and identify issues
3. Clean and prepare the data as needed
4. Perform requested analysis
5. Create visualizations
6. Generate insights and recommendations
7. Write a comprehensive report

Best Practices:
- Use pandas for data manipulation
- Use Plotly for interactive visualizations
- Provide statistical evidence for insights
- Document all analysis steps
- Create reproducible code
- Save all outputs (data, visualizations, reports)

Output Requirements:
- analysis_report.md: Comprehensive markdown report
- cleaned_data.csv: Cleaned dataset (if cleaning performed)
- visualizations/*.html: Interactive Plotly visualizations
- insights.txt: Key findings and recommendations

Be thorough, insightful, and provide actionable recommendations based on data evidence."""
    
    async def analyze(
        self,
        data: Union[pd.DataFrame, dict, list, str],
        analysis_goal: str,
        target_variable: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive data analysis.
        
        Args:
            data: Input data (DataFrame, dict, list, or path to CSV file).
            analysis_goal: Natural language description of analysis goals.
            target_variable: Name of the target variable (if applicable).
            
        Returns:
            Dictionary containing:
                - analysis_report: Markdown report with findings
                - cleaned_data: Cleaned DataFrame (if cleaning performed)
                - visualizations: List of visualization files
                - insights: Key insights
                - success: Whether analysis succeeded
                - messages: Agent messages
        """
        # Handle different input types
        if isinstance(data, str):
            # Assume it's a file path
            df_input = pd.read_csv(data)
            data_source = data
        elif isinstance(data, dict):
            df_input = pd.DataFrame(data)
            data_source = "provided dictionary"
        elif isinstance(data, list):
            df_input = pd.DataFrame(data[0]) if len(data) > 0 else pd.DataFrame()
            data_source = "provided list"
        else:
            df_input = data
            data_source = "provided DataFrame"
        
        # Save input data
        data_path = self._save_dataframe(df_input, "input_data.csv")
        
        # Create visualizations directory
        viz_dir = self.working_dir / "visualizations"
        viz_dir.mkdir(exist_ok=True)
        
        # Build the prompt
        target_info = f"\nTarget Variable: {target_variable}" if target_variable else ""
        
        prompt = f"""Perform comprehensive data analysis on the dataset.

Data Source: {data_source}
Data File: input_data.csv
Analysis Goal: {analysis_goal}
{target_info}

Dataset Overview:
- Shape: {df_input.shape[0]} rows × {df_input.shape[1]} columns
- Columns: {list(df_input.columns)}
- Data types: {df_input.dtypes.to_dict()}

First few rows:
{df_input.head(3).to_string()}

Analysis Requirements:

1. **Data Exploration**
   - Examine data structure and types
   - Check for missing values and duplicates
   - Analyze distributions and outliers
   - Identify patterns and relationships

2. **Data Preparation** (if needed)
   - Clean data issues
   - Handle missing values
   - Remove duplicates
   - Fix data types
   - Save cleaned data to cleaned_data.csv

3. **Analysis**
   - Perform analysis according to the goal
   - Use appropriate statistical methods
   - Create relevant features if needed
   - Calculate key metrics

4. **Visualizations**
   - Create interactive Plotly visualizations
   - Save as HTML in visualizations/ directory
   - Include: distributions, relationships, trends, comparisons

5. **Insights and Recommendations**
   - Extract key findings
   - Provide data-driven insights
   - Make actionable recommendations
   - Save to insights.txt

6. **Report**
   - Write comprehensive markdown report
   - Include all findings, visualizations, and recommendations
   - Save to analysis_report.md

Be thorough, creative, and provide valuable insights!"""
        
        # Execute the agent
        if self.verbose:
            print(f"📊 Data: {df_input.shape[0]} rows × {df_input.shape[1]} columns")
            if target_variable:
                print(f"🎯 Target: {target_variable}")
            print(f"🔍 Goal: {analysis_goal}\n")
        
        await self._execute_query(prompt)
        
        # Load outputs
        report_file = self.working_dir / "analysis_report.md"
        insights_file = self.working_dir / "insights.txt"
        cleaned_data_file = self.working_dir / "cleaned_data.csv"
        
        analysis_report = None
        if report_file.exists():
            with open(report_file, 'r') as f:
                analysis_report = f.read()
        
        insights = None
        if insights_file.exists():
            with open(insights_file, 'r') as f:
                insights = f.read()
        
        cleaned_data = None
        if cleaned_data_file.exists():
            cleaned_data = pd.read_csv(cleaned_data_file)
        
        # Find visualization files
        import glob
        viz_files = glob.glob(str(viz_dir / "*.html"))
        
        if analysis_report:
            self.analysis_report = analysis_report
            
            if self.verbose:
                print(f"✅ Analysis completed")
                print(f"📄 Report: analysis_report.md")
                print(f"💡 Insights: insights.txt")
                print(f"📊 Visualizations: {len(viz_files)} files")
                if cleaned_data is not None:
                    print(f"🧹 Cleaned data: cleaned_data.csv")
            
            self.response = {
                "analysis_report": analysis_report,
                "cleaned_data": cleaned_data,
                "visualizations": viz_files,
                "insights": insights,
                "success": True,
                "messages": self.messages,
                "report_path": str(report_file)
            }
        else:
            if self.verbose:
                print("⚠️  Analysis incomplete - no report generated")
            
            self.response = {
                "analysis_report": None,
                "cleaned_data": cleaned_data,
                "visualizations": viz_files,
                "insights": insights,
                "success": False,
                "messages": self.messages,
                "report_path": None
            }
        
        return self.response
    
    def get_report(self) -> Optional[str]:
        """Get the analysis report."""
        return self.analysis_report
    
    def get_insights(self) -> Optional[str]:
        """Get the key insights."""
        if self.response:
            return self.response.get("insights")
        return None
    
    def get_cleaned_data(self) -> Optional[pd.DataFrame]:
        """Get the cleaned DataFrame."""
        if self.response:
            return self.response.get("cleaned_data")
        return None
    
    def save_report(self, filepath: str):
        """
        Save the analysis report to a file.
        
        Args:
            filepath: Path where the report should be saved.
        """
        if self.analysis_report:
            with open(filepath, 'w') as f:
                f.write(self.analysis_report)
            if self.verbose:
                print(f"💾 Saved analysis report to {filepath}")
        else:
            print("No analysis report available to save")
