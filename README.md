

# BeauBot: WhatsApp Appointment Assistant

BeauBot is a sophisticated multi-agent system designed to facilitate appointment bookings via WhatsApp. Built with FastAPI and SQLite3, and leveraging Twilio's API for WhatsApp communication, this system utilizes advanced agents from Agno (PhiData) to process requests and manage bookings. BeauBot is an ideal solution for businesses looking to streamline their appointment scheduling processes through WhatsApp.

## Features
- **WhatsApp Communication**: Directly interact with clients via WhatsApp for all appointment needs.
- **Multi-Agent System**: Utilizes multiple specialized agents for tasks such as SQL querying, chat management, data retrieval, and user interaction.
- **Database Integration**: Manages user and appointment data securely with SQLite3.

## System Architecture
BeauBot integrates various components:
- **FastAPI**: Serves the backend application and handles incoming webhook requests.
- **SQLite3**: Manages a local database to store user data, appointment details, and chat logs.
- **Twilio API**: Handles incoming and outgoing WhatsApp messages.
- **Agno (PhiData) Agents**: Power the logic for generating SQL queries, managing chat sessions, and formatting data.

## Setup Guide

### Prerequisites
- Python 3.8 or higher
- pip for package installation
- ngrok account (for local testing)

### Cloning the Repository
Start by cloning the BeauBot repository to your local machine.

git clone https://github.com/ZainRaz03/BeauBot-Multi-Agent-Whatsapp_Appointment-Assistant.git


cd beaubot


### Environment Setup
Create a `.env` file in the root directory of your project and populate it with your Twilio and Google API credentials:

GOOGLE_API_KEY=your_google_api_key

TWILIO_ACCOUNT_SID=your_twilio_account_sid

TWILIO_AUTH_TOKEN=your_twilio_auth_token

WHATSAPP_NUMBER=your_whatsapp_number


### Installing Dependencies
Install all required Python libraries:

pip install fastapi uvicorn sqlite3 python-dotenv twilio agno


### Database Initialization
Run the `database.py` script to set up the initial database and populate it with sample data.

python database.py


### Running the Server
Start the FastAPI server using Uvicorn:

uvicorn app:app --host 0.0.0.0 --port 8000


### Setting Up ngrok
To make your local server accessible on the internet, use ngrok:

ngrok http 8000

Copy the HTTPS URL provided by ngrok.

### Configuring Twilio Webhook
Go to your Twilio dashboard, and set the messaging webhook for WhatsApp to the ngrok URL followed by `/webhook/whatsapp`.

## Agents Overview
### SQLAgent
Handles SQL query generation for checking user existence and managing chat sessions.

### ChatAgent
Manages chat states and interactions, ensuring smooth user communication and logging.

### DataAgent
Fetches necessary data regarding products, artists, and appointments for booking purposes.

### BookingAgent
Processes user messages to facilitate the booking of appointments and manage conversational logic.

### FormattingAgent
Formats raw data into user-friendly messages that enhance the chat experience.

## Using BeauBot
Send a WhatsApp message to the configured Twilio number to start interacting with BeauBot. Follow the prompts to book an appointment or inquire about services.
