import sys
import io
import ollama
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
    orgstdout = sys.stdout
    buffer = io.StringIO()
    sys.stdout = buffer
    try:
        exec(code)
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
            'description': ''''Executes Python code and returns output.
Always print the output when using this and define your own functions, please.''',
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
    }
    
]
while True:
    prompt = input('>> ')
    response = ollama.chat(
    tools = thetools,
    options={'temperature': 0.7},
    model="llama3.1",
    messages=[{"role": "system", "content": """
You are an AI named Wrought.
Start the chat immediately without booting or initializing messages.
Try to make your messages very short and use only lowercase letters.
Only execute python code(execute_python_code) when asked to.Else, use send_message.
"""},{"role": "system","content": f'previous messages: {responses}'},
{"role": "user",
"content": prompt},],
)
    msg = response['message']
    if msg.get("tool_calls"):
        for tool in msg["tool_calls"]:
            if tool["function"]["name"] == "execute_python_code":
                code = tool["function"]["arguments"]["code"]
                print(f"[executing code... ]")
                output = execute_python_code(code)
                print(f"output: {output}\n")
                responses.append([f"executed code: {code} -> output: {output}", prompt])
            elif tool["function"]["name"] == "send_message":
                reply= tool["function"]["arguments"]["text"]
                print(reply)
                responses.append([reply, prompt])
