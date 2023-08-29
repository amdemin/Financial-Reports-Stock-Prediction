# Import libraries
import os
import sys
import time
import pickle
import pandas as pd

# Import Local Modules
sys.path.append("Pipeline/")
from module_text_blocks import split_text_into_blocks, clean_text_blocks

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


if __name__ == "__main__":

    last_report = True
    if last_report:
        # Load the latest pdf text and heading from the pickle file
        pdf_texts = pickle.load(open("Src/pdf_texts_last_report.pkl", "rb"))
        pdf_headings = pickle.load(open("Src/pdf_headings_last_report.pkl", "rb"))
        pdf_headings_context = pickle.load(open("Src/pdf_headings_context_last_report.pkl", "rb"))

    else:
        # Load 50 pdf texts and headings from the pickle file
        pdf_texts = pickle.load(open("Src/pdf_texts.pkl", "rb"))
        pdf_headings = pickle.load(open("Src/pdf_headings.pkl", "rb"))
        pdf_headings_context = pickle.load(open("Src/pdf_headings_context.pkl", "rb"))
    
    # set start time
    start = time.time()

    sentiment_scores = {}

    for pdf_file in pdf_texts:

        # Get text, headings and headings context
        text = pdf_texts[pdf_file]
        headings = pdf_headings[pdf_file]
        headings_context = pdf_headings_context[pdf_file]

        # Split text into blocks
        text_blocks = split_text_into_blocks(text, headings, headings_context)

        # Clean text blocks
        text_blocks = clean_text_blocks(text_blocks)

        # Calculate sentiment score
        sentiment_score = calculate_google_polarity(text_blocks, headings, text)

        sentiment_scores[pdf_file] = sentiment_score

    # set end time
    end = time.time()
    print('Time taken to calculate sentiment using Google model: ', end - start)

    # convert dictionary to dataframe
    google_polarity_df = pd.DataFrame.from_dict(sentiment_scores, orient='index', columns=['polarity']).reset_index()
    # rename index column
    google_polarity_df.rename(columns={'index': 'pdf_name'}, inplace=True)

    print(google_polarity_df.head())

    # export dataframe to csv
    # google_polarity_df.to_csv('Scores/google_polarity.csv', index=False)