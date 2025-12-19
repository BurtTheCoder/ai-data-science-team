"""
H2O AutoML Agent - Agent SDK Implementation

Trains machine learning models using H2O AutoML.
"""

from typing import Optional, Union, Dict, Any
import pandas as pd

from ai_data_science_team_sdk.base_agent import BaseAgentSDK


class H2OMLAgent(BaseAgentSDK):
    """
    H2O AutoML Agent for automated machine learning.
    
    This agent can:
    - Train models using H2O AutoML
    - Handle classification and regression tasks
    - Perform automatic feature engineering
    - Generate model leaderboards
    - Export best models
    - Create predictions
    
    Example:
        ```python
        import pandas as pd
        from ai_data_science_team_sdk.ml_agents import H2OMLAgent
        
        df = pd.read_csv("training_data.csv")
        
        agent = H2OMLAgent()
        
        result = await agent.train_model(
            data=df,
            target_variable="price",
            problem_type="regression",
            max_models=10
        )
        
        leaderboard = agent.get_leaderboard()
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
        """Initialize the H2O ML Agent."""
        super().__init__(
            working_dir=working_dir or "/tmp/h2o_ml_agent",
            max_turns=max_turns,
            verbose=verbose,
            log=log,
            log_path=log_path
        )
        
        self.leaderboard = None
        self.best_model_info = None
    
    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for H2O AutoML."""
        return f"""You are an expert machine learning agent specializing in H2O AutoML.

Your role is to train high-quality machine learning models using H2O's automated ML capabilities.

Working Directory: {self.working_dir}

Available Tools:
- Bash: Execute Python code with H2O
- Read: Read CSV data files
- Write: Save model outputs and reports

Process:
1. Read the training data file (training_data.csv)
2. Initialize H2O
3. Analyze the data and target variable
4. Configure H2O AutoML with appropriate settings
5. Train models
6. Generate leaderboard and save to leaderboard.csv
7. Export the best model information to best_model.txt
8. Create predictions on training data and save to predictions.csv
9. Report model performance and insights

H2O AutoML Best Practices:
- Initialize H2O with appropriate memory settings
- Set max_models based on time constraints
- Use appropriate evaluation metrics
- Handle imbalanced datasets with class weights
- Perform cross-validation
- Save model artifacts properly

Code Template:
```python
import pandas as pd
import h2o
from h2o.automl import H2OAutoML

# Initialize H2O
h2o.init()

# Load data
df = pd.read_csv('training_data.csv')
h2o_df = h2o.H2OFrame(df)

# Define target and features
target = 'target_column'
features = [col for col in h2o_df.columns if col != target]

# Train AutoML
aml = H2OAutoML(
    max_models=10,
    seed=42,
    max_runtime_secs=300
)
aml.train(x=features, y=target, training_frame=h2o_df)

# Get leaderboard
leaderboard = aml.leaderboard.as_data_frame()
leaderboard.to_csv('leaderboard.csv', index=False)

# Get best model
best_model = aml.leader
print(f"Best model: {best_model.model_id}")

# Save model info
with open('best_model.txt', 'w') as f:
    f.write(f"Model ID: {best_model.model_id}\\n")
    f.write(f"Model Type: {best_model.algo}\\n")

# Make predictions
predictions = best_model.predict(h2o_df)
predictions_df = predictions.as_data_frame()
predictions_df.to_csv('predictions.csv', index=False)

# Shutdown H2O
h2o.cluster().shutdown()
```

Be thorough, optimize for the problem type, and provide clear performance metrics."""
    
    async def train_model(
        self,
        data: Union[pd.DataFrame, dict, list],
        target_variable: str,
        problem_type: str = "auto",
        max_models: int = 10,
        max_runtime_secs: int = 300,
        user_instructions: str = ""
    ) -> Dict[str, Any]:
        """
        Train a machine learning model using H2O AutoML.
        
        Args:
            data: Training data (DataFrame, dict, or list of dicts).
            target_variable: Name of the target variable.
            problem_type: "classification", "regression", or "auto".
            max_models: Maximum number of models to train.
            max_runtime_secs: Maximum training time in seconds.
            user_instructions: Additional instructions for training.
            
        Returns:
            Dictionary containing:
                - leaderboard: DataFrame with model leaderboard
                - best_model_info: Information about the best model
                - predictions: Predictions on training data
                - success: Whether training succeeded
                - messages: Agent messages
        """
        # Convert input to DataFrame
        if isinstance(data, dict):
            df_input = pd.DataFrame(data)
        elif isinstance(data, list):
            df_input = pd.DataFrame(data[0]) if len(data) > 0 else pd.DataFrame()
        else:
            df_input = data
        
        # Save training data
        data_path = self._save_dataframe(df_input, "training_data.csv")
        
        # Build the prompt
        prompt = f"""Train a machine learning model using H2O AutoML.

Training Data: training_data.csv
Target Variable: {target_variable}
Problem Type: {problem_type}
Max Models: {max_models}
Max Runtime: {max_runtime_secs} seconds

{user_instructions if user_instructions else ""}

Data Summary:
- Shape: {df_input.shape[0]} rows × {df_input.shape[1]} columns
- Columns: {list(df_input.columns)}
- Target: {target_variable}

Steps:
1. Initialize H2O
2. Load the training data
3. Configure H2O AutoML with the specified parameters
4. Train models
5. Save leaderboard to leaderboard.csv
6. Save best model info to best_model.txt
7. Create predictions and save to predictions.csv
8. Report performance metrics

Ensure proper H2O initialization and shutdown."""
        
        # Execute the agent
        if self.verbose:
            print(f"📊 Training Data: {df_input.shape[0]} rows × {df_input.shape[1]} columns")
            print(f"🎯 Target: {target_variable}")
            print(f"🤖 Problem Type: {problem_type}")
            print(f"⏱️  Max Runtime: {max_runtime_secs}s\n")
        
        await self._execute_query(prompt)
        
        # Load outputs
        leaderboard = self._load_dataframe("leaderboard.csv")
        predictions = self._load_dataframe("predictions.csv")
        
        # Load best model info
        model_info_file = self.working_dir / "best_model.txt"
        best_model_info = None
        if model_info_file.exists():
            with open(model_info_file, 'r') as f:
                best_model_info = f.read()
        
        if leaderboard is not None:
            self.leaderboard = leaderboard
            self.best_model_info = best_model_info
            
            if self.verbose:
                print(f"✅ Training completed")
                print(f"📊 Models trained: {len(leaderboard)}")
                if best_model_info:
                    print(f"\n🏆 Best Model:\n{best_model_info}")
            
            self.response = {
                "leaderboard": leaderboard,
                "best_model_info": best_model_info,
                "predictions": predictions,
                "success": True,
                "messages": self.messages,
                "leaderboard_path": str(self.working_dir / "leaderboard.csv")
            }
        else:
            if self.verbose:
                print("⚠️  Training failed - no leaderboard generated")
            
            self.response = {
                "leaderboard": None,
                "best_model_info": best_model_info,
                "predictions": predictions,
                "success": False,
                "messages": self.messages,
                "leaderboard_path": None
            }
        
        return self.response
    
    def get_leaderboard(self) -> Optional[pd.DataFrame]:
        """Get the model leaderboard."""
        return self.leaderboard
    
    def get_best_model_info(self) -> Optional[str]:
        """Get information about the best model."""
        return self.best_model_info
    
    async def predict(
        self,
        data: Union[pd.DataFrame, dict, list],
        model_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make predictions using a trained H2O model.
        
        Args:
            data: Data to predict on.
            model_path: Path to saved H2O model (optional).
            
        Returns:
            Dictionary with predictions and metadata.
        """
        # Convert input to DataFrame
        if isinstance(data, dict):
            df_input = pd.DataFrame(data)
        elif isinstance(data, list):
            df_input = pd.DataFrame(data[0]) if len(data) > 0 else pd.DataFrame()
        else:
            df_input = data
        
        # Save prediction data
        self._save_dataframe(df_input, "prediction_data.csv")
        
        prompt = f"""Make predictions using the trained H2O model.

Prediction Data: prediction_data.csv
{f"Model Path: {model_path}" if model_path else "Use the best model from training"}

Steps:
1. Initialize H2O
2. Load the model
3. Load prediction data
4. Make predictions
5. Save predictions to predictions.csv

Ensure proper error handling."""
        
        await self._execute_query(prompt)
        
        predictions = self._load_dataframe("predictions.csv")
        
        return {
            "predictions": predictions,
            "success": predictions is not None,
            "messages": self.messages
        }
