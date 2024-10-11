import openai
import json
from datetime import datetime, timedelta

from openai import OpenAI

expected_fields = ['title', 'date', 'location']
PROMPT = """
Your task is to serialize a human-written sentence into a JSON object for an event.
Each event needs 3 fields:
 - `title`: A suitable title or very short summary for the event. Probably the band name.
 - `date`: The date of the event in the format "YYYY-MM-DD".
 - `start`: The start time of the event in the format "HH:MM" using 24 hour time.
 - `end` (optional): The end time of the event in the format "HH:MM" using 24 hour time. If no end time is provided, you can omit this field.
 - `location`: The location of the event.
 
 An example serialization for this sentence:
 'Looking for some live jazz in October?: 19th: Stephane Wrembel with Jean Michel-Pilc: Triptych – Phase III @ Lovin Cup Bistro & Brews, 8:00 pm (more info & tickets)'
 Would be:
    {
        "title": "Stephane Wrembel with Jean Michel-Pilc: Triptych – Phase III",
        "date": "2024-10-19",
        "start": "20:00",
        "location": "Lovin Cup Bistro & Brews"
    }

 In your response, do not include anything other than this JSON object. Do not include any other information or text.
 
 Please serialize the following human-written event:
 
"""

def ask_chatgpt(client: OpenAI, prompt: str):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content

def find_json_in_string(s: str) -> str:
    # find first {
    first_bracket = s.find('{')
    # find last }
    last_bracket = s.rfind('}')
    if first_bracket < 0 or last_bracket < 0:
        return s
    else:
        return s[first_bracket:last_bracket + 1]


def serialize_event(client: OpenAI, sentence: str) -> dict:
    prompt = PROMPT + sentence
    response = ask_chatgpt(client, prompt)
    data = json.loads(find_json_in_string(response))

    if 'start' not in data:
        data['start'] = '17:00'
        data['end'] = '22:00'

    if not all(k in data for k in expected_fields):
        raise Exception(f"Missing fields: {expected_fields - data.keys()} \n\nSource sentence: {sentence}")

    # modify 'start' to be a datetime object
    data['start'] = datetime.strptime(data['date'] + ';' + data['start'], '%Y-%m-%d;%H:%M')
    if 'end' not in data:
        # assume the event is 1.5 hours long
        # use datetime to calculate the new end time
        data['end'] = data['start'] + timedelta(hours=1, minutes=30)
    else:
        data['end'] = datetime.strptime(data['date'] + ';' + data['end'], '%Y-%m-%d;%H:%M')

    # convert start and end to iso format
    data['start'] = data['start'].isoformat()
    data['end'] = data['end'].isoformat()
    return data