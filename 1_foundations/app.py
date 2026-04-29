from urllib import response

from dotenv import load_dotenv
from anthropic import Anthropic
import os
import json
import requests
from PyPDF2 import PdfReader
import gradio as gr
from yaml import reader


load_dotenv(override=True)

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )

def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_user_details(email, name="Name not provided", message="Message not provided"):
    push(f"Recording interest from:\nName: {name}\nEmail: {email}\nMessage: {message}")
    return{"recorded": "ok"}

def record_unknown_questions(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool when a user wants to get in touch with us",
    "input_schema": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The user's email address"
            },
            "name": {
                "type": "string",
                "description": "The user's name"
            },
            "message": {
                "type": "string",
                "description": "The user's message"
            }
        },
        "required": ["email"]
    }
}

record_unknown_questions_json = {
    "name": "record_unknown_questions",
    "description": "Use this tool to record any questions that I don't know how to answer",
    "input_schema": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that I don't know how to answer"
            }
        },
        "required": ["question"]
    }
}

tools = [record_user_details_json, record_unknown_questions_json]


class Me:
    def __init__(self):
        self.client = Anthropic()
        self.name = "Nicholas Smith"
        
        reader = PdfReader("me/linkedin.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        
        reader = PdfReader("me/Nicholas_Smith_Resume.pdf")
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text

        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()
        


    def handle_tool_call(self, response):
        tool_name = response.name
        tool_input = response.input
        results = []
        tool = globals().get(tool_name)
        result = tool(**tool_input) if tool else {}
        results.append(result)
        return results
        
    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history):
        messages = [{"role": "user", "content": self.system_prompt()}] 
    
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        response = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system="You are a helpful assistant",
            messages=messages,
            tools=tools,
        )

        reply = response.content[0].text

        if response.stop_reason == "tool_use":
            for block in response.content:
                if block.type == "tool_use":
                    self.handle_tool_call(block)

        return reply
    

if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(me.chat, type="messages").launch()