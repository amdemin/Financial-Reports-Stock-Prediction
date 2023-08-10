# import pdfplumber
import fitz
import os
import re
import sys
import traceback
import pickle
from tqdm import tqdm


# Define headings in the document using word size function
def word_ratio_func(word):
    try:
        # calculate word size parameters
        word_length = len(word[4])
        word_bottom = float(word[1])
        word_top = float(word[3])
        return abs(word_bottom - word_top), word_length, word[4]
        
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

# Transform pdf into the text
def process_pdf(pdf_paths):
    
    # store the pdf text and headings in dictionaries
    pdf_texts = {}
    pdf_headings = {}

    # iterate over the pdf files
    for file_path in tqdm(pdf_paths):

        try:
            
            # open the pdf file using pdfplumber library
            reader = fitz.open(file_path)

            # store the text and headings within one pdf file
            texts = {}
            headings = []
            headings_count = 0

            for page_number in range(len(reader)):

                # get the specific page from the pdf file
                page = reader.load_page(page_number)
                # get text from page
                text = page.get_text()
                # add text to dictionary
                texts[page_number] = text

                # get headings from page
                words = page.get_text("words")
                word_count = 0
                while word_count < len(words):
                    # find if the words are large enough to be headings
                    word_size, word_length, word_text = word_ratio_func(words[word_count])
                    heading = []

                    if word_size > 15 and word_length > 1:
                        while True:
                            heading.append(word_text)
                            word_count += 1
                            if word_count >= len(words):
                                break
                            word_size, word_length, word_text = word_ratio_func(words[word_count])
                            if not word_size > 15 and word_length > 1:
                                headings.append(" ".join(heading))
                                word_count += 10
                                break
                    headings_count += 1
                    word_count += 1
                
                # break if the page covers the reference section
                if "Reference" in heading:
                    break
            
            # preprocess the text
            text = preprocess_text(texts)
            final_text = " ".join(text).strip()

            # optionally, export the text to a txt file
            # with open("Txt/" + file_path.split("/")[-1].split(".")[0] + ".txt", "w", encoding='utf-8') as f:
            #     f.write(final_text)

            # add the text to the dictionary
            pdf_texts[file_path.split("/")[-1].split(".")[0]] = final_text
            # clean the headings
            headings = [x.replace("\u200b", "remove") for x in headings]
            headings = [x for x in headings if not re.search("remove", x)]    
            # add the headings to the dictionary
            pdf_headings[file_path.split("/")[-1].split(".")[0]] = headings

        except Exception as e:

            # in case of error, print the specifics of issue
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = traceback.extract_tb(exc_traceback)
            filename = traceback_details[-1][0]
            line_no = traceback_details[-1][1]
            func = traceback_details[-1][2]
            print(f"Exception occurred in file {filename} at line {line_no} in function {func}")
            print(f"Exception type: {exc_type.__name__}, Exception message: {str(e)}")

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
