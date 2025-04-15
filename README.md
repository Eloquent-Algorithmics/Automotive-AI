# Automotive AI: Voice Activated Vehicle Diagnostic Assistant 🚗🗣️

Join the [Discord Server](https://discord.gg/VsVuxche)

An experimental open-source application that integrates OpenAi gpt-4o or gpt-4o-mini, NLP, TTS, STT, and an OBD-II ELM327 device to create a voice-activated, hands-free, vehicle diagnostic assistant.


⚠️ ***This is a work in progress*** ⚠️
04/15/2025 - 


## 🛠️ Built and tested using:

- Windows 11 24H2, Ubuntu 24.04
- Python 3.13.2
- [OBDlink MX+ Bluetooth ELM327](https://www.obdlink.com/products/obdlink-mxp/)
- Desktop testing is possible using an [ELM327 emulator](https://github.com/Ircama/ELM327-emulator)

## 🚀 Installation

1. Fork this repository and clone it to your local machine:

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
python automotive_ai/app.py
```

With an ELM327 device connected:

```bash
python automotive_ai/app --device elm327
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
python automotive_ai/app.py
```

With an ELM327 device connected:

```bash
python automotive_ai/app.py --device elm327
```

</details>

<br>

<details>
<summary>To use Azure OpenAI Service</summary>

```bash
azd auth login
azd up
```

#### Running the Application

Without a vehicle communication interface:

```bash
python automotive_ai/app.py
```

With an ELM327 device connected:

```bash
python automotive_ai/app.py --device elm327
```

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
