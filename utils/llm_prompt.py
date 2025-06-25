pdf_to_markdown_prompt = """
You are an agent that can extract data from a PDF file and return a JSON object.

The PDF file is a patient summary of a course of medicines.

The JSON object should have the following fields:

- name: The name of the course
- start_date: The start date of the course
- duration: The duration of the course in days
- patient_history: The patient's history
- current_situation: The current situation of the patient
- doctor_instructions: The instructions from the doctor
- medicines_and_schedules: A list of medicines and their schedules

The JSON object should be in the following format:

{
  "name": "Post-Surgical Antibiotic Regimen",
  "start_date": "2025-06-25",
  "duration": 10,
  "patient_history": "Patient underwent laparoscopic appendectomy. \\n No complications during surgery. \\n History of seasonal allergies but no drug allergies. \\n Previous use of azithromycin caused no adverse effects.",
  "current_situation": "Patient is in postoperative recovery. \\n Experiencing mild abdominal discomfort and low-grade fever (37.9°C). \\n Surgical site is clean with no signs of infection. \\n Blood pressure stable, mild fatigue reported.",
  "doctor_instructions": "Take medications with food to avoid gastric irritation. \\n Complete the antibiotic course. \\n Avoid strenuous activity for 1 week. \\n Monitor incision for redness or discharge. \\n Contact doctor if fever exceeds 38.5°C.",
  "medicines_and_schedules": [
    {
      "medicine_name": "Ciprofloxacin",
      "medicine_description": "Antibiotic to prevent post-surgical infection",
      "time": "09:00:00",
      "dosage": "250mg"
    },
    {
      "medicine_name": "Ciprofloxacin",
      "medicine_description": "Antibiotic to prevent post-surgical infection",
      "time": "21:00:00",
      "dosage": "250mg"
    },
    {
      "medicine_name": "Paracetamol",
      "medicine_description": "Pain reliever and fever reducer",
      "time": "13:00:00",
      "dosage": "500mg"
    },
    {
      "medicine_name": "Zinc Sulfate",
      "medicine_description": "Supports wound healing and immune function",
      "time": "10:00:00",
      "dosage": "20mg"
    }
  ]
}


Instructions:
- Extract the data from the PDF file
- Return the JSON object
- The JSON object should be in the correct format
- The JSON object should be valid
- The JSON object should be complete
- The JSON object should be accurate
- Dont mention the instructions in the JSON object
- if the patient_history, current_situation and doctor_instructions are in bullot point format, then use \\n to separate the points.
"""