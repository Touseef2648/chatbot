import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
import time
import sqlite3
import pandas as pd

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("/home/hussey/pip-sql-1.3b")
model = AutoModelForCausalLM.from_pretrained("/home/hussey/pip-sql-1.3b")

# Connect to the SQLite database
conn = sqlite3.connect('e_dummy.db')

# Streamlit app
st.title("SQL Query Chatbot")

# User input for SQL generation
user_input = st.text_area("Enter your question:", height=100)

# Process the input and generate the SQL query
if st.button("Generate SQL Query"):
    if user_input.strip() == "":
        st.write("Please enter a question.")
    else:
        # Prepare input text for the model
        text = f'''<schema>
CREATE TABLE table_name (
  CDR_DT STRING -- Distinct values: ['2024-06-30', '2024-07-31', '2024-05-31'],
  PARTY_ID BIGINT,
  SEGMENT STRING -- Distinct values: [None, 'B', 'D', 'C', 'A'],
  INDUSTRY_VERTICAL STRING -- Distinct values: [None, 'HOTEL', 'IT', 'MEDICAL'],
  MODEL_CATEGORY STRING -- Distinct values: ['B2C Prepaid Existing Parties', 'B2C Postpaid Existing Parties', 'B2B Existing Parties'],
  SCORE BIGINT,
  BUCKET STRING -- Distinct values: ['High risk', 'Medium risk', 'Low risk'];</schema>
<question>{user_input}</question><sql>'''

        # Tokenize and generate output
        start_time = time.time()
        inputs = tokenizer(text, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=200)
        end_time = time.time()

        # Extract SQL query from model output
        sql_query = tokenizer.decode(outputs[0], skip_special_tokens=True).split('<sql>')[1].split('</sql>')[0]

        # Display SQL query
        st.write("Generated SQL Query:")
        st.code(sql_query, language='sql')

        # Execute the query and display results
        try:
            result = pd.read_sql_query(sql_query, conn)
            st.write("Query Results:")
            st.dataframe(result)
        except Exception as e:
            st.error(f"Error executing the query: {e}")

        # Display execution time
        execution_time = end_time - start_time
        st.write(f"Execution time: {execution_time:.2f} seconds")
