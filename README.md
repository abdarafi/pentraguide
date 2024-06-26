# PentraGuide - Penetration Testing Assistant

PentraGuide is a web application designed to assist penetration testers in generating detailed reports of their findings. The application allows users to input findings, validate their sufficiency, and generate comprehensive Markdown reports.

## Features

- Input and validation of penetration testing findings.
- Generation of Markdown formatted reports.
- Customizable project details including project name, scope, testing dates, and client name.
- Easy download of generated reports.

## Requirements

- Python 3.7+
- Streamlit
- LangChain
- OpenAI or Ollama API keys

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/pentraguide.git
    cd pentraguide
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file based on the `.env.example` file and fill in your API keys:
    ```bash
    cp .env.example .env
    ```

## Usage

1. Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```

2. Open your web browser and navigate to `http://localhost:8501`.

3. Fill in the project details and submit your findings to generate the report.

## Configuration

The application can be configured using environment variables specified in the `.env` file.

### .env.example

```plaintext
USE_GPT=false
OPENAI_API_KEY=your_openai_api_key_here
