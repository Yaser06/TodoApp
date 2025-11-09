# AI Tools Configuration Guide

The orchestration system is **UNIVERSAL** - it works with **ANY AI tool** that can be called from CLI.

No longer limited to Claude, Gemini, or OpenAI - use Llama, Mistral, DeepSeek, or any custom AI!

## Quick Start - 3 Ways to Use

### 🚀 Option 1: ZERO CONFIG (Easiest!)
**No setup needed! Just run and use any AI tool manually**

```bash
# Just start - that's it!
./orchestrate.sh

# System will:
# ✅ Auto-select GENERIC INTERACTIVE mode
# ✅ Create CURRENT_TASK.md with task details
# ✅ Wait for you to implement with ANY AI tool
# ✅ Auto-detect changes and continue
```

Use any AI you want:
- Claude Code in terminal
- Cursor AI chat
- ChatGPT web interface
- Gemini web/CLI
- GitHub Copilot
- Or ANY other AI tool!

### ⚡ Option 2: Custom CLI (Full Automation)
**Set command once, system runs fully automatic**

```bash
# Example 1: Using Ollama with Llama3
export CUSTOM_AI_COMMAND="ollama run llama3"
./orchestrate.sh

# Example 2: Using local LLM server
export CUSTOM_AI_COMMAND="curl -X POST http://localhost:8000/generate -d"
./orchestrate.sh

# Example 3: Using your own wrapper script
export CUSTOM_AI_COMMAND="./my-ai-wrapper.sh"
./orchestrate.sh
```

### 🔧 Option 3: Pre-configured Tools
**Use built-in integrations for Claude, Gemini, OpenAI**

See "Pre-configured AI Tools" section below.

---

## Pre-configured AI Tools

### 1. Claude Code (Built-in)
**CLI Command:** `claude`

The system automatically detects Claude Code if installed. No configuration needed.

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Run orchestrator (auto-detects)
./orchestrate.sh
```

### 2. Google Gemini (CLI)
**Supported CLI tools:** `gemini`, `genai`, `google-ai`, `gcloud-ai`

#### Option A: Auto-detection
If you have a Gemini CLI tool installed with one of the standard names:
```bash
./orchestrate.sh  # Auto-detects gemini/genai/google-ai/gcloud-ai
```

#### Option B: Custom Command
If you have a custom wrapper script:
```bash
export GEMINI_COMMAND="./my-gemini-wrapper.sh"
export AI_TOOL="gemini-cli"
./orchestrate.sh
```

#### Example Wrapper Script
Create `my-gemini-wrapper.sh`:
```bash
#!/bin/bash
# Simple Gemini wrapper using API
curl -s -X POST "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=$GEMINI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d "{\"contents\":[{\"parts\":[{\"text\":\"$1\"}]}]}"
```

### 3. OpenAI Codex (CLI)
**Supported CLI tools:** `openai`, `oai`

#### Option A: Auto-detection
If you have OpenAI CLI installed:
```bash
./orchestrate.sh  # Auto-detects openai/oai
```

#### Option B: Custom Command
```bash
export OPENAI_COMMAND="./my-openai-wrapper.sh"
export AI_TOOL="openai-cli"
./orchestrate.sh
```

#### Example Wrapper Script
Create `my-openai-wrapper.sh`:
```bash
#!/bin/bash
# OpenAI wrapper using official CLI
openai api chat.completions.create \
  -m gpt-4 \
  -c "$1" \
  --max-tokens 4000
```

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `CUSTOM_AI_COMMAND` | **Universal - works with ANY AI** | `export CUSTOM_AI_COMMAND="ollama run llama3"` |
| `AI_TOOL` | Force specific tool (optional) | `export AI_TOOL="custom-cli"` |
| `GEMINI_COMMAND` | Custom Gemini CLI command | `export GEMINI_COMMAND="gemini"` |
| `OPENAI_COMMAND` | Custom OpenAI CLI command | `export OPENAI_COMMAND="openai"` |
| `ANTHROPIC_API_KEY` | Claude API key (fallback) | `export ANTHROPIC_API_KEY="sk-..."` |
| `OPENAI_API_KEY` | OpenAI API key (fallback) | `export OPENAI_API_KEY="sk-..."` |
| `GEMINI_API_KEY` | Gemini API key (fallback) | `export GEMINI_API_KEY="..."` |

**Recommended:** Just use `CUSTOM_AI_COMMAND` for any AI tool - it's universal!

## How It Works

### Zero Config Mode (Generic Interactive)

When no AI tool is configured:

1. **Agent starts** and detects no AI tool
2. **Auto-selects GENERIC INTERACTIVE mode**
3. **Creates CURRENT_TASK.md** with full task details
4. **Shows instructions** on screen
5. **Waits for changes** (checks git status every 5-30 seconds)
6. **You implement** using any AI tool you want
7. **System detects changes** and continues automatically
8. **Auto-commits** your changes (if enabled)
9. **Creates PR** and merges (if enabled)

**Example workflow:**
```bash
$ ./orchestrate.sh

🎯 GENERIC INTERACTIVE MODE - Task Ready!
📋 Task: Setup project structure
📁 Details: CURRENT_TASK.md

💡 HOW TO IMPLEMENT:
   1. Open CURRENT_TASK.md - read task details
   2. Use ANY AI tool you want
   3. Implement the task
   4. System will auto-detect changes and continue

⏳ Waiting for changes (timeout: 15 minutes)...

# (You open Cursor, ChatGPT, or any AI tool)
# (You implement the task)
# (System detects your changes)

✅ Changes detected! Implementation complete.
🔄 System will now commit and continue...
```

## Detection Priority

The system checks for AI tools in this order:

1. **Environment override:** `AI_TOOL` variable (forces specific tool)
2. **Universal Custom AI:** `CUSTOM_AI_COMMAND` variable ⭐ **Fully automatic**
3. **Claude Code CLI:** `claude` command
4. **Cursor:** `TERM_PROGRAM=Cursor` environment
5. **Aider:** `aider` command
6. **Copilot CLI:** `github-copilot-cli` command
7. **Gemini CLI:** `gemini`, `genai`, `google-ai`, `gcloud-ai` commands
8. **OpenAI CLI:** `openai`, `oai` commands
9. **Claude API:** `ANTHROPIC_API_KEY` environment
10. **OpenAI API:** `OPENAI_API_KEY` environment
11. **Gemini API:** `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment
12. **⭐ Generic Interactive:** No config needed - works with ANY AI manually!

## Testing Your Configuration

Test if your AI tool is detected:

```bash
# Set your preferred tool
export AI_TOOL="gemini-cli"
export GEMINI_COMMAND="gemini"

# Start one agent
./orchestrate.sh

# Check agent log (you should see "Using Gemini CLI: gemini")
tail -f .orchestrator/logs/agent-*.log
```

## Troubleshooting

### "No AI tool detected"
- Make sure your CLI command is in PATH: `which gemini`
- Or set custom command: `export GEMINI_COMMAND="/full/path/to/gemini"`
- Or force tool selection: `export AI_TOOL="gemini-cli"`

### "AI tool returned error"
- Test your CLI manually: `gemini "Hello, test"`
- Check wrapper script has execute permissions: `chmod +x my-gemini-wrapper.sh`
- Verify API keys are set if needed

### Agent stuck in "manual mode"
- Check detection logs at agent startup
- Verify your CLI tool works standalone
- Set `AI_TOOL` environment variable to force detection

## Creating Custom CLI Wrappers

If you're using an AI tool not listed above, create a wrapper script that:

1. Accepts prompt as first argument: `$1`
2. Calls your AI tool
3. Returns 0 on success, non-zero on failure
4. Prints output to stdout

Example template:
```bash
#!/bin/bash
# my-ai-wrapper.sh

PROMPT="$1"

# Call your AI tool here
# Replace this with your actual AI service
your-ai-tool --prompt "$PROMPT" --max-tokens 4000

# Exit with appropriate code
exit $?
```

Make it executable and use:
```bash
chmod +x my-ai-wrapper.sh
export CUSTOM_AI_COMMAND="./my-ai-wrapper.sh"
./orchestrate.sh
```

## Real-World Examples

### Example 1: Ollama with Llama 3
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama 3
ollama pull llama3

# Use with orchestrator
export CUSTOM_AI_COMMAND="ollama run llama3"
./orchestrate.sh
```

### Example 2: Mistral via API
```bash
#!/bin/bash
# mistral-wrapper.sh

PROMPT="$1"

curl -s https://api.mistral.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -d "{
    \"model\": \"mistral-large-latest\",
    \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}]
  }" | jq -r '.choices[0].message.content'

exit 0
```

```bash
chmod +x mistral-wrapper.sh
export MISTRAL_API_KEY="your-key"
export CUSTOM_AI_COMMAND="./mistral-wrapper.sh"
./orchestrate.sh
```

### Example 3: DeepSeek Coder
```bash
#!/bin/bash
# deepseek-wrapper.sh

PROMPT="$1"

curl -s https://api.deepseek.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -d "{
    \"model\": \"deepseek-coder\",
    \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}]
  }" | jq -r '.choices[0].message.content'

exit 0
```

```bash
chmod +x deepseek-wrapper.sh
export DEEPSEEK_API_KEY="your-key"
export CUSTOM_AI_COMMAND="./deepseek-wrapper.sh"
./orchestrate.sh
```

### Example 4: Local LLM Server (LlamaCpp, vLLM, etc.)
```bash
#!/bin/bash
# local-llm-wrapper.sh

PROMPT="$1"

curl -s http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"$PROMPT\",
    \"max_tokens\": 4000,
    \"temperature\": 0.7
  }" | jq -r '.choices[0].text'

exit 0
```

```bash
chmod +x local-llm-wrapper.sh
export CUSTOM_AI_COMMAND="./local-llm-wrapper.sh"
./orchestrate.sh
```

### Example 5: Qwen (Alibaba Cloud)
```bash
#!/bin/bash
# qwen-wrapper.sh

PROMPT="$1"

curl -s https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation \
  -H "Authorization: Bearer $QWEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"qwen-max\",
    \"input\": {\"prompt\": \"$PROMPT\"}
  }" | jq -r '.output.text'

exit 0
```

```bash
chmod +x qwen-wrapper.sh
export QWEN_API_KEY="your-key"
export CUSTOM_AI_COMMAND="./qwen-wrapper.sh"
./orchestrate.sh
```

## FAQ

**Q: Do I need to configure ANYTHING to start?**
A: **NO!** Just run `./orchestrate.sh` - system auto-selects Generic Interactive mode. Use any AI tool you want manually.

**Q: Can I use ANY AI tool, even ones not mentioned here?**
A: **YES!** Two ways:
   - Zero config: Use Generic Interactive mode (just run, no config)
   - Full auto: Set `CUSTOM_AI_COMMAND` for automatic implementation

**Q: Do I need to modify the code to add a new AI tool?**
A: **NO!** Either:
   - Use Generic Interactive mode (no config)
   - Create a wrapper script and set `CUSTOM_AI_COMMAND`
   - No code changes ever needed

**Q: What's the difference between Generic Interactive and Custom CLI?**
A:
   - **Generic Interactive:** You implement manually with any AI tool, system waits for changes
   - **Custom CLI:** System calls your AI command automatically, fully hands-off

**Q: Can I use multiple AI tools at once?**
A: Yes! Each agent instance uses one tool. Run multiple agents with different configs.

**Q: Which tool is fastest?**
A: Local models (Ollama, llama.cpp) are fastest. Claude Code CLI is fast for cloud. Generic Interactive depends on you!

**Q: Do I need API keys?**
A: Only for API-based tools. Generic Interactive mode needs nothing - works out of the box!

**Q: Can I use a local LLM?**
A: **Absolutely!** Use Generic Interactive mode or set `CUSTOM_AI_COMMAND="ollama run llama3"`

**Q: What if my AI tool has a different command format?**
A: Use Generic Interactive mode (works with ANY tool) or create a wrapper script for automation.

**Q: How long does Generic Interactive mode wait?**
A: 15 minutes by default. Checks for changes every 5-30 seconds.

**Q: Can I switch tools mid-execution?**
A: No, the tool is detected at agent startup. Restart the agent with new environment variables to switch tools.
