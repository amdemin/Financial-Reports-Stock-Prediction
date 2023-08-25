# Import libraries
import os
import tiktoken

# Import libraries
import pandas as pd
import numpy as np
import os
import openai

# Import credentials
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