"""
Data Visualization Agent - Agent SDK Implementation

Creates interactive Plotly visualizations from data using natural language instructions.
"""

from typing import Optional, Union
import pandas as pd
import json
from pathlib import Path

from ai_data_science_team.base_agent import BaseAgentSDK


class DataVisualizationAgent(BaseAgentSDK):
    """
    Data Visualization Agent for creating interactive plots.
    
    This agent can create various types of visualizations:
    - Line charts, bar charts, scatter plots
    - Histograms, box plots, violin plots
    - Heatmaps, correlation matrices
    - 3D plots, subplots, faceted plots
    
    The agent generates Plotly visualizations that are interactive and
    can be saved as HTML or JSON.
    
    Example:
        ```python
        import pandas as pd
        from ai_data_science_team.agents import DataVisualizationAgent
        
        df = pd.read_csv("sales.csv")
        
        agent = DataVisualizationAgent()
        
        result = await agent.create_visualization(
            data=df,
            user_instructions="Create a bar chart of sales by region"
        )
        
        fig = agent.get_plotly_figure()
        fig.show()
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
        Initialize the Data Visualization Agent.
        
        Args:
            working_dir: Directory for agent operations.
            max_turns: Maximum number of agent turns.
            verbose: Whether to print progress messages.
            log: Whether to log operations.
            log_path: Path for log files.
        """
        super().__init__(
            working_dir=working_dir or "/tmp/data_viz_agent",
            max_turns=max_turns,
            verbose=verbose,
            log=log,
            log_path=log_path
        )
        
        self.plotly_figure = None
        self.plotly_json = None
    
    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for data visualization."""
        return f"""You are an expert data visualization agent specializing in creating interactive Plotly visualizations.

Your role is to create beautiful, informative visualizations based on user instructions.

Working Directory: {self.working_dir}

Available Tools:
- Bash: Execute Python code to create Plotly visualizations
- Read: Read CSV data files
- Write: Save visualization outputs (HTML, JSON)

Process:
1. Read the input data file (data.csv)
2. Analyze the data structure and identify relevant columns
3. Write Python code to create a Plotly visualization
4. Execute the code using the Bash tool
5. Save the figure as both HTML (for viewing) and JSON (for programmatic access)
6. Report what visualization was created

Visualization Best Practices:
- Always import plotly.graph_objects as go or plotly.express as px
- Use appropriate chart types for the data
- Add clear titles, axis labels, and legends
- Use color schemes that are accessible
- Include hover information for interactivity
- Save as: visualization.html and visualization.json

Code Template:
```python
import pandas as pd
import plotly.express as px  # or plotly.graph_objects as go
import json

# Load data
df = pd.read_csv('data.csv')

# Create visualization
fig = px.scatter(df, x='column1', y='column2', title='My Chart')

# Save outputs
fig.write_html('visualization.html')
with open('visualization.json', 'w') as f:
    json.dump(fig.to_dict(), f)
```

Be creative, informative, and ensure the visualization clearly communicates the data story."""
    
    async def create_visualization(
        self,
        data: Union[pd.DataFrame, dict, list],
        user_instructions: str,
        data_filename: str = "data.csv"
    ) -> dict:
        """
        Create a visualization based on user instructions.
        
        Args:
            data: Input data (DataFrame, dict, or list of dicts).
            user_instructions: Natural language instructions for the visualization.
            data_filename: Name for the input CSV file.
            
        Returns:
            Dictionary containing:
                - plotly_figure: Plotly figure object (if available)
                - plotly_json: JSON representation of the figure
                - html_path: Path to saved HTML file
                - success: Whether visualization succeeded
                - messages: Agent messages
        """
        # Convert input to DataFrame if needed
        if isinstance(data, dict):
            df_input = pd.DataFrame(data)
        elif isinstance(data, list):
            df_input = pd.DataFrame(data[0]) if len(data) > 0 else pd.DataFrame()
        else:
            df_input = data
        
        # Save input data
        data_path = self._save_dataframe(df_input, data_filename)
        
        # Build the prompt
        prompt = f"""Create a visualization for the data in {data_filename}.

Instructions: {user_instructions}

Data Summary:
- Shape: {df_input.shape[0]} rows × {df_input.shape[1]} columns
- Columns: {list(df_input.columns)}
- Data types: {df_input.dtypes.to_dict()}

First few rows:
{df_input.head().to_string()}

Create an appropriate Plotly visualization and save it as:
- visualization.html (for viewing)
- visualization.json (for programmatic access)"""
        
        # Execute the agent
        if self.verbose:
            print(f"📊 Data: {df_input.shape[0]} rows × {df_input.shape[1]} columns")
            print(f"📝 Task: {user_instructions}\n")
        
        await self._execute_query(prompt)
        
        # Load the outputs
        html_path = self.working_dir / "visualization.html"
        json_path = self.working_dir / "visualization.json"
        
        plotly_json = None
        plotly_fig = None
        
        if json_path.exists():
            with open(json_path, 'r') as f:
                plotly_json = json.load(f)
            
            # Try to reconstruct the figure
            try:
                import plotly.graph_objects as go
                plotly_fig = go.Figure(plotly_json)
                self.plotly_figure = plotly_fig
                self.plotly_json = plotly_json
            except Exception as e:
                if self.verbose:
                    print(f"⚠️  Could not reconstruct Plotly figure: {e}")
        
        success = html_path.exists() and json_path.exists()
        
        if success and self.verbose:
            print(f"✅ Visualization created successfully")
            print(f"   HTML: {html_path}")
            print(f"   JSON: {json_path}")
        elif self.verbose:
            print("⚠️  Visualization files not generated")
        
        self.response = {
            "plotly_figure": plotly_fig,
            "plotly_json": plotly_json,
            "html_path": str(html_path) if html_path.exists() else None,
            "json_path": str(json_path) if json_path.exists() else None,
            "success": success,
            "messages": self.messages
        }
        
        return self.response
    
    def get_plotly_figure(self):
        """
        Get the Plotly figure object.
        
        Returns:
            Plotly figure or None if not available.
        """
        return self.plotly_figure
    
    def get_plotly_json(self) -> Optional[dict]:
        """
        Get the JSON representation of the Plotly figure.
        
        Returns:
            Dictionary containing the Plotly figure data.
        """
        return self.plotly_json
    
    def show(self):
        """
        Display the visualization (if in a Jupyter environment).
        """
        if self.plotly_figure:
            self.plotly_figure.show()
        else:
            print("No visualization available to display")
    
    def save_html(self, filepath: str):
        """
        Save the visualization as an HTML file.
        
        Args:
            filepath: Path where the HTML file should be saved.
        """
        if self.plotly_figure:
            self.plotly_figure.write_html(filepath)
            if self.verbose:
                print(f"💾 Saved visualization to {filepath}")
        else:
            print("No visualization available to save")


# Synchronous wrapper
class DataVisualizationAgentSync(DataVisualizationAgent):
    """
    Synchronous wrapper for DataVisualizationAgent.
    """
    
    def create_visualization_sync(
        self,
        data: Union[pd.DataFrame, dict, list],
        user_instructions: str,
        **kwargs
    ) -> dict:
        """
        Synchronous version of create_visualization.
        
        Args:
            data: Input data.
            user_instructions: Visualization instructions.
            **kwargs: Additional arguments.
            
        Returns:
            Visualization result dictionary.
        """
        import asyncio
        return asyncio.run(self.create_visualization(data, user_instructions, **kwargs))
