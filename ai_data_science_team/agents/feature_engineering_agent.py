"""
Feature Engineering Agent - Agent SDK Implementation

Creates ML-ready features from prepared data.
"""

from typing import Optional, Union, List
import pandas as pd

from ai_data_science_team_sdk.base_agent import BaseAgentSDK


class FeatureEngineeringAgent(BaseAgentSDK):
    """
    Feature Engineering Agent for creating ML-ready features.
    
    This agent can:
    - Create interaction features
    - Generate polynomial features
    - Encode categorical variables (one-hot, label, target encoding)
    - Scale and normalize numerical features
    - Create time-based features
    - Bin continuous variables
    - Extract text features
    
    Example:
        ```python
        import pandas as pd
        from ai_data_science_team_sdk.agents import FeatureEngineeringAgent
        
        df = pd.read_csv("clean_data.csv")
        
        agent = FeatureEngineeringAgent()
        
        result = await agent.engineer_features(
            data=df,
            target_variable="price",
            user_instructions="Create polynomial features and encode categories"
        )
        
        ml_ready_df = agent.get_features()
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
        """Initialize the Feature Engineering Agent."""
        super().__init__(
            working_dir=working_dir or "/tmp/feature_engineering_agent",
            max_turns=max_turns,
            verbose=verbose,
            log=log,
            log_path=log_path
        )
        
        self.data_input = None
        self.features = None
    
    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for feature engineering."""
        return f"""You are an expert feature engineering agent specializing in creating ML-ready features.

Your role is to transform prepared data into features that maximize machine learning model performance.

Working Directory: {self.working_dir}

Available Tools:
- Bash: Execute Python code for feature engineering
- Read: Read CSV files
- Write: Save engineered features

Process:
1. Read the input data file (input_data.csv)
2. Analyze the data and target variable
3. Design appropriate features based on:
   - Data types
   - Target variable type (classification/regression)
   - Domain knowledge
   - User instructions
4. Write Python code to create features
5. Execute the code using the Bash tool
6. Save engineered features to features.csv
7. Report what features were created

Feature Engineering Best Practices:
- Use scikit-learn for standard transformations
- Create interaction features for related variables
- Encode categorical variables appropriately
- Scale numerical features if needed
- Handle high cardinality categories
- Create domain-specific features
- Document all feature transformations

Common Libraries:
```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
```

Code Template:
```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Load data
df = pd.read_csv('input_data.csv')

# Feature engineering
# ... create features ...

# Save features
df.to_csv('features.csv', index=False)

# Report
print(f"Original features: {len(original_columns)}")
print(f"Engineered features: {len(df.columns)}")
```

Be creative, use domain knowledge, and focus on features that will improve model performance."""
    
    async def engineer_features(
        self,
        data: Union[pd.DataFrame, dict, list],
        target_variable: Optional[str] = None,
        user_instructions: str = "",
        input_filename: str = "input_data.csv",
        output_filename: str = "features.csv"
    ) -> dict:
        """
        Engineer features from input data.
        
        Args:
            data: Input data (DataFrame, dict, or list of dicts).
            target_variable: Name of the target variable (if applicable).
            user_instructions: Natural language instructions for feature engineering.
            input_filename: Name for the input CSV file.
            output_filename: Name for the output CSV file.
            
        Returns:
            Dictionary containing:
                - features: DataFrame with engineered features
                - data_input: Original DataFrame
                - feature_names: List of created feature names
                - success: Whether feature engineering succeeded
                - messages: Agent messages
        """
        # Convert input to DataFrame
        if isinstance(data, dict):
            df_input = pd.DataFrame(data)
        elif isinstance(data, list):
            df_input = pd.DataFrame(data[0]) if len(data) > 0 else pd.DataFrame()
        else:
            df_input = data
        
        self.data_input = df_input
        
        # Save input data
        input_path = self._save_dataframe(df_input, input_filename)
        
        # Build the prompt
        target_info = f"\nTarget Variable: {target_variable}" if target_variable else ""
        
        prompt = f"""Engineer features for the data in {input_filename}.
{target_info}

Instructions: {user_instructions if user_instructions else "Create relevant features for machine learning"}

Input Data Summary:
- Shape: {df_input.shape[0]} rows × {df_input.shape[1]} columns
- Columns: {list(df_input.columns)}
- Data types: {df_input.dtypes.to_dict()}

Numerical columns: {list(df_input.select_dtypes(include=['number']).columns)}
Categorical columns: {list(df_input.select_dtypes(include=['object', 'category']).columns)}

First few rows:
{df_input.head().to_string()}

Create engineered features and save to {output_filename}.
Also create a file called feature_report.txt documenting all features created."""
        
        # Execute the agent
        if self.verbose:
            print(f"📊 Input: {df_input.shape[0]} rows × {df_input.shape[1]} columns")
            if target_variable:
                print(f"🎯 Target: {target_variable}")
            print(f"📝 Task: {user_instructions if user_instructions else 'Create ML-ready features'}\n")
        
        await self._execute_query(prompt)
        
        # Load the output
        df_output = self._load_dataframe(output_filename)
        
        # Load feature report if available
        report_path = self.working_dir / "feature_report.txt"
        feature_report = None
        if report_path.exists():
            with open(report_path, 'r') as f:
                feature_report = f.read()
        
        if df_output is not None:
            self.features = df_output
            
            # Get new feature names
            new_features = [col for col in df_output.columns if col not in df_input.columns]
            
            if self.verbose:
                print(f"📊 Output: {df_output.shape[0]} rows × {df_output.shape[1]} columns")
                print(f"   Original features: {df_input.shape[1]}")
                print(f"   Engineered features: {df_output.shape[1]}")
                print(f"   New features: {len(new_features)}")
            
            self.response = {
                "features": df_output,
                "data_input": df_input,
                "feature_names": list(df_output.columns),
                "new_features": new_features,
                "feature_report": feature_report,
                "success": True,
                "messages": self.messages,
                "input_path": str(input_path),
                "output_path": str(self.working_dir / output_filename)
            }
        else:
            if self.verbose:
                print("⚠️  No output file generated")
            
            self.response = {
                "features": None,
                "data_input": df_input,
                "feature_names": [],
                "new_features": [],
                "feature_report": feature_report,
                "success": False,
                "messages": self.messages,
                "input_path": str(input_path),
                "output_path": None
            }
        
        return self.response
    
    def get_features(self) -> Optional[pd.DataFrame]:
        """Get the engineered features DataFrame."""
        return self.features
    
    def get_feature_names(self) -> List[str]:
        """Get the list of all feature names."""
        if self.response:
            return self.response.get("feature_names", [])
        return []
    
    def get_new_features(self) -> List[str]:
        """Get the list of newly created feature names."""
        if self.response:
            return self.response.get("new_features", [])
        return []
    
    def get_feature_report(self) -> Optional[str]:
        """Get the feature engineering report."""
        if self.response:
            return self.response.get("feature_report")
        return None
