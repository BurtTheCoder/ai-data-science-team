"""
Basic Usage Examples for AI Data Science Team SDK

This script demonstrates how to use the refactored agents with the Anthropic Agent SDK.
"""

import asyncio
import pandas as pd
from pathlib import Path

# Import SDK agents
from ai_data_science_team.agents import (
    DataWranglingAgent,
    DataVisualizationAgent,
    DataCleaningAgent,
    FeatureEngineeringAgent,
    SQLDatabaseAgent
)
from ai_data_science_team.ml_agents import H2OMLAgent
from ai_data_science_team.ds_agents import EDAToolsAgent
from ai_data_science_team.multiagents import PandasDataAnalyst


async def example_data_wrangling():
    """Example: Data Wrangling Agent"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Data Wrangling Agent")
    print("="*70 + "\n")
    
    # Create sample data
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'category': ['A', 'B', 'C'] * 3 + ['A'],
        'sales': [100, 150, 200, 120, 180, 160, 140, 190, 170, 130],
        'quantity': [10, 15, 20, 12, 18, 16, 14, 19, 17, 13]
    })
    
    print("Input Data:")
    print(df)
    print()
    
    # Initialize agent
    agent = DataWranglingAgent(
        working_dir="/tmp/examples/wrangling",
        verbose=True
    )
    
    # Wrangle data
    result = await agent.wrangle_data(
        data_raw=df,
        user_instructions="""
        Group by 'category' and calculate:
        - Total sales
        - Average quantity
        - Count of transactions
        Sort by total sales descending.
        """
    )
    
    if result["success"]:
        print("\nWrangled Data:")
        print(agent.get_data_wrangled())


async def example_data_visualization():
    """Example: Data Visualization Agent"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Data Visualization Agent")
    print("="*70 + "\n")
    
    # Create sample data
    df = pd.DataFrame({
        'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'revenue': [45000, 52000, 48000, 61000, 58000, 67000],
        'expenses': [32000, 35000, 33000, 38000, 36000, 40000]
    })
    
    print("Input Data:")
    print(df)
    print()
    
    # Initialize agent
    agent = DataVisualizationAgent(
        working_dir="/tmp/examples/visualization",
        verbose=True
    )
    
    # Create visualization
    result = await agent.create_visualization(
        data=df,
        user_instructions="Create a line chart showing revenue and expenses over time"
    )
    
    if result["success"]:
        print(f"\n✅ Visualization saved to: {result['html_path']}")


async def example_data_cleaning():
    """Example: Data Cleaning Agent"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Data Cleaning Agent")
    print("="*70 + "\n")
    
    # Create messy data
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', None, 'David', 'Eve'],
        'age': [25, 30, 28, None, 35],
        'salary': [50000, 60000, 55000, 65000, 1000000],  # Last one is outlier
        'department': ['Sales', 'IT', 'Sales', 'IT', 'Sales']
    })
    
    print("Input Data (with issues):")
    print(df)
    print()
    
    # Initialize agent
    agent = DataCleaningAgent(
        working_dir="/tmp/examples/cleaning",
        verbose=True
    )
    
    # Clean data
    result = await agent.clean_data(
        data_raw=df,
        user_instructions="Handle missing values and detect/remove outliers in salary"
    )
    
    if result["success"]:
        print("\nCleaned Data:")
        print(agent.get_data_cleaned())


async def example_feature_engineering():
    """Example: Feature Engineering Agent"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Feature Engineering Agent")
    print("="*70 + "\n")
    
    # Create sample data
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 45],
        'income': [50000, 60000, 75000, 80000, 90000],
        'education': ['Bachelor', 'Master', 'Bachelor', 'PhD', 'Master']
    })
    
    print("Input Data:")
    print(df)
    print()
    
    # Initialize agent
    agent = FeatureEngineeringAgent(
        working_dir="/tmp/examples/feature_eng",
        verbose=True
    )
    
    # Engineer features
    result = await agent.engineer_features(
        data=df,
        target_variable="income",
        user_instructions="Create polynomial features for age and encode education"
    )
    
    if result["success"]:
        print("\nEngineered Features:")
        print(agent.get_features())
        print(f"\nNew features created: {len(result['new_features'])}")


async def example_pandas_analyst():
    """Example: Pandas Data Analyst (Multi-Agent)"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Pandas Data Analyst (Multi-Agent)")
    print("="*70 + "\n")
    
    # Create sample sales data
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100),
        'product': ['A', 'B', 'C'] * 33 + ['A'],
        'region': ['North', 'South', 'East', 'West'] * 25,
        'sales': range(1000, 1100),
        'quantity': range(10, 110)
    })
    
    print("Input Data:")
    print(df.head(10))
    print(f"... ({len(df)} total rows)")
    print()
    
    # Initialize analyst
    analyst = PandasDataAnalyst(
        working_dir="/tmp/examples/analyst",
        verbose=True
    )
    
    # Perform comprehensive analysis
    result = await analyst.analyze(
        data=df,
        analysis_goal="""
        Analyze sales performance across products and regions.
        Identify trends, top performers, and provide recommendations.
        """
    )
    
    if result["success"]:
        print("\n✅ Analysis completed!")
        print(f"📄 Report: {result['report_path']}")
        print(f"📊 Visualizations: {len(result['visualizations'])} files")


async def example_eda():
    """Example: EDA Tools Agent"""
    print("\n" + "="*70)
    print("EXAMPLE 6: EDA Tools Agent")
    print("="*70 + "\n")
    
    # Create sample data
    df = pd.DataFrame({
        'feature1': range(50),
        'feature2': [x**2 for x in range(50)],
        'feature3': ['A', 'B'] * 25,
        'target': [x + 10 for x in range(50)]
    })
    
    print("Input Data:")
    print(df.head(10))
    print()
    
    # Initialize agent
    agent = EDAToolsAgent(
        working_dir="/tmp/examples/eda",
        verbose=True
    )
    
    # Perform EDA
    result = await agent.perform_eda(
        data=df,
        target_variable="target"
    )
    
    if result["success"]:
        print("\n✅ EDA completed!")
        print(f"📄 Report: {result['report_path']}")
        print(f"📊 Visualizations: {len(result['visualizations'])} files")


async def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("AI DATA SCIENCE TEAM SDK - USAGE EXAMPLES")
    print("Anthropic Agent SDK Implementation")
    print("="*70)
    
    # Run examples
    await example_data_wrangling()
    await example_data_visualization()
    await example_data_cleaning()
    await example_feature_engineering()
    await example_pandas_analyst()
    await example_eda()
    
    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
