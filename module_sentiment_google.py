# Import libraries
import os

# Connect to Google API
from google.cloud import language_v1
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials_google.json"


def google_sentiment_analysis(final_prompt):
    
    client = language_v1.LanguageServiceClient()

    if isinstance(final_prompt, bytes):
        final_prompt = final_prompt.decode("utf-8")

    type_ = language_v1.Document.Type.PLAIN_TEXT
    document = {"type_": type_, "content": final_prompt}

    response = client.analyze_sentiment(request={"document": document})
    sentiment = response.document_sentiment
    
    polarity_score = sentiment.score

    return polarity_score


def calculate_google_polarity(text_blocks, headings, text):

    try:

        final_prompt = ''
        if len(headings) > 0:
            for heading, text in text_blocks.items():
                final_prompt += heading + ': ' + text + " "
        else:
            final_prompt = text

        polarity_score = google_sentiment_analysis(final_prompt)
        
        return polarity_score

    except Exception as e:

        print(f"Exception message: {str(e)}")