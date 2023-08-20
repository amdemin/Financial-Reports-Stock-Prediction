# Import libraries
import pandas as pd
import numpy as np
import re

# Preprocess the text before splitting into blocks
def preprocess_text(text):

    text = text.replace("\u200b", "")
    text = ' '.join(text.split())

    return text

# Split the text into blocks based on the headings
def split_text_into_blocks(text, headings, headings_context):

    text = preprocess_text(text)

    # define dictionary for storing text blocks
    text_blocks = {}

    # Iterate over the headings
    for heading in range(len(headings)):
        
        # get the heading context
        heading_context = list(headings_context.items())[heading][1]
        heading_context = " ".join(heading_context)

        # in the beginning of document, there is no heading, so let's define it as document intro
        if heading == 0:
            
            try:
                if re.search(headings[heading] + " " + heading_context, text):
                    document_intro = text.split(headings[heading] + " " + heading_context)[0]
                elif re.search(heading_context + " " + headings[heading], text):
                    document_intro = text.split(heading_context + " " + headings[heading])[0]
                    document_intro = heading_context + " " + document_intro
                else:
                    document_intro = text.split(headings[heading])[0]
            except:
                document_intro = text.split(headings[heading])[0]
            
            text_blocks['Document_intro'] = document_intro

        # prevent the error of index out of range
        if len(text.split(headings[heading])) > 1:
            
            try:
                if re.search(headings[heading] + " " + heading_context, text):
                    text_after_heading = text.split(headings[heading] + " " + heading_context)[1]
                    text_after_heading = heading_context + text_after_heading
                elif re.search(heading_context + " " + headings[heading], text):
                    text_after_heading = text.split(heading_context + " " + headings[heading])[1]
                else:
                    text_after_heading = text.split(headings[heading])[1]
            except:
                text_after_heading = text.split(headings[heading])[1]

        else:
            text_after_heading = ""

        # identify the last heading
        if heading == len(headings) - 1:

            text_blocks[headings[heading]] = text_after_heading
            break

        else:

            # identify middle headings with surrounding context
            next_heading_context = list(headings_context.items())[heading+1][1]
            next_heading_context = " ".join(next_heading_context)

            try:
                if re.search(headings[heading+1] + " " + next_heading_context, text_after_heading):
                    text_of_heading = text_after_heading.split(headings[heading+1] + " " + next_heading_context)[0]
                elif re.search(next_heading_context + " " + headings[heading+1], text_after_heading):
                    text_of_heading = text_after_heading.split(next_heading_context + " " + headings[heading+1])[0]
                    text_of_heading = text_of_heading + next_heading_context
                else:
                    text_of_heading = text_after_heading.split(headings[heading+1])[0]
            except:
                text_of_heading = text_after_heading.split(headings[heading+1])[0]
                
            text_blocks[headings[heading]] = text_of_heading
        
    return text_blocks


# Clean the text blocks
def clean_text_blocks(text_blocks):

    # iterate over text blocks, removing '\u200b' and extra spaces
    for key in text_blocks:
        text_blocks[key] = re.sub('\u200b', '', text_blocks[key])
        text_blocks[key] = re.sub('\xa0', '', text_blocks[key])
        text_blocks[key] = re.sub(' +', ' ', text_blocks[key])

    return text_blocks