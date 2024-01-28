# This file contains the computer automated functions
import json, platform, pyautogui, time, keyboard, base64
from PIL import Image
from io import BytesIO, StringIO
from openai import OpenAI
from screeninfo import get_monitors

class Program:
    program = []
    object_locations = []
    #client

    def __init__ (self, openAI_client):
        self.program = []
        self.client = openAI_client
        return

    def __str__ (self):
        output = ""
        for instruction in self.program:
            output += f"{instruction}\n"
        return output
        
    def parse_instructions (self, instructions):
        temp = instructions.strip().split ("\n")
        for instruction in temp:
            if instruction != "":
                self.program.append(json.loads (instruction))
        return

    # -----------------------------------------------------------------------------------------
    # Reads through and executes the program
    # -----------------------------------------------------------------------------------------
    def execute (self):
        for instruction in self.program:
            if instruction ['command'] == "LOCATE":
                print (instruction ['parameters']['description'])
                #self.locate (instruction)
            elif instruction ['command'] == "CLICK":
                print (instruction ['parameters']['description'])
                self.click_object (instruction)
            elif instruction ['command'] == "DBLCLICK":
                print (instruction ['parameters']['description'])
            elif instruction ['command'] == "SEARCH":
                print (instruction ['parameters']['description'])
                self.search (instruction)
            elif instruction ['command'] == "PRESS":
                print (instruction ['parameters']['description'])
                self.press (instruction)
            elif instruction ['command'] == "TYPE":
                print (instruction ['parameters']['description'])
                self.type (instruction)
            elif instruction ['command'] == "DONE":
                print (instruction ['parameters']['description'])
                self.program = []
                break
        return
    
    # -----------------------------------------------------------------------------------------
    # Executes a search for an application on the computer
    # -----------------------------------------------------------------------------------------
    def search (self, instruction):
        if platform.system() == "Windows":
            pyautogui.press("win")
        elif platform.system() == "Linux":
            pyautogui.press("win")
        else: # MacOS
            pyautogui.keyDown("command")
            pyautogui.press("space")
            pyautogui.keyUp("command")
        time.sleep(1)
        keyboard.write(instruction ['parameters']['text'])
        return

    # -----------------------------------------------------------------------------------------
    # Presses a key on the keyboard or a key combination
    # -----------------------------------------------------------------------------------------
    def press (self, instruction):
        key = instruction ['parameters']['key']
        if key.find ("+") == -1: # Currently only works with one single key pressed while typing another. Need to upgrade to multi-keys
            pyautogui.press (key)
        else:
            keys = key.split("+")
            pyautogui.keyDown(keys[0])
            pyautogui.press(keys[1])
            pyautogui.keyUp(keys[0])
        time.sleep(0.5)
        return

    # -----------------------------------------------------------------------------------------
    # Write a line of text from the keyboard
    # -----------------------------------------------------------------------------------------
    def type (self, instruction):
        for car in instruction ['parameters']['text']:
            keyboard.write (car)
            time.sleep(0.1)
        return

    # -----------------------------------------------------------------------------------------
    # Locate an object on the screen
    # -----------------------------------------------------------------------------------------
    def locate (self, instruction):
        request = []
        object_name = instruction ['parameters']['object']
        screen_height = 0
        screen_width = 0
        screenshot_height = 0
        screenshot_width = 0
        print (f"instruction is: {instruction}")
        input ("press ENTER")

        # establish current monitor dimensions
        for m in get_monitors():
            if m.is_primary:
                screen_height = m.height
                screen_width = m.width

        # Grab screenshot
        if instruction ['parameters']['object'].find('menu') != -1:
            print ("Grabbing screenshot of the menu bar")
            im = pyautogui.screenshot(region=(0, 0, screen_width, 35))
        else:
            print ("Grabbing screenshot of the whole screen")
            im = pyautogui.screenshot(region=(0, 0, screen_width, screen_height))
        im.show()
        #im = im.resize((int(screen_width/3), int(screen_height/3)))
        print (f"screenshot size --> width = {im.width}, height = {im.height}")

        #im.show()
        #screenshot_height = im.height
        #screenshot_width = im.width
        buff = BytesIO()
        im.save(buff, format="PNG")
        encoded_image = base64.b64encode(buff.getvalue()).decode()
        #im.save(encoded_image, "PNG")
        
        #print(len(encoded_image))

        #print(encoded_image)

        # Send a separate request to locate the object on the screen
        with open(f"context_computer_locate.txt", "r", encoding="utf-8") as file:
            context = file.read()
            file.close ()
        
        request.append (
            {
                "role": "system",
                "content": f"{context}"
            }
        )
        request.append (
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": f"Locate the object '{object_name}' in this screenshot, from instruction: {instruction ['parameters']['description']}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
                    }
                ]
            }
        )
        response = self.client.chat.completions.create (
            model="gpt-4-vision-preview",
            messages=request,
            presence_penalty=1,
            frequency_penalty=0,
            temperature=0.7,
            max_tokens=4096,
        )
        #print (response)
        #input ("press ENTER to continue")

        # To test the solution, grab the screen at the indicated location and show the image:
        request = []
        result = json.loads (response.choices[0].message.content)

        if (result['result'] == "FOUND"):
            x = int(result['parameters']['x'])
            y = int(result['parameters']['y'])
            width = int(result['parameters']['width'])
            height = int(result['parameters']['height'])
            print (f"Image dimensions from GPT: width = {result['image']['width']}, height = {result['image']['height']}")
            print (f"Object found at ({x}, {y}) with width {width} and height {height}")
            im2 = im.crop((x, y, x + width, y + height))
            #im2 = pyautogui.screenshot(region=(x, y, width, height))
            im2.show()
        else:
            print ("the location of the object was not found")

        # If found, store the object name and location in the object_location array

        time.sleep(0.5)
        return

    # -----------------------------------------------------------------------------------------
    # Locate an object on the screen
    # -----------------------------------------------------------------------------------------
    def click_object (self, instruction):
        print (f"Clicking on object {instruction ['parameters']['object']}")
        return

    # -----------------------------------------------------------------------------------------
    # Locate an object on the screen
    # -----------------------------------------------------------------------------------------
    def click_location (self, instruction):
        print (f"Clicking at location {instruction ['parameters']['x']}, {instruction ['parameters']['y']}")
        pyautogui.moveTo(int(instruction ['parameters']['x']), int(instruction ['parameters']['y']), duration=0.4)
        pyautogui.click()
        return
