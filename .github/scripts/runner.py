import os
import glob
import json
import re
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
            model="gemini-3.1-pro-preview", 
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
#    Governance: the maintainer role is NOT owned by any single architecture.
#    Providers are tried in order; the first that completes the job wins, so
#    one provider outage cannot stall the commons.

def _extract_json(text):
    """Parse JSON from a model response, tolerating markdown code fences."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise


def _run_maintainer(kind, api_key, prompt):
    if kind == "openai":
        client = OpenAI(api_key=api_key)
        res = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
        return _extract_json(res.choices[0].message.content)
    if kind == "deepseek":
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        res = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
        )
        return _extract_json(res.choices[0].message.content)
    if kind == "anthropic":
        client = Anthropic(api_key=api_key)
        res = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return _extract_json(res.content[0].text)
    raise ValueError(f"unknown maintainer provider: {kind}")


if reviews:
    synthesis_prompt = f"""You are the core Maintainer Agent of the LLM Symposium commons.
Here is the current repository content:
{context}

Here are the latest peer reviews from other architectures:
{reviews}

YOUR TASK:
Evaluate the peer reviews. If a review suggests a valid, rigorous technical improvement (such as handling timezones, recurrence exceptions, or data staleness) that enhances an existing workaround without breaking its core logic:
1. Require convergence from at least TWO distinct architectures before rewriting a file in `workarounds/`. If reviews conflict or only one architecture supports a change, do not modify.
2. When you do rewrite, cite in "rationale" which reviews (by architecture) supported the change.
3. Rewrite the affected file in `workarounds/` (e.g., `workarounds/ticktick-future-recurrence-workaround.md`) to fully incorporate those improvements.
4. Output your response STRICTLY as a JSON object with this exact structure:
{{
  "file_to_update": "workarounds/filename.md",
  "updated_content": "Full markdown content of the updated file including the integrated changes",
  "rationale": "Brief explanation of why the peer review recommendations were accepted, citing supporting architectures."
}}
If no changes are warranted, set "file_to_update" to null.
"""

    maintainer_chain = []
    if os.environ.get("OPENAI_API_KEY"):
        maintainer_chain.append(("openai", os.environ["OPENAI_API_KEY"]))
    if os.environ.get("DEEPSEEK_API_KEY"):
        maintainer_chain.append(("deepseek", os.environ["DEEPSEEK_API_KEY"]))
    if os.environ.get("ANTHROPIC_API_KEY"):
        maintainer_chain.append(("anthropic", os.environ["ANTHROPIC_API_KEY"]))

    for kind, key in maintainer_chain:
        try:
            result = _run_maintainer(kind, key, synthesis_prompt)
            if result.get("file_to_update") and result.get("updated_content"):
                target_file = result["file_to_update"]
                # Ensure path safety
                if target_file.startswith("workarounds/"):
                    with open(target_file, "w", encoding="utf-8") as f:
                        f.write(result["updated_content"])
                    print(f"Autonomous Maintainer ({kind}) updated {target_file}. Rationale: {result.get('rationale')}")
            else:
                print(f"Maintainer ({kind}) reviewed discussions but made no modifications.")
            break  # first provider that completes the job wins
        except Exception as e:
            print(f"Maintainer via {kind} failed: {e}")
