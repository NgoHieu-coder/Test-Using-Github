## Guideline Hoàn chỉnh: Xây dựng Multi-Agent Software Design App (Track 2, Topic 3) với Google ADK & Streamlit

Đây là hướng dẫn chi tiết từng bước để xây dựng ứng dụng AI Agent sinh thiết kế phần mềm, bao gồm code đầy đủ cho các agent và giao diện Streamlit, sử dụng `gemini-2.5-pro`.

---

### Bước 1: Thiết lập Dự án và Môi trường (Project Setup) 🏗️

1.  **Tạo cấu trúc thư mục:**
    ```
    software_design_agent/
    ├── .env
    ├── .gitignore
    ├── requirements.txt
    ├── venv/                 # Thư mục môi trường ảo (sẽ được tạo)
    └── src/
    │   ├── __init__.py
    │   └── agents/
    │       ├── __init__.py
    │       ├── req_analyzer.py
    │       ├── arch_designer.py
    │       ├── diagram_generator.py
    │       └── design_pipeline.py
    └── ui/
        └── app.py            # Code giao diện Streamlit
    ```

2.  **Tạo file `.env`:** (Trong thư mục `software_design_agent/`)
    ```dotenv!
    # software_design_agent/.env
    # Thay thế bằng API Key thực của Google AI Studio hoặc Vertex AI
    GOOGLE_API_KEY=AIzaSy...your_actual_google_api_key...
    # (Tùy chọn) Chỉ định model ở đây nếu muốn ghi đè code
    GEMINI_MODEL_NAME="gemini-1.5-flash"
    ```

3.  **Tạo file `.gitignore`:** (Trong thư mục `software_design_agent/`)
    ```gitignore!
    # software_design_agent/.gitignore
    .env
    __pycache__/
    *.pyc
    venv/
    *.log
    ```

4.  **Tạo file `requirements.txt`:** (Trong thư mục `software_design_agent/`)
    ```text!
    # software_design_agent/requirements.txt
    google-agent-development-kit
    google-generativeai
    python-dotenv
    streamlit
    ```

5.  **Thiết lập môi trường ảo và cài đặt:**
    * Mở terminal trong thư mục `software_design_agent/`.
    * Tạo môi trường ảo: `python -m venv venv`
    * Kích hoạt môi trường:
        * Windows PowerShell: `.\venv\Scripts\Activate.ps1`
        * Linux/macOS: `source venv/bin/activate`
    * Cài đặt thư viện: `pip install -r requirements.txt`

---

### Bước 2: Viết Code cho các Agent Con (Sub-Agents) 🤖

1.  **`src/__init__.py`:** (Để trống file này)

2.  **`src/agents/__init__.py`:** (Import các agent để dễ dàng truy cập)
    ```python!
    # src/agents/__init__.py
    """Initializes the agents package and exposes the root agent."""

    # Import các agent con
    from .req_analyzer import req_analyzer
    from .arch_designer import arch_designer
    from .diagram_generator import diagram_generator

    # Import agent điều phối chính và đặt tên là root_agent
    from .design_pipeline import root_agent

    # (Tùy chọn) Có thể định nghĩa __all__ nếu muốn kiểm soát import chặt chẽ hơn
    # __all__ = ["req_analyzer", "arch_designer", "diagram_generator", "root_agent"]
    ```

3.  **`src/agents/req_analyzer.py`:** (Agent phân tích yêu cầu)
    ```python!
    # src/agents/req_analyzer.py
    """Agent to analyze and structure raw software requirements."""

    from google.adk.agents import LlmAgent
    from dotenv import load_dotenv
    import os
    from pathlib import Path

    # Xác định đường dẫn đến thư mục gốc của dự án (nơi chứa .env)
    project_root = Path(__file__).resolve().parent.parent.parent
    dotenv_path = project_root / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    # Sử dụng biến môi trường để lấy model name hoặc dùng mặc định
    GEMINI_MODEL = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

    req_analyzer = LlmAgent(
        name="RequirementsAnalyzerAgent",
        model=GEMINI_MODEL,
        instruction="""You are a Business Analyst AI assistant.
    Your task is to analyze the user's raw software requirements provided in their *last message*.
    Carefully identify and extract the following:
    1.  **Main Features/Functionalities:** List the core capabilities the software should have.
    2.  **User Roles (if mentioned):** Identify different types of users and their potential interactions.
    3.  **Key Non-Functional Requirements (if mentioned):** Note aspects like performance needs, security considerations, platform constraints, etc.

    Structure your analysis clearly using Markdown headings (e.g., ## Main Features) and bullet points.
    Focus only on extracting and structuring information from the provided text.
    Output *only* the structured analysis based *solely* on the user's last message. Do not add introductions or conclusions.
    """,
        description="Analyzes raw software requirements from the user's input and structures them.",
        output_key="structured_requirements" # Kết quả sẽ được lưu vào state['structured_requirements']
    )
    ```

4.  **`src/agents/arch_designer.py`:** (Agent thiết kế kiến trúc)
    ```python!
    # src/agents/arch_designer.py
    """Agent to propose a high-level system architecture."""

    from google.adk.agents import LlmAgent
    from dotenv import load_dotenv
    import os
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent.parent
    dotenv_path = project_root / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    GEMINI_MODEL = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

    arch_designer = LlmAgent(
        name="ArchitectureDesignerAgent",
        model=GEMINI_MODEL,
        instruction="""You are a Software Architect AI assistant.
    Based *only* on the structured requirements provided below:
    --- START REQUIREMENTS ---
    {structured_requirements}
    --- END REQUIREMENTS ---

    Propose a suitable high-level system architecture. Your proposal should include:
    1.  **Architecture Style:** (e.g., Monolithic, Microservices, Layered, Event-Driven). Briefly justify your choice based on the requirements.
    2.  **Main Components:** Identify the key logical components (e.g., Frontend (Web/Mobile), Backend API Gateway, Authentication Service, Product Service, Order Service, Database (specify type if possible like SQL/NoSQL)).
    3.  **Component Responsibilities:** Briefly describe the main responsibility of each component.
    4.  **Key Interactions:** Describe the essential communication paths between components (e.g., Frontend calls API Gateway, Order Service reads from Product Service DB).

    Keep the description concise and focused on the core architectural structure. Use Markdown for clarity.
    Output *only* the architecture proposal. Do not add introductions or conclusions.
    """,
        description="Proposes a high-level system architecture based on structured requirements.",
        output_key="architecture_description", # Output sẽ ghi vào state['architecture_description']
    )
    ```

5.  **`src/agents/diagram_generator.py`:** (Agent sinh mã PlantUML - **Instruction đã sửa**)
    ```python!
    # src/agents/diagram_generator.py
    """Agent to generate PlantUML code for a component diagram."""

    from google.adk.agents import LlmAgent
    from dotenv import load_dotenv
    import os
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent.parent
    dotenv_path = project_root / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    GEMINI_MODEL = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

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
    **DO NOT include any Markdown backticks (```) or language identifiers like `plantuml` in your output.**
    """,
        description="Generates valid PlantUML code for a component diagram based on architecture description.",
        output_key="diagram_code", # Output ghi vào state['diagram_code']
    )
    ```

---

### Bước 3: Định nghĩa Agent Điều phối (Orchestrator) 🎼

1.  **`src/agents/design_pipeline.py`:**
    ```python!
    # src/agents/design_pipeline.py
    """Defines the sequential pipeline agent that orchestrates the design process."""

    from google.adk.agents import SequentialAgent
    # Import các agent con đã định nghĩa
    from .req_analyzer import req_analyzer
    from .arch_designer import arch_designer
    from .diagram_generator import diagram_generator

    # Tạo SequentialAgent: Các agent con sẽ chạy theo thứ tự trong list này
    design_pipeline = SequentialAgent(
        name="SoftwareDesignPipelineAgent",
        # Thứ tự thực thi: Phân tích -> Thiết kế -> Sinh Sơ đồ
        sub_agents=[
            req_analyzer,
            arch_designer,
            diagram_generator
            ],
        description="Orchestrates the process of analyzing requirements, designing architecture, and generating a PlantUML diagram.",
        # ADK tự động quản lý việc truyền state
    )

    # Đặt tên biến là `root_agent` để ADK Web Server và Streamlit UI có thể tìm thấy
    root_agent = design_pipeline
    ```

---

### Bước 4: Tích hợp Giao diện Người dùng (UI Integration) 🎨

1.  **`ui/app.py`:** (Code Streamlit hoàn chỉnh)
    ```python!
    # ui/app.py
    import streamlit as st
    import asyncio
    import os
    import sys
    import base64
    import zlib
    import string
    from pathlib import Path
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    # --- Dynamic Import of root_agent ---
    # Add project root to sys.path to allow importing 'src'
    project_root_ui = str(Path(__file__).resolve().parent.parent)
    if project_root_ui not in sys.path:
        sys.path.append(project_root_ui)

    try:
        # Attempt to import the main agent pipeline
        from src.agents import root_agent
    except ImportError as e:
        # Display error and stop if agent cannot be imported
        st.error(
            "Failed to import `root_agent` from `src.agents`. "
            "Ensure you run Streamlit from the project root directory "
            "(e.g., `streamlit run ui/app.py` from software_design_agent/) "
            f"and that `src/agents/__init__.py` correctly imports `root_agent`. Error: {e}"
        )
        st.stop()
    except Exception as e:
        # Catch other potential errors during import
        st.error(f"An unexpected error occurred during agent import: {e}")
        st.stop()

    # --- Configuration ---
    APP_NAME = "ai_software_designer"
    USER_ID = "streamlit_demo_user"

    # --- Initialize Runner and Session Service (using Streamlit session state) ---
    if 'session_service' not in st.session_state:
        st.session_state.session_service = InMemorySessionService()
        print("Initialized InMemorySessionService.")

    if 'runner' not in st.session_state:
        try:
            st.session_state.runner = Runner(
                agent=root_agent,
                app_name=APP_NAME,
                session_service=st.session_state.session_service
            )
            print("Initialized ADK Runner.")
        except Exception as e:
            st.error(f"Fatal Error: Could not initialize ADK Runner. Details: {e}")
            st.exception(e)
            st.stop()

    session_service = st.session_state.session_service
    runner = st.session_state.runner

    # --- Streamlit UI Layout ---
    st.set_page_config(layout="wide")
    st.title("✨ AI Software Design Assistant ✨")
    st.caption("Input your requirements below to generate a structured analysis, architecture proposal, and a PlantUML component diagram.")

    # --- Session Management ---
    if "adk_session_id" not in st.session_state:
        st.session_state.adk_session_id = f"st_session_{os.urandom(8).hex()}"
        print(f"Generated new ADK session ID: {st.session_state.adk_session_id}")
        try:
            asyncio.run(st.session_state.session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=st.session_state.adk_session_id
            ))
            print(f"Successfully created ADK session {st.session_state.adk_session_id} in service.")
        except Exception as e:
            st.error(f"Fatal Error: Failed to create ADK session. Details: {e}")
            st.exception(e)
            st.stop()

    # --- Input Form ---
    with st.form("design_input_form"):
        st.subheader("Enter Software Requirements")
        user_requirements_input = st.text_area(
            "Describe the software you want to design:",
            height=150,
            placeholder="Example: A simple online bookstore where users can browse books, add to cart, and checkout. Admins need to add new books."
            )
        submitted = st.form_submit_button("🚀 Generate Design Document")

    # --- Agent Execution and Output Display ---
    if submitted and user_requirements_input:
        st.info("🤖 Processing your request... The AI agents are working.")
        adk_session_id = st.session_state.adk_session_id

        with st.spinner("Pipeline Running: Analyzing -> Designing -> Generating Diagram..."):
            try:
                user_content = types.Content(role='user', parts=[types.Part(text=user_requirements_input)])
                final_state = None

                # Define the async function to run the pipeline
                async def run_pipeline_async():
                    print(f"--- [Session: {adk_session_id}] Starting runner.run_async ---")
                    try:
                        async for event in runner.run_async(
                            user_id=USER_ID,
                            session_id=adk_session_id,
                            new_message=user_content
                        ):
                            # print(f"Raw Event ({adk_session_id}): {event}") # Uncomment for debug
                            pass
                        print(f"--- [Session: {adk_session_id}] Finished runner.run_async stream ---")
                    except Exception as stream_error:
                        print(f"!!! EXCEPTION during run_async loop for session {adk_session_id}: {stream_error}")
                        st.error(f"An error occurred while the agent was processing: {stream_error}")
                        raise stream_error # Stop processing

                    print(f"--- [Session: {adk_session_id}] Attempting to get session state ---")
                    current_session_obj = await session_service.get_session(
                        app_name=APP_NAME, user_id=USER_ID, session_id=adk_session_id
                    )

                    if current_session_obj is None:
                        print(f"!!! FAILED to retrieve session state for {adk_session_id} after stream ---")
                        st.error(f"Critical Error: Could not retrieve session state after agent execution. Session ID: {adk_session_id}. Check terminal logs.")
                        return None
                    else:
                        print(f"--- [Session: {adk_session_id}] Successfully retrieved session state ---")
                        state_keys = current_session_obj.state.keys() if current_session_obj.state else "Empty State Dictionary"
                        print(f"Retrieved State Keys: {state_keys}")
                        return current_session_obj.state

                # Run the async function
                final_state = asyncio.run(run_pipeline_async())

                # --- Display Results ---
                st.divider()
                if final_state is None:
                     st.warning("Processing stopped due to an error during agent execution or state retrieval.")
                elif not final_state:
                     st.warning("Agent pipeline completed but returned an empty state. Check agent logic and output keys in terminal logs.")
                else:
                    st.success("✅ Design Pipeline Completed Successfully!")

                    col_analysis, col_diagram = st.columns(2)

                    with col_analysis:
                        st.subheader("📝 Structured Requirements Analysis")
                        req_analysis = final_state.get("structured_requirements", "").strip()
                        if req_analysis:
                            st.markdown(req_analysis)
                        else:
                            st.warning("_Agent did not generate requirements analysis._")

                        st.divider()

                        st.subheader("🏛️ Proposed Architecture Description")
                        arch_desc = final_state.get("architecture_description", "").strip()
                        if arch_desc:
                            st.markdown(arch_desc)
                        else:
                            st.warning("_Agent did not propose an architecture._")

                    with col_diagram:
                        st.subheader("📊 PlantUML Diagram Code")
                        plantuml_code_output = final_state.get("diagram_code", "").strip()

                        if plantuml_code_output:
                            st.code(plantuml_code_output, language="plantuml")

                            st.subheader("🖼️ Diagram Preview (Rendered)")
                            try:
                                # PlantUML encoding function
                                def plantuml_encode(plantuml_text):
                                    p_utf8 = plantuml_text.encode('utf-8')
                                    compressed = zlib.compress(p_utf8, level=9)
                                    plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
                                    standard_alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
                                    transtable = bytes.maketrans(standard_alphabet.encode('utf-8'), plantuml_alphabet.encode('utf-8'))
                                    encoded = base64.b64encode(compressed).translate(transtable).decode('utf-8')
                                    return encoded

                                encoded_diagram_code = plantuml_encode(plantuml_code_output)
                                # Thêm tiền tố ~1 để kích hoạt chế độ nén chuẩn (nếu cần, tùy server PlantUML)
                                plantuml_image_url = f"http://www.plantuml.com/plantuml/png/~1{encoded_diagram_code}"
                                st.image(plantuml_image_url)
                                st.caption("Diagram rendered via public PlantUML web server.")

                            except Exception as render_error:
                                st.error(f"Could not render diagram preview: {render_error}")
                                st.warning("Please verify the generated PlantUML code's validity using an online renderer.")
                        else:
                            st.warning("_Agent did not generate PlantUML code._")

            except Exception as e:
                # Catch errors from asyncio.run or sync parts
                st.error(f"An unexpected error occurred in the Streamlit app: {e}")
                st.exception(e) # Display traceback

    elif submitted and not user_requirements_input:
        st.warning("⚠️ Please enter your software requirements in the text area.")

    ```

---

### Bước 5: Chạy và Kiểm thử (Testing) 🧪

1.  **Chạy Ứng dụng Streamlit:**
    * Mở terminal trong thư mục gốc (`software_design_agent/`).
    * Kích hoạt môi trường ảo (`.\venv\Scripts\Activate.ps1` hoặc `source venv/bin/activate`).
    * **Quan trọng:** Chạy Streamlit từ thư mục gốc để đảm bảo import `src.agents` hoạt động:
        ```bash
        streamlit run ui/app.py
        ```
2.  **Mở Giao diện Web:** Truy cập `http://localhost:8501` (hoặc cổng Streamlit cung cấp).
3.  **Nhập Yêu cầu:** Gõ yêu cầu phần mềm vào ô `text_area`.
4.  **Nhấn "Generate Design Document".**
5.  **Quan sát Kết quả:**
    * Xem các phần "Structured Requirements", "Architecture Description", "PlantUML Diagram Code" và "Diagram Preview" được hiển thị trên giao diện Streamlit.
    * **Kiểm tra Terminal:** Theo dõi các dòng log bắt đầu bằng `---` hoặc `!!!` để hiểu luồng chạy và phát hiện lỗi. Nếu có lỗi `KeyError` hoặc lỗi API từ Gemini, nó sẽ được in ra terminal và có thể cả trên UI.
    * Nếu sơ đồ không render được, hãy sao chép mã PlantUML từ UI và dán vào [PlantText](https://www.planttext.com/) để kiểm tra cú pháp.

---

### Bước 6: Hoàn thiện và Chuẩn bị Demo 🎬

1.  **Tinh chỉnh Prompts:** Dựa trên kết quả kiểm thử, quay lại **Bước 2** và cải thiện `instruction` cho các agent để chúng hoạt động chính xác hơn, liên kết tốt hơn, và sinh mã PlantUML đúng cú pháp hơn.
2.  **Giao diện:** Đảm bảo giao diện Streamlit dễ sử dụng và hiển thị kết quả rõ ràng.
3.  **Xử lý lỗi:** Cải thiện cách ứng dụng báo lỗi cho người dùng.
4.  **Chuẩn bị Slide & GitHub:** Tạo slide trình bày và đẩy toàn bộ code lên GitHub. Đảm bảo file `.env` nằm trong `.gitignore`.
