# core/select_beat.py
import traceback
import os
import json
import random

def select_beat(beats_dir="beats", used_beats_file="used_beats.json"):
    """
    Selects a new beat (if available), or reuses an old one.
    Returns (beat_file_name, full_path_to_beat).
    """
    # Load previously used beats
    if os.path.exists(used_beats_file):
        with open(used_beats_file, "r") as f:
            used_beats = json.load(f)
    else:
        used_beats = []

    # List all mp3 files in the beats directory
    all_beats = [f for f in os.listdir(beats_dir) if f.endswith(".mp3")]

    # Filter unused beats
    unused_beats = [b for b in all_beats if b not in used_beats]

    # Choose a beat
    if unused_beats:
        beat_file = random.choice(unused_beats)
        print(f"🎵 Using NEW beat: {beat_file}")
        used_beats.append(beat_file)
        with open(used_beats_file, "w") as f:
            json.dump(used_beats, f, indent=2)
    else:
        beat_file = random.choice(all_beats)
        print(f"🎵 All beats used — reusing OLD beat: {beat_file}")

    return beat_file, os.path.join(beats_dir, beat_file)

def title_extract(title,):
    try:
        
        
        title=os.path.basename(title)

        


        title = title.replace(".mp3", "")
        description_title=title

        if "(" in title and ")" in title:
            open_index = title.index("(")
            close_index = title.index(")")
            beat_number = title[open_index+1:close_index].strip()


        if "(" in title:
            title = title[:title.index("(")].strip()
   
        return description_editor(title, description_title,beat_number)
    except Exception as e:
        traceback.print_exc()
def description_editor(title,description_title,beat_number):  
    try:  
        print("DEscription")
        script_dir = os.path.dirname(__file__)  # path to the current file (select_beat.py)
        description_file = os.path.normpath(os.path.join(script_dir, '..', 'beats', 'description.txt'))

        with open(description_file, 'r', encoding='utf-8') as f:
            description = f.read()
            
            description=description_title+description
   
        return title,description,beat_number    
    except Exception as e:
        traceback.print_exc()