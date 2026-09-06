from e2b_code_interpreter import Sandbox
from pydantic import BaseModel, Field
from config import E2B_API_KEY

class SandboxSchema(BaseModel):
    code: str = Field(description="The Python code to execute in the sandbox. Use print() to output results.")

def run_python(code: str) -> str:
    """Executes Python code safely in the E2B Sandbox."""
    if not E2B_API_KEY:
        return "Error: E2B_API_KEY not found in environment."
            
    try:
        with Sandbox.create() as sandbox:
            execution = sandbox.run_code(code)
            
            output = []
            if execution.logs.stdout:
                output.append(f"STDOUT:\n{'-'*10}\n{''.join(execution.logs.stdout)}\n{'-'*10}")
            if execution.logs.stderr:
                output.append(f"STDERR:\n{'-'*10}\n{''.join(execution.logs.stderr)}\n{'-'*10}")
            if execution.text:
                output.append(f"RESULT:\n{'-'*10}\n{execution.text}\n{'-'*10}")
                
            if execution.error:
                output.append(f"ERROR:\n{'-'*10}\n{execution.error.name}: {execution.error.value}\n{execution.error.traceback}\n{'-'*10}")

            if not output:
                return "Code executed successfully with no output (did you forget to print?)."
                
            return "\n\n".join(output)
    except Exception as e:
        return f"Sandbox execution error: {str(e)}"