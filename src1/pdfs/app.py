import os
import cv2
import base64
import numpy as np
from io import BytesIO

import matplotlib.pyplot as plt
from PIL import Image, ImageChops

import difflib
import pdfplumber
import pymupdf


class PDF():
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def read_and_extract_text(self, ):
        with pdfplumber.open(self.pdf_path) as pdf:
            total_text = ""
            for page in pdf.pages:
                text = page.extract_text_simple()
                
                # add new line character to last line in page
                text = text+"\n"
                
                total_text+=text
            pdf.close()
        return total_text

    def get_sentence_by_rows(text):
        return text.splitlines()
    

class Differences():
    def __init__(self, text, text1):
        self.differ = difflib.Differ()
        self.text = text
        self.text1 = text1
        self.text_differences = []


    def show_text_differences(self):
        # Compare using difflib
        diff = list(self.differ.compare(self.text, self.text1))

        # Store differences
        for line in diff:
            if line.startswith('- ') or line.startswith('+ ') or line.startswith('? '):
                self.text_differences.append(line)
        return None

    def show_text_differences_in_detail(self):
        removals, additions, changes = [],[],[]

        # Compare using difflib
        diff = list(self.differ.compare(self.text, self.text1))

        for line in diff:
            if line.startswith("- "):
                removals.append(line)
            elif line.startswith("+ "):
                additions.append(line)
            elif line.startswith("? "):
                changes.append(line)
        return removals, additions, changes
    
    def filter_out_removals(self,):
        exact_differences = []

        for i, line in enumerate(self.text_differences):
            # '?' line shows ^ to highlight differences
            if line.startswith('? '): 
                prev_line = self.text_differences[i - 1] if i > 0 else ""
                
                # removals can't be found once they are removed in pdf
                if prev_line.startswith('+ '):
                    # remove \n characted at end
                    prev_word = prev_line[2:][:-1]
                    # remove \n characted at end
                    markers = line[2:][:-1]
                    exact_differences.append({'text': prev_word, 'diff': markers})
        return exact_differences

    def get_new_additions(self):
        new_additions = []
        
        for i, line in enumerate(self.text_differences):
            if line.startswith("+ "):
                # its previous or next line should not have ?
                prev_line = self.text_differences[i - 1] if i > 0 else ""
                next_line = self.text_differences[i + 1] if i > 0 else ""

                if not prev_line.startswith("? ") and not next_line.startswith("? "):
                    print(prev_line, next_line)
                    word = line[2:][:-1]
                    markers = "+"*len(word)

                    new_additions.append({"text": word, "diff": markers})
        return new_additions
    
    
    

