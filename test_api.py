import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY not found. Create a .env file with your key.")
    print("   Or run: export GROQ_API_KEY=your_key_here")
    exit(1)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY,
)

print(f"✅ API key loaded: {GROQ_API_KEY[:10]}...")

try:
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": "Print 'Hello'"}],
        tools=[{
            "type": "function",
            "function": {
                "name": "execute_python",
                "description": "Execute Python code",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to run"
                        }
                    },
                    "required": ["code"]
                }
            }
        }],
        tool_choice="auto",
        temperature=0.1,
    )

    print("\n📝 Response received:")
    print(f"  Content: {response.choices[0].message.content}")
    print(f"  Tool calls: {response.choices[0].message.tool_calls}")

except Exception as e:
    print(f"❌ API error: {e}")
