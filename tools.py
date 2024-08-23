from langchain_core.tools import tool
import datetime


APPOINTMENTS = []

@tool
def get_next_available_appointment():
    """Returns the next available appointment"""
    current_time = datetime.datetime.now()
    return f"One appointment available at {current_time + datetime.timedelta(minutes=(30 - current_time.minute % 30))}"

@tool
def book_appointment(appointment_year: int, appointment_month: int, appointment_day: int, appointment_hour: int, appointment_minute: int, appointment_name: str):
    """Book an appointment at the given time, you must know the exact time to book

    Args:
        appointment_year: The year of the appointment
        appointment_month: The month of the appointment
        appointment_day: The day of the appointment
        appointment_hour: The hour of the appointment
        appointment_minute: The minute of the appointment
        appointment_name: The name of the person booking the appointment
    """
    time = datetime.datetime(appointment_year, appointment_month, appointment_day, appointment_hour, appointment_minute)
    for appointment in APPOINTMENTS:
        if appointment.time >= time and appointment.time < time + datetime.timedelta(minutes=30):
            return f"Appointment at {time} is already booked"
    APPOINTMENTS.append({"time": time, "name": appointment_name})
    return f"Appointment booked for {time}"

@tool
def cancel_appointment(appointment_year: int, appointment_month: int, appointment_day: int, appointment_hour: int, appointment_minute: int):
    """Cancel the appointment at the given time

    Args:
        appointment_year: The year of the appointment
        appointment_month: The month of the appointment
        appointment_day: The day of the appointment
        appointment_hour: The hour of the appointment
        appointment_minute: The minute of the appointment
    """
    time = datetime.datetime(appointment_year, appointment_month, appointment_day, appointment_hour, appointment_minute)
    for appointment in APPOINTMENTS:
        if appointment["time"] == time:
            APPOINTMENTS.remove(appointment)
            return f"Appointment at {time} cancelled"
    return f"No appointment found at {time}"

