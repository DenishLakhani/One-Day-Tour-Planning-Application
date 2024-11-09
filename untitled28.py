# -*- coding: utf-8 -*-
"""Untitled28.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1QdYLc5XPXYQdCXRm4dqE8PVzyI7NKPjq
"""

pip install streamlit fastapi neo4j transformers outlines

from fastapi import FastAPI, Request
from pydantic import BaseModel
import outlines
from neo4j import GraphDatabase

app = FastAPI()

# Connect to Neo4j database
neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

# Define a model for user input
class UserRequest(BaseModel):
    city: str
    start_time: str
    end_time: str
    budget: float
    interests: list
    starting_point: str = None

@app.post("/generate-itinerary")
async def generate_itinerary(request: UserRequest):
    # Process input using LLM and graph database
    itinerary = await generate_itinerary_plan(request)
    return {"itinerary": itinerary}

def store_user_preferences(user_id, preferences):
    with neo4j_driver.session() as session:
        query = """
        MERGE (user:User {id: $user_id})
        SET user.preferences = $preferences
        """
        session.run(query, user_id=user_id, preferences=preferences)

def get_user_preferences(user_id):
    with neo4j_driver.session() as session:
        query = "MATCH (user:User {id: $user_id}) RETURN user.preferences"
        result = session.run(query, user_id=user_id)
        return result.single()[0] if result.single() else None

import outlines

def generate_itinerary_plan(request):
    prompt = f"""
    Generate a one-day itinerary for exploring {request.city}.
    The user is interested in {request.interests} and has a budget of ${request.budget}.
    Start the trip at {request.start_time} from {request.starting_point} and end by {request.end_time}.
    """
    response = outlines.openai.Completion.create(prompt=prompt, max_tokens=200)
    return response['choices'][0]['text']

import streamlit as st
import requests

st.title("One-Day Tour Planner")

city = st.text_input("Enter the city:")
start_time = st.text_input("Start time (e.g., 9:00 AM):")
end_time = st.text_input("End time (e.g., 6:00 PM):")
budget = st.number_input("Enter your budget ($):", min_value=0)
interests = st.multiselect("Select your interests", ["Culture", "Adventure", "Food", "Shopping"])
starting_point = st.text_input("Enter your starting point (Optional):")

if st.button("Generate Itinerary"):
    payload = {
        "city": city,
        "start_time": start_time,
        "end_time": end_time,
        "budget": budget,
        "interests": interests,
        "starting_point": starting_point
    }
    response = requests.post("http://localhost:8000/generate-itinerary", json=payload)
    st.write(response.json()["itinerary"])