# src/agents/req_analyzer.py
from google.adk.agents import LlmAgent
from dotenv import load_dotenv
import os
from pathlib import Path

script_location = Path(__file__).resolve().parent.parent.parent
dotenv_path = script_location / ".env"
load_dotenv(dotenv_path=dotenv_path)

GEMINI_MODEL = "gemini-2.5-flash"

diagram_generator = LlmAgent(
    name="DiagramGeneratorAgent",
    model=GEMINI_MODEL,
    instruction="""You are a PlantUML Code Generator AI assistant specialized in creating component diagrams.
Based *only* on the architecture description provided below:
--- START ARCHITECTURE DESCRIPTION ---
{architecture_description}
--- END ARCHITECTURE DESCRIPTION ---

Generate VALID PlantUML code for a **component diagram** that visually represents this architecture.
- Represent the main components identified in the description.
- Show the key relationships (dependencies or communication lines) between them using arrows (`-->` or `->`).
- Label the relationships clearly using a colon `:` after the arrow (e.g., `[ComponentA] --> [ComponentB] : Uses API`). **Do NOT put labels inside brackets on the arrow itself like `-[Label]->` as that is invalid syntax.**
- Use rectangles or components for the elements. You can group related components using `rectangle` blocks if appropriate.
- Include a title for the diagram using `title Your Diagram Title`.
- The code MUST start *exactly* with `@startuml` on the first line.
- The code MUST end *exactly* with `@enduml` on the last line.

**Example of valid syntax for a relationship label:**
`[Frontend] --> [API Gateway] : Makes HTTP requests`

Output *only* the complete, valid PlantUML code itself, starting with `@startuml` and ending with `@enduml`.
**DO NOT include Markdown triple backticks (```) or the `plantuml` language identifier in your output.**
""",
    description="Generates valid PlantUML code for a component diagram based on architecture description.",
    output_key="diagram_code", # Output ghi vào state['diagram_code']
)
