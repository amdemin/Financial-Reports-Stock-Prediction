# Import libraries
from textblob import TextBlob
import pandas as pd
import numpy as np
import pickle
import time
import os
import sys

# Import Local Modules
sys.path.append("Pipeline/")
from module_text_blocks import split_text_into_blocks, clean_text_blocks


def calculate_textblob_polarity(text_blocks, headings, text):

    try:

        final_prompt = ''

        # if there are headings, add them into the prompt
        if len(headings) > 0:
            for heading, text in text_blocks.items():
                final_prompt += heading + ': ' + text + " "
        else:
            final_prompt = text

        polarity_score = TextBlob(final_prompt).sentiment.polarity
        
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
        sentiment_score = calculate_textblob_polarity(text_blocks, headings, text)

        sentiment_scores[pdf_file] = sentiment_score

    # set end time
    end = time.time()
    print('Time taken to calculate sentiment using TextBlob model: ', end - start)

    # convert dictionary to dataframe
    textblob_polarity_df = pd.DataFrame.from_dict(sentiment_scores, orient='index', columns=['polarity']).reset_index()
    # rename index column
    textblob_polarity_df.rename(columns={'index': 'pdf_name'}, inplace=True)

    print(textblob_polarity_df.head())

    # export dataframe to csv
    # textblob_polarity_df.to_csv('Src/textblob_polarity_df.csv', index=False)