import json
import logging
from typing import Generator, Dict, Any, Optional
from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME
from prompts import SYSTEM_PROMPT, get_openai_tools
from tools import AVAILABLE_TOOLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
)

def run_agent(
    user_prompt: str,
    max_steps: int = 10,
    tool_budgets: Optional[Dict[str, int]] = None,
    default_budget: int = 2,
) -> Generator[Dict[str, Any], None, None]:

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    all_tools = get_openai_tools()
    tool_budgets = tool_budgets or {}
    tool_counts = {t["function"]["name"]: 0 for t in all_tools}
    executed_calls = set()
    step_count = 0

    while step_count < max_steps:
        step_count += 1
        yield {"type": "status", "content": f"Step {step_count}: Thinking..."}

        is_final_step = step_count >= max_steps - 1

        active_tools = [
            t for t in all_tools
            if not is_final_step
            and tool_counts[t["function"]["name"]] < tool_budgets.get(t["function"]["name"], default_budget)
        ]

        tools_param = active_tools or None
        tool_choice_param = "auto" if tools_param else None

        if not tools_param and messages[-1].get("role") != "user":
            messages.append({
                "role": "user",
                "content": "You have gathered sufficient data. Produce your final, comprehensive answer now — no more tool calls.",
            })

        try:
            api_kwargs = {"model": MODEL_NAME, "messages": messages, "temperature": 0.2}
            if tools_param:
                api_kwargs["tools"] = tools_param
                api_kwargs["tool_choice"] = tool_choice_param

            response = client.chat.completions.create(**api_kwargs)

            if not response.choices:
                logger.error("Empty model response: %s", response.model_dump(exclude_none=False))
                yield {"type": "error", "content": "The model returned an empty response."}
                break

            assistant_message = response.choices[0].message
            logger.info(
                "Step %d | Finish: %s | Tool calls: %s",
                step_count, response.choices[0].finish_reason, bool(assistant_message.tool_calls),
            )

            if not assistant_message.tool_calls:
                final_text = (assistant_message.content or "").strip()
                if final_text:
                    yield {"type": "final_answer", "content": final_text}
                else:
                    yield {"type": "error", "content": "Model returned an empty answer."}
                return

            messages.append(assistant_message.model_dump(exclude_none=True))

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                raw_args = tool_call.function.arguments

                try:
                    args_dict = json.loads(raw_args)
                except json.JSONDecodeError:
                    messages.append({
                        "role": "tool", "tool_call_id": tool_call.id, "name": tool_name,
                        "content": "Error: Invalid JSON arguments generated.",
                    })
                    continue

                call_sig = (tool_name, json.dumps(args_dict, sort_keys=True))
                if call_sig in executed_calls:
                    messages.append({
                        "role": "tool", "tool_call_id": tool_call.id, "name": tool_name,
                        "content": "Already executed with identical arguments. Check earlier tool outputs.",
                    })
                    continue
                executed_calls.add(call_sig)

                yield {"type": "tool_start", "tool_name": tool_name, "args": raw_args}
                try:
                    tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
                    if tool_name not in AVAILABLE_TOOLS:
                        result_text = f"Error: Tool '{tool_name}' not found."
                    else:
                        tool_func = AVAILABLE_TOOLS[tool_name]["function"]
                        result_text = str(tool_func(**args_dict))
                except Exception:
                    logger.exception("Tool execution failed: %s", tool_name)
                    result_text = f"Tool '{tool_name}' failed to execute."  # no raw exception to the user

                yield {"type": "tool_end", "tool_name": tool_name, "result": result_text}
                messages.append({
                    "role": "tool", "tool_call_id": tool_call.id, "name": tool_name,
                    "content": result_text,
                })

        except Exception:
            logger.exception("Agent loop error")
            yield {"type": "error", "content": "Agent execution failed. Check the server logs."}
            return

    yield {"type": "error", "content": "Max iterations reached without a final synthesis."}