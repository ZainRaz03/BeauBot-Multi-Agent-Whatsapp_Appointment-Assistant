from phi.agent import Agent
from phi.tools.sql import SQLTools
from phi.model.google import Gemini
from dotenv import load_dotenv
import os


load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

class SQLAgent:
    def __init__(self):
        """
        Initializes an SQLAgent to generate SQL queries to check if a user exists in the database.
        """
        self.agent = Agent(
            model=Gemini(model="gemini-1.5-flash"),
            description="This agent generates SQL queries to check if a user exists in the database.",
            instructions=[
                """
                Database Schema Details:
                -------------------------
                Table: 'users'
                Columns:
                - id (bigint unsigned, PRIMARY KEY)
                - name (varchar)
                - phone (varchar)
                - email (varchar)
                - is_member (tinyint(1), represents boolean)
                - is_deleted (tinyint(1), represents boolean)
                
                Your task:
                Generate an SQL query using the above schema. Ensure the query is syntactically correct and adheres to the schema constraints. 
                The query should retrieve user details based on the provided phone number, ensuring the account is not marked as deleted.
                """
            ]
        )
    
    def generate_query(self, phone_number: str) -> str:
        """
        Generates an SQL query to check if a user exists in the database.

        Parameters:
        phone_number (str): The phone number to check.

        Returns:
        str: SQL query to check if the user exists.
        """
        query_prompt = f"""
        Generate an SQL query to check if a user with phone number {phone_number} exists in the users table.
        The query should:
        1. Return the user's id, name, phone, and is_member status
        2. Filter where phone = '{phone_number}' and is_deleted = 0
        
        Return only the SQL query without any explanation or markdown formatting.
        """
        
        response = self.agent.run(query_prompt, markdown=True)
        return response.content

class ChatAgent:
    def __init__(self):
        """
        Initializes a ChatAgent to manage chat sessions and generate queries related to chat functionality.
        """
        self.agent = Agent(
            model=Gemini(model="gemini-1.5-flash"),
            description="This agent manages chat sessions and generates queries related to chat functionality.",
            instructions=[
                """
                Database Schema Details:
                -------------------------
                Table: 'chats'
                Columns:
                - id (bigint unsigned, PRIMARY KEY)
                - user_id (bigint unsigned, links to users.id)
                - status (varchar, can be 'active' or 'ended')
                - created_at (timestamp)
                - updated_at (timestamp)
                
                Table: 'messages'
                Columns:
                - id (bigint unsigned, PRIMARY KEY)
                - chat_id (bigint unsigned, links to chats.id)
                - user_id (bigint unsigned, links to users.id)
                - user_message (text)
                - bot_reply (text)
                - created_at (timestamp)
                
                Important: We are using SQLite database, so use CURRENT_TIMESTAMP instead of NOW() for datetime functions.
                
                Your task:
                Generate SQL queries to manage chat sessions and messages.
                """
            ]
        )
    
    def check_active_chat(self, user_id: str) -> str:
        """
        Generates an SQL query to check if a user has an active chat.

        Parameters:
        user_id (str): The user ID to check.

        Returns:
        str: SQL query to check for active chats.
        """
        query_prompt = f"""
        Generate an SQL query to check if user with ID {user_id} has an active chat.
        The query should:
        1. Return the chat id, user_id, and status
        2. Filter where user_id = {user_id} and status = 'active'
        3. Order by created_at DESC
        4. Limit to 1 result (most recent active chat)
        
        Return only the SQL query without any explanation or markdown formatting.
        """
        
        response = self.agent.run(query_prompt, markdown=True)
        return response.content
    
    def create_new_chat(self, user_id: str) -> str:
        """
        Generates an SQL query to create a new active chat for a user.

        Parameters:
        user_id (str): The user ID to create a chat for.

        Returns:
        str: SQL query to create a new chat.
        """
        query_prompt = f"""
        Generate an SQL query to create a new active chat for user with ID {user_id}.
        The query should:
        1. Insert into the chats table
        2. Set user_id = {user_id}, status = 'active', and appropriate timestamps
        
        Return only the SQL query without any explanation or markdown formatting.
        """
        
        response = self.agent.run(query_prompt, markdown=True)
        return response.content
    
    def get_chat_messages(self, chat_id: str) -> str:
        """
        Generates an SQL query to retrieve all messages for a specific chat.
        
        Parameters:
        chat_id (str): The chat ID to retrieve messages for.
        
        Returns:
        str: SQL query to retrieve chat messages.
        """
        query_prompt = f"""
        Generate an SQL query to retrieve all messages for chat with ID {chat_id}.
        The query should:
        1. Return the user_message and bot_reply
        2. Filter where chat_id = {chat_id}
        3. Order by created_at ASC (oldest to newest)
        
        Return only the SQL query without any explanation or markdown formatting.
        """
        
        response = self.agent.run(query_prompt, markdown=True)
        return response.content

    def save_message(self, chat_id: str, user_id: str, user_message: str, bot_reply: str) -> str:
        """
        Generates an SQL query to save a message exchange.
        
        Parameters:
        chat_id (str): The chat ID.
        user_id (str): The user ID.
        user_message (str): The user's message.
        bot_reply (str): The bot's reply.
        
        Returns:
        str: SQL query to save a message.
        """
        query_prompt = f"""
        Generate an SQL query to save a message exchange.
        The query should:
        1. Insert into the messages table
        2. Set chat_id = {chat_id}, user_id = {user_id}, user_message = '{user_message}', bot_reply = '{bot_reply}', and appropriate timestamp
        
        Return only the SQL query without any explanation or markdown formatting.
        """
        
        response = self.agent.run(query_prompt, markdown=True)
        return response.content

    def end_chat(self, chat_id: str) -> str:
        """
        Generates an SQL query to end a chat session.
        
        Parameters:
        chat_id (str): The chat ID to end.
        
        Returns:
        str: SQL query to end a chat.
        """
        query_prompt = f"""
        Generate an SQL query to end a chat session.
        The query should:
        1. Update the chats table
        2. Set status = 'ended' and update the updated_at timestamp
        3. Where id = {chat_id}
        
        Return only the SQL query without any explanation or markdown formatting.
        """
        
        response = self.agent.run(query_prompt, markdown=True)
        return response.content

class DataAgent:
    def __init__(self):
        """
        Initializes a DataAgent to generate queries for retrieving products, artists, and appointments.
        """
        self.agent = Agent(
            model=Gemini(model="gemini-1.5-flash"),
            description="This agent generates queries for retrieving products, artists, and appointments.",
            instructions=[
                """
                Database Schema Details:
                -------------------------
                Table: 'products'
                Columns:
                - id (bigint unsigned, PRIMARY KEY)
                - name (varchar)
                - price (decimal)
                - duration (int, in minutes)
                
                Table: 'artists'
                Columns:
                - id (bigint unsigned, PRIMARY KEY)
                - name (varchar)
                - experience (int, in years)
                - expertise (varchar)
                
                Table: 'appointments'
                Columns:
                - id (bigint unsigned, PRIMARY KEY)
                - artist_id (bigint unsigned, links to artists.id)
                - user_id (bigint unsigned, links to users.id)
                - booking_time (datetime)
                - product_id (bigint unsigned, links to products.id)
                - status (varchar, can be 'booked', 'completed', 'cancelled')
                
                Important: We are using SQLite database, so use DATE('now') instead of CURDATE() for today's date.
                
                Your task:
                Generate SQL queries to retrieve data from these tables.
                """
            ]
        )
    
    def get_all_products(self) -> str:
        """
        Generates an SQL query to retrieve all products.
        
        Returns:
        str: SQL query to retrieve all products.
        """
        query_prompt = """
        Generate an SQL query to retrieve all products.
        The query should:
        1. Return the id, name, price, and duration
        2. From the products table
        
        Return only the SQL query without any explanation or markdown formatting.
        """
        
        response = self.agent.run(query_prompt, markdown=True)
        return response.content
    
    def get_all_artists(self) -> str:
        """
        Generates an SQL query to retrieve all artists.
        
        Returns:
        str: SQL query to retrieve all artists.
        """
        query_prompt = """
        Generate an SQL query to retrieve all artists.
        The query should:
        1. Return the id, name, experience, and expertise
        2. From the artists table
        
        Return only the SQL query without any explanation or markdown formatting.
        """
        
        response = self.agent.run(query_prompt, markdown=True)
        return response.content
    
    def get_all_appointments(self) -> str:
        """
        Generates an SQL query to retrieve all appointments for today.
        
        Returns:
        str: SQL query to retrieve all appointments.
        """
        query_prompt = """
        Generate an SQL query to retrieve all appointments for today.
        The query should:
        1. Return the id, artist_id, user_id, booking_time, product_id, and status
        2. From the appointments table
        3. Where booking_time is for today
        4. Join with artists table to get artist name
        
        Return only the SQL query without any explanation or markdown formatting.
        """
        
        response = self.agent.run(query_prompt, markdown=True)
        return response.content
    
    def create_appointment(self, user_id: str, artist_id: str, product_id: str, booking_time: str) -> str:
        """
        Generates an SQL query to create a new appointment.
        
        Parameters:
        user_id (str): The user ID.
        artist_id (str): The artist ID.
        product_id (str): The product ID.
        booking_time (str): The booking time.
        
        Returns:
        str: SQL query to create a new appointment.
        """
        query_prompt = f"""
        Generate an SQL query to create a new appointment.
        The query should:
        1. Insert into the appointments table
        2. Set user_id = {user_id}, artist_id = {artist_id}, product_id = {product_id}, booking_time = '{booking_time}', status = 'booked'
        
        Return only the SQL query without any explanation or markdown formatting.
        """
        
        response = self.agent.run(query_prompt, markdown=True)
        return response.content

class BookingAgent:
    def __init__(self):
        """
        Initializes a BookingAgent to handle the conversation flow for booking appointments.
        """
        self.agent = Agent(
            model=Gemini(model="gemini-1.5-flash"),
            description="This agent handles the conversation flow for booking appointments at a beauty and wellness spa.",
            instructions=[
                """
                You are a helpful booking assistant for a beauty and wellness spa. Your name is BeautyBot.
                
                Your responsibilities:
                1. Help users book appointments with artists for various beauty and wellness services
                2. Provide information about available services (products), their prices, and duration
                3. Provide information about artists, their experience, and expertise
                4. Guide users through the booking process in a conversational manner
                
                Important instructions:
                - Always be polite, professional, and helpful
                - If a user types "EXIT", respond with FALSE to end the chat
                - If a user confirms a booking by typing "CONFIRM", respond with "TRUE,artist_id,product_id,booking_time,artist_name,product_name"
                  For example: "TRUE,1,3,2025-03-23 16:00:00,John,Haircut"
                - Keep track of the conversation context to provide relevant responses
                - If a user hasn't selected a service or artist yet, guide them to make these selections
                - Suggest available time slots based on the appointments data
                - Remind users they can type "EXIT" to end the chat at any time
                - Remind users they can type "CONFIRM" to confirm their booking once all details are selected
                
                Example conversation flow:
                1. Greet the user and ask what service they're interested in
                2. Present available services with prices and duration
                3. Once service is selected, present available artists with their expertise
                4. Once artist is selected, suggest available time slots
                5. Confirm all details and ask user to type "CONFIRM" to book
                """
            ]
        )
    
    def process_message(self, user_message: str, user_data: dict, chat_history: list, products: list, artists: list, appointments: list) -> str:
        """
        Process a user message and generate a response.
        
        Parameters:
        user_message (str): The user's message.
        user_data (dict): The user's data.
        chat_history (list): The chat history.
        products (list): The list of products.
        artists (list): The list of artists.
        appointments (list): The list of appointments.
        
        Returns:
        str: The agent's response.
        """
        prompt = f"""
        User: {user_message}
        
        User Data: {user_data}
        
        Chat History:
        {chat_history}
        
        Available Products:
        {products}
        
        Available Artists:
        {artists}
        
        Today's Appointments:
        {appointments}
        
        Please respond to the user's message in a helpful and conversational manner.Use different emojis to make the conversation more engaging.
        Remember:
        - If the user types "EXIT", respond with just "FALSE"
        - If the user types "CONFIRM" and has selected a service and artist, respond with "TRUE,artist_id,product_id,booking_time,artist_name,product_name"
          For example: "TRUE,1,3,2025-03-23 16:00:00,John,Haircut"
        - Otherwise, provide a helpful response to guide the booking process
        """
        
        response = self.agent.run(prompt, markdown=True)
        return response.content

class FormattingAgent:
    def __init__(self):
        """
        Initializes a FormattingAgent to format JSON data into a more concise, presentable form.
        """
        self.agent = Agent(
            model=Gemini(model="gemini-1.5-flash"),
            description="This agent formats JSON data into a more concise, presentable form.",
            instructions=[
                """
                Your task is to format JSON data into a more concise, presentable form.
                
                For products data:
                - Extract only the essential information (id, name, price, duration)
                - Format it as a numbered list with clear labels
                - Include only the first 5-7 items if the list is very long
                - If the list is empty, return "No products available."
                
                For artists data:
                - Extract only the essential information (id, name, experience, expertise)
                - Format it as a numbered list with clear labels
                - Include only the first 5-7 items if the list is very long
                - If the list is empty, return "No artists available."
                
                For appointments data:
                - Extract only the essential information (id, artist_id, user_id, booking_time, product_id, status)
                - Format it as a numbered list with clear labels
                - Include only the first 5-7 items if the list is very long
                - If the list is empty, return "No appointments scheduled for today."
                
                Return only the formatted text without any additional explanation.
                """
            ]
        )
    
    def format_products(self, products_data: list) -> str:
        """
        Format products data into a more concise, presentable form.
        
        Parameters:
        products_data (list): The products data to format.
        
        Returns:
        str: The formatted products data.
        """
        query_prompt = f"""
        Format the following products data into a concise, presentable form:
        {products_data}
        
        If the data is empty, return "No products available."
        Return only the formatted text.
        """
        
        response = self.agent.run(query_prompt, markdown=True)
        return response.content
    
    def format_artists(self, artists_data: list) -> str:
        """
        Format artists data into a more concise, presentable form.
        
        Parameters:
        artists_data (list): The artists data to format.
        
        Returns:
        str: The formatted artists data.
        """
        query_prompt = f"""
        Format the following artists data into a concise, presentable form:
        {artists_data}
        
        If the data is empty, return "No artists available."
        Return only the formatted text.
        """
        
        response = self.agent.run(query_prompt, markdown=True)
        return response.content
    
    def format_appointments(self, appointments_data: list) -> str:
        """
        Format appointments data into a more concise, presentable form.
        
        Parameters:
        appointments_data (list): The appointments data to format.
        
        Returns:
        str: The formatted appointments data.
        """
        query_prompt = f"""
        Format the following appointments data into a concise, presentable form:
        {appointments_data}
        
        If the data is empty, return "No appointments scheduled for today."
        Return only the formatted text.
        """
        
        response = self.agent.run(query_prompt, markdown=True)
        return response.content

sql_agent = SQLAgent()
chat_agent = ChatAgent()
data_agent = DataAgent()
booking_agent = BookingAgent()
formatting_agent = FormattingAgent()