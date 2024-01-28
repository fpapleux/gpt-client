import os, sys, time, platform
import whisper, pyaudio, wave, tempfile, audioop  # for audio recordings
from pathlib import Path
from ctypes import *
from dotenv import load_dotenv
from openai import OpenAI
from computer_functions import Program


DEBUG = False
history = []
voice_input = False
voice_output = False
local = False
scope = "computer"
operating_system = "MacOS" if (platform.system() == "Darwin") else platform.system()
print (f"Operating System: {operating_system}")


## --------------------------------------------------------------------------
def main ():
    global scope, prg

    # scope = get_scope ()

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

        response = query_gpt (question)
        prg.parse_instructions (response)
        print ()
        prg.execute ()



## --------------------------------------------------------------------------
## Speaks text in a natural voice using OpenAI's text-to-speech API
## --------------------------------------------------------------------------
def speak (response):
    speech_file_path = "last_response.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=response
    )
    response.stream_to_file(speech_file_path)
    os.system("ffplay -nodisp -hide_banner -autoexit last_response.mp3 > nil")
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
        frequency_penalty=0,
        temperature=0.7,
        max_tokens=5000,
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
    threshold = 64

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
        if arg == "-local":
            local = True
    if (voice_input):
        model = whisper.load_model("base")
    if local:
        client = OpenAI (base_url="http://localhost:9007/v1", api_key="not-needed")
    else:
        load_dotenv()
        client = OpenAI (api_key = os.getenv("OPENAI_API_KEY"))
    
    prg = Program (client)
    main()
