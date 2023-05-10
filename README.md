# This is a basic experiment to see what integrating LLMS, NLP, TTS and STT into the automobile environment may do to help to improve hands free operations of technology and the use of On-Board vehicle diagnostics.

An experimental open-source application that integrates the following technologies: gpt-3.5-turbo or gpt-4, NLP, TTS, STT and an OBD-II ELM327 device to create a voice activated, hands free, vehicle diagnostic assistant.

*** This is a work in progress ***

ElevenLabs TTS and Gmail and Google Calendar integration coming soon.

Built and tested using:

Windows 11

Python 3.11.3

OBDlink MX+ Bluetooth ELM327

2005 and 2021 Ford Vehicles along with desktop testing using an ELM327 emulator.

## Install by cloning the repository 

`git clone https://github.com/Explorergt92/Automotive-AI.git`

## Run the following commands in the root directory:

`pip install -r requirements.txt`

`pip install --upgrade pint`

Then install the spacy NLP model by running the following command in the root directory:

`python -m spacy download en_core_web_lg`

set your API keys and variables in the .env.template file and "save as" .env without a file extension.

## run the application by running the following command in the root directory:

```python main.py```

Current voice commands include the following:

    "start a diagnostic report": "DIAGNOSTIC_REPORT",
    "send a diagnostic report to my email": "send_diagnostic_report",
    "engine rpm": "010C",
    "intake air temperature": "010F",
    "fuel tank level": "012F",
    "time run with MIL on": "014D",
    "engine coolant temperature": "0105",
    "read trouble codes": "03",
    "freeze frame data": "0202",
    "pending trouble codes": "07",
    "clear trouble codes": "04",
    "service 9 supported pids": "0900",
    "vehicle identification number": "0902",
    "calibration verification numbers": "0906",
    "in-use performance tracking message count": "0907",
    "in-use performance tracking spark ignition": "0908",
    "in-use performance tracking compression ignition": "090B",
    "what's next on my calendar": "next_appointment",
    "create a new appointment": "create_appointment",
    "do I have any new emails": "check_outlook_email",
    "send an email with an attachment": "send_email",
    "I have a question": "ASK_CHATGPT_QUESTION"


### ELM Simulator

ELM327 emulator found here:

https://github.com/Ircama/ELM327-emulator 

https://sourceforge.net/projects/com0com/ to create a virtual COM port pair.

*** in my testing the com port pair created was COM6 and COM7 ***

After installing com0com, run the following command to start the emulator:

`elm -p COM6 -a 500000`

Set the COM port in the .env file to COM7

## Data Stream *** Under Construction ***

`python data_stream.py` 

Streams data from the OBD-II ELM327 device to the console but there's currently no way to stop the stream other than to close the application.
