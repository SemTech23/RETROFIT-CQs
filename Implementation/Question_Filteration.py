!pip install python-Levenshtein
!pip install fuzzywuzzy

import pandas as pd
from fuzzywuzzy import fuzz

def remove_duplicates_fuzzy(input_file, output_file, column_name, threshold=80):
    # Read data from the Excel file into a DataFrame
    df = pd.read_excel(input_file)

    # Check if the column name exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in the DataFrame.")

    # Function to detect duplicate questions using fuzzy matching
    def is_duplicate(question, question_list):
        for existing_question in question_list:
            if fuzz.partial_ratio(question, existing_question) >= threshold:
                return True
        return False

    # Remove duplicate rows based on the column containing questions
    unique_questions = []
    for question in df[column_name]:
        if not is_duplicate(question, unique_questions):
            unique_questions.append(question)

    df_filtered = df[df[column_name].isin(unique_questions)]

    # Save the filtered data back to a new Excel file
    df_filtered.to_excel(output_file, index=False)

    print(f"Processed data has been saved to '{output_file}'.")

input_file = 'input_file'
output_file = 'output_file'
column_name = 'questions'
threshold =  -  # Adjust the threshold
remove_duplicates_fuzzy(input_file, output_file, column_name, threshold)