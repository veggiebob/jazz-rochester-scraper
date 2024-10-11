from openai import OpenAI
import json

from jazz_calendar import JazzCalendar
from parser import serialize_event
from scraper import get_event_entries
from multiprocessing import Pool, Lock
import sys

openai_client: OpenAI = None
logfile_lock: Lock = Lock()
my_stdout = sys.stdout

def serialize_entry(e: str):
    try:
        result = serialize_event(openai_client, e)
    except Exception as err:
        print(f'Failed to serialize {e}', file=my_stdout)
        print(err, file=my_stdout)
        return None
    try:
        logfile_lock.acquire()
        print(f'Successfully serialized {e}', file=my_stdout)
        with open('log.txt', 'a') as f:
            f.writelines([e, '\n', json.dumps(result), '\n'])
    except Exception as err:
        print(f'Failed to log result for {e}: {err}')
    finally:
        logfile_lock.release()
        return e, result

def json_load(fp: str, *args, **kwargs):
    with open(fp, 'r') as f:
        return json.load(f, **args, **kwargs)

def json_dump(obj, fp: str, *args, **kwargs):
    with open(fp, 'w') as f:
        return json.dump(obj, f, *args, **kwargs)

def main(url):
    global openai_client

    cal = JazzCalendar()
    print(f'calendar_id={cal.jazz_calendar_id}')

    event_listings_path = 'event-listings.json'
    try:
        with open(event_listings_path, 'r') as f:
            entries = json.load(f)
    except Exception as e:
        # Get event entries
        raw_entries = get_event_entries(url)
        # Parse each entry
        openai_config = json_load('creds/openai/openai-key.json')
        openai_client = OpenAI(api_key=openai_config['key'].strip())
        with Pool() as p:
            entries = p.map(serialize_entry, raw_entries)
        json_dump(entries, event_listings_path)


    err_events = []

    # Add each entry to calendar
    for entry in entries:
        if entry is None:
            continue
        original, serialized = entry
        serialized: dict
        print(original)
        if True: # input('add to calendar? (y/n) ').strip() == 'y':
            e = serialized
            event = {
                'summary': e['title'],
                'location': e['location'],
                'description': original,
                'start': {
                    'dateTime': e['start'],  # Start date and time
                    'timeZone': 'America/New_York',  # Time zone
                },
                'end': {
                    'dateTime': e['end'],  # End date and time
                    'timeZone': 'America/New_York',
                },
                # 'attendees': [
                #     {'email': 'example@example.com'},
                # ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        # {'method': 'email', 'minutes': 24 * 60},  # Send email 24 hours before event
                        {'method': 'popup', 'minutes': 3 * 60},  # Popup reminder 10 minutes before event
                    ],
                },
            }
            try:
                cal.add_calendar_event(event)
            except Exception as e:
                serialized.update({ 'error': str(e) })
                err_events.append(serialized)

    with open('event-errors.json', 'w') as f:
        json.dump(err_events, f)



if __name__ == '__main__':
    main('https://www.jazzrochester.com/2024/10/rochester-jazz-listings-20241009.html')