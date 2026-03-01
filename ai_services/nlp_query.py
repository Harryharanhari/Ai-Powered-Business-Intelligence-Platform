from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.chat_models import ChatOllama
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from the local .env in ai_services/
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

class NLPQueryService:
    def __init__(self, file_path, model_name=None):
        self.df = pd.read_csv(file_path)
        self.ollama_key = os.environ.get("OLLAMA_API_KEY")
        self.ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = model_name or os.environ.get("OLLAMA_MODEL", "llama3")

    def get_suggestions(self):
        """Generate smart suggestions based on columns."""
        cols = self.df.columns.tolist()
        num_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = self.df.select_dtypes(exclude=['number']).columns.tolist()
        
        suggestions = []
        if num_cols:
            suggestions.append(f"What is the average {num_cols[0]}?")
            if len(num_cols) > 1:
                suggestions.append(f"Compare {num_cols[0]} vs {num_cols[1]}")
        if cat_cols:
            suggestions.append(f"Unique count of {cat_cols[0]}")
            if num_cols:
                suggestions.append(f"Total {num_cols[0]} by {cat_cols[0]}?")
        
        return suggestions[:4]

    def query(self, user_question):
        try:
            # Use ChatOllama for better instruction following in agents
            if not self.ollama_url:
                return "Config Error: OLLAMA_BASE_URL is not set in your .env file."
            
            llm = ChatOllama(
                base_url=self.ollama_url, 
                model=self.model_name,
                temperature=0,
                timeout=120 # Increased timeout for long-running analyst tasks
            )
            
            # Create a more robust agent
            agent = create_pandas_dataframe_agent(
                llm, 
                self.df, 
                verbose=True, 
                allow_dangerous_code=True,
                max_iterations=15, # Maximized iteration allowance for deeper data probing
                early_stopping_method="force",
                handle_parsing_errors=True
            )
            
            # Execute query with enhanced context grounding
            schema_info = f"Columns available: {', '.join(self.df.columns)}. Types: {self.df.dtypes.to_dict()}."
            response = agent.invoke({
                "input": f"Context: This dataset has {len(self.df)} rows. {schema_info}\n"
                         f"Question: {user_question}\n"
                         f"Instruction: Use the data to answer accurately. If unsure, say you don't have enough data."
            })
            
            return response.get('output', "I processed the data but couldn't formulate a final answer.")
            
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower():
                return f"Connection Error: Could not reach Ollama at {self.ollama_url}. Is the service running?"
            return f"Analysis Error: {error_msg}"
