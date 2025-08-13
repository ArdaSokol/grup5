import os
import requests
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# Your DenizBank Qwen API endpoint
API_URL = "https://api-qwen-31-load-predictor-tmp-automation-test-3.apps.datascience.prod2.deniz.denizbank.com"

# Define a custom tool to call the endpoint
@tool("qwen_load_predictor", return_direct=True)
def qwen_load_predictor() -> str:
    """Call the Qwen Load Predictor API (GET) and return the response."""
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    return r.text  # or r.json() if it's JSON

# Set your OpenAI API key in environment (replace with your key)
os.environ["OPENAI_API_KEY"] = "sk-your-openai-key"

# Initialize the LLM and agent
llm = ChatOpenAI(temperature=0)
agent = initialize_agent(
    tools=[qwen_load_predictor],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# Ask the agent to call the API
response = agent.run("Call the Qwen Load Predictor API and show the result.")
print("\n--- API Response ---")
print(response)
