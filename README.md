# 🤖 Gato Bot — Smart Slack Assistant

**Gato Bot** is a smart Slack assistant built with **Django** and **Slack SDK**, designed to automate common team tasks like FAQs, reminders, feedback collection, and interactive check-ins — all directly inside Slack.  
Perfect for teams who want quick answers, daily mood tracking, and light automation.

---

## 🚀 Features

- 💬 `/mybot help` — Displays all available commands  
- 📄 `/mybot faq [topic]` — Answers company FAQs (e.g., leave policy, benefits)  
- 📚 `/mybot list faqs` — Lists all available FAQ topics  
- ⏰ `/mybot remind me to [task] in/at [time]` — Creates time-based reminders  
- 🧠 `/mybot feedback [message]` — Collects user feedback in Django Admin  
- 😊 `/mybot checkin` — Sends mood-tracking buttons (Great / Okay / Meh)  
- 💡 Responds to casual messages like “hi”, “joke”, “help”, or “status”

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | Django + Django REST Framework |
| **API Integration** | Slack SDK (`slack_sdk`) |
| **Deployment** | Render (Free Web Service) |
| **Database** | SQLite (local) / PostgreSQL (Render optional) |
| **Language** | Python 3.13 |
| **Tools** | Gunicorn, Requests, Dateparser |

---

## ⚙️ Local Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/akhil1812-pro/slack-faq-reminder-bot.git
cd slack-faq-reminder-bot
```

### 2️⃣ Install Dependencies
```
pip install -r requirements.txt
```

### 3️⃣ Add Environment Variables

Create a .env file in the project root with:

```
SLACK_CLIENT_ID=your_client_id
SLACK_CLIENT_SECRET=your_client_secret
SLACK_BOT_USER_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_VERIFICATION_TOKEN=your-verification-token
SLACK_REDIRECT_URI=https://yourdomain.com/slack/oauth_redirect/
```

### 4️⃣ Run Database & Start Server
```
python manage.py migrate
python manage.py runserver
```

## 💬 Slack App Configuration

In your Slack API Dashboard:

| Section                 | Setting                                                                      |
| ----------------------- | ---------------------------------------------------------------------------- |
| **Slash Command**       | `/mybot` → `https://yourdomain.com/slack/command/`                           |
| **Interactivity**       | Request URL → `https://yourdomain.com/slack/interactions/`                   |
| **Event Subscriptions** | Request URL → `https://yourdomain.com/slack/events/`                         |
| **OAuth Redirect URL**  | `https://yourdomain.com/slack/oauth_redirect/`                               |
| **Scopes**              | `commands`, `chat:write`, `users:read`, `channels:read`, `app_mentions:read` |

## ☁️ Deployment on Render

1. Push your project to GitHub

2. Create a new Web Service on Render
   
3. Set the Build Command:
   ```
   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   ```
4. Set the Start Command:
   ```
   gunicorn slackbot_project.wsgi:application --bind 0.0.0.0:$PORT
   ```

5. Add your environment variables in Render’s Environment tab

6. Deploy 🎉

## 🧪 Example Commands

```
/mybot help
/mybot faq leave policy
/mybot list faqs
/mybot remind me to drink water in 30 minutes
/mybot feedback I love this bot!
/mybot checkin
```

## 🧠 What I Learned

- How to integrate Django REST Framework with Slack APIs

- Handling OAuth 2.0 app install flows securely

- Managing tokens and environment variables

- Deploying Django apps to Render

- Keeping free web services alive using uptime pingers

## 👤 Author

### Akhil Bhojane
🎓 Computer Engineering Graduate | 🌱 Aspiring Software Developer | 💬 Exploring Python, APIs & Automation

- GitHub: https://github.com/akhil1812-pro
- LinkedIn: www.linkedin.com/in/akhil-bhojane-4ba15331b

## ⭐ Support

If you like this project, give it a ⭐ on GitHub and feel free to fork it or contribute!

