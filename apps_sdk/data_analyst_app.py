"""
Data Analyst Streamlit App - Agent SDK Version

A simple web interface for the Pandas Data Analyst agent.
"""

import streamlit as st
import pandas as pd
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_data_science_team_sdk.multiagents import PandasDataAnalyst


st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide"
)

st.title("🤖 AI Data Analyst")
st.markdown("*Powered by Anthropic Agent SDK*")

st.markdown("""
Upload your data and let the AI Data Analyst perform comprehensive analysis,
create visualizations, and provide insights.
""")

# Sidebar
st.sidebar.header("Configuration")

working_dir = st.sidebar.text_input(
    "Working Directory",
    value="/tmp/streamlit_analyst"
)

max_turns = st.sidebar.slider(
    "Max Agent Turns",
    min_value=5,
    max_value=30,
    value=20
)

verbose = st.sidebar.checkbox("Verbose Output", value=True)

# Main content
st.header("1. Upload Data")

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=['csv']
)

if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file)
    
    st.success(f"✅ Loaded {len(df)} rows × {len(df.columns)} columns")
    
    # Show data preview
    with st.expander("📊 Data Preview"):
        st.dataframe(df.head(20))
    
    # Show data info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", len(df))
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Missing Values", df.isnull().sum().sum())
    
    # Analysis configuration
    st.header("2. Configure Analysis")
    
    analysis_goal = st.text_area(
        "Analysis Goal",
        value="Perform comprehensive exploratory data analysis and provide insights.",
        height=100,
        help="Describe what you want to learn from the data"
    )
    
    # Target variable (optional)
    columns = ["None"] + list(df.columns)
    target_variable = st.selectbox(
        "Target Variable (Optional)",
        options=columns,
        help="Select the target variable for supervised learning analysis"
    )
    
    if target_variable == "None":
        target_variable = None
    
    # Run analysis
    st.header("3. Run Analysis")
    
    if st.button("🚀 Start Analysis", type="primary"):
        with st.spinner("🤖 AI Agent is analyzing your data..."):
            try:
                # Initialize analyst
                analyst = PandasDataAnalyst(
                    working_dir=working_dir,
                    max_turns=max_turns,
                    verbose=verbose
                )
                
                # Run analysis
                result = asyncio.run(analyst.analyze(
                    data=df,
                    analysis_goal=analysis_goal,
                    target_variable=target_variable
                ))
                
                if result["success"]:
                    st.success("✅ Analysis completed!")
                    
                    # Display report
                    st.header("4. Analysis Report")
                    
                    report = result.get("analysis_report")
                    if report:
                        st.markdown(report)
                    
                    # Display insights
                    insights = result.get("insights")
                    if insights:
                        st.header("💡 Key Insights")
                        st.info(insights)
                    
                    # Display visualizations
                    visualizations = result.get("visualizations", [])
                    if visualizations:
                        st.header("📊 Visualizations")
                        
                        for viz_file in visualizations:
                            viz_path = Path(viz_file)
                            if viz_path.exists():
                                st.subheader(viz_path.stem.replace('_', ' ').title())
                                
                                # Read and display HTML
                                with open(viz_path, 'r') as f:
                                    html_content = f.read()
                                st.components.v1.html(html_content, height=500, scrolling=True)
                    
                    # Download options
                    st.header("5. Download Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if report:
                            st.download_button(
                                label="📄 Download Report (Markdown)",
                                data=report,
                                file_name="analysis_report.md",
                                mime="text/markdown"
                            )
                    
                    with col2:
                        if insights:
                            st.download_button(
                                label="💡 Download Insights",
                                data=insights,
                                file_name="insights.txt",
                                mime="text/plain"
                            )
                    
                    # Cleaned data
                    cleaned_data = result.get("cleaned_data")
                    if cleaned_data is not None:
                        st.subheader("🧹 Cleaned Data")
                        st.dataframe(cleaned_data.head(20))
                        
                        csv = cleaned_data.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Cleaned Data (CSV)",
                            data=csv,
                            file_name="cleaned_data.csv",
                            mime="text/csv"
                        )
                
                else:
                    st.error("❌ Analysis failed. Please check the logs.")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)

else:
    st.info("👆 Upload a CSV file to get started")

# Footer
st.markdown("---")
st.markdown("""
**AI Data Science Team SDK** - Powered by [Anthropic Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)

This app uses the refactored Agent SDK implementation for simplified, powerful data analysis.
""")
