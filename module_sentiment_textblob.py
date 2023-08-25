# Import libraries
from textblob import TextBlob


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