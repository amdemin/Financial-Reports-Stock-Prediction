# Import libraries
from tqdm.notebook import tqdm
import pdfplumber
import fitz
import os
import re
import sys
import traceback
import pickle


# Define headings in the document using word size function (Fitz)
def word_ratio_func(word):
    try:
        # calculate word size parameters
        word_length = len(word["text"])
        word_bottom = float(word['bottom'])
        word_top = float(word['top'])
        return (word_bottom - word_top), word_length, word["text"]
        
    except:
        # in case of error, return zeros
        return 0, 0, 0

# Preprocess the text
def preprocess_text(texts):

    # join the text and perform cleansing operations
    text = "".join(texts.values()).strip("●").strip("*")
    text = text.split("\n")
    text = [x for x in text if x != '' and x.startswith("Source") == False]
    text = [x[0].replace("●", "") + x[1:] if x[0] == "●" else x for x in text]
    text = [x[0].replace("1", "") + x[1:] if x[1:3] in ["Q1", "Q2", "Q3", "Q4"] else x for x in text]
    text = text[2:]

    return text

# Define if table is correctly identified by calculating digit to character ratio
def digit_character_ratio(s):
    digit_count = 0
    char_count = 0

    for char in s:
        if char.isdigit():
            digit_count += 1
        if char.isalpha() or char.isdigit():
            char_count += 1

    # Avoid division by zero
    if char_count == 0:
        return 0

    return digit_count / char_count

# Transform pdf into the text
def process_pdf(pdf_paths):
    
    # store the pdf text and headings in dictionaries
    pdf_texts = {}
    pdf_headings = {}

    # iterate over the pdf files
    for file_path in tqdm(pdf_paths):

        try:

            # store the text and headings within one pdf file
            texts = {}
            headings = []
            headings_count = 0
            fitz_flag = False

            # open the pdf file using pdfplumber library
            plumber_reader = pdfplumber.open(file_path)

            # for page_number in range(len(fitz_reader)):
            # iterate over pages in the pdf document
            for page_number in range(0, len(plumber_reader.pages)):

                # get the specific page from the pdf plumber
                plumber_page = plumber_reader.pages[page_number]
                # get text from page using pdf plumber
                text = plumber_page.extract_text()

                # if text is not correctly extracted and spaced using pdf plumber
                if len(text.split(" ")) / len(text) < 0.15 or fitz_flag:
                    # set fitz library flag as true for further pages
                    fitz_flag = True
                    # open the pdf file using fitz library
                    fitz_reader = fitz.open(file_path)
                    # get the specific page from the fitz library
                    fitz_page = fitz_reader.load_page(page_number)
                    # get text from page using fitz library
                    text = fitz_page.get_text()

                ### Extract and Remove tables
                # find table from the page
                table = plumber_page.extract_tables()
                # if table exists on the page
                if len(table):
                    # define the beginning of table
                    start_table = table[0][0][0].split("\n")[0]
                    # define the end of table
                    end_table = table[-1][-1]
                    end_table = [x for x in end_table if x is not None][-1]
                    # if table has non-empty start and ending
                    if start_table != '' and end_table != '':
                        # flatten the table list of words and digits
                        table_list = [item for sublist in table for subsublist in sublist for item in subsublist]
                        # remove None values from the list
                        table_list = [x for x in table_list if x is not None]
                        # join the list as single string
                        table_list = " ".join(table_list)
                        # calculate the digit to character ratio
                        ratio = digit_character_ratio(table_list)
                        # remove table if digit to character ratio is over 0.2, meaning that table contains numeric data
                        if ratio > 0.2:
                            # update the page text by removing table
                            text = text.split(start_table)[0] + text.split(end_table)[-1]

                # add text to dictionary of texts
                texts[page_number] = text

                ### Get headings
                # extract words
                words = plumber_page.extract_words()
                word_count = 0
                # iterate over words
                while word_count < len(words):
                    # find if the words are large enough to be headings by calculating their size
                    word_size, word_length, word_text = word_ratio_func(words[word_count])
                    heading = []

                    # if word size is over 13.5, this means that the word is heading
                    if word_size > 13.5 and word_length > 1:
                        # append the following words if they satisfy this heading size condition
                        while True:
                            heading.append(word_text)
                            word_count += 1
                            if word_count >= len(words):
                                break
                            word_size, word_length, word_text = word_ratio_func(words[word_count])
                            # if word is small again, break the loop and finish the heading
                            if not word_size > 13.5 and word_length > 1:
                                headings.append(" ".join(heading))
                                # add the indent of 10 words to avoid issues 
                                word_count += 10
                                break
                    headings_count += 1
                    word_count += 1
        
                # break if the heading reaches "Reference" or page number is 10
                if "Reference" in heading or page_number == 10:
                    break
            
            # preprocess the text
            text = preprocess_text(texts)
            final_text = " ".join(text).strip()

            # optionally, export the text to a txt file
            with open("Txt/" + file_path.split("/")[-1].split(".")[0] + ".txt", "w", encoding='utf-8') as f:
                f.write(final_text)

            # add the text to the dictionary
            pdf_texts[file_path.split("/")[-1].split(".")[0]] = final_text
            # clean the headings
            headings = [x.replace("\u200b", "remove") for x in headings]
            headings = [x for x in headings if not re.search("remove", x)]    
            # add the headings to the dictionary
            pdf_headings[file_path.split("/")[-1].split(".")[0]] = headings

            # break

        except Exception as e:

            # in case of error, print the specifics of issue
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = traceback.extract_tb(exc_traceback)
            filename = traceback_details[-1][0]
            line_no = traceback_details[-1][1]
            func = traceback_details[-1][2]
            print(f"Exception occurred in file {filename} at line {line_no} in function {func}")
            print(f"Exception type: {exc_type.__name__}, Exception message: {str(e)}")

            # break

            continue
    
    return pdf_texts, pdf_headings


# Get file paths for the pdf files
folder_path = "ShareholderLetters/" # put '/' sign at the end of the folder
file_paths = []
for root, directories, files in os.walk(folder_path):
    for filename in files:
        filepath = os.path.join(root, filename)
        file_paths.append(filepath)


# Transform pdf files into texts and headings and store them as dictionaries
pdf_texts, pdf_headings = process_pdf(file_paths) # total run time: 2 min 20 s 20 files

# Save pdf texts and headings to pickle files
with open("pdf_texts.pkl", "wb") as f:
    pickle.dump(pdf_texts, f)
with open("pdf_headings.pkl", "wb") as f:
    pickle.dump(pdf_headings, f)
