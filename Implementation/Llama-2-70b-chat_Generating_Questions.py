!pip install replicate

import os
import requests
import csv
import replicate
import pandas as pd
from openpyxl import load_workbook
from getpass import getpass

# get a token: https://replicate.com/account
REPLICATE_API_TOKEN = getpass()
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

from google.colab import drive
# Mounting Google Drive
try:
    drive.mount("/content/gdrive")
except Exception as e:
    print(f"Error mounting Google Drive: {e}")

class ReplicateError(Exception):
    pass

# Function to generate questions based on rows (statements) and a list of prompts
def generate_questions(rows):
    questions = []
    # List of prompts 
    prompts = [
        "Based on the statement, generate a list of relevant questions",
        "Based on the triple, generate a list of competency question.Definition of competency questions: the questions that outline the scope of ontology and provide an idea about the knowledge that needs to be entailed in the ontology.",
        "As an ontology engineer, generate a list of competency questions based on the triple. Definition of competency questions: the questions that outline the scope of ontology and provide an idea about the knowledge that needs to be entailed in the ontology."
    ]
    
    for row in rows:
        complete_prompt = f"Subject: {row[0]}, Predicate: {row[1]}, Object: {row[2]}"
        
        for prompt in prompts:
            try:
                # Create the full prompt by combining the prompt from the list and the complete prompt
                full_prompt = f"{prompt}\n\n{complete_prompt}"
                
                # Call llama visa Replicate API to generate questions
                response = replicate.run(
                    "replicate/llama-2-70b-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1",
                    input={"prompt": full_prompt}
                )
                output_list = list(response)
                output_str = "".join(map(str, output_list))
                questions.append(output_str)
            except replicate.ReplicateError:
                questions.append("Error generating question using Replicate")
            except requests.exceptions.RequestException:
                questions.append("Error with the request to the Replicate API")
            except Exception as e:
                questions.append(f"Unexpected error: {e}")
    
    return questions

# Function to read file, generate questions, and write to Excel
def generate_questions_from_csv(file_path, output_file):
    try:
        df = pd.read_csv(file_path, sep='\t')
        df_chunks = [df[i:i+10] for i in range(0, df.shape[0], 10)]  # Start from row 0

        for i, chunk in enumerate(df_chunks):
            rows = chunk.values.tolist()
            questions = generate_questions(rows)
            chunk['Question'] = questions

            book = load_workbook(output_file)
            writer = pd.ExcelWriter(output_file, engine='openpyxl')
            writer.book = book

            chunk.to_excel(writer, sheet_name=f'Sheet{i+1}', index=False)

            writer.save()
            writer.close()
    except Exception as e:
        print(f"Error processing CSV or writing to Excel: {e}")

# add your input file path and output file path
try:
    file_path = 'input_file'
    output_questionsFile = 'output_file'
    generate_questions_from_csv(file_path, output_questionsFile)
except Exception as e:
    print(f"Unexpected error: {e}")
