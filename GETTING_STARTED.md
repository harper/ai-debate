# Getting Started with AI Debate Arena

This guide walks you through setting up API access for each AI provider.

## Quick Setup

```bash
# 1. Clone and install
git clone https://github.com/harper/ai-debate.git
cd ai-debate
uv sync

# 2. Copy the environment template
cp env.template .env

# 3. Edit .env and add your API keys (see instructions below)

# 4. Run your first debate
uv run python scripts/run_debate.py
```

---

## Getting API Keys

### Anthropic (Claude Opus 4.5)

**Console:** https://console.anthropic.com/

1. **Create an account** at [console.anthropic.com](https://console.anthropic.com/)
   - Note: This is separate from a Claude.ai subscription

2. **Navigate to API Keys**
   - From the dashboard, click "API Keys" in the left sidebar
   - Or go directly to: https://console.anthropic.com/settings/keys

3. **Create a new key**
   - Click "+ Create Key"
   - Name it something descriptive (e.g., "ai-debate-dev")
   - Copy the key immediately — **it's only shown once**

4. **Add credits**
   - Go to "Billing" in the left sidebar
   - Add at least $5 in credits (minimum)
   - The API won't work without credits, even for small tests

5. **Add to your .env file:**
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...
   ```

**Model ID:** `claude-opus-4-5-20251101`

**Pricing:** $5/million input tokens, $25/million output tokens for Opus 4.5

---

### OpenAI (GPT-5.2)

**Console:** https://platform.openai.com/

1. **Create an account** at [platform.openai.com](https://platform.openai.com/)
   - You can use Google, Microsoft, or Apple SSO

2. **Verify your account**
   - Confirm your email
   - Add phone number for SMS verification

3. **Navigate to API Keys**
   - Click your profile icon → "API keys"
   - Or go directly to: https://platform.openai.com/api-keys

4. **Create a new key**
   - Click "+ Create new secret key"
   - Name it (e.g., "ai-debate")
   - Set permissions (full access is fine for development)
   - Copy the key immediately — **it's only shown once**

5. **Set up billing**
   - Go to "Billing" in the sidebar
   - Add a payment method
   - New accounts may get $5 free credit (valid 3 months)

6. **Add to your .env file:**
   ```
   OPENAI_API_KEY=sk-proj-xxxxx...
   ```

**Model ID:** `gpt-5.2`

**Pricing:** $1.75/million input tokens, $14/million output tokens for GPT-5.2 (90% discount on cached inputs)

---

### Google (Gemini 3 Pro)

**Console:** https://aistudio.google.com/

1. **Go to Google AI Studio** at [aistudio.google.com](https://aistudio.google.com/)
   - Sign in with your Google account

2. **Get an API Key**
   - Click "Get API Key" in the top-left corner
   - Accept the Terms of Service

3. **Create your key**
   - Click "Create API key"
   - Choose "Create API key in new project" (recommended)
   - Copy the key immediately

4. **Add to your .env file:**
   ```
   GOOGLE_API_KEY=AIzaSy...
   ```

**Model ID:** `gemini-3-pro-preview` (currently in preview)

**Free tier:** 5 requests/minute (may need paid tier for full debates)

**For higher limits:** Use Google Cloud Console at [console.cloud.google.com](https://console.cloud.google.com/) and enable the Gemini API with billing.

---

### xAI (Grok 4)

**Console:** https://console.x.ai/

1. **Create an account** at [console.x.ai](https://console.x.ai/)
   - You can sign in with X (Twitter), Google, or email

2. **Add credits**
   - Go to Billing and add payment method
   - Load credits to your account
   - Note: API access may take 24-48 hours to activate

3. **Generate an API Key**
   - Go to "API Keys" section
   - Click "Create API Key"
   - Name it and copy immediately — **only shown once**

4. **Add to your .env file:**
   ```
   XAI_API_KEY=xai-xxxxx...
   ```

**Model ID:** `grok-4`

**Note:** xAI's API is compatible with OpenAI's SDK format (endpoint: `https://api.x.ai/v1`).

---

## Verifying Your Setup

Test that your keys work:

```bash
# Test Anthropic
uv run python -c "
from ai_debate.models import AnthropicModel
m = AnthropicModel()
print(f'✓ Anthropic: {m.name} ({m.model_id})')
"

# Test OpenAI
uv run python -c "
from ai_debate.models import OpenAIModel
m = OpenAIModel()
print(f'✓ OpenAI: {m.name} ({m.model_id})')
"

# Test Google
uv run python -c "
from ai_debate.models import GoogleModel
m = GoogleModel()
print(f'✓ Google: {m.name} ({m.model_id})')
"

# Test xAI
uv run python -c "
from ai_debate.models import XAIModel
m = XAIModel()
print(f'✓ xAI: {m.name} ({m.model_id})')
"
```

---

## Running Your First Debate

Once you have at least two API keys set up:

```bash
# Run with default topic
uv run python scripts/run_debate.py

# Run with custom topic
uv run python scripts/run_debate.py "Resolved: Universal basic income is preferable to traditional welfare"
```

The debate will:
1. Print progress to the terminal as each phase completes
2. Save a Markdown transcript to `debates/debate-<id>.md`

---

## Using 1Password for API Keys

If you use 1Password, you can store API keys securely and inject them at runtime.

1. **Store your keys in 1Password** (e.g., in a vault called "Private")

2. **Update your .env file with `op://` references:**
   ```
   ANTHROPIC_API_KEY="op://Private/Anthropic API/password"
   OPENAI_API_KEY="op://Private/OpenAI API/password"
   GOOGLE_API_KEY="op://Private/Google AI/password"
   XAI_API_KEY="op://Private/xAI API/password"
   ```

3. **Run using the 1Password wrapper script:**
   ```bash
   ./scripts/run.sh

   # Or with a custom topic
   ./scripts/run.sh "Resolved: Your topic here"
   ```

The script uses `op run` to resolve secrets from 1Password before executing.

---

## Cost Estimates

A single Lincoln-Douglas debate uses approximately:
- **~5,000 words** of output across all phases
- **~15,000-20,000 tokens** total per model

Estimated cost per debate (both models combined):
- Claude Opus 4.5 + GPT-5.2: ~$1-2
- Using smaller models (Sonnet, GPT-4o): ~$0.10-0.30

A full 4-model matrix (12 debates) would cost approximately $12-24 with flagship models.

---

## Troubleshooting

### "API key not set" error
- Make sure your `.env` file exists and has the key
- Run `source .env` or restart your terminal
- Check for typos in the variable name

### "Insufficient credits" error
- Add credits/billing to your provider account
- Anthropic requires prepaid credits
- OpenAI uses pay-as-you-go billing

### Rate limit errors
- Google's free tier has strict limits (5 req/min)
- Add delays between API calls or upgrade to paid tier
- Consider using smaller models for testing

### Model not found
- Verify the model ID is correct for your account tier
- Some models require special access (e.g., GPT-5.2 may need waitlist)
- Try a different model variant (e.g., `gpt-4o` instead of `gpt-5.2`)
