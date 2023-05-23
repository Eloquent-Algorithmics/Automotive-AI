import serial
import requests
from api.nhtsa_functions.vin_decoder import parse_vin_response, decode_vin, get_vehicle_data_from_nhtsa
from api.microsoft_functions.graph_api import send_email_with_attachments
from config import GRAPH_EMAIL_ADDRESS


def process_data(command, response, value):
    formatted_data = f"{command} - Value: {value}"
    return formatted_data


def send_command(ser, command):
    ser.write((command + "\r\n").encode())
    response = ser.readline().decode().strip()
    response = response.replace("\r", "").replace(">", "")
    return response


def run_diagnostic_report(ser):
    report_data = []

    # Get VIN
    vin_response = send_command(ser, "0902")
    vin = parse_vin_response(vin_response)
    vehicle_data = get_vehicle_data_from_nhtsa(vin)
    report_data.append(f"VIN: {vin}")
    report_data.append(f"Vehicle Data: {vehicle_data}")

    # Get DTCs
    dtc_response = send_command(ser, "03")
    report_data.append(f"DTCs: {dtc_response}")

    # Get Freeze Frame Data
    freeze_frame_response = send_command(ser, "02")
    report_data.append(f"Freeze Frame Data: {freeze_frame_response}")

    # Add more commands for Mode 6 and Mode 9 data as needed

    # Save the report to a text file
    with open("diagnostic_report.txt", "w") as f:
        for line in report_data:
            f.write(line + "\n")

    return "Diagnostic report generated and saved as diagnostic_report.txt"


def get_recall_data(year, make):
    url = f"https://api.nhtsa.gov/products/vehicle/models?modelYear={year}&make={make}&issueType=r"
    response = requests.get(url)
    return response.json()


def get_complaint_data(year, make, model):
    url = f"https://api.nhtsa.gov/complaints/complaintsByVehicle?make={make}&model={model}&modelYear={year}"
    response = requests.get(url)
    return response.json()


def send_diagnostic_report(ser):
    # Send the commands to the ELM327 device and process the responses
    vin_response = send_command(ser, "0902")
    vin = parse_vin_response(vin_response)
    vehicle_data = get_vehicle_data_from_nhtsa(vin)

    # Get recall and complaint data
    recall_data = get_recall_data(
        vehicle_data['Model Year'], vehicle_data['Make'])
    complaint_data = get_complaint_data(
        vehicle_data['Model Year'], vehicle_data['Make'], vehicle_data['Model'])

    trouble_codes_response = send_command(ser, "03")

    freeze_frame_data_response = send_command(ser, "0202")

    pending_trouble_codes_response = send_command(ser, "07")

    calibration_ids_response = send_command(ser, "0904")

    # Extract relevant recall and complaint information
    recalls = [recall['model'] for recall in recall_data['results']
               if recall['model'].lower() == vehicle_data['Model'].lower()]
    complaints = [complaint['summary']
                  for complaint in complaint_data['results']] if 'results' in complaint_data else []

    # Combine the data into a single string with proper formatting
    diagnostic_data = (
        f"VIN: {vin}\n"
        f"Model Year: {vehicle_data['Model Year']}\n"
        f"Make: {vehicle_data['Make']}\n"
        f"Model: {vehicle_data['Model']}\n"
        f"Trim Level: {vehicle_data['Trim Level']}\n"
        f"Engine Displacement (L): {vehicle_data['Engine Displacement (L)']}\n"
        f"Trouble Codes: {trouble_codes_response}\n"
        f"Freeze Frame Data: {freeze_frame_data_response}\n"
        f"Pending Trouble Codes: {pending_trouble_codes_response}\n"
        f"Calibration IDs: {calibration_ids_response}\n"
        f"Recalls: {len(recalls)}\n"
        f"{'-'*20}\n"
        f"Complaints: {len(complaints)}\n"
        f"{'-'*20}\n"
    )

    for i, complaint in enumerate(complaints):
        diagnostic_data += f"Complaint {i+1}: {complaint}\n\n"

    # Send the email
    to_email = GRAPH_EMAIL_ADDRESS
    subject = "Diagnostic Report"
    body = diagnostic_data

    send_email_with_attachments(to_email, subject, body)
