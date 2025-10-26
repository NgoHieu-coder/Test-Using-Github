from dotenv import load_dotenv
from google.adk.agents import Agent
import google.generativeai as genai

load_dotenv()

def generate_python_function(description: str) -> dict:
    """Generates a basic Python function based on a description using the Gemini API.

    Args:
        description (str): A natural language description of the function's purpose.

    Returns:
        dict: status and the generated code or an error message.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        # 3. Tạo prompt yêu cầu chỉ sinh ra cấu trúc hàm
        prompt = (
            "Generate ONLY the Python function based on the following description. "
            "Include a docstring explaining the function and its parameters. \n\n"
            f"Description: \"{description}\""
        )

        # 4. Gọi Gemini API để sinh nội dung
        # Xem tài liệu: https://ai.google.dev/tutorials/python_quickstart#generate_text
        response = model.generate_content(prompt)

        # 5. Xử lý kết quả trả về
        # Loại bỏ các dấu ```python và ``` nếu Gemini trả về trong markdown
        if hasattr(response, 'text'):
             generated_code = response.text.strip().replace("```python", "").replace("```", "").strip()
             if not generated_code:
                 # Đôi khi API có thể trả về trống nếu có vấn đề an toàn hoặc lỗi khác
                 error_info = f"API response was empty. Parts: {response.parts}, Prompt Feedback: {response.prompt_feedback}"
                 return {"status": "error", "error_message": error_info}
             return {"status": "success", "code": generated_code}
        else:
             # Xử lý trường hợp response không có text (ví dụ: bị chặn do an toàn)
             error_info = f"API response blocked or invalid. Parts: {response.parts}, Prompt Feedback: {response.prompt_feedback}"
             return {"status": "error", "error_message": error_info}


    except Exception as e:
        # Bắt lỗi chung trong quá trình gọi API
        return {"status": "error", "error_message": f"An error occurred while calling the Gemini API: {str(e)}"}


root_agent = Agent(
    name="python_code_generator_agent",
    model="gemini-2.5-flash",
    description="Agent to generate Python code based on a given description.",
    instruction="You are a helpful assistant that generates Python code based on user descriptions.",
    tools=[generate_python_function],    
)