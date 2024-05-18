from dotenv import load_dotenv
import os
import re
import streamlit as st
from langchain_community.llms import Ollama

load_dotenv()
gpt = bool(os.getenv("USE_GPT", "false").lower() in ("true", "1", "t"))

if gpt:
    from langchain.llms import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    model = OpenAI(api_key=api_key)
else:
    model = Ollama(model="lily")


st.title("PentraGuide - Penetration Testing Assistant")

project_name = st.text_input("Project Name")
scope = st.text_area("Scope of Testing", height=100)
testing_dates = st.date_input("Testing Dates")
client_name = st.text_input("Client Name")

if 'findings' not in st.session_state:
    st.session_state['findings'] = []

if 'markdown_report' not in st.session_state:
    st.session_state['markdown_report'] = ""

if st.session_state['findings']:
    st.subheader("Submitted Findings")
    for idx, finding in enumerate(st.session_state['findings'], 1):
        st.markdown(f"**Finding {idx}:**")
        st.text(finding)

input_findings = st.text_area(
    "Enter your findings:",
    height=300,
    placeholder='Example: found SQL injection in the search product API.\n```\nGET /api/products?query=1%27%20OR%201%20=%201-- HTTP/1.1\nHost: example.com\n...\n\nHTTP/1.1 200 OK\nContent-Type: application/json\n...\n{"message":"Successfully fetched products!","data":[...]}\n```',
)

if st.button("Submit Finding"):
    from langchain.prompts import PromptTemplate

    validation_template = PromptTemplate(
        input_variables=["findings"],
        template="""
    ### Instruction:
    Act as a penetration testing report generator. Your job is to review the following penetration test findings and validate their sufficiency based on the input findings provided in the Input section below. The findings should include three main components: a short description, an HTTP request, and an HTTP response. 

    ### Input:
    {findings}

    ### Validation Criteria:
    1. **Description**: A brief overview of the vulnerability.
    2. **HTTP Request**: The exact HTTP request used to identify the vulnerability.
    3. **HTTP Response**: The HTTP response received that demonstrates the vulnerability.

    ### Validation Output:
    - **Status**: Sufficient or Insufficient
    - **Feedback**: If any component is missing, incomplete, or redundant, specify which parts are missing or provide clear feedback on what additional information is needed or which parts are redundant.

    ### Response Example:
    **Status**: Insufficient
    **Feedback**: The findings are missing the HTTP response. Please include the full HTTP response to demonstrate the vulnerability.

    **Status**: Insufficient
    **Feedback**: The findings are redundant. Multiple findings indicate the same issue without additional unique information. Consolidate into a single, detailed finding.

    **Status**: Sufficient
    **Feedback**: All required components are present. Proceed to the next step.
    """,
    )

    from langchain.chains import LLMChain

    validation_chain = LLMChain(
        llm=model,
        prompt=validation_template,
        verbose=True,
        output_key="validation_feedback",
    )

    if input_findings:
        validation_feedback = validation_chain.run(findings=input_findings)
        print("[debug]: model validator response:\n", validation_feedback)
        if "insufficient" in validation_feedback.lower():
            match = re.search(r'\*\*Feedback\*\*:\s*(.*)', validation_feedback)
            if match:
                validation_feedback = match.group(1)
            st.error(validation_feedback)
            st.error(
                "Please provide your input with this format: \n"
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
        else:
            report_template = PromptTemplate(
                input_variables=["findings"],
                template="""
            ### Instruction:
            I want you to act as a penetration testing report generator. Your job is to generate a Markdown formatted report based on the input findings provided in the Input section below. Ensure the response is structured as illustrated in the example.

            ### Input:
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

            ### Response Example:
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

            report_chain = LLMChain(
                llm=model,
                prompt=report_template,
                verbose=True,
                output_key="markdown_report",
            )

            markdown_report = report_chain.run(findings=input_findings)
            print("[debug]: model response:\n", markdown_report)
            print("length", len(markdown_report))
            st.markdown(markdown_report)
            st.session_state['findings'].append(input_findings)
            st.success("Finding added successfully!")

