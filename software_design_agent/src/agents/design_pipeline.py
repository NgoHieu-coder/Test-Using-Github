# src/agents/design_pipeline.py
from google.adk.agents import SequentialAgent
from .req_analyzer import req_analyzer
from .arch_designer import arch_designer
from .diagram_generator import diagram_generator

design_pipeline = SequentialAgent(
    name="SoftwareDesignPipelineAgent",
    # Thứ tự chạy: Phân tích -> Thiết kế -> Vẽ sơ đồ
    sub_agents=[req_analyzer, arch_designer, diagram_generator],
    description="Executes a sequence of requirements analysis, architecture design, and diagram generation.",
)

# Đặt tên biến là root_agent cho ADK Web
root_agent = design_pipeline
