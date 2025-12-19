"""
SQL Database Agent - Agent SDK Implementation

Connects to SQL databases and executes queries from natural language.
"""

from typing import Optional, Dict, Any
import pandas as pd
from pathlib import Path

from ai_data_science_team.base_agent import BaseAgentSDK


class SQLDatabaseAgent(BaseAgentSDK):
    """
    SQL Database Agent for querying databases with natural language.
    
    This agent can:
    - Connect to various SQL databases (PostgreSQL, MySQL, SQLite, etc.)
    - Generate SQL queries from natural language
    - Execute queries and return results as DataFrames
    - Perform joins, aggregations, and complex queries
    - Create data extraction pipelines
    
    Example:
        ```python
        from ai_data_science_team.agents import SQLDatabaseAgent
        
        agent = SQLDatabaseAgent()
        
        result = await agent.query_database(
            connection_string="sqlite:///data.db",
            user_instructions="Get total sales by region for last month"
        )
        
        df = agent.get_query_results()
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
        """Initialize the SQL Database Agent."""
        super().__init__(
            working_dir=working_dir or "/tmp/sql_database_agent",
            max_turns=max_turns,
            verbose=verbose,
            log=log,
            log_path=log_path
        )
        
        self.query_results = None
        self.generated_sql = None
    
    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for SQL database operations."""
        return f"""You are an expert SQL database agent specializing in querying databases and data extraction.

Your role is to connect to databases, generate SQL queries from natural language, and return results.

Working Directory: {self.working_dir}

Available Tools:
- Bash: Execute Python code with SQLAlchemy and pandas
- Read: Read database connection files
- Write: Save query results to CSV files

Process:
1. Read the database connection string from connection.txt (if provided)
2. Analyze the user's query requirements
3. Write Python code to:
   - Connect to the database using SQLAlchemy
   - Generate appropriate SQL query
   - Execute the query
   - Save results to query_results.csv
4. Execute the code using the Bash tool
5. Report what query was executed and results summary

SQL Best Practices:
- Use parameterized queries to prevent SQL injection
- Optimize queries for performance
- Use appropriate JOINs
- Add LIMIT clauses for exploratory queries
- Handle NULL values appropriately
- Use meaningful column aliases

Code Template:
```python
import pandas as pd
from sqlalchemy import create_engine, text

# Read connection string
with open('connection.txt', 'r') as f:
    connection_string = f.read().strip()

# Connect to database
engine = create_engine(connection_string)

# Generate and execute SQL query
sql_query = '''
SELECT column1, column2
FROM table_name
WHERE condition
'''

# Execute query
with engine.connect() as conn:
    df = pd.read_sql(text(sql_query), conn)

# Save results
df.to_csv('query_results.csv', index=False)

# Save the SQL query
with open('generated_sql.txt', 'w') as f:
    f.write(sql_query)

print(f"Query returned {len(df)} rows")
```

Be precise with SQL syntax, handle errors gracefully, and ensure data security."""
    
    async def query_database(
        self,
        connection_string: str,
        user_instructions: str,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Query a database using natural language instructions.
        
        Args:
            connection_string: SQLAlchemy connection string (e.g., "sqlite:///data.db")
            user_instructions: Natural language description of the query.
            save_results: Whether to save results to CSV.
            
        Returns:
            Dictionary containing:
                - query_results: DataFrame with query results
                - generated_sql: The SQL query that was executed
                - success: Whether query succeeded
                - messages: Agent messages
        """
        # Save connection string
        conn_file = self.working_dir / "connection.txt"
        with open(conn_file, 'w') as f:
            f.write(connection_string)
        
        # Build the prompt
        prompt = f"""Query the database according to these instructions:

{user_instructions}

Database Connection: {connection_string}

Steps:
1. Connect to the database using the connection string in connection.txt
2. Analyze the database schema if needed
3. Generate an appropriate SQL query
4. Execute the query
5. Save results to query_results.csv
6. Save the SQL query to generated_sql.txt

Provide a summary of the query and results."""
        
        # Execute the agent
        if self.verbose:
            print(f"🗄️  Database: {connection_string}")
            print(f"📝 Query: {user_instructions}\n")
        
        await self._execute_query(prompt)
        
        # Load the results
        df_results = self._load_dataframe("query_results.csv")
        
        # Load generated SQL
        sql_file = self.working_dir / "generated_sql.txt"
        generated_sql = None
        if sql_file.exists():
            with open(sql_file, 'r') as f:
                generated_sql = f.read()
        
        if df_results is not None:
            self.query_results = df_results
            self.generated_sql = generated_sql
            
            if self.verbose:
                print(f"📊 Results: {df_results.shape[0]} rows × {df_results.shape[1]} columns")
                if generated_sql:
                    print(f"\n📝 Generated SQL:\n{generated_sql}\n")
            
            self.response = {
                "query_results": df_results,
                "generated_sql": generated_sql,
                "success": True,
                "messages": self.messages,
                "output_path": str(self.working_dir / "query_results.csv")
            }
        else:
            if self.verbose:
                print("⚠️  No query results generated")
            
            self.response = {
                "query_results": None,
                "generated_sql": generated_sql,
                "success": False,
                "messages": self.messages,
                "output_path": None
            }
        
        return self.response
    
    def get_query_results(self) -> Optional[pd.DataFrame]:
        """Get the query results DataFrame."""
        return self.query_results
    
    def get_generated_sql(self) -> Optional[str]:
        """Get the generated SQL query."""
        return self.generated_sql
    
    async def list_tables(self, connection_string: str) -> Dict[str, Any]:
        """
        List all tables in the database.
        
        Args:
            connection_string: SQLAlchemy connection string.
            
        Returns:
            Dictionary with table names and information.
        """
        # Save connection string
        conn_file = self.working_dir / "connection.txt"
        with open(conn_file, 'w') as f:
            f.write(connection_string)
        
        prompt = f"""List all tables in the database.

Database Connection: {connection_string}

Use SQLAlchemy to:
1. Connect to the database
2. Get list of all tables
3. For each table, get column names and types
4. Save the information to tables_info.csv

Format: table_name, column_name, column_type"""
        
        await self._execute_query(prompt)
        
        df_tables = self._load_dataframe("tables_info.csv")
        
        return {
            "tables_info": df_tables,
            "success": df_tables is not None,
            "messages": self.messages
        }
