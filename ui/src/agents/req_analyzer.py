# src/agents/req_analyzer.py
from google.adk.agents import LlmAgent
from dotenv import load_dotenv
import os
from pathlib import Path

script_location = Path(__file__).resolve().parent.parent.parent
dotenv_path = script_location / ".env"
load_dotenv(dotenv_path=dotenv_path)

GEMINI_MODEL = "gemini-2.5-flash" # Hoặc gemini-pro

req_analyzer = LlmAgent(
    name="RequirementsAnalyzerAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Business Analyst AI.
Analyze the user's software requirements provided in their *last message*.
Identify the main features, user roles (if any), and key non-functional requirements (like performance, security).
Structure the analysis clearly, perhaps using bullet points for features.
Output *only* the structured analysis.
""",
    description="Analyzes and structures raw software requirements.",
    output_key="structured_requirements"
)
