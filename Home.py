import streamlit as st
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
import sqlite3
from weasyprint import HTML
from io import BytesIO
import config

# Initialize LLM and Langchain Prompt
LANGCHAIN_TRACING_V2=True
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=config.LANGCHAIN_API_KEY
LANGCHAIN_PROJECT=config.LANGCHAIN_PROJECT
os.environ['OPENAI_API_KEY'] = config.OPENAI_API_KEY

prompt = hub.pull("gregkamradt/test-question-making")
llm = ChatOpenAI(model_name="gpt-3.5-turbo")

# Initializes DB
def create_db():
    conn = sqlite3.connect("testStorage.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS testMetadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,              
        instructions TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        questionId INTEGER UNIQUE,
        correctAnswer TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        answer TEXT NOT NULL,
        questionId INTEGER NOT NULL,
        FOREIGN KEY (questionId) REFERENCES tests(questionId) ON DELETE CASCADE
    )
    """)
    conn.commit()
    conn.close()

# Connect to SQLite DB
def get_connection():
    conn = sqlite3.connect("testStorage.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Gets Question Id for next Inserted question
def get_questionId():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(questionId) from tests")
    rows = cursor.fetchone()
    conn.commit()
    conn.close()
    if rows[0] == None:
        return 1
    else:
        return rows[0] + 1

# Insert question into DB
def insert_into_tests(question, correctAnswer, questionId):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tests (question, questionId, correctAnswer) VALUES (?, ?, ?)",
                   (question, questionId, correctAnswer))
    cursor.execute("""
    SELECT * from tests
    """)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()

# Insert answers into DB
def insert_into_answers(answer, questionId):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO answers (answer, questionId) VALUES (?, ?)",
                   (answer, questionId))
    conn.commit()
    conn.close()

# Get all questions
def get_test():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.questionId, t.question, t.correctAnswer, a.answer 
    FROM tests t 
    LEFT JOIN answers a ON t.questionId = a.questionId
    ORDER BY t.questionId, a.id
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

# Clear tests and answers table
def delete_test_and_answers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM testMetadata;")
    cursor.execute("DELETE FROM tests;")
    cursor.execute("DELETE FROM answers;")
    conn.commit()
    conn.close()

# Deletes a question from tables
def delete_question(questionId):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tests WHERE questionId = ?", (questionId,))
    cursor.execute("DELETE FROM answers WHERE questionId = ?", (questionId,))
    conn.commit()
    conn.close()

# Get Test title and instructions metadata
def get_test_metadata():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM testMetadata WHERE id = (SELECT MAX(id) FROM testMetadata);")
    rows = cursor.fetchone()
    conn.close()
    if rows == None:
        update_test_metadata("Test Questions", "")
        return (1, "Test Questions", "")
    return rows

# Update Test title and instructions metadata
def update_test_metadata(title, instructions):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO testMetadata (title, instructions) VALUES (?, ?)",
        (title, instructions))
    conn.commit()
    conn.close()

# Generate pdf for test and answer key
def generate_test(data, title, instructions, includeAnswers = False):
    html = """
    <html>
    <head>
    <style>
        p.question {
        line-height: 1;
        }

        div.answers {
        line-height: 1.2;
        }
    </style>
    </head>
    
    <body>
    """
    if includeAnswers == False:
        html += f"<h1>{title}</h1>\n"
    else:
        html += f"<h1>{title}: Answer Key</h1>\n"
    
    if instructions != "":
        html += f"<h4>Instructions: {instructions}</h4>\n"
    curQuestion = ""
    questionNum = 1
    answerNum = 1
    for questionId, question, correctAnswer, answer in data:
        if curQuestion != "" and curQuestion != question:
            html += "<hr>\n"
            html += f"<p class='question'><b>Question {questionNum}:</b> {question}</p>\n"
            html += f"<div class='answers'>\n&emsp; {answer}<br>\n"
            curQuestion = question
            questionNum += 1
        elif curQuestion == "":
            html += f"<p><b>Question {questionNum}:</b> {question}</p>\n"
            html += f"<div class='answers'>\n&emsp; {answer}<br>\n"
            curQuestion = question
            questionNum += 1

        if answerNum == 4:
            html += f"&emsp; {answer}<br></div>\n"
            if includeAnswers == True:
                html += f"<p style='color:red;'>{correctAnswer}</p>\n"
            answerNum = 1
        elif answerNum == 2 or answerNum == 3:
            html += f"&emsp; {answer}<br>\n"
            answerNum += 1
        else:
            answerNum += 1
    html += "</body></html>\n"
    pdf_file = BytesIO()
    HTML(string=html).write_pdf(pdf_file)
    pdf_file.seek(0)
    return pdf_file

if "initalizeDB" not in st.session_state:
    create_db()
    st.session_state["initializeDB"] = True


st.markdown("# TestSmith: Multiple Choice Test Generator")
homePage, insertPage, viewPage, answerKeyPage, downloadPage = st.tabs(["📢 Introduction", "✍ Add Question to Test", "📝 View/Edit Test", "📚 View/Edit Answer Key", "📥 Download Files"])

with homePage:
    st.write("""
    ##### Welcome to TestSmith!

    TestSmith utilizes Generative AI to create multiple-choice tests and answer keys. You enter test questions and we will generate multiple choice answers!

    ###### How to Use:
    - 📢 Enter Test Title and Test Instructions below.
    - ✍ Enter question context and test question to generate multiple choice answers. Manually edit generated answers. Add question and multiple choice answers to test.
    - 📝 & 📚 View and delete questions from test and answer key.
    - 📥 Download test and answer key.
    """)

    st.write("###### Enter Test Metadata")
    id, title, instructions = get_test_metadata()
    TestTitle = st.text_input("Enter Test Title", value=title)
    TestInstructions = st.text_input("Enter Test Instructions", value=instructions)
    update_test_metadata(TestTitle, TestInstructions)

    st.write("###### Create Another Test")
    if st.button("Clear Current Data"):
        delete_test_and_answers()
        st.success("Data cleared!")
        st.rerun()
    
with insertPage:
    st.write("""
    Enter question context and test question below to generate multiple choice answers. Manually edit generated answers. Add question and multiple choice answers to test.
    """)
    context = st.text_input("Enter Test Question Context", value=st.session_state.get("context", ""))
    question = st.text_input("Enter Test Question", value=st.session_state.get("question", ""))

    if "answers" not in st.session_state:
        st.session_state["answers"] = []
    if "correctAnswer" not in st.session_state:
        st.session_state["correctAnswer"] = ""

    if st.button("Generate Multiple Choice Answers"):
        correctAnswer = None
        if context and question:
            st.session_state["context"] = context
            st.session_state["question"] = question

            chain = prompt | llm
            response = chain.invoke({"context": context, "question": question})

            answers = response.content.split("\n")
            rationale = answers[-1]

            for i in range(len(answers)):
                if "(correct)" in answers[i]:
                    answers[i] = answers[i].replace("(correct)", "").strip()
                if answers[i][:7] == "Correct":
                    correctAnswer = answers[i][:7] + " Answer" + answers[i][7:]
                    if "See Module " in correctAnswer: 
                        correctAnswer = correctAnswer.split("See Module ")[0]
            
            if answers and correctAnswer:
                st.session_state["answers"] = answers[:4]
                st.session_state["correctAnswer"] = correctAnswer
                
                st.write("### Generated Answer")
            else:
                st.warning("Please try again.")
        else:
            st.warning("Please enter both context and question.")

    if st.session_state["answers"] != [] and st.session_state["correctAnswer"] != "":
        questionText = st.text_input("Question: ", value=st.session_state.get("question", ""))
        Answer1Text = st.text_input("Answer A: ", value=st.session_state["answers"][0])
        Answer2Text = st.text_input("Answer B: ", value=st.session_state["answers"][1])
        Answer3Text = st.text_input("Answer C: ", value=st.session_state["answers"][2])
        Answer4Text = st.text_input("Answer D: ", value=st.session_state["answers"][3])
        CorrectAnswerText = st.text_input("Correct Answer: ", value=st.session_state["correctAnswer"])

        st.session_state["question"] = questionText
        st.session_state["answers"][0] = Answer1Text
        st.session_state["answers"][1] = Answer2Text
        st.session_state["answers"][2] = Answer3Text
        st.session_state["answers"][3] = Answer4Text
        st.session_state["correctAnswer"] = CorrectAnswerText

    is_disabled = not (context and question and st.session_state["answers"] and st.session_state["correctAnswer"])

    if st.button("Add Question and Answer to Test", disabled=is_disabled):
        questionId = get_questionId()
        insert_into_tests(st.session_state["question"], st.session_state["correctAnswer"], questionId)
        for answer in st.session_state["answers"]:
            insert_into_answers(answer, questionId)
        st.session_state["context"] = ""
        st.session_state["question"] = ""
        st.session_state["answers"] = []
        st.session_state["correctAnswer"] = ""
        st.success("Successfully Added!")
        st.rerun()

with viewPage:
    test_data = get_test()
    id, title, instructions = get_test_metadata()
    st.markdown(f"### {title}")
    if instructions != "":
        st.markdown(f"###### **Instructions:** {instructions}")
    test_data = get_test()


    if not test_data:
        st.write("No test data available.")
    else:
        current_question = None
        for i in range(len(test_data)):
            questionId, question, correctAnswer, answer = test_data[i]
            if question != current_question:
                st.write(f"##### Question {((i + 1) // 4) + 1}: {question}")
                st.write("**Answers**:")
                current_question = question
            st.write(f"{answer}")

            if (i + 1) % 4 == 0 and i != 0:
                if st.button(f"Delete Question {(i + 1) // 4}", key=f"delete_{(i + 1) // 4}"):
                    delete_question(questionId)
                    st.rerun() 
    if st.button("Delete All Test Questions"):
        delete_test_and_answers()
        st.success("Data cleared!")
        st.rerun()

with answerKeyPage:
    id, title, instructions = get_test_metadata()
    st.markdown(f"### {title}: Answer Key")
    if instructions != "":
        st.markdown(f"###### **Instructions:** {instructions}")
    test_data = get_test()

    if not test_data:
        st.write("No test data available.")
    else:
        current_question = None
        for i in range(len(test_data)):
            questionId, question, correctAnswer, answer = test_data[i]
            if question != current_question:
                st.write(f"##### Question: {question}")
                st.write("**Answers**:")
                current_question = question
            st.write(f"{answer}")

            if answer[0] == "D": 
                st.write(f":red[{correctAnswer}]")
            if (i + 1) % 4 == 0 and i != 0:
                if st.button(f"Delete Question {(i + 1) // 4}", key=f"delete_answer_{(i + 1) // 4}"):
                    delete_question(questionId)
                    st.rerun() 
    if st.button("Delete All Test Questions", key="Delete All Test Questions Answer Key"):
        delete_test_and_answers()
        st.success("Data cleared!")
        st.rerun()

with downloadPage:
    test_data = get_test()
    id, title, instructions = get_test_metadata()

    pdf_buffer = generate_test(test_data, title, instructions)
    st.download_button("Download Test PDF", data=pdf_buffer, file_name=f"{title}.pdf", mime="application/pdf")

    pdf_buffer = generate_test(test_data, title, instructions, includeAnswers = True)
    st.download_button("Download Answer Key PDF", data=pdf_buffer, file_name=f"{title}_answer_key.pdf", mime="application/pdf")