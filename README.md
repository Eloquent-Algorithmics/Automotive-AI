# Automotive AI: Voice Activated Vehicle Diagnostic Assistant 🚗🗣️

Join the [Discord Server](https://discord.gg/VsVuxche)

An experimental open-source application that integrates the OpenAi gpt-3.5-turbo-0125 or gpt-4-turbo models via API, NLP, TTS, STT, and an OBD-II ELM327 device to create a voice-activated, hands-free, vehicle diagnostic assistant.

⚠️ ***This is a work in progress*** ⚠️

03/17/2024: Updated to use [OpenAI v1](https://github.com/openai/openai-python/releases/)

11/14/2023: Added "development" branch with the option to use text input in the terminal instead of voice commands.

## 🛠️ Built and tested using:

- Windows 11 & Ubuntu 22.04
- Python 3.12
- Requires [Miniconda](https://docs.anaconda.com/free/miniconda/#latest-miniconda-installer-links)
- [OBDlink MX+ Bluetooth ELM327](https://www.obdlink.com/products/obdlink-mxp/)
- Desktop testing is possible using an [ELM327 emulator](https://github.com/Ircama/ELM327-emulator)

## 🚀 Installation

1. Fork the repository and clone it to your local machine:

```bash
git clone https://github.com/<your_username>/Automotive-AI.git
```

<details>
<summary>Linux Installation and use Instructions</summary>

```bash
./install.sh
```

Set your API keys and variables in `.env.template` and save it as `.env`

```bash
cp .env.template .env
```

#### Running the Application

Without a vehicle communication interface:

```bash
python -m app
```

With an ELM327 device connected:

```bash
python -m app --device elm327
```

</details>
<br>

<details>

<summary>Windows Installation an Use Instructions</summary>

```PowerShell
.\install.bat
```

Set your API keys and variables in `.env.template` and save it as `.env`

```pwsh
copy .env.template .env
```
#### Running the Application

Without a vehicle communication interface:

```bash
python -m app
```

With an ELM327 device connected:

```bash
python -m app --device elm327
```

</details>

## 🎙️ Voice Commands

<details>

<summary>Current voice commands include:</summary>

- "engine rpm"
- "intake air temperature"
- "fuel tank level"
- "time run with MIL on"
- "engine coolant temperature"
- "read trouble codes"
- "freeze frame data"
- "pending trouble codes"
- "clear trouble codes"
- "vehicle identification number"
- "calibration id message count"
- "calibration id"
- "calibration verification numbers"
- "start a diagnostic report"
- "send a diagnostic report"
- "next on outlook calendar"
- "create a new outlook appointment"
- "check outlook"
- "send an email with outlook"
- "ask question"
- "start a conversation"
- "check gmail"
- "what's next on my google calendar"

To start a conversation that uses JSON for conversation history, use the "start a conversation" command.

After a conversation has been started you can use the following voice commands to manage the conversation history:

- "clear all history"
- "delete the last message"
- "summarize the conversation history"
- "end the conversation"

</details>

## 📟 Using an ELM Simulator

<details>
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
</details>
