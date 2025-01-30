import logging
from dotenv import load_dotenv
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import json
from datetime import datetime, timedelta
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Import env variables and API Keys
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# User data storage
users = {}


# User analytics
class Analytics:
    def __init__(self):
        self.data = {}

    def add_data_point(self, user_id: int, day: int, views: int):
        if user_id not in self.data:
            self.data[user_id] = []
        self.data[user_id].append({"day": day, "views": views})

    def get_growth_rate(self, user_id: int) -> float:
        if user_id not in self.data or len(self.data[user_id]) < 2:
            return 0.0

        # Get views growth rate
        first_views = self.data[user_id][0]["views"]
        last_views = self.data[user_id][-1]["views"]
        return (
            ((last_views - first_views) / first_views) * 100 if first_views > 0 else 0
        )

    def generate_growth_chart(self, user_id: int) -> BytesIO:
        if user_id not in self.data:
            return None

        # This will be generated once a cycle of 7 days completes
        df = pd.DataFrame(self.data[user_id])
        plt.figure(figsize=(10, 6))
        plt.plot(df["day"], df["views"], marker="o")
        plt.title("Your Content Growth")
        plt.xlabel("Day")
        plt.ylabel("Views")
        plt.grid(True)

        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        return buf


class CreatorBot:
    def __init__(self):
        self.challenge_participants = {}
        self.analytics = Analytics()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when /start is issued."""
        user_id = update.effective_user.id
        users[user_id] = {"state": "initial"}

        welcome_text = (
            "🎉 Welcome to the Content Creator Guide Bot! 🎉\n\n"
            "I'm here to help you become a successful content creator. "
            "Let's start by getting to know you better!"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "Share Social Handle 📱", callback_data="share_handle"
                )
            ],
            [
                InlineKeyboardButton(
                    "View Creator Guide 📚", callback_data="creator_guide"
                )
            ],
            [
                InlineKeyboardButton(
                    "Start 21-Day Challenge 🎯", callback_data="challenge_info"
                )
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button presses."""
        query = update.callback_query
        await query.answer()

        if query.data == "share_handle":
            await self.request_social_handle(update, context)
        elif query.data == "creator_guide":
            await self.show_creator_guide(update, context)
        elif query.data == "challenge_info":
            await self.show_challenge_info(update, context)
        elif query.data == "start_challenge":
            await self.start_challenge(update, context)

    async def request_social_handle(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Request user's social media handle."""
        text = "Please share your main social media handle (e.g., @username)"
        users[update.effective_user.id]["state"] = "awaiting_handle"
        await update.callback_query.message.reply_text(text)

    async def handle_social_handle(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Process the social media handle."""
        user_id = update.effective_user.id
        handle = update.message.text

        users[user_id]["social_handle"] = handle
        await update.message.reply_text(
            "Thanks! Now, could you share the link to your most viral content "
            "and its view count? (Format: link, views)"
        )
        users[user_id]["state"] = "awaiting_viral_content"

    async def show_creator_guide(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Display the content creator guide."""
        guide_text = """
📚 Content Creator Guide 2025 📚

1. Finding Your Niche
- Identify your passions and expertise
- Research market demand
- Analyze competition
- Find your unique angle

2. Content Strategy
- Define your target audience
- Create content pillars
- Develop a consistent posting schedule
- Plan content themes and series

3. Content Creation Tips
- Focus on quality over quantity
- Use trending topics strategically
- Create shareable moments
- Optimize for each platform

4. Growth Strategies
- Engage with your community
- Collaborate with other creators
- Use platform-specific features
- Analyze and adapt based on metrics

Want to put this knowledge into practice? Start the 21-day challenge! 🎯
"""
        keyboard = [
            [
                InlineKeyboardButton(
                    "Start 21-Day Challenge 🎯", callback_data="challenge_info"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(
            guide_text, reply_markup=reply_markup
        )

    async def show_challenge_info(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Show information about the 21-day challenge."""
        challenge_text = """
🎯 21-Day Createathon Challenge 🎯

Challenge Rules:
1. Create and post content every day for 21 days
2. Share your content link and views daily
3. Get feedback and improvement suggestions
4. Track your growth journey

Ready to transform your content creation journey?
"""
        keyboard = [
            [
                InlineKeyboardButton(
                    "Start Challenge Now! 🚀", callback_data="start_challenge"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if isinstance(update.callback_query.message, object):
            await update.callback_query.message.reply_text(
                challenge_text, reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(challenge_text, reply_markup=reply_markup)

    async def start_challenge(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the 21-day challenge for a user."""
        user_id = update.effective_user.id
        self.challenge_participants[user_id] = {
            "start_date": datetime.now(),
            "current_day": 1,
            "posts": [],
            # new method job.run_once() was not working
            "last_reminder": datetime.now(),
        }

        await update.callback_query.message.reply_text(
            "🎉 Challenge started! Get ready for 21 days of content creation!\n"
            "I'll send you daily reminders to post your content."
        )

        # await self.send_daily_reminder(user_id, context)
        reminder_text = (
            "Day 1/21 of your Createathon Challenge!\n\n"
            "Please share today's content link and views count (Format: link, views)"
        )

        await update.callback_query.message.reply_text(reminder_text)
        users[user_id]["state"] = "in_challenge"

    async def send_daily_reminder(
        self, user_id: int, context: ContextTypes.DEFAULT_TYPE
    ):
        """Send daily reminder to challenge participants."""
        if user_id in self.challenge_participants:
            participant = self.challenge_participants[user_id]
        if participant["current_day"] <= 21:
            reminder_text = (
                f"Day {participant['current_day']}/21 of your Createathon Challenge!\n\n"
                "Please share today's content link and views count (Format: link, views)"
            )
            await context.bot.send_message(user_id, reminder_text)

            # Schedule next reminder for tomorrow at the same time
            if participant["current_day"] < 21:
                next_time = datetime.now() + timedelta(days=1)

                job_name = f"reminder_{user_id}_{participant['current_day'] + 1}"
                context.job_queue.run_once(
                    lambda ctx: asyncio.create_task(
                        self.send_daily_reminder(user_id, ctx)
                    ),
                    when=next_time,
                    name=job_name,
                )

    async def handle_viral_content(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Process the viral content information."""
        user_id = update.effective_user.id

        content_link, views = map(str.strip, update.message.text.split(","))
        views = int(views)

        users[user_id]["viral_content"] = {"link": content_link, "views": views}

        # Analyze creator potential
        recommendation = ""
        if views >= 10000:
            recommendation = "Your content shows high viral potential! Consider starting the challenge."
        elif views >= 1000:
            recommendation = (
                "Good start! The challenge can help you reach bigger audiences."
            )
        else:
            recommendation = (
                "Let's work on growing your audience through the challenge!"
            )

        keyboard = [
            [
                InlineKeyboardButton(
                    "Start 21-Day Challenge 🎯", callback_data="challenge_info"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Thanks for sharing! {recommendation}", reply_markup=reply_markup
        )

        users[user_id]["state"] = "ready_for_challenge"

    async def handle_challenge_update(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle daily challenge updates from participants."""
        user_id = update.effective_user.id

        if user_id not in self.challenge_participants:
            await update.message.reply_text("Please start the challenge first!")
            return

        content_link, views = map(str.strip, update.message.text.split(","))
        views = int(views)

        participant = self.challenge_participants[user_id]
        current_day = participant["current_day"]

        # Store the daily update
        participant["posts"].append(
            {
                "day": current_day,
                "link": content_link,
                "views": views,
                "timestamp": datetime.now(),
            }
        )

        # Update analytics
        self.analytics.add_data_point(user_id, current_day, views)

        # Generate progress report
        growth_rate = self.analytics.get_growth_rate(user_id)

        # Send progress update
        progress_text = (
            f"✅ Day {current_day} Update Recorded!\n\n"
            f"📈 Growth Rate: {growth_rate:.1f}%\n"
            f"📊 Total Posts: {len(participant['posts'])}\n"
            f"🎯 Days Remaining: {21 - current_day}"
        )

        # Send growth chart every 7 days
        if current_day % 7 == 0:
            chart = self.analytics.generate_growth_chart(user_id)
            if chart:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=chart,
                    caption="Your 7-day growth chart 📈",
                )

        # Check for challenge completion
        if current_day >= 21:
            await self.handle_challenge_completion(update, context)

        # Check progress for test = 2 days
        # if current_day >= 2:
        #     await self.handle_challenge_completion(update, context)

        else:
            participant["current_day"] += 1
            await update.message.reply_text(progress_text)


    # handler function for after completion of challenge
    async def handle_challenge_completion(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle completion of the 21-day challenge."""
        user_id = update.effective_user.id
        participant = self.challenge_participants[user_id]

        # Calculate final statistics
        total_views = sum(post["views"] for post in participant["posts"])
        avg_views = total_views / len(participant["posts"])
        growth_rate = self.analytics.get_growth_rate(user_id)

        completion_text = (
            "🎉 Congratulations on completing the 21-day challenge! 🎉\n\n"
            f"📊 Final Statistics:\n"
            f"- Total Views: {total_views:,}\n"
            f"- Average Views: {avg_views:,.1f}\n"
            f"- Growth Rate: {growth_rate:.1f}%\n\n"
        )

        # Generate recommendations based on performance
        if growth_rate > 100:
            completion_text += (
                "🌟 Outstanding growth! You're ready for brand partnerships!"
            )
        elif growth_rate > 50:
            completion_text += "💪 Great progress! Consider starting another challenge!"
        else:
            completion_text += (
                "📈 Good effort! Let's analyze and improve your strategy!"
            )

        # Send final growth chart
        chart = self.analytics.generate_growth_chart(user_id)
        if chart:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=chart,
                caption="Your complete challenge growth chart 📈",
            )

        await update.message.reply_text(completion_text)

        # Clean up challenge data but keep analytics
        del self.challenge_participants[user_id]

    # async def get_analytics_summary(self, user_id: int) -> str:
    #     """Generate an analytics summary for a user."""
    #     if user_id not in self.analytics.data:
    #         return "No analytics data available yet."

    #     data = self.analytics.data[user_id]
    #     total_views = sum(point["views"] for point in data)
    #     avg_views = total_views / len(data)
    #     growth_rate = self.analytics.get_growth_rate(user_id)

    #     return (
    #         "📊 Analytics Summary:\n\n"
    #         f"- Total Views: {total_views:,}\n"
    #         f"- Average Views: {avg_views:,.1f}\n"
    #         f"- Growth Rate: {growth_rate:.1f}%\n"
    #         f"- Days Tracked: {len(data)}"
    #     )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages based on user state."""
        user_id = update.effective_user.id

        if user_id not in users:
            await self.start(update, context)
            return

        state = users[user_id].get("state")

        if state == "awaiting_handle":
            await self.handle_social_handle(update, context)
        elif state == "awaiting_viral_content":
            await self.handle_viral_content(update, context)
        elif state == "in_challenge":
            await self.handle_challenge_update(update, context)

            # After handling the update, send the next day's task
            if user_id in self.challenge_participants[user_id]:
                participant = self.challenge_participants[user_id]
                if participant["current_day"] <= 21:
                    next_reminder = (
                        f"Day {participant['current_day']}/21 of your Createathon Challenge!\n\n"
                        "Please share tomorrow's content link and views count when ready (Format: link, views)"
                    )
                    await update.message.reply_text(next_reminder)

                # In order to test out the remaining days, days fixed = 2
                # if participant["current_day"] <= 2:
                #     next_reminder = (
                #         f"Day {participant['current_day']}/21 of your Createathon Challenge!\n\n"
                #         "Please share tomorrow's content link and views count when ready (Format: link, views)"
                #     )
                #     await update.message.reply_text(next_reminder)

    def run(self, token: str):
        """Run the bot."""
        application = Application.builder().token(token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        # Start the bot
        application.run_polling()


if __name__ == "__main__":
    # Replace with your bot token
    BOT_TOKEN = os.getenv("MY_BOT_TOKEN")

    bot = CreatorBot()
    bot.run(BOT_TOKEN)
