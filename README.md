# Briefing_Agent

A Streamlit-based AI assistant that helps users prepare for meetings by providing CRM insights, web search capabilities, and email drafting functionality.

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Git

### Installation

#### Option 1: Using Setup Scripts (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/shuminCA/Briefing_Agent.git
   cd Briefing_Agent
   ```

2. Run the appropriate setup script:
   ```bash
   ./setup.sh
   ```
   This will create a virtual environment (.venv) using Python 3.10 or higher, activate it, and install all required dependencies.
   This will create a virtual environment (.venv), activate it, and install all required dependencies.

#### Option 2: Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/shuminCA/Briefing_Agent.git
   cd Briefing_Agent
   ```

2. Create a virtual environment with Python 3.10 or higher:
   ```bash
   python3.10 -m venv .venv
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

The application uses an API endpoint and bearer token for authentication. These are configured using environment variables in a `.env` file for enhanced security:

1. Create a `.env` file based on the provided example:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and update the API credentials:
   ```
   # API endpoint for the Briefing Agent
   API_URL=your_api_url_here
   
   # Bearer token for authentication
   BEARER_TOKEN=your_bearer_token_here
   ```

This approach keeps sensitive credentials out of version control, as `.env` is included in `.gitignore`. The application uses python-dotenv to load these environment variables at runtime.

Note: If you use the setup scripts, they will automatically create the `.env` file from the template if it doesn't exist.

### Running the Application

1. Ensure your virtual environment is activated:
   ```bash
   source .venv/bin/activate
   ```

2. Run the Streamlit application:
   ```bash
   streamlit run Briefing_Agent.py
   ```
3. The application will open in your default web browser at `http://localhost:8501`

## Usage

Simply tell the agent who you're meeting with, their company name, and if you need to follow up with an email. For example:

> "I'm meeting with Sarah Johnson and Michael Lee from Acme Corporation tomorrow. After the meeting, send them a thank-you email."

The agent will compile a detailed briefing and draft a professional email for your approval.

## Project Structure

- `Briefing_Agent.py`: Main application file
- `APIHandler.py`: Handles API requests and responses
- `ResponseHandler.py`: Processes server responses
- `UIComponents.py`: UI components for the application
- `data/briefing_agent.md`: Welcome message content
- `.env.example`: Template for environment variables (safe to commit)
- `.env`: Actual environment variables with credentials (excluded from git)
- `requirements.txt`: List of Python dependencies
- `setup.sh`: Setup script for macOS/Linux
- `setup.bat`: Setup script for Windows
- `.gitignore`: Specifies files to exclude from version control (including .venv and .env)

## Troubleshooting

If you encounter any issues:

1. Ensure all dependencies are installed correctly:
   ```bash
   pip install -r requirements.txt
   ```
   
2. Check that the API endpoint is accessible

3. Verify that the bearer token is valid

4. If you're having issues with the setup scripts:
   - Make sure you have Python 3.10 or higher installed:
     ```bash
     python --version  # Should show 3.10.x or higher
     ```
   - On macOS/Linux, ensure the setup.sh script is executable:
     ```bash
     chmod +x setup.sh
     ```
   - If you're using a different Python version, you may need to update the version check in the setup scripts
