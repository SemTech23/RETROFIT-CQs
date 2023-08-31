!pip install openai
!pip install --upgrade openai
!pip install pandas openpyxl
import csv
import pandas as pd
from openpyxl import load_workbook
import openai
from google.colab import drive

def mount_drive():
    try:
        drive.mount("/content/gdrive") # specify the path for input/output files
    except Exception as e:
        print(f"Error mounting Google Drive: {e}")
        return False
    return True

openai.api_key = 'add your api_key'

# Function to generate questions based on rows (statements) and a given prompt
def generate_questions(rows, prompt):
    questions = []  # List to store generated questions
    for row in rows:
        # Create a complete prompt using the row data (statements)
        complete_prompt = f"Subject: {row[0]}, Predicate: {row[1]}, Object: {row[2]}"
        
        try:
            # Call OpenAI API to generate questions
            response = openai.ChatCompletion.create(
                model='gpt-4',
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": complete_prompt}
                ],
                max_tokens=4166,
                n=1,
                stop=None,
                temperature=1
            )
            # Extract and store the generated question
            question = response['choices'][0]['message']['content'].strip()
            questions.append(question)
        except Exception as e:
            print(f"Error generating question for row {row}: {e}")
            questions.append("Error generating question")
    
    return questions

# Function to read CSV, generate questions, and write to Excel
def generate_questions_from_csv(file_path, output_file):
    # List of prompts to use for generating questions
    prompts = [
        "Based on the statement, generate a list of relevant questions",
        "Based on the triple, generate a list of competency question.Definition of competency questions: the questions that outline the scope of ontology and provide an idea about the knowledge that needs to be entailed in the ontology.",
        "As an ontology engineer, generate a list of competency questions based on the triple. Definition of competency questions: the questions that outline the scope of ontology and provide an idea about the knowledge that needs to be entailed in the ontology."
    ]

    try:
        df = pd.read_csv(file_path, sep='\t')
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Split the DataFrame into chunks of 10 rows each
    df_chunks = [df[i:i+10] for i in range(0, df.shape[0], 10)]

    # Loop through each chunk to generate questions
    for i, chunk in enumerate(df_chunks):
        rows = chunk.values.tolist()
        
        # Loop through each prompt to generate questions
        for prompt in prompts:
            questions = generate_questions(rows, prompt)
            # Add generated questions to a new column in the chunk
            chunk[f'Question_{prompt[:10]}'] = questions  # Truncate prompt for column name

        try:
           
            book = load_workbook(output_file)
            writer = pd.ExcelWriter(output_file, engine='openpyxl')
            writer.book = book

          
            chunk.to_excel(writer, sheet_name=f'Sheet{i+1}', index=False)

            writer.save()
            writer.close()
        except Exception as e:
            print(f"Error writing to Excel file: {e}")


if mount_drive():
    # Define file paths
    file_path = 'input_file'
    output_questionsFile = 'output_file'
    
    # Call the function to generate questions and write to Excel
    generate_questions_from_csv(file_path, output_questionsFile)
