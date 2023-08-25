# Import libraries
import openai
import tiktoken
import re

# Load local modules
from module_text_blocks import split_text_into_blocks, clean_text_blocks

# load credentials for OpenAI API
from credentials_openai import *
openai.api_key = openai_api_key


def split_text_by_chars(text, num_chars):
    """Split the input text every num_chars characters."""
    return [text[i:i+num_chars] for i in range(0, len(text), num_chars)]


# define the number of tokens in the prompt
def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def summarize_long_text_blocks(text_blocks):

    for heading, text in text_blocks.items():
        
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
                # top_p=1, frequency_penalty=0, presence_penalty=0, stop=["\n"]
                # add the summarized text to the list of responses
                responses.append(completion.choices[0].message.content)

            # join the responses into a single text block
            text_blocks[heading] = ' '.join(responses)
    
    return text_blocks


def openai_sentiment_analysis(final_prompt):

    # run the request for ChatGPT
    fine_tune_messages = {"role": "system", "content":
                    "You are a helpful financial assistant who is expert in evaluating sentiment scores for financial statements \
                You give precise answers to questions \
                the quality of your answers is highly important, you never hallucinate answers - only \
                answering based on your knowledge. Where the answer requires creative thought you engage \
                in reflective internal dialogue to ascertain the best answer"
    }

    user_content = "The overall polarity and subjectivity scores on the strict range (very negative, moderately negative, slightly negative, neutral, slightly positive, moderately positive, very positive) for the text: "

    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        fine_tune_messages,
        {"role": "user", "content": user_content + final_prompt}
    ],
    temperature=0.0,
    max_tokens=50
    )

    return completion.choices[0].message.content

def preprocess_response(original_response):
    
    try:

        response = " ".join(original_response.split(":")[1:])
        response = response.split("Subjectivity")[0]

        # Extract the sentiment from the responses
        extract_sentiment_words = '(very negative|moderately negative|slightly negative|neutral|slightly positive|moderately positive|very positive)'

        sentiment = re.findall(extract_sentiment_words, response, re.IGNORECASE)

        if sentiment == []:

            response = " ".join(original_response.split(".")[0])
            sentiment = re.findall('(mixed|positive)', original_response, re.IGNORECASE)

        if len(sentiment) > 1:
            return "Multiple sentiments detected"

        else:
            return sentiment[0].lower()        
    
    except Exception as e:

        print(f"Exception message: {str(e)}")


# Convert the sentiment to a number
def sentiment_to_number(sentiment):
    """Converts the sentiment to a number."""
    sentiment_dict = {"very negative": -1, "moderately negative": -0.5, "slightly negative": -0.25, "neutral": 0, "mixed": 0, "slightly positive": 0.25, "moderately positive": 0.5, "positive": 0.5, "very positive": 1}
    return sentiment_dict[sentiment]


def calculate_openai_polarity(text_blocks, headings, text):

    try:

        # if there are headings, add headings to the text blocks and summarize if needed
        if len(headings) > 0:

            # summarize the text blocks
            text_blocks = summarize_long_text_blocks(text_blocks)

            # Create a final prompt
            final_prompt = ''
            for heading, text in text_blocks.items():
                if num_tokens_from_string(final_prompt + text, "cl100k_base") >= 3750:
                    break
                final_prompt += heading + ': ' + text + " "

        # if there are no headings  
        else:
            
            tokens_number = num_tokens_from_string(text, "cl100k_base")  # number of tokens in the text block
            chars_number = len(text)                                     # number of characters in the text block
            
            # if the block is exceeding the token limit, cut it
            if tokens_number > 3500:

                text_split_threshold = int(chars_number / (tokens_number / 2500))
                text = text[:text_split_threshold]

            final_prompt = text
            

        # Perform openAI sentiment analysis
        response = openai_sentiment_analysis(final_prompt)

        # Preprocess the response
        response = preprocess_response(response)
        
        if response != "Multiple sentiments detected":
            response = sentiment_to_number(response)
            return response
        else:
            return response


    except Exception as e:

        print(f"Exception message: {str(e)}")