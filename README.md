# Content_bot_telegram
A telegram bot for content creators which helps them in guiding, tracking and analysing their content growth through different guides and a 21 day challenge. The bot, when challenge started, will give daily reminders for posting and keeping track of the posted content for the respective creator.    

Each day, after the user provides the content details, the bot stores and analyses the past data to show the growth rate. Also after a cycle of 7 days, the bot also shows the growth graph for the posted contents over the last 7 days. At the end of challenge completion, if the growth rate is good enough, it asks the user for further branch collaborations and stuffs. But if the growth is not good enough, then it encourages the user to restart the challenge again.

# How to use
1. Download the complete project
```ruby 
git clone https://github.com/Himangshu-Sarma/content-bot-telegram.git
```
2. Navigate to directory and install python-telegram-bot and other required dependencies if not already installed
```ruby
pip install python-telegram-bot  <add other dependencies if not previously installed>
```
3. Create a .env file and store the Telegram Bot Api Token in it and replace it with the bot token which is used here.
  
   NOTE: The Telegram Bot Api Token can be generated from the telegram bot ```TheBotFather```

4. Inside the directory run the command to run the python app
```ruby
python content_21_bot.py
```
5. Open Telegram and test the bot by typing any command perferably ( /start  :) ).

# Collaborations
If anyone is interested in trying new stuffs and adding extra features to this, he/she is welcome to do so !!!
