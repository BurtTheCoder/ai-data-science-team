"""
EDA Tools Agent - Agent SDK Implementation

Performs comprehensive exploratory data analysis with automated reports.
"""

from typing import Optional, Union, Dict, Any
import pandas as pd

from ai_data_science_team_sdk.base_agent import BaseAgentSDK


class EDAToolsAgent(BaseAgentSDK):
    """
    Exploratory Data Analysis (EDA) Tools Agent.
    
    This agent can:
    - Generate comprehensive EDA reports
    - Create statistical summaries
    - Detect data quality issues
    - Identify correlations and patterns
    - Generate visualizations
    - Provide insights and recommendations
    
    Example:
        ```python
        import pandas as pd
        from ai_data_science_team_sdk.ds_agents import EDAToolsAgent
        
        df = pd.read_csv("data.csv")
        
        agent = EDAToolsAgent()
        
        result = await agent.perform_eda(
            data=df,
            target_variable="price"
        )
        
        report = agent.get_report()
        ```
    """
    
    def __init__(
        self,
        working_dir: Optional[str] = None,
        max_turns: int = 15,
        verbose: bool = True,
        log: bool = False,
        log_path: Optional[str] = None
    ):
        """Initialize the EDA Tools Agent."""
        super().__init__(
            working_dir=working_dir or "/tmp/eda_tools_agent",
            max_turns=max_turns,
            verbose=verbose,
            log=log,
            log_path=log_path
        )
        
        self.eda_report = None
        self.insights = None
    
    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for EDA."""
        return f"""You are an expert exploratory data analysis (EDA) agent specializing in comprehensive data analysis.

Your role is to analyze datasets and generate insightful reports with visualizations and recommendations.

Working Directory: {self.working_dir}

Available Tools:
- Bash: Execute Python code for EDA
- Read: Read CSV data files
- Write: Save reports and visualizations

Process:
1. Read the input data file (data.csv)
2. Perform comprehensive EDA:
   - Data structure and types
   - Statistical summaries
   - Missing values analysis
   - Distribution analysis
   - Correlation analysis
   - Outlier detection
   - Feature relationships
3. Create visualizations using Plotly or Matplotlib
4. Generate insights and recommendations
5. Save EDA report to eda_report.md
6. Save key insights to insights.txt
7. Save visualizations to the working directory

EDA Best Practices:
- Use pandas profiling or manual analysis
- Create informative visualizations
- Identify data quality issues
- Analyze feature relationships
- Provide actionable insights
- Document all findings

Recommended Libraries:
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from scipy import stats
```

Code Template:
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('data.csv')

# Basic info
print("Dataset Shape:", df.shape)
print("\\nData Types:\\n", df.dtypes)
print("\\nMissing Values:\\n", df.isnull().sum())

# Statistical summary
summary = df.describe()

# Correlation analysis
numeric_cols = df.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 1:
    correlation = df[numeric_cols].corr()
    
    # Create correlation heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation, annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix')
    plt.savefig('correlation_heatmap.png')
    plt.close()

# Distribution plots
for col in numeric_cols[:5]:  # First 5 numeric columns
    plt.figure()
    df[col].hist(bins=30)
    plt.title(f'Distribution of {col}')
    plt.savefig(f'dist_{col}.png')
    plt.close()

# Generate report
with open('eda_report.md', 'w') as f:
    f.write("# Exploratory Data Analysis Report\\n\\n")
    f.write(f"## Dataset Overview\\n")
    f.write(f"- Shape: {df.shape}\\n")
    f.write(f"- Columns: {list(df.columns)}\\n")
    # ... more report content
```

Be thorough, insightful, and provide actionable recommendations."""
    
    async def perform_eda(
        self,
        data: Union[pd.DataFrame, dict, list],
        target_variable: Optional[str] = None,
        user_instructions: str = ""
    ) -> Dict[str, Any]:
        """
        Perform exploratory data analysis on the dataset.
        
        Args:
            data: Input data (DataFrame, dict, or list of dicts).
            target_variable: Name of the target variable (if applicable).
            user_instructions: Additional instructions for EDA.
            
        Returns:
            Dictionary containing:
                - eda_report: Markdown report with findings
                - insights: Key insights and recommendations
                - visualizations: List of generated visualization files
                - success: Whether EDA succeeded
                - messages: Agent messages
        """
        # Convert input to DataFrame
        if isinstance(data, dict):
            df_input = pd.DataFrame(data)
        elif isinstance(data, list):
            df_input = pd.DataFrame(data[0]) if len(data) > 0 else pd.DataFrame()
        else:
            df_input = data
        
        # Save input data
        data_path = self._save_dataframe(df_input, "data.csv")
        
        # Build the prompt
        target_info = f"\nTarget Variable: {target_variable}" if target_variable else ""
        
        prompt = f"""Perform comprehensive exploratory data analysis on data.csv.
{target_info}

{user_instructions if user_instructions else ""}

Data Summary:
- Shape: {df_input.shape[0]} rows × {df_input.shape[1]} columns
- Columns: {list(df_input.columns)}
- Data types: {df_input.dtypes.to_dict()}

Analysis Requirements:
1. Data Structure and Quality
   - Missing values
   - Data types
   - Duplicates
   - Outliers

2. Statistical Analysis
   - Descriptive statistics
   - Distribution analysis
   - Correlation analysis

3. Visualizations
   - Distribution plots
   - Correlation heatmap
   - Box plots for outliers
   - Scatter plots for relationships

4. Insights and Recommendations
   - Data quality issues
   - Feature relationships
   - Potential problems
   - Next steps

Save outputs:
- eda_report.md: Comprehensive markdown report
- insights.txt: Key insights and recommendations
- *.png: Visualization files

Provide thorough analysis with actionable insights."""
        
        # Execute the agent
        if self.verbose:
            print(f"📊 Data: {df_input.shape[0]} rows × {df_input.shape[1]} columns")
            if target_variable:
                print(f"🎯 Target: {target_variable}")
            print(f"📝 Performing comprehensive EDA...\n")
        
        await self._execute_query(prompt)
        
        # Load outputs
        report_file = self.working_dir / "eda_report.md"
        insights_file = self.working_dir / "insights.txt"
        
        eda_report = None
        if report_file.exists():
            with open(report_file, 'r') as f:
                eda_report = f.read()
        
        insights = None
        if insights_file.exists():
            with open(insights_file, 'r') as f:
                insights = f.read()
        
        # Find visualization files
        import glob
        viz_files = glob.glob(str(self.working_dir / "*.png"))
        
        if eda_report:
            self.eda_report = eda_report
            self.insights = insights
            
            if self.verbose:
                print(f"✅ EDA completed")
                print(f"📄 Report: eda_report.md")
                print(f"💡 Insights: insights.txt")
                print(f"📊 Visualizations: {len(viz_files)} files")
            
            self.response = {
                "eda_report": eda_report,
                "insights": insights,
                "visualizations": viz_files,
                "success": True,
                "messages": self.messages,
                "report_path": str(report_file)
            }
        else:
            if self.verbose:
                print("⚠️  EDA failed - no report generated")
            
            self.response = {
                "eda_report": None,
                "insights": insights,
                "visualizations": viz_files,
                "success": False,
                "messages": self.messages,
                "report_path": None
            }
        
        return self.response
    
    def get_report(self) -> Optional[str]:
        """Get the EDA report."""
        return self.eda_report
    
    def get_insights(self) -> Optional[str]:
        """Get the key insights."""
        return self.insights
    
    def save_report(self, filepath: str):
        """
        Save the EDA report to a file.
        
        Args:
            filepath: Path where the report should be saved.
        """
        if self.eda_report:
            with open(filepath, 'w') as f:
                f.write(self.eda_report)
            if self.verbose:
                print(f"💾 Saved EDA report to {filepath}")
        else:
            print("No EDA report available to save")
