import streamlit as st

st.title("PentraGuide - Penetration Testing Assistant")

# Text input from the user (penetration tester)
input_findings = st.text_area(
    "Enter your findings:",
    height=300,
    placeholder='Example: found SQL injection in the search product API.\n```\nGET /api/products?query=1%27%20OR%201%20=%201-- HTTP/1.1\nHost: example.com\n...\n\nHTTP/1.1 200 OK\nContent-Type: application/json\n...\n{"message":"Successfully fetched products!","data":[...]}\n```',
)


def check_input_sufficiency(input_text):
    required_elements = ["description", "request", "response"]
    if all(element in input_text.lower() for element in required_elements):
        return True
    return False


from langchain.prompts import PromptTemplate

# Setting up the prompt template for report generation
report_template = PromptTemplate(
    input_variables=["findings"],
    template="""
### Instructions:
Please generate a Markdown formatted report based on the input findings provided below. Ensure the response is structured as illustrated in the example.

### Input Findings:
{findings}

### Expected Markdown Format:
**Vulnerability Title:** [Extract and infer from findings]
**Severity:** [Infer from findings]
**Description:** [Detailed description extracted from findings]
**CWE:** [Find the suitable CWE code for the findings]
**Remediation:** [Suggest possible remediations based on common practices]
**Proof of Concept:**
- **Request:** [Extract and display request from findings]
- **Response:** [Extract and display response from findings]

### Example Format:
**Vulnerability Title:**
SQL Injection Vulnerability in Product Search API
**Severity:**
High
**Description:**
A SQL injection vulnerability was identified in the search product API, allowing unauthorized database query manipulation through the API endpoint.

**Proof of Concept:**
- **Request:**
  ```
  GET /api/products?query=1%27%20OR%201%20=%201-- HTTP/1.1
  Host: example.com
  ```
- **Response:**
  ```
  HTTP/1.1 200 OK
  Content-Type: application/json
  {{"message":"Successfully fetched products!", "data":[...]}}
  ```

**CWE:**
CWE-89

**Remediation:**
Use parameterized queries or prepared statements to prevent SQL injection.

### Please format your response to match the example provided above.
""",
)

# from langchain.memory import ConversationBufferMemory

# memory = ConversationBufferMemory()
# memory.chat_memory.add_user_message(
#     """
#                                     Description: I found a SQL Injection Vulnerability on the search page.

#                                     Request:
#                                     GET /api/products?query=1%27%20OR%201%20=%201-- HTTP/1.1
#                                     Host: example.com

#                                     Response:
#                                     HTTP/1.1 200 OK
#                                     Content-Type: application/json
#                                     {"message":"Successfully fetched products!","data":[...]}
#                                     """
# )
# memory.chat_memory.add_ai_message(
#     """
# ### Vulnerability Title:
# SQL Injection Vulnerability in Product Search API

# ### Severity:
# High

# ### Description:
# A SQL injection vulnerability was identified in the search product API, allowing unauthorized database query manipulation through the API endpoint.

# ### Proof of Concept:
# - **Request:**
# ```
# GET /api/products?query=1%27%20OR%201%20=%201-- HTTP/1.1
# Host: example.com
# ```
# - **Response:**
# ```
# HTTP/1.1 200 OK
# Content-Type: application/json
# {"message":"Successfully fetched products!","data":[...]}
# ```

# ### CWE:
# CWE-89

# ### Remediation:
# Use parameterized queries or prepared statements to prevent SQL injection.
# """
# )

# from langchain_community.llms import Ollama
# model = Ollama(model="lily")

from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI

api_key = "sk-proj-asfd"
model = OpenAI(api_key=api_key)

from langchain.chains import LLMChain

# Create an LLMChain to generate Markdown formatted reports, retaining conversation context
report_chain = LLMChain(
    llm=model,
    prompt=report_template,
    verbose=True,
    output_key="markdown_report",
    # memory=memory,
)

if input_findings:
    if check_input_sufficiency(input_findings):
        markdown_report = report_chain.run(findings=input_findings)
        st.markdown(markdown_report, unsafe_allow_html=True)
    else:
        st.error(
            "Information is not sufficient. Please provide more information with this format: \n"
            "- Short description about the vulnerability,\n"
            "- HTTP request,\n"
            "- HTTP response.\n\n"
            "Example:\n"
            "```\n"
            "Found SQL injection in the search product API.\n"
            "GET /api/products?query=1%27%20OR%201%20=%201-- HTTP/1.1\n"
            "Host: example.com\n"
            "...\n\n"
            "HTTP/1.1 200 OK\n"
            "Content-Type: application/json\n"
            "...\n"
            '{"message":"Successfully fetched products!","data":[...]}\n'
            "```"
        )
