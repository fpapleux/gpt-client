<h1 align="center">Multi-Use GPT Client</h1>

<p align="center">
  <strong>A framework to quickly develop GPT clients</strong>
</p>
<p align="center">
    Using this code you can very quickly develop new GPT clients that do all sorts of things. Your imagination is the limit.
</p>

## Installation

### General installation instructions

To install this system, follow these instructions:

**Base Requirements:**

- Python 3.9 or later.
- A developer account on OpenAI with access to OpenAI's API. The system uses GPT-4, so you will need a paid OpenAI account.
- A valid ChatGPT API Key


**Installation of generic use packages:**

The following are required for the program to run with minimal functionality:
- **OpenAI** is used to query ChatGPT.
The command to install the openai module is: `` pip install openai ``

- **Dotenv** is used to store the API key safely and prevent the file containing your key from being shared with your source control tool. The command to install dotenv is: ``pip install dotenv ``





### Voice input and output

Using audio is dependent on the platform being used. In this version, only MacOS is supported but the port to Windows and Linux is not very complicated and will follow.

**Installing ffmpeg**
