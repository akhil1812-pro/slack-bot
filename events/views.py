from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from slack_sdk import WebClient
import json
import logging
import dateparser
import re
from datetime import datetime, timedelta
from .models import FAQ
FAQS = {
    "leave policy": "📄 *Leave Policy*\nYou get 24 paid leaves per year. Carry forward up to 12 leaves.",
    "work from home": "🏠 *Work From Home*\nYou can work remotely up to 3 days a week with manager approval.",
    "salary": "💰 *Salary Info*\nSalary is credited on the last working day of each month.",
    "benefits": "🎁 *Benefits*\nWe offer health insurance, wellness reimbursements, and learning budgets.",
    "probation": "📝 *Probation Period*\nNew employees have a 3-month probation period with monthly reviews."
}

# Setup logging
logger = logging.getLogger(__name__)

# Load tokens from settings
SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)

# Initialize Slack client
Client = WebClient(token=SLACK_BOT_USER_TOKEN)

class InteractionView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.data.get('payload'))
            user_id = payload['user']['id']
            action_value = payload['actions'][0]['value']
            channel_id = payload['channel']['id']

            logger.warning(f"Button clicked: {action_value} by {user_id}")

            mood_map = {
                "great": "😊 Glad you're feeling great!",
                "okay": "😐 Hope your day gets better!",
                "meh": "😞 Sending good vibes your way!"
            }

            reply = mood_map.get(action_value, "Thanks for checking in!")
            Client.chat_postMessage(channel=channel_id, text=f"<@{user_id}> {reply}")
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Interaction error: {e}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Events(APIView):
    def post(self, request, *args, **kwargs):
        try:
            slack_message = request.data
            logger.warning(f"Incoming Slack message: {slack_message}")

            if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
                return Response(status=status.HTTP_403_FORBIDDEN)

            if slack_message.get('type') == 'url_verification':
                challenge = slack_message.get("challenge")
                return Response({"challenge": challenge}, status=status.HTTP_200_OK)

            event = slack_message.get('event', {})
            if event:
                if event.get('bot_id') or event.get('subtype') == 'bot_message':
                    return Response(status=status.HTTP_200_OK)

                user = event.get('user')
                text = event.get('text', '')
                channel = event.get('channel')

                bot_text = None
                if user and text:
                    lowered = text.lower()
                    if 'hello' in lowered:
                        bot_text = f"Hello Akhil <@{user}> 👋🎉 How can I help you? 🤖"
                    elif "hi" in lowered:
                        bot_text = f"Hi <@{user}> 👋"
                    elif "help" in lowered:
                        bot_text = (
                            "Here's what I can do:\n"
                            "- Say `hi` → I’ll greet you\n"
                            "- Say `joke` → I’ll tell you a joke\n"
                            "- Say `status` → I’ll check my health\n"
                            "- Say `help` → I’ll show this message again"
                        )
                    elif "joke" in lowered:
                        bot_text = "Why don’t programmers like nature? It has too many bugs. 🐛"
                    elif "status" in lowered:
                        bot_text = "All systems go! ✅ I'm running smoothly."

                if bot_text:
                    try:
                        Client.chat_postMessage(channel=channel, text=bot_text)
                    except Exception as e:
                        logger.error(f"Slack message failed: {e}", exc_info=True)
                    return Response(status=status.HTTP_200_OK)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unhandled exception: {e}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SlashCommandView(APIView):
    def post(self, request, *args, **kwargs):
        logger.warning(f"Slash command received: {request.data}")

        text = request.data.get('text', '').lower()
        user_id = request.data.get('user_id')
        channel_id = request.data.get('channel_id')

        reply = "I didn’t understand that. Try `/mybot help`"

        try:
            if "hi" in text:
                reply = f"Hi <@{user_id}> 👋"
            elif "help" in text:
                reply = "Try `/mybot joke`, `/mybot status`, `/mybot faq`, `/mybot remind`, or `/mybot checkin`"
            elif "joke" in text:
                reply = "Why do Java developers wear glasses? Because they don’t C#."
            elif "status" in text:
                reply = "Bot is alive and kicking! ✅"
            elif "list faqs" in text:
                faqs = FAQ.objects.all()
                if faqs:
                    reply = "*Here are the available FAQ topics:*\n"
                    for faq in faqs:
                        reply += f"• {faq.question}\n"
                else:
                    reply = "There are no FAQs available right now. Please check back later."
                from django.http import JsonResponse
                import os

                def slack_event_view(request):
                    token = os.getenv("SLACK_BOT_TOKEN")
                    secret = os.getenv("SLACK_SIGNING_SECRET")
                    # Use these to verify and respond to Slack
            elif "faq" in text:
                matched = None
                faqs = FAQ.objects.all()
                if faqs:
                    for faq in faqs:
                        if faq.question.lower() in text:
                            matched = faq.answer
                            break
                else:
                    for key in FAQS:
                        if key in text:
                            matched = FAQS[key]
                            break
                reply = matched or "❓ I couldn’t find that FAQ. Try asking about something listed in the admin panel." 
            elif "remind" in text:
                parts = text.split("remind me to", 1)
                if len(parts) < 2:
                    reply = "Please use the format: `/mybot remind me to [task] in [time]`"
                else:
                    task_part = parts[1].strip()

                    if " in " in task_part:
                        task, time_phrase = task_part.rsplit(" in ", 1)
                    elif " at " in task_part:
                        task, time_phrase = task_part.rsplit(" at ", 1)
                    else:
                        reply = "Please include both the task and time, like 'remind me to stretch in 30 minutes' or 'submit report at 5:30pm'."
                        return Response({"text": reply}, status=status.HTTP_200_OK)

                    time_phrase = time_phrase.strip()

                    # Try to extract minutes from "in X minutes"
                    match = re.match(r"(\d+)\s*minute", time_phrase)
                    if match:
                        minutes = int(match.group(1))
                        reminder_time = datetime.now() + timedelta(minutes=minutes)
                    else:
                        reminder_time = dateparser.parse(time_phrase)

                    logger.warning(f"Parsed reminder time: {reminder_time}")

                    if not reminder_time:
                        reply = "I couldn’t understand the time. Try something like 'in 30 minutes' or 'at 5pm'."
                    else:
                        post_at = int(reminder_time.timestamp())
                        now = int(datetime.now().timestamp())

                        if post_at - now < 60:
                            post_at = now + 120
                            reply = f"Reminder set for *{task}* in 2 minutes (adjusted for safety)."
                        else:
                            reply = f"Reminder set for *{task}* at {reminder_time.strftime('%I:%M %p')}!"

                        Client.chat_scheduleMessage(
                            channel=channel_id,
                            text=f"⏰ Reminder: {task}",
                            post_at=post_at
                        )
            elif "checkin" in text:
                Client.chat_postMessage(
                    channel=channel_id,
                    text="Good morning! How are you feeling today?",
                    blocks=[
                        {
                            "type": "actions",
                            "elements": [
                                {"type": "button", "text": {"type": "plain_text", "text": "😊 Great"}, "value": "great"},
                                {"type": "button", "text": {"type": "plain_text", "text": "😐 Okay"}, "value": "okay"},
                                {"type": "button", "text": {"type": "plain_text", "text": "😞 Meh"}, "value": "meh"}
                            ]
                        }
                    ]
                )
                reply = "Check-in sent!"
        except Exception as e:
            logger.error(f"Slash command error: {e}", exc_info=True)
            reply = "Something went wrong while processing your command."

        return Response({"text": reply}, status=status.HTTP_200_OK)