import os, sys, time, platform
import whisper, pyaudio, wave, tempfile, audioop  # for audio recordings
from pathlib import Path
from ctypes import *
from dotenv import load_dotenv
from openai import OpenAI
import pyautogui, keyboard


DEBUG = False
history = []
voice_input = False
voice_output = False
scope = "general" # setting default value before loading from file
response_mp3 = "last_response.mp3"
operating_system = platform.system()

load_dotenv()
client = OpenAI (api_key = os.getenv("OPENAI_API_KEY"))


## --------------------------------------------------------------------------
def main ():
    global scope

    scope = get_scope ()

    # Setting the context for the interaction
    with open(f"context_{scope}.txt", "r", encoding="utf-8") as file:
        context = file.read()
        file.close ()
    history.append (
        {
            "role": "system",
            "content": f"{context}"
        }
    )

    # Loading the welcome message
    with open(f"welcome_{scope}.txt", "r", encoding="utf-8") as file:
        welcome = file.read()
        file.close ()
    if (voice_output):
        speak (welcome)
    else:
        print (welcome)


    # Execute program in an endless loop
    while True:

        if (voice_input):
            question = get_input_voice ()
        else:
            question = get_input_keyboard ()
        
        if question == "":
            break 

        if (DEBUG):
            print (f"\n----------\nHistory: {history}\n----------")
            input ("press ENTER to continue")

        response = query_gpt (question)

        if (voice_output):
            speak (response)
        else:
            print (f"\n{response}\n")



## --------------------------------------------------------------------------
## Speaks text in a natural voice using OpenAI's text-to-speech API
## --------------------------------------------------------------------------
def speak (response):
    speech_file_path = response_mp3
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=response
    )
    response.stream_to_file(speech_file_path)
    os.system(f"ffplay -nodisp -hide_banner -autoexit {response_mp3}")
    return



## --------------------------------------------------------------------------
## Sends a new query to GPT, taking session history into consideration
## --------------------------------------------------------------------------
def query_gpt (question):
    history.append (
        {
            "role": "user",
            "content": question
        }
    )
    response = client.chat.completions.create (
        model="gpt-4",
        messages=history,
        presence_penalty=1,
        frequency_penalty=1,
        temperature=0.5,
        max_tokens=300,
    )
    history.append (
        {
            "role": "assistant",
            "content": response.choices[0].message.content
        }
    )
    return response.choices[0].message.content




## --------------------------------------------------------------------------
## Takes input from the keyboard, using the prompt predefined in "welcome-[context].txt"
## --------------------------------------------------------------------------
def get_input_keyboard ():
    global scope
    with open(f"prompt_{scope}.txt", "r", encoding="utf-8") as prompt_file:
        prompt = prompt_file.read()
    question = input (f"\n{prompt}")
    return question






## --------------------------------------------------------------------------
## Takes input from the microphone
## --------------------------------------------------------------------------
def get_input_voice ():

    # Create a temporary file to store the recorded audio (this will be deleted once we've finished transcription)
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav")

    sample_rate = 8192
    bits_per_sample = 16
    chunk_size = 1024
    audio_format = pyaudio.paInt16
    channels = 1
    threshold = 96

    '''
    def callback(in_data, frame_count, time_info, status):
        wav_file.writeframes(in_data)
        return None, pyaudio.paContinue
    '''

    started = False
    number_of_chunks_to_stop = 24
    current_blank_streak = 0

    # Open the wave file for writing
    wav_file = wave.open(temp_file.name, 'wb')
    wav_file.setnchannels(channels)
    wav_file.setsampwidth(bits_per_sample // 8)
    wav_file.setframerate(sample_rate)

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Start recording audio
    '''
    stream = audio.open(format=audio_format,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk_size,
                        stream_callback=callback)
    input (f"\nListening to you... Press [ENTER] when done.")
    '''
    stream = audio.open(format=audio_format,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk_size)


    print(f"\n\nListening to you....")
    while True:
        in_data = stream.read (chunk_size)
        rms_value = audioop.rms(in_data, bits_per_sample // 8)
        if (rms_value >= threshold) and not started:
            current_blank_streak = 0
            started = True
            print ("recording...")
        if started:
            wav_file.writeframes(in_data)
        if (rms_value < threshold) and started:
            current_blank_streak += 1
        if (current_blank_streak > number_of_chunks_to_stop):
            break
    
    # Stop and close the audio stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Close the wave file
    wav_file.close()

    # And transcribe the audio to text (suppressing warnings about running on a CPU)
    result = model.transcribe(temp_file.name, fp16=False)
    temp_file.close()

    print (f"\n\n")
    return result["text"].strip()


## --------------------------------------------------------------------------
## --------------------------------------------------------------------------
def get_scope ():
    global scope
    choice = 0
    while not choice:
        os.system ('clear')     # MacOS and Linux only
        print ("Welcome to the Generative AI Universal Assistant")
        print (f"-------------------------------------------------\n")
        print (f"Please choose an assistant scope in the following choices:\n")
        print ("     1. General: a generic assistant that will answer most of your question")
        print ("     2, Supermarket: the assistant for the Joyful Groceries supermarket which directs you to the products you are looking for")
        print ("     3. Karen: Karen works are your company and she is mad at the world.")
        print ("     4. Computer Assistant: This computer assistant gives you the step-by-step instructions to accomplish any task on your computer.")
        user_input = input (f"\nYour choice [1-4]: ")
        try:

            choice = int(user_input)
        except:
            choice = 0
            print (f"\nPlease limit your answer to the provided choices.")
            time.sleep (2)
    if (choice == 1):
        scope = "general"
    elif (choice == 2):
        scope = "supermarket"
    elif (choice == 3):
        scope = "karen"
    elif (choice == 4):
        scope = "computer"
    print ("")
    return scope



## --------------------------------------------------------------------------
## Calls GPT to translate a piece of text
## --------------------------------------------------------------------------
def translate (src_language, dest_language, text):
    if src_language == dest_language:
        return text
    request = [
        {
            "role": "user",
            "content": f"""Translate the following text from {src_language} to {dest_language}: \"{text}\""""
        }
    ]
    response = client.chat.completions.create (
        model="gpt-4",
        messages=request,
        presence_penalty=1,
        frequency_penalty=1,
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message.content





## --------------------------------------------------------------------------
if __name__ == "__main__":
    for arg in sys.argv:
        if arg == "-vo":
            voice_output = True
        if arg == "-vi":
            voice_input = True
    if (voice_input):
        model = whisper.load_model("base")
    main()
