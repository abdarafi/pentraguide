import streamlit as st

st.title('PentraGuide - Penetration Testing Assistant')

# Text input from the user (penetration tester)
input_findings = st.text_area(
    'Enter your findings:', 
    height=300, 
    placeholder="Example: found SQL injection in the search product API.\n```\nGET /api/products?query=1%27%20OR%201%20=%201-- HTTP/1.1\nHost: example.com\n...\n\nHTTP/1.1 200 OK\nContent-Type: application/json\n...\n{\"message\":\"Successfully fetched products!\",\"data\":[...]}\n```"
)

def check_input_sufficiency(input_text):
    required_elements = ['description', 'request', 'response']
    if all(element in input_text.lower() for element in required_elements):
        return True
    return False

from langchain.prompts import PromptTemplate
# Setting up the prompt template for report generation
report_template = PromptTemplate(
    input_variables=['findings'],
    template='''Format the following penetration test findings into a Markdown formatted report:
    **Vulnerability Title:** Extracted or inferred from findings
    **Severity:** To be inferred from findings
    **Description:**
    Extracted from findings: {findings}
    **Proof of Concept:**
    - **Request:** [Extract from findings]
    - **Response:** [Extract from findings]
    **References:** [If applicable]
    **Remediation:**
    Suggest remediations based on common practices for the vulnerability type identified.
    '''
)

from langchain.memory import ConversationBufferMemory
# We use the ConversationBufferMemory to store a history of the conversation
memory = ConversationBufferMemory(input_key='findings', memory_key='chat_history')

from langchain_community.llms import Ollama
model = Ollama(model="lily")

from langchain.chains import LLMChain
# Create an LLMChain to generate Markdown formatted reports
report_chain = LLMChain(llm=model, prompt=report_template, verbose=True, output_key='markdown_report', memory=memory)

# Check input and display the formatted report if sufficient, otherwise notify the user
if input_findings:
    if check_input_sufficiency(input_findings):
        markdown_report = report_chain.run(findings=input_findings)
        st.markdown(markdown_report, unsafe_allow_html=True)
    else:
        st.error("Information is not sufficient. Please provide a complete finding including a short description, HTTP request, and HTTP response as follows:\n"
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
                 "{\"message\":\"Successfully fetched products!\",\"data\":[...]}\n"
                 "```")