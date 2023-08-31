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

# Function to generate questions based on rows (statements) and a list of prompts
def generate_questions(row, prompts):
    questions = []
    for prompt in prompts:
        # Create a complete prompt using the row data (statements)
         complete_prompt = f"{prompt} {', '.join(row)}?"
        
        try:
            # Call OpenAI API to generate questions
            response = openai.Completion.create(
                engine='text-davinci-003',
                prompt= complete_prompt,
                max_tokens=3000,  # max token for gpt3.5 turbo
                n=1,
                stop=None,
                temperature=0
            )
            # Extract and store question
            question = response['choices'][0]['text'].strip()
            questions.append(question)
        except Exception as e:
            print(f"Error generating question for row {row}: {e}")
            questions.append("Error generating question")
    
    return questions

# Function to read CSV, generate questions, and write to Excel
def generate_questions_from_csv(file_path, output_file):
    data = []
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter='\t')  
        for i, row in enumerate(reader):
            sub, pre, obj = row  # Extract subject, predicate, and object from the row

            # List of prompts 
            prompts = [
        "Based on the statement, generate a list of relevant questions",
        "Based on the triple, generate a list of competency question.Definition of competency questions: the questions that outline the scope of ontology and provide an idea about the knowledge that needs to be entailed in the ontology.",
        "As an ontology engineer, generate a list of competency questions based on the triple. Definition of competency questions: the questions that outline the scope of ontology and provide an idea about the knowledge that needs to be entailed in the ontology."
    ]
            
            questions = generate_questions(row, prompts)
            data.extend(questions)

    # questions to an Excel file
    df = pd.DataFrame(data, columns=['Question'])
    df.to_excel(output_file, index=False)

# replace these with your actual file paths
file_path = 'input_file'
output_file = 'output_file'

# Call generate questions and write to Excel
generate_questions_from_csv(file_path, output_file)
