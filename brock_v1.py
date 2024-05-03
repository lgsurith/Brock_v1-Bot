import os
import io
import logging
import PIL.Image
import sys
import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode, ChatActions
from aiogram.utils import executor

# Use os.getenv for the Google Cloud Project ID and Location
PROJECT_ID = os.getenv('PROJECT_ID')
LOCATION = os.getenv('LOCATION')  
ENDPOINT_ID = os.getenv('ENDPOINT_ID')  # Your Vertex AI endpoint ID
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Create the Vertex AI model instance
model = GenerativeModel(f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT_ID}")

# Create the bot object
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

# Optional: Generation and Safety Settings
generation_config = {
    "max_output_tokens": 2048,
    "temperature": 1,
    "top_p": 1,
}
safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

@dp.message_handler(commands=['brock'])
async def gemi_handler(message: types.Message):
    loading_message = None
    try:
        loading_message = await message.answer("<b>Brock is thinking , please wait...</b>", parse_mode='html')

        if len(message.text.strip()) <= 5:
            await message.answer("<b>Please provide a prompt after the command.</b>", parse_mode='html')
            return

        prompt = message.text.split(maxsplit=1)[1:]

        # Start a chat session with the Vertex AI model
        chat = model.start_chat()

        # Send the prompt and get the response
        response = chat.send_message(prompt, generation_config=generation_config, safety_settings=safety_settings)
        print(f"Debug : Response obtained is : {response}") #debug for response
        response_text = response.text

        if len(response_text) > 4000:
            parts = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
            for part in parts:
                await message.answer(part, parse_mode='markdown')
        else:
            await message.answer(response_text, parse_mode='markdown')
    
    #exception handling if anything 
    except Exception as e:
        await message.answer(f"An error occurred: {str(e)}")
    finally:
        if loading_message:
            await bot.delete_message(chat_id=loading_message.chat.id, message_id=loading_message.message_id)



if __name__ == '__main__' and '--debug' in sys.argv:
    prompt = input("Enter your prompt : ")
    chat = model.start_chat()
    response = chat.send_message(prompt, generation_config=generation_config, safety_settings=safety_settings)
    print(f"Debug : response {response}")
else:
    executor.start_polling(dp, skip_updates=True)