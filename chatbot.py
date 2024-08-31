from openai import OpenAI
from fastapi import FastAPI, Form, Request, WebSocket, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import os
from dotenv import load_dotenv
from typing import Dict, List
from datetime import datetime, timedelta
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

# Load environment variables from .env file
load_dotenv()

# Get API key and secret key from environment variables
API_SECRET_KEY = os.getenv('OPENAI_API_SECRET_KEY')

openai = OpenAI(
    api_key=API_SECRET_KEY
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Session management
SECRET_KEY = API_SECRET_KEY  # Use the API secret key for session management as well
SESSION_EXPIRATION_HOURS = 2  # Session expiration time in hours
serializer = URLSafeTimedSerializer(SECRET_KEY)
# Store chat history in memory (you can use a database or Redis for persistence)
user_sessions: Dict[str, Dict] = {}

# Middleware to add a session ID to each user
@app.middleware("http")
async def add_session_id(request: Request, call_next):
    session_id = request.cookies.get("session_id")
    session_valid = True

    if session_id:
        try:
            session_data = serializer.loads(session_id, max_age=SESSION_EXPIRATION_HOURS * 3600)
            request.state.session_id = session_data["id"]
        except (BadSignature, SignatureExpired):
            session_valid = False
    else:
        session_valid = False

    if not session_valid:
        new_session_id = os.urandom(16).hex()
        session_id = serializer.dumps({"id": new_session_id})
        request.state.session_id = new_session_id

    response = await call_next(request)
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response

# Helper function to get or create chat log for a session
def get_chat_log(session_id: str) -> List[Dict[str, str]]:
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            "chat_log": [{'role': 'system',
                          'content': 'You are an Energy Efficiency AI Assistant, completely dedicated to answering questions '
                                     'on how people can maximize their energy by asking them questions on their home energy consumption and '
                                     'carrying out energy audit calculations. Also, help give users trusted advice and recommendations on '
                                     'various practices that can help reduce their overall energy consumption.'}],
            "expires_at": datetime.utcnow() + timedelta(hours=SESSION_EXPIRATION_HOURS)
        }
    return user_sessions[session_id]["chat_log"]

# Function to clean up expired sessions
def cleanup_expired_sessions():
    now = datetime.utcnow()
    expired_sessions = [session_id for session_id, session_data in user_sessions.items()
                        if session_data["expires_at"] < now]
    for session_id in expired_sessions:
        del user_sessions[session_id]

@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    cleanup_expired_sessions()
    session_id = request.state.session_id
    chat_responses = get_chat_log(session_id)
    
    # Filter out 'system' messages before passing to the template
    filtered_chat_responses = [msg for msg in chat_responses if msg['role'] != 'system']
    
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": filtered_chat_responses})

@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    session_id = websocket.cookies.get("session_id")
    chat_log = get_chat_log(session_id)
    
    # Filter out 'system' messages before sending to the client
    filtered_chat_log = [msg for msg in chat_log if msg['role'] != 'system']
    
    while True:
        user_input = await websocket.receive_text()
        filtered_chat_log.append({'role': 'user', 'content': user_input})
        
        try:
            response = openai.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=filtered_chat_log,
                temperature=0.6,
                stream=True
            )
            ai_response = ''
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    ai_response += chunk.choices[0].delta.content
                    await websocket.send_text(chunk.choices[0].delta.content)
            filtered_chat_log.append({'role': 'assistant', 'content': ai_response})
        
        except Exception as e:
            await websocket.send_text(f'Error: {str(e)}')
            break

@app.post("/", response_class=HTMLResponse)
async def chat(request: Request, user_input: Annotated[str, Form()]):
    cleanup_expired_sessions()
    session_id = request.state.session_id
    chat_log = get_chat_log(session_id)
    
    chat_log.append({'role': 'user', 'content': user_input})
    
    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=chat_log,
        temperature=0.6
    )
    
    bot_response = response.choices[0].message.content
    chat_log.append({'role': 'assistant', 'content': bot_response})
    
    # Filter out 'system' messages before passing to the template
    filtered_chat_log = [msg for msg in chat_log if msg['role'] != 'system']
    
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": filtered_chat_log})

@app.get("/image", response_class=HTMLResponse)
async def image_page(request: Request):
    return templates.TemplateResponse("image.html", {"request": request})

@app.post("/image", response_class=HTMLResponse)
async def create_image(request: Request, user_input: Annotated[str, Form()]):
    response = openai.images.generate(
        prompt=user_input,
        n=1,
        size="256x256"
    )
    image_url = response.data[0].url
    return templates.TemplateResponse("image.html", {"request": request, "image_url": image_url})
