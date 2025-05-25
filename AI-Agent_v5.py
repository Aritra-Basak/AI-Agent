#!/usr/bin/env python
# coding: utf-8

# In[1]:


# AI Agent with the capabilities of getting real time weather of a location, 
# Searching a file/folder in local system, 
# Writing an sending emails to people and Normal Query
import os
import json
import re
import requests
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from groq import Groq

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Groq API Key
client = Groq(
    api_key='---groq-api-key---'
)

# Email Configuration (Update these with your email settings)
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",  # Gmail SMTP server
    "smtp_port": 587,
    "sender_email": "xyz@gmail.com",  # Your email-Id
    "sender_password": "---App Password Generated from the Google Accounts ---"   # Your app password (not regular password)
}

# ========== TOOL FUNCTION 1: WEATHER ==========
def get_weather(latitude: float, longitude: float) -> Dict[str, Any]:
    try:
        response = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
            f"&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
        )
        response.raise_for_status()
        return response.json()["current"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"Weather API error: {str(e)}")


# ========== TOOL FUNCTION 2: FILE/FOLDER SEARCH ==========
def search_file_or_folder(name: str) -> Dict[str, Any]:
    def get_all_drives():
        return [f"{d}:/" for d in string.ascii_uppercase if os.path.exists(f"{d}:/")]

    def search_files(filename_with_ext, directory, visited_dirs=set(), exclude_dirs=set()):
        results = []
        for root, _, files in os.walk(directory, topdown=True, onerror=lambda e: None):
            if root in visited_dirs or root in exclude_dirs:
                continue
            visited_dirs.add(root)
            for file in files:
                if file.lower() == filename_with_ext.lower():
                    results.append(os.path.join(root, file))
        return results

    def search_folders(foldername, directory, visited_dirs=set(), exclude_dirs=set()):
        results = []
        for root, dirs, _ in os.walk(directory, topdown=True, onerror=lambda e: None):
            if root in visited_dirs or root in exclude_dirs:
                continue
            visited_dirs.add(root)
            for dir_name in dirs:
                if dir_name.lower() == foldername.lower():
                    results.append(os.path.join(root, dir_name))
        return results

    is_file = '.' in os.path.basename(name)
    exclude_subpath = os.path.join('Users', 'User', 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Recent')

    results = []
    for drive in get_all_drives():
        exclude_dirs = {os.path.join(drive, exclude_subpath)}
        if is_file:
            results.extend(search_files(name, drive, visited_dirs=set(), exclude_dirs=exclude_dirs))
        else:
            results.extend(search_folders(name, drive, visited_dirs=set(), exclude_dirs=exclude_dirs))

    return {"results": results if results else ["No matching files/folders found."]}


# ========== TOOL FUNCTION 3: EMAIL GENERATION ==========
def generate_email(topic: str, recipient_name: str = "", tone: str = "professional") -> Dict[str, Any]:
    """Generate an email using Groq LLM"""
    try:
        system_prompt = f"""You are an expert email writer. Generate a well-structured email based on the given topic.
        
        Guidelines:
        - Use a {tone} tone
        - Create a clear and concise subject line (don't include "Subject:" prefix)
        - Structure the email with proper greeting using recipient's name, body, and professional closing
        - The sender is Aritra Basak with mobile number (+91) 9836610724
        - Include proper email signature at the end
        - Make it concise but comprehensive
        - Return ONLY a JSON object with 'subject' and 'body' keys
        - Do not include any markdown formatting or extra text outside the JSON
        
        Email Structure:
        - Greeting: Dear {recipient_name if recipient_name else '[Recipient Name]'},
        - Body: Well-structured content about the topic
        - Closing: Best regards, / Sincerely,
        - Signature: Aritra Basak with contact information
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Write an email about: {topic}{f' to {recipient_name}' if recipient_name else ''}"}
        ]
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7
        )
        
        response_content = completion.choices[0].message.content.strip()
        
        # Clean up response - remove any markdown formatting
        if response_content.startswith('```json'):
            response_content = response_content.replace('```json', '').replace('```', '').strip()
        
        # Try to parse JSON response
        try:
            email_data = json.loads(response_content)
            
            # Ensure proper email signature is included
            body = email_data.get("body", "")
            if "Aritra Basak" not in body:
                body += f"\n\nBest regards,\nAritra Basak\nMobile: (+91) 9836610724"
            
            return {
                "subject": email_data.get("subject", "Email Subject"),
                "body": body,
                "success": True
            }
        except json.JSONDecodeError:
            # Fallback: extract subject and body manually
            lines = response_content.strip().split('\n')
            subject = "Generated Email"
            body = response_content
            
            # Try to find subject line
            for i, line in enumerate(lines):
                if line.lower().startswith('subject:'):
                    subject = line.split(':', 1)[1].strip()
                    # Remove subject line from body
                    body = '\n'.join(lines[:i] + lines[i+1:])
                    break
            
            # Ensure proper signature
            if "Aritra Basak" not in body:
                body += f"\n\nBest regards,\nAritra Basak\nMobile: (+91) 9836610724"
            
            return {
                "subject": subject,
                "body": body,
                "success": True
            }
            
    except Exception as e:
        return {
            "subject": "Error generating email",
            "body": f"Error occurred while generating email: {str(e)}",
            "success": False
        }


# ========== TOOL FUNCTION 4: EMAIL SENDING ==========
def send_email(subject: str, body: str, recipients: List[str]) -> Dict[str, Any]:
    """Send email to specified recipients"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"Aritra Basak <{EMAIL_CONFIG['sender_email']}>"
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()  # Enable security
        server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
        
        # Send email
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG["sender_email"], recipients, text)
        server.quit()
        
        return {
            "success": True,
            "message": f"Email sent successfully to {len(recipients)} recipient(s): {', '.join(recipients)}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}"
        }


# ========== TOOL DEFINITIONS ==========
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature for provided coordinates in celsius.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number", "description": "Latitude coordinate"},
                    "longitude": {"type": "number", "description": "Longitude coordinate"}
                },
                "required": ["latitude", "longitude"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_file_or_folder",
            "description": "Search for a file (with extension) or a folder across the entire system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the file (with extension) or folder"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_email",
            "description": "Generate an email about a specific topic with proper formatting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The main topic or purpose of the email"},
                    "recipient_name": {"type": "string", "description": "Name of the recipient to personalize the email"},
                    "tone": {"type": "string", "description": "Tone of the email: professional, casual, formal, friendly"}
                },
                "required": ["topic"]
            }
        }
    }
]


# ========== QUERY TYPE DETECTORS ==========
def is_weather_query(query: str) -> bool:
    weather_patterns = [
        r'weather.*in', r'temperature.*in', r'how.*hot.*in',
        r'how.*cold.*in', r'what.*weather.*like.*in',
        r'weather.*forecast.*in', r'weather.*of', r'temperature.*of',
        r'climate.*in'
    ]
    query = query.lower()
    return any(re.search(p, query) for p in weather_patterns)


def is_search_query(query: str) -> bool:
    patterns = [
        r"find.*file", r"locate.*file", r"search.*file", r"where.*file",
        r"find.*folder", r"locate.*folder", r"search.*folder", r"where.*folder",
        r"find.*\.([a-z0-9]+)", r"locate.*\.([a-z0-9]+)"
    ]
    query = query.lower()
    return any(re.search(p, query) for p in patterns)


def is_email_query(query: str) -> bool:
    email_patterns = [
        r'write.*email', r'compose.*email', r'draft.*email', r'create.*email',
        r'write.*mail', r'compose.*mail', r'draft.*mail', r'create.*mail',
        r'send.*email', r'send.*mail', r'email.*about', r'mail.*about',
        r'shoot.*email', r'shoot.*mail', r'shoot.*an.*email', r'shoot.*an.*mail',
        r'fire.*email', r'fire.*mail', r'prepare.*email', r'prepare.*mail',
        r'make.*email', r'make.*mail', r'generate.*email', r'generate.*mail'
    ]
    query = query.lower()
    return any(re.search(p, query) for p in email_patterns)


# ========== EMAIL WORKFLOW HANDLER ==========
def handle_email_workflow(query: str) -> str:
    """Handle the complete email generation and sending workflow"""
    try:
        # Get recipient name first
        while True:
            recipient_name = input(f"{BLUE}Enter the recipient's name: {RESET}").strip()
            if recipient_name:
                break
            else:
                print(f"{RED}Please enter a recipient name{RESET}")
        
        # Generate email using LLM
        print(f"{BLUE}🤖 Generating email for {recipient_name}...{RESET}")
        
        # Extract topic from query
        topic = query
        
        # Call the generate_email function with recipient name
        email_result = generate_email(topic, recipient_name)
        
        if not email_result["success"]:
            return f"{RED}Failed to generate email: {email_result['body']}{RESET}"
        
        subject = email_result["subject"]
        body = email_result["body"]
        
        # Display generated email
        print(f"\n{GREEN}📧 Generated Email:{RESET}")
        print(f"{YELLOW}To: {recipient_name}{RESET}")
        print(f"{YELLOW}Subject: {subject}{RESET}")
        print(f"{YELLOW}Body:{RESET}")
        print(f"{'='*60}")
        print(f"{body}")
        print(f"{'='*60}")
        
        # Ask user if they want to send the email
        while True:
            send_choice = input(f"\n{BLUE}Would you like to send this email? (yes/no): {RESET}").strip().lower()
            
            if send_choice in ['no', 'n']:
                return f"{GREEN}Email draft saved. Not sent.{RESET}"
            elif send_choice in ['yes', 'y']:
                break
            else:
                print(f"{RED}Please answer 'yes' or 'no'{RESET}")
        
        # Get recipient email addresses
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        while True:
            recipients_input = input(f"{BLUE}Enter {recipient_name}'s email address(es) (separate multiple emails with commas): {RESET}").strip()
            
            if not recipients_input:
                print(f"{RED}Please enter at least one email address{RESET}")
                continue
            
            # Parse and validate email addresses
            recipients = [email.strip() for email in recipients_input.split(',')]
            valid_recipients = []
            
            for recipient in recipients:
                if re.match(email_pattern, recipient):
                    valid_recipients.append(recipient)
                else:
                    print(f"{RED}Invalid email format: {recipient}{RESET}")
            
            if valid_recipients:
                recipients = valid_recipients
                break
            else:
                print(f"{RED}No valid email addresses provided. Please try again.{RESET}")
        
        # Send the email
        print(f"{BLUE}📤 Sending email to {recipient_name}...{RESET}")
        send_result = send_email(subject, body, recipients)
        
        if send_result["success"]:
            return f"{GREEN}✅ {send_result['message']}{RESET}"
        else:
            return f"{RED}❌ {send_result['message']}{RESET}"
            
    except Exception as e:
        return f"{RED}Error in email workflow: {str(e)}{RESET}"


# ========== FUNCTION CALL EXECUTOR ==========
def call_function(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "get_weather":
        return get_weather(**args)
    elif name == "search_file_or_folder":
        return search_file_or_folder(**args)
    elif name == "generate_email":
        return generate_email(**args)
    raise ValueError(f"Unknown function: {name}")


# ========== Main AI workflow (LLM + tools) ==========
def get_assistant_response(query: str) -> str:
    try:
        # Check if it's an email query first and handle the full workflow
        if is_email_query(query):
            return handle_email_workflow(query)
        
        # Tool routing for other queries
        if is_weather_query(query):
            tool_name = "get_weather"
            system_message = "You are a helpful weather assistant. Use the get_weather function."
        elif is_search_query(query):
            tool_name = "search_file_or_folder"
            system_message = "You are a helpful assistant for locating files and folders."
        else:
            tool_name = None

        # Tool-assisted response
        if tool_name:
            # Build Message History for LLM
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": query}
            ]
            # First LLM Call: Tool Selection
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            tool_calls = completion.choices[0].message.tool_calls
            # If Groq chooses to call a tool
            if tool_calls:
                messages.append(completion.choices[0].message)
                
                for tool_call in tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    result = call_function(name, args)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                # Send Tool Result Back to LLM
                final_completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages
                )
                return final_completion.choices[0].message.content

            return completion.choices[0].message.content

        # Fallback generic response
        else:
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": query}
            ]
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages
            )
            return completion.choices[0].message.content

    except Exception as e:
        return f"{RED}Error getting response: {str(e)}{RESET}"


# ========== MAIN LOOP ==========
def main():
    print(f"{GREEN}🤖 AI Assistant with Email Functionality{RESET}")
    print(f"{BLUE}Available commands:{RESET}")
    print(f"  • Weather queries (e.g., 'weather in New York')")
    print(f"  • File/folder search (e.g., 'find file example.txt')")
    print(f"  • Email generation (e.g., 'write email about project update')")
    print(f"  • General questions")
    print(f"{YELLOW}Note: Configure EMAIL_CONFIG in the code before using email features{RESET}\n")
    
    try:
        while True:
            query = input("🧑🏽‍💻 Enter your question (or 'quit' to exit): ")
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            result = get_assistant_response(query)
            print(f"\n{GREEN}🤖 Assistant: {result}{RESET}\n")

    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"{RED}Error: {str(e)}{RESET}")


if __name__ == "__main__":
    main()


# In[ ]:




