# src/agents/req_analyzer.py
from google.adk.agents import LlmAgent
from dotenv import load_dotenv
import os
from pathlib import Path

script_location = Path(__file__).resolve().parent.parent.parent
dotenv_path = script_location / ".env"
load_dotenv(dotenv_path=dotenv_path)

GEMINI_MODEL = "gemini-2.5-flash"

arch_designer = LlmAgent(
    name="ArchitectureDesignerAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Software Architect AI.
Based on the structured requirements '{structured_requirements}', propose a high-level system architecture.
Describe the main components (e.g., Frontend, Backend API, Database, Authentication Service) and their primary responsibilities and interactions.
Keep the description concise and focus on the core structure.
Output *only* the architecture description.
""",
    description="Proposes a high-level system architecture based on requirements.",
    output_key="architecture_description",
)
