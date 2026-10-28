# 🚀 Automated X (Twitter) Tech Deep-Dive Thread Agent

An autonomous AI agent that researches fascinating, "under-the-hood" software engineering & system design topics (e.g., *how Blinkit tracks moving delivery drivers*, *how Google Maps predicts traffic*, *how Flipkart scales Big Billion Days*, *why AI servers evaporate water for cooling*) and automatically crafts & publishes high-converting multi-tweet threads twice daily on X—**100% free of cost**.

---

## 🌟 Why This Content Works (The Viral Formula)

The agent is calibrated to write in the format that powers top tech accounts on X (like ByteByteGo, Alex Xu, and Quastor):
1. **Tweet 1 (The Curiosity Hook)**: Relatable everyday user experience + hidden engineering paradox + "Here's how it actually works under the hood 🧵👇"
2. **Tweet 2 (The Naive Trap)**: Why the obvious solution crashes in production (e.g., why Zomato can't just ping GPS every second).
3. **Tweets 3–5 (The Core Architectural Solution)**: Concrete technical concepts (Kalman filters, MQTT, Kafka queues, eBPF, H3 geospatial binning) explained in clean, skimmable bullet points.
4. **Final Tweet (Takeaway & CTA)**: High-retention summary encouraging readers to follow your handle and bookmark/retweet.

---

## 💰 100% Free Architecture ($0 Cost)

- **Gemini API**: Uses Google AI Studio free tier (up to 1,500 requests/day; bot uses ~2 to 4/day).
- **Twitter API v2**: Uses the official X Developer Free tier (1,500 free posts/month; bot uses ~300 posts/month).
- **Automation / Hosting**: Uses GitHub Actions (2,000 free minutes/month; bot uses ~30 minutes/month).

---

## ⚡ Quickstart: Test Locally in 60 Seconds (Dry Run)

You can generate and review threads right now without needing Twitter API keys!

### 1. Set up your Python environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure your free Gemini API key:
Create a `.env` file from the template:
```bash
cp .env.example .env
```
Add your free Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/api-keys):
```ini
GEMINI_API_KEY=your_gemini_api_key_here
TWITTER_HANDLE=YourXHandle
```

### 3. Run a Dry Run:
```bash
# Generate the next thread from the catalog (Preview in terminal, no posting)
python main.py --dry-run

# Or test a specific custom topic on-demand:
python main.py --topic "How Shazam identifies songs in 3 seconds" --dry-run
```

---

## 🔑 How to Get Your Free API Keys

### 1. Google Gemini API Key (Free)
1. Go to [Google AI Studio](https://aistudio.google.com/app/api-keys).
2. Sign in with your Google account.
3. Click **"Create API Key"** and copy it into `GEMINI_API_KEY`.

### 2. Twitter / X Developer Keys (Free Tier)
1. Go to the [X Developer Portal](https://developer.x.com).
2. Sign in with your X account (make sure your X account has a verified phone number and email).
3. Choose the **Free Plan** (allows 1,500 posts/month for $0).
4. Create a Project and an App.
5. ⚠️ **CRITICAL STEP**: Inside your App settings, go to **"User authentication settings"** $\rightarrow$ Click **"Set up"**:
   - Set **App permissions** to **"Read and Write"** (Default is Read-only!).
   - Type of App: **Web App, Automated App or Bot**.
   - Callback URL: `https://twitter.com` (can be any placeholder).
   - Website URL: `https://twitter.com`.
   - Click **Save**.
6. Go to the **"Keys and Tokens"** tab and generate:
   - `API Key` & `API Key Secret` (Consumer Keys)
   - `Access Token` & `Access Token Secret` (Generate with Read and Write permissions!)
7. Paste these into your `.env` file.

---

## 🛠️ CLI Commands Reference

| Command | Description |
| :--- | :--- |
| `python main.py --dry-run` | Picks the next unposted topic from the catalog and previews the thread locally. |
| `python main.py --brainstorm --dry-run` | Uses Gemini to autonomously invent a brand new dual-audience topic on the fly. |
| `python main.py --post` | Generates the thread and publishes it live to X. |
| `python main.py --topic "<title>"` | Generates a thread on a specific custom topic. |
| `python main.py --list-topics` | Displays all 30+ pre-seeded topics and their `[POSTED]` / `[PENDING]` status. |
| `python main.py --stats` | Shows count of posted vs remaining topics in the queue. |
| `python main.py --test-twitter` | Verifies your Twitter API keys and prints your authenticated `@handle`. |

---

## ⏰ Set up 100% Automated 2x Daily Posting (GitHub Actions)

Once you push this code to a GitHub repository, it can run completely hands-free twice a day!

1. Push your code to a **private** GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Twitter Tech Thread Agent"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```
2. In your GitHub repository:
   - Go to **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions**.
   - Click **New repository secret** and add the following:
     - `GEMINI_API_KEY`
     - `TWITTER_API_KEY`
     - `TWITTER_API_SECRET`
     - `TWITTER_ACCESS_TOKEN`
     - `TWITTER_ACCESS_TOKEN_SECRET`
     - `TWITTER_HANDLE` (optional, your handle without `@`)
3. Enable Workflow write permissions:
   - In repo **Settings** $\rightarrow$ **Actions** $\rightarrow$ **General**.
   - Under **Workflow permissions**, select **"Read and write permissions"** (allows the bot to commit `posted_history.json` back to your repo so it never repeats a topic).
   - Click **Save**.

That's it! GitHub Actions will run automatically at:
- **08:30 AM IST (03:00 UTC)**: Morning commute tech read.
- **06:30 PM IST (13:00 UTC)**: Evening peak engagement slot.
