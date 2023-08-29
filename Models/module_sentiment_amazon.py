# Import libraries
import pandas as pd
import numpy as np
import os
import sys
import openai
import tiktoken
import time
import pickle

# Import Local Modules
sys.path.append("Pipeline/")
from module_text_blocks import split_text_into_blocks, clean_text_blocks

# Import credentials
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from credentials_amazon import *
from credentials_openai import *
openai.api_key = openai_api_key

# Connect to Amazon API
import boto3
os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
os.environ["AWS_REGION"] = AWS_REGION


def amazon_analyze_sentiment(text):
    comprehend = boto3.client(service_name='comprehend', region_name="us-west-2")
    sentiment_response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    return sentiment_response["SentimentScore"]


def split_text_by_chars(text, num_chars):
    """Split the input text every num_chars characters."""
    return [text[i:i+num_chars] for i in range(0, len(text), num_chars)]


# define the number of tokens in the prompt
def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def summarize_long_text_blocks(text):
        
    text_length = len(text.split(' '))                           # number of words in the text block
    tokens_number = num_tokens_from_string(text, "cl100k_base")  # number of tokens in the text block
    chars_number = len(text)                                     # number of characters in the text block
                    
    summarization_blocks = [text]                                # list of text blocks to summarize
    responses = []

    # if the block contains over 750 words, summarize it
    if text_length > 750:

        # if the block is exceeding the token limit, split it into multiple blocks
        if tokens_number > 3500:

            text_split_threshold = int(chars_number / (tokens_number / 2500))
            summarization_blocks = split_text_by_chars(text, text_split_threshold)
            
        for summarization_block in summarization_blocks:

            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "user", "content": "Please effectively summarize the following text: " + summarization_block}
                ],
                temperature=0.3,
                max_tokens=500
            )                
            # add the summarized text to the list of responses
            responses.append(completion.choices[0].message.content)

        # join the responses into a single text block
        text = ' '.join(responses)
    
    return text


def calculate_amazon_polarity(text_blocks, headings, text):

    try:

        text_blocks_scores = []

        # iterate over the text blocks individually, otherwise single request with all text will fail
        if len(headings) > 0:

            for heading, text_block in text_blocks.items():

                if heading == "Reference":
                    break

                if len(text_block) == 0:
                    continue

                # the prompt for amazon sentiment analysis should be less than 5000 bytes
                if len(text_block) < 4750:
                    polarity_score = amazon_analyze_sentiment(text_block)
                    key = max(polarity_score, key=polarity_score.get)
                    text_blocks_scores.append(polarity_score[key])
                
                # split into multi blocks if the text is too long
                else:
                    text_block = summarize_long_text_blocks(text_block)
                    polarity_score = amazon_analyze_sentiment(text_block)
                    key = max(polarity_score, key=polarity_score.get)
                    text_blocks_scores.append(polarity_score[key])
                

        # if there are no headings, just split the text into block of 4000 characters
        else:
            print("--- No headings found, splitting text into blocks of 4000 characters")
            text_blocks = split_text_by_chars(text, 4000)
            for text in text_blocks:
                polarity_score = amazon_analyze_sentiment(text)
                key = max(polarity_score, key=polarity_score.get)
                text_blocks_scores.append(polarity_score[key])
                
        polarity_score = np.mean(text_blocks_scores)

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
        sentiment_score = calculate_amazon_polarity(text_blocks, headings, text)

        # Add sentiment score to dictionary
        sentiment_scores[pdf_file] = sentiment_score

    # set end time
    end = time.time()
    print('Time taken to calculate sentiment using Amazon model: ', end - start)

    # convert dictionary to dataframe
    amazon_polarity_df = pd.DataFrame.from_dict(sentiment_scores, orient='index', columns=['polarity']).reset_index()
    # rename index column
    amazon_polarity_df.rename(columns={'index': 'pdf_name'}, inplace=True)

    print(amazon_polarity_df.head())

    # export dataframe to csv
    # amazon_polarity_df.to_csv("Scores/amazon_polarity.csv", index=False)