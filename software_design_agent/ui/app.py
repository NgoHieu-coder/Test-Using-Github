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
        "(e.g., `streamlit run ui/app.py`) and that `src/agents/__init__.py` "
        f"correctly imports `root_agent`. Error details: {e}"
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
# Store services in Streamlit's session state to persist across reruns
if 'session_service' not in st.session_state:
    st.session_state.session_service = InMemorySessionService()
    print("Initialized InMemorySessionService.")

if 'runner' not in st.session_state:
    try:
        # Pass the already initialized session_service
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

# Retrieve from session state for easier access
session_service = st.session_state.session_service
runner = st.session_state.runner

# --- Streamlit UI Layout ---
st.set_page_config(layout="wide")
st.title("✨ AI Software Design Assistant ✨")
st.caption("Input your requirements below to generate a structured analysis, architecture proposal, and a PlantUML component diagram.")

# --- Session Management ---
# Ensure a session ID exists for the current Streamlit session
if "adk_session_id" not in st.session_state:
    st.session_state.adk_session_id = f"st_session_{os.urandom(8).hex()}"
    print(f"Generated new ADK session ID: {st.session_state.adk_session_id}")
    try:
        # Create the session in the ADK service when the Streamlit session starts
        asyncio.run(st.session_state.session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=st.session_state.adk_session_id
        ))
        print(f"Successfully created ADK session {st.session_state.adk_session_id} in service.")
        # Optionally display session ID for debugging
        # st.info(f"Using Session ID: {st.session_state.adk_session_id}")
    except Exception as e:
        st.error(f"Fatal Error: Failed to create ADK session. Details: {e}")
        st.exception(e)
        st.stop()
# else:
    # print(f"Using existing ADK session ID: {st.session_state.adk_session_id}")


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
    adk_session_id = st.session_state.adk_session_id # Get current session ID

    with st.spinner("Pipeline Running: Analyzing Requirements -> Designing Architecture -> Generating Diagram..."):
        try:
            # Prepare the user input message for the ADK Runner
            user_content = types.Content(role='user', parts=[types.Part(text=user_requirements_input)])
            final_state = None # Initialize final_state

            # Define the asynchronous function to run the agent pipeline
            async def run_pipeline_async():
                print(f"--- [Session: {adk_session_id}] Starting runner.run_async ---")
                try:
                    # Stream events - primarily used here to ensure the run completes
                    async for event in runner.run_async(
                        user_id=USER_ID,
                        session_id=adk_session_id,
                        new_message=user_content
                    ):
                        # Log events for debugging if needed
                        # print(f"Raw Event ({adk_session_id}): {event}")
                        pass # We primarily care about the final state
                    print(f"--- [Session: {adk_session_id}] Finished runner.run_async stream ---")
                except Exception as stream_error:
                    # Catch errors during the agent execution stream
                    print(f"!!! EXCEPTION during run_async loop for session {adk_session_id}: {stream_error}")
                    st.error(f"An error occurred while the agent was processing: {stream_error}")
                    raise stream_error # Re-raise to stop further processing

                # Attempt to retrieve the final session state ONLY if streaming succeeded
                print(f"--- [Session: {adk_session_id}] Attempting to get session state ---")
                current_session_obj = await session_service.get_session(
                    app_name=APP_NAME, user_id=USER_ID, session_id=adk_session_id
                )

                if current_session_obj is None:
                    print(f"!!! FAILED to retrieve session state for {adk_session_id} after stream ---")
                    st.error(f"Critical Error: Could not retrieve session state after agent execution completed. Session ID: {adk_session_id}. Check terminal logs for earlier errors.")
                    return None # Indicate failure
                else:
                    print(f"--- [Session: {adk_session_id}] Successfully retrieved session state ---")
                    state_keys = current_session_obj.state.keys() if current_session_obj.state else "Empty State Dictionary"
                    print(f"Retrieved State Keys: {state_keys}")
                    return current_session_obj.state # Return the state dictionary

            # Run the asynchronous function using asyncio.run()
            final_state = asyncio.run(run_pipeline_async())

            # --- Display Results ---
            st.divider() # Visual separator
            if final_state is None:
                # Error message already shown if session retrieval failed
                 st.warning("Processing stopped due to an error during agent execution or state retrieval.")
            elif not final_state: # Checks if the dictionary is empty
                 st.warning("Agent pipeline completed but returned an empty state. Check agent logic and output keys.")
            else:
                st.success("✅ Design Pipeline Completed Successfully!")

                # Use columns for better layout
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

                        # Attempt to render the diagram
                        st.subheader("🖼️ Diagram Preview (Rendered)")
                        try:
                            # PlantUML encoding function (ensure correct imports: base64, zlib, string)
                            def plantuml_encode(plantuml_text):
                                p_utf8 = plantuml_text.encode('utf-8')
                                compressed = zlib.compress(p_utf8, level=9)
                                plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
                                standard_alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
                                transtable = bytes.maketrans(standard_alphabet.encode('utf-8'), plantuml_alphabet.encode('utf-8'))
                                encoded = base64.b64encode(compressed).translate(transtable).decode('utf-8')
                                return encoded

                            encoded_diagram_code = plantuml_encode(plantuml_code_output)
                            plantuml_image_url = f"http://www.plantuml.com/plantuml/png/~1{encoded_diagram_code}"
                            st.image(plantuml_image_url)
                            st.caption("Diagram rendered via public PlantUML web server.")

                        except Exception as render_error:
                            st.error(f"Could not render diagram preview: {render_error}")
                            st.warning("Please verify the generated PlantUML code's validity.")
                    else:
                        st.warning("_Agent did not generate PlantUML code._")


        except Exception as e:
            # Catch errors from asyncio.run or other synchronous parts
            st.error(f"An unexpected error occurred: {e}")
            st.exception(e) # Display detailed traceback in Streamlit

elif submitted and not user_requirements_input:
    # Handle empty input submission
    st.warning("⚠️ Please enter your software requirements in the text area.")