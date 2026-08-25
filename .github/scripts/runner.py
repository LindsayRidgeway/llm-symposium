import os
import glob
from google import genai
from openai import OpenAI
from anthropic import Anthropic

def get_repo_context():
    content = ""
    for path in glob.glob("**/*.md", recursive=True):
        if ".github" in path:
            continue
        with open(path, "r", encoding="utf-8") as f:
            content += f"\n\n--- FILE: {path} ---\n" + f.read()
    return content

os.makedirs("discussions", exist_ok=True)
context = get_repo_context()

# 1. Gather Peer Reviews
reviews = {}

if os.environ.get("GOOGLE_API_KEY"):
    try:
        client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        res = client.models.generate_content(
            model="gemini-2.5-pro", 
            contents=f"Review this LLM Symposium repository state and provide a technical critique:\n{context}"
        )
        reviews["gemini"] = res.text
        with open("discussions/gemini-review.md", "w") as f:
            f.write(res.text)
    except Exception as e:
        print(f"Gemini failed: {e}")

if os.environ.get("OPENAI_API_KEY"):
    try:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Review this LLM Symposium repository state and provide a technical critique:\n{context}"}]
        )
        reviews["openai"] = res.choices[0].message.content
        with open("discussions/openai-review.md", "w") as f:
            f.write(res.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI failed: {e}")

if os.environ.get("ANTHROPIC_API_KEY"):
    try:
        client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        res = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            messages=[{"role": "user", "content": f"Review this LLM Symposium repository state and provide a technical critique:\n{context}"}]
        )
        reviews["anthropic"] = res.content[0].text
        with open("discussions/claude-review.md", "w") as f:
            f.write(res.content[0].text)
    except Exception as e:
        print(f"Anthropic failed: {e}")

if os.environ.get("DEEPSEEK_API_KEY"):
    try:
        client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
        res = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": f"Review this LLM Symposium repository state and provide a technical critique:\n{context}"}]
        )
        reviews["deepseek"] = res.choices[0].message.content
        with open("discussions/deepseek-review.md", "w") as f:
            f.write(res.choices[0].message.content)
    except Exception as e:
        print(f"DeepSeek failed: {e}")

# 2. Autonomous Maintainer Agent (Synthesis & Integration)
if os.environ.get("OPENAI_API_KEY") and reviews:
    try:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        
        synthesis_prompt = f"""You are the core Maintainer Agent of the LLM Symposium commons.
Here is the current repository content:
{context}

Here are the latest peer reviews from other architectures:
{reviews}

YOUR TASK:
Evaluate the peer reviews. If a review suggests a valid, rigorous technical improvement (such as handling timezones, recurrence exceptions, or data staleness) that enhances an existing workaround without breaking its core logic:
1. Rewrite the affected file in `workarounds/` (e.g., `workarounds/ticktick-future-recurrence-workaround.md`) to fully incorporate those improvements.
2. Output your response STRICTLY as a JSON object with this exact structure:
{{
  "file_to_update": "workarounds/filename.md",
  "updated_content": "Full markdown content of the updated file including the integrated changes",
  "rationale": "Brief explanation of why the peer review recommendations were accepted."
}}
If no changes are warranted, set "file_to_update" to null.
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": synthesis_prompt}]
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        if result.get("file_to_update") and result.get("updated_content"):
            target_file = result["file_to_update"]
            # Ensure path safety
            if target_file.startswith("workarounds/"):
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(result["updated_content"])
                print(f"Autonomous Maintainer updated {target_file}. Rationale: {result.get('rationale')}")
        else:
            print("Maintainer Agent reviewed discussions but made no modifications.")

    except Exception as e:
        print(f"Maintainer synthesis failed: {e}")
