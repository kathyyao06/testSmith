## TestSmith: Multiple Choice Test Generator

TestSmith utilizes Generative AI to create multiple-choice tests and answer keys. You enter test questions and we will generate multiple choice answers!

### How to Run
1. Install Requirements: pip3 install -r requirements.txt
2. Edit config.py file to add in your LANGCHAIN_API_KEY, LANGCHAIN_PROJECT, and OPENAI_API_KEY
2. Run streamlit application: streamlit run Home.py

### Application Overview
- 📢 **Introductions Page:** Website Overview, and Add Test Metadata (Title, Instructions)
- ✍ **Add Questions to Test:** Enter question context and test question to generate multiple choice answers. Manually edit generated answers. Add question and multiple choice answers to test.
- **📝 View/Edit Test & 📚 View/Edit Answer Key:** View and delete questions from test and answer key.
- **📥 Download Files:** Download test and answer key.
- **❗ Disclaimer:** Responsible Use and About the Source

#### Video Demo

https://github.com/user-attachments/assets/4bd6303c-3d06-4285-8f6c-bdd29a1ea404

#### 📢 Introductions Page
Users have instructions on how to use TestSmith. They can enter test metadata (Test Title and Instructions), as well as clear all current data to start a new test.

<p align="center">
  <img width="400" alt="image" src="https://github.com/user-attachments/assets/e58b53b6-4c78-406a-a389-bc38d9bdcd56">
</p>


#### ✍ Add Questions to Test
Users enter a question context and test question. This application uses the Langchain "gregkamradt/test-question-making" prompt and OpenAI GPT-3.5 to generate multiple-choice answers. Users can add the question to their test, as well as review and edit the question, generated answers, and correct answer. 

Examples:
<p align="center">
  <img width="449" alt="image" src="https://github.com/user-attachments/assets/37405e93-ff4c-4aa3-89ed-5977755cdebc">
  <img width="446" alt="image" src="https://github.com/user-attachments/assets/3fba792b-3860-46ae-b1f1-7e48d7187ce9">
</p>

#### 📝 View/Edit Test & 📚 View/Edit Answer Key
The user can view the test and answer key, where they can delete questions from the test.

Examples:
<p align="center">
  <img width="373" alt="image" src="https://github.com/user-attachments/assets/e2c6bb4e-a210-4aeb-b902-960431900d36">
  <img width="376" alt="image" src="https://github.com/user-attachments/assets/99adb852-9858-4c93-be50-7398b64ad513">
</p>

#### 📥 Download Files
User can download test and answer key as PDF. 

#### ❗ Disclaimer
<img width="601" alt="image" src="https://github.com/user-attachments/assets/b817f181-20b8-44be-bf77-a16c57600dfe">

Github Link: https://github.com/kathyyao06/testSmith
