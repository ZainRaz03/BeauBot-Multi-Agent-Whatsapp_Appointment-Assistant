from fastapi import FastAPI, Request, Response, Form
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from dotenv import load_dotenv
import os
import logging
from typing import Optional
import json
import requests
from Agents import sql_agent, chat_agent, data_agent, booking_agent, formatting_agent
from database import execute_query, init_db

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


load_dotenv()


app = FastAPI()


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"


twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
validator = RequestValidator(TWILIO_AUTH_TOKEN)


MOCK_MODE = False  


async def verify_twilio_request(request: Request) -> bool:
    try:
        url = str(request.url)
        form_data = await request.form()
        signature = request.headers.get("X-Twilio-Signature", "")
        
        logger.debug(f"Validating request - URL: {url}")
        logger.debug(f"Form data: {form_data}")
        logger.debug(f"Twilio signature: {signature}")
        
        is_valid = validator.validate(url, form_data, signature)
        logger.debug(f"Request validation result: {is_valid}")
        return is_valid
    except Exception as e:
        logger.error(f"Error validating request: {e}", exc_info=True)
        return False

@app.get("/")
async def root():
    logger.info("Root endpoint hit")
    return {"message": "Beauty Spa Booking System is running"}


init_db()

def query_database(query: str):
    """
    Execute query against the SQLite database
    """
    try:
        logger.debug(f"Executing query: {query}")
        
        
        clean_query = query.strip()
        if clean_query.startswith("```"):
          
            clean_query = clean_query.split("\n", 1)[-1]  
            if clean_query.endswith("```"):
                clean_query = clean_query.rsplit("\n", 1)[0] 
        
        clean_query = clean_query.replace("`", "").strip().rstrip(';')
        
        clean_query = clean_query.replace("NOW()", "CURRENT_TIMESTAMP")
        clean_query = clean_query.replace("CURDATE()", "DATE('now')")
        
        logger.debug(f"Cleaned query: {clean_query}")
        
        result = execute_query(clean_query)
        logger.debug(f"Query result: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return False

def send_whatsapp_message(body, to_number):
    """Send WhatsApp message with mock mode support"""
    try:
        if MOCK_MODE:
            logger.info(f"MOCK MODE: Would send message to {to_number}: {body}")
            return {"sid": "MOCK_SID_" + str(hash(body))[:8]}
        else:
            response = twilio_client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                body=body,
                to=to_number
            )
            return response
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return {"sid": "ERROR_SID", "error": str(e)}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Webhook endpoint for WhatsApp messages - Beauty Spa Booking System
    """
    print('Webhook hit')
    try:
        form_data = await request.form()
        form_dict = dict(form_data)
        logger.debug(f"Received WhatsApp webhook data: {form_dict}")

        from_number = form_dict.get("From", "")
        body = form_dict.get("Body", "")
        wa_id = form_dict.get("WaId", "")
        
        logger.info(f"WhatsApp message received - From: {from_number}, Body: {body}, WaId: {wa_id}")
        
        if wa_id:
            try:
                clean_number = from_number.replace("whatsapp:", "")
                
                sql_query = sql_agent.generate_query(clean_number)
                logger.info(f"Generated SQL query for user check: {sql_query}")
                
                user_result = query_database(sql_query)
                
                if not user_result or not user_result[0].get("is_member"):
                    response = twilio_client.messages.create(
                        from_=TWILIO_WHATSAPP_NUMBER,
                        body="You are not subscribed to our membership. Please contact zainxaidi2003@gmail.com for membership details.",
                        to=from_number
                    )
                    logger.info(f"Non-member message sent with SID: {response.sid}")
                    return Response(
                        content="<?xml version='1.0' encoding='UTF-8'?><Response></Response>",
                        media_type="application/xml"
                    )
                
                user_data = user_result[0]
                user_id = user_data["id"]
                
                active_chat_query = chat_agent.check_active_chat(user_id)
                logger.info(f"Generated SQL query for active chat: {active_chat_query}")
                
                active_chat_result = query_database(active_chat_query)
                
                chat_id = None
                chat_history = []
                
                if not active_chat_result:
                    
                    new_chat_query = chat_agent.create_new_chat(user_id)
                    logger.info(f"Generated SQL query for new chat: {new_chat_query}")
                    
                    new_chat_result = query_database(new_chat_query)
                    if new_chat_result and isinstance(new_chat_result, dict) and "id" in new_chat_result:
                        chat_id = new_chat_result["id"]
                        logger.info(f"Created new chat with ID: {chat_id}")
                    else:
    
                        logger.error(f"Failed to create new chat: {new_chat_result}")
                        response = twilio_client.messages.create(
                            from_=TWILIO_WHATSAPP_NUMBER,
                            body="Sorry, I encountered an error setting up your chat session. Please try again later.",
                            to=from_number
                        )
                        return Response(
                            content="<?xml version='1.0' encoding='UTF-8'?><Response></Response>",
                            media_type="application/xml"
                        )
                else:
                   
                    chat_id = active_chat_result[0]["id"]
                    
                   
                    chat_history_query = chat_agent.get_chat_messages(chat_id)
                    logger.info(f"Generated SQL query for chat history: {chat_history_query}")
                    
                    chat_history = query_database(chat_history_query)
                    
                    logger.info(f"Retrieved chat history with {len(chat_history)} messages")
                
            
                products_query = data_agent.get_all_products()
                artists_query = data_agent.get_all_artists()
                appointments_query = data_agent.get_all_appointments()
                
                products = query_database(products_query)
                artists = query_database(artists_query)
                appointments = query_database(appointments_query)
                

                formatted_products = formatting_agent.format_products(products)
                formatted_artists = formatting_agent.format_artists(artists)
                formatted_appointments = formatting_agent.format_appointments(appointments)
                
            
                agent_response = booking_agent.process_message(
                    body, 
                    user_data, 
                    chat_history, 
                    formatted_products,  
                    formatted_artists,   
                    formatted_appointments  
                )
                
                logger.info(f"Booking agent response: {agent_response}")
               
                try:
                    save_message_query = chat_agent.save_message(
                        chat_id, user_id, body, agent_response
                    )
                    logger.debug(f"Save message query: {save_message_query}")
                    save_result = query_database(save_message_query)
                    
                    if not save_result:
                      
                        logger.warning("Failed to save message with agent query, trying direct insert")
                        direct_save_query = f"""
                        INSERT INTO messages (chat_id, user_id, user_message, bot_reply, created_at) 
                        VALUES ({chat_id}, {user_id}, '{body.replace("'", "''")}', '{agent_response.replace("'", "''")}', CURRENT_TIMESTAMP)
                        """
                        logger.debug(f"Direct save message query: {direct_save_query}")
                        direct_save_result = query_database(direct_save_query)
                        logger.debug(f"Direct save result: {direct_save_result}")
                    else:
                        logger.info(f"Message saved successfully with ID: {save_result.get('id', 'unknown')}")
                except Exception as e:
                    logger.error(f"Error saving message: {e}", exc_info=True)
                
                    logger.warning("Continuing despite message save failure")
                
        
                if agent_response == "FALSE":
                   
                    end_chat_query = chat_agent.end_chat(chat_id)
                    query_database(end_chat_query)
                    
                    goodbye_message = "Thanks! Looking forward to meeting you again."
                    
                    response = twilio_client.messages.create(
                        from_=TWILIO_WHATSAPP_NUMBER,
                        body=goodbye_message,
                        to=from_number
                    )
                elif agent_response.startswith("TRUE"):
                   
                    parts = agent_response.split(",")
                    if len(parts) >= 6:
                        artist_id = parts[1]
                        product_id = parts[2]
                        booking_time = parts[3] 
                        artist_name = parts[4]
                        product_name = parts[5]
                    else:
                        artist_id = parts[1] if len(parts) > 1 else "1"
                        product_id = parts[2] if len(parts) > 2 else "1"
                        booking_time = "2025-03-23 16:00:00"
                        
                        artist_name = None
                        product_name = None
                        
                        for artist in artists:
                            if str(artist["id"]) == artist_id:
                                artist_name = artist["name"]
                                break
                        
                        for product in products:
                            if str(product["id"]) == product_id:
                                product_name = product["name"]
                                break
                    
                        if not artist_name:
                            artist_name = "your stylist"
                        if not product_name:
                            product_name = "your service"
                    
    
                    create_appointment_query = data_agent.create_appointment(
                        user_id, artist_id, product_id, booking_time
                    )
                    logger.debug(f"Create appointment query: {create_appointment_query}")
                    appointment_result = query_database(create_appointment_query)
                    logger.debug(f"Appointment creation result: {appointment_result}")
                    
                    if not appointment_result:
                        direct_query = f"""
                        INSERT INTO appointments (artist_id, user_id, booking_time, product_id, status)
                        VALUES ({artist_id}, {user_id}, '{booking_time}', {product_id}, 'booked')
                        """
                        logger.debug(f"Trying direct appointment query: {direct_query}")
                        direct_result = query_database(direct_query)
                        logger.debug(f"Direct appointment result: {direct_result}")
                    
                    end_chat_query = chat_agent.end_chat(chat_id)
                    query_database(end_chat_query)
                    
                    confirmation_message = (
                        f"BOOKING CONFIRMED!\n\n"
                        f"Service: {product_name}\n"
                        f"Stylist: {artist_name}\n"
                        f"Time: {booking_time}\n\n"
                        f"Please arrive 10 minutes before your appointment. We look forward to seeing you!"
                    )
                    
                    response = twilio_client.messages.create(
                        from_=TWILIO_WHATSAPP_NUMBER,
                        body=confirmation_message,
                        to=from_number
                    )
                else:
                    response = twilio_client.messages.create(
                        from_=TWILIO_WHATSAPP_NUMBER,
                        body=agent_response,
                        to=from_number
                    )
                
                logger.info(f"Response sent with SID: {response.sid}")
                
            except Exception as e:
                logger.error(f"Error in processing: {e}", exc_info=True)
                response = twilio_client.messages.create(
                    from_=TWILIO_WHATSAPP_NUMBER,
                    body="Sorry, I encountered an error processing your request. Please try again later.",
                    to=from_number
                )
        else:
            logger.warning("No WaId found in the request")
            response = twilio_client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                body="Sorry, I couldn't identify your phone number.",
                to=from_number
            )

        return Response(
            content="<?xml version='1.0' encoding='UTF-8'?><Response></Response>",
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Error in WhatsApp webhook: {e}", exc_info=True)
        return Response(
            content="<?xml version='1.0' encoding='UTF-8'?><Response></Response>",
            media_type="application/xml"
        )

if __name__ == "__main__":
    import uvicorn
    print("Starting Beauty Spa Booking System server...")
    logger.info("Starting server with WhatsApp number: %s", TWILIO_WHATSAPP_NUMBER)
    uvicorn.run(app, host="0.0.0.0", port=8001) 