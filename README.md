# Automotive AI: Voice Activated Vehicle Diagnostic Assistant 🚗🗣️

Join the Discord Server (https://discord.gg/VsVuxche)

An experimental open-source application that integrates GPT-3.5-turbo (or GPT-4), NLP, TTS, STT, and an OBD-II ELM327 device to create a voice-activated, hands-free, vehicle diagnostic assistant.

⚠️ ***This is a work in progress*** ⚠️

🔜 ElevenLabs TTS, Google Calendar integration coming soon.

## 🛠️ Built and tested using:

- Windows 11
- Python 3.11.3
- OBDlink MX+ Bluetooth ELM327
- 2005 and 2021 Ford Vehicles
- Desktop testing using an ELM327 emulator

## 🚀 Installation

1. Clone the repository:

```bash
git clone https://github.com/Explorergt92/Automotive-AI.git
```

2. Run the following commands in the root directory:

```bash
pip install -r requirements.txt
pip install --upgrade pint
```

3. Install the spacy NLP model:

```bash
python -m spacy download en_core_web_lg
```

4. Set your API keys and variables in the `.env.template` file and save it as `.env` without a file extension.

## 🏁 Running the Application

Without a vehicle communication interface:

```bash
python main.py
```

With an ELM327 device connected:

```bash
python main.py --device elm327
```

***COMING SOON***
with a CarDAQ-Plus®3 (OPUS IVS is currently working on a 64-Bit version of the driver needed to enable j2534 use with this application)

download [J2534_cffi](https://github.com/MCU-Innovations/J2534_cffi.git), then:

```bash
cd J2534_cffi
pip install .
python main.py --device j2534
```

## 🎙️ Voice Commands

Current voice commands include:

"engine rpm": "010C",
"intake air temperature"
"fuel tank level"
"time run with MIL on"
"engine coolant temperature"
"read trouble codes"
"freeze frame data"
"pending trouble codes"
"clear trouble codes"
"vehicle identification number"
"calibration id message count"
"calibration id"
"calibration verification numbers"
"start a diagnostic report"
"send a diagnostic report"
"next on outlook calendar"
"create a new outlook appointment"
"check outlook"
"send an email with outlook"
"ask question"
"start conversation"
"check gmail"
"what's next on my google calendar"

After a conversation has been started you can use the following voice commands to manage the conversation:

- "clear all history"
- "delete the last message"
- "end the conversation"
- "summarize the conversation history"


## 📟 ELM Simulator

ELM327 emulator: [GitHub](https://github.com/Ircama/ELM327-emulator)
com0com virtual serial port driver: [SourceForge](https://sourceforge.net/projects/com0com/) (to create a virtual COM port pair).

After installing com0com, run:

```bash
elm -p COM6 -a 500000
```

Set the COM port in the `.env` file to `COM7`.

## 📈 Data Stream (Under Construction)

```bash
python air_fuel_datastream.py
```

Streams data from the OBD-II ELM327 device to the console, but there's currently no way to stop the stream other than closing the application.
