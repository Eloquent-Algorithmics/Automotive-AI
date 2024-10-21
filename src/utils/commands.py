"""
This module defines a dictionary for voice commands.
"""

# voice commands dictionary
voice_commands = {
    "engine rpm": "010C",
    "intake air temperature": "010F",
    "fuel tank level": "012F",
    "time run with MIL on": "014D",
    "engine coolant temperature": "0105",
    "read trouble codes": "03",
    "freeze frame data": "0202",
    "pending trouble codes": "07",
    "clear trouble codes": "04",
    "vehicle identification number": "0902",
    "calibration id message count": "0903",
    "calibration id": "0904",
    "calibration verification numbers": "0906",
    "start a diagnostic report": "DIAGNOSTIC_REPORT",
    "send a diagnostic report": "send_diagnostic_report",
    "next on outlook calendar": "next_appointment",
    "create a new outlook appointment": "create_appointment",
    "check outlook": "check_outlook_email",
    "send an email with outlook": "send_email",
    "start data stream": "START_DATA_STREAM",
    "stop data stream": "STOP_DATA_STREAM",
    "save data to spreadsheet": "SAVE_DATA_TO_SPREADSHEET",
    "ask a question": "ASK_CHATGPT_QUESTION",
    "start conversation": "START_CONVERSATION",
}

# ELM327 commands set
ELM327_COMMANDS = {
    "DIAGNOSTIC_REPORT",
    "010C",
    "010F",
    "012F",
    "014D",
    "0105",
    "03",
    "0202",
    "07",
    "04",
    "0900",
    "0901",
    "0902",
    "0903",
    "0904",
    "0905",
    "0906",
    "0907",
    "0908",
    "0909",
    "090A",
    "090B",
}
