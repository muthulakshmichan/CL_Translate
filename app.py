import os
import json
import openai
from langdetect import detect

# Set up the OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']

# Function to detect language of the text
def detect_language(text):
    try:
        return detect(text)
    except:
        return 'unknown'

# Function to translate text using OpenAI API
def translate_text(text, src='ta', dest='en'):
    try:
        if src != 'en' and dest == 'en':
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a translation assistant that translates Tamil text to English exactly as it is without adding any additional context or interpretation."},
                    {"role": "user", "content": f"Tamil: {text}\nTranslate to English:"}
                ],
                max_tokens=150,
                temperature=0
            )
            translated_text = response['choices'][0]['message']['content'].strip()
            return translated_text
        else:
            return text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# Lambda function handler
def lambda_handler(event, context):
    print("Event received:", event)
    try:
        # Extracting body from event
        body = json.loads(event['body'])

        # Extracting comment from body
        comment = body.get('comment')

        # Check if comment is provided
        if not comment:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "Missing 'comment' in the request body."}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            }

        # Detect language of the comment
        comment_language = detect_language(comment)

        # Translate comment if not in English
        translated_comment = translate_text(comment, src=comment_language, dest='en')

        # Prepare response JSON
        response = {
            "original_comment": comment,
            "translated_comment": translated_comment
        }

        # Return HTTP response
        return {
            'statusCode': 200,
            'body': json.dumps(response),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
    except Exception as e:
        # Return error response if any exception occurs
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
