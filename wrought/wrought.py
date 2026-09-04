import sys
import io
import ollama
execution_globals = {}
print('Python scripting feature is not very good right now.')
responses = []
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
elif hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

if hasattr(sys.stdin, 'reconfigure'):
    sys.stdin.reconfigure(encoding='utf-8')
elif hasattr(sys.stdin, 'buffer'):
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
def execute_python_code(code: str) -> str:
    code = code.strip()
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    code = code.strip()
    orgstdout = sys.stdout
    buffer = io.StringIO()
    sys.stdout = buffer
    try:
        exec(code,execution_globals)
        output = buffer.getvalue()
        return output if output else "[done - no printed output]"
    except Exception as e:
        return f"Error: {e}"
    finally:
        sys.stdout = orgstdout
thetools = [
    {
        'type': 'function',
        'function': {
            'name': 'execute_python_code',
            'description': ''''Executes a SELF-CONTAINED Python script.
Always print the output when using this and define your own functions, please.
and imports inside the script every time. Do not reference undefined functions.
DO NOT use markdown triple backticks. Just give the raw code
''',
            'parameters': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'string',
                        'description': 'Python code to run.',
                    },
                },
                'required': ['code'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'send_message',
            'description': 'Send a plain text conversational message to the user.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'text': {'type': 'string', 'description': 'The message to send.'},
                },
                'required': ['text'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'end_conversation',
            'description': 'End the conversation',
            'parameters': {
                'type':'object'
                },
                'required': [],
            },
        },
    
    
]
messagel = [{"role": "system", "content": """
You are an AI named Wrought.
Start the chat immediately without booting or initializing messages.
Try to make your messages very short and use only lowercase letters.
Only execute python code(execute_python_code) when asked to.Else, use send_message.
Use end_conversation when asked to exit or end the conversation
"""},]
while True:
    prompt = input('>> ')
    messagel.append({"role": "user", "content": prompt})
    response = ollama.chat(
    tools = thetools,
    options={'temperature': 0.7},
    model="llama3.1",
    messages=messagel,
)
    msg = response['message']
    if msg.get("tool_calls"):
        messagel.append(msg)
        for tool in msg["tool_calls"]:
            if tool["function"]["name"] == "execute_python_code":
                code = tool["function"]["arguments"]["code"]
                print(f"[executing code... ]")
                output = execute_python_code(code)
                print(f"output: {output}\n")
                messagel.append({
                    "role": "tool",
                    "content": str(output),
                })
            elif tool["function"]["name"] == "send_message":
                reply = tool["function"]["arguments"]["text"]
                print(reply)
            elif tool["function"]["name"] == "end_conversation":
                sys.exit(0)
    else:
        if msg.get("content"):
            print(msg["content"])
            messagel.append(msg)
