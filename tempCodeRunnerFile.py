from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from fpdf import FPDF
import google.generativeai as genai
import os
from datetime import datetime


API_KEY = os.getenv('API_KEY')

genai.configure(api_key=API_KEY)

app = Flask(__name__)
CORS(app)


class PDF(FPDF):
    def header(self):
        # self.set_font("Arial", size=12)
        # self.cell(0, 10, "Om Tours and Travel", align="C", ln=1)
        self.set_font("Arial", 'B', 15)
        # Add header text
        self.cell(0, 10, "Itinero", ln=1, align="C")
        # Add a line below the header
        self.line(10, 20, 200, 20)  
        self.ln(5)

    def add_day(self, day, content):
        self.set_font("Arial", style="B", size=12)
        self.multi_cell(0, 10, f"{day}", ln=1)
        self.set_font("Arial", size=12)
        self.multi_cell(0, 10, content)
        self.ln(5)  

    def footer(self):
        self.set_y(-15)
        # Set font for the footer
        self.set_font("Arial", 'I', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def calculate_duration(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return (end - start).days + 1


def generate_itinerary(source, destination, duration, budget, preferences,trip_type):
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    
    prompt = (
        f"Generate a detailed {duration}-day travel itinerary from {source} to {destination} "
        f"with a budget of Rs. {budget}. Preferences: {preferences}.  Trip type: {trip_type}. "
        f"Format the itinerary with 'Day X:' followed by activities for each day wirh time slots divided as 'Day X HH:MM AM OR PM : Do Z' and then at the end of the itinerary followed by each day budget as 'Day X Budget: Rs. Y' in a table like formatting. "
        f"Include travel tips and local cuisine recommendations. "
        f"Use plain text and avoid Markdown or bullet points."
    )

    response = model.generate_content([prompt])
    
    
    itinerary_text = response.text.replace("*", "").replace("#", "").replace("-", "").strip()
    
    return itinerary_text

# Function to save itinerary to a PDF file
def save_to_pdf(text):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    
    text = text.replace("₹", "Rs.")
    
    
    lines = text.split("\n")
    for line in lines:
        if line.startswith("Day "):  
            pdf.set_font("Arial", style="B", size=12)  
            pdf.multi_cell(0, 10, line)
        elif "Budget:" in line:  
            pdf.set_font("Arial", style="I", size=12)  
            pdf.multi_cell(0, 10, line)
        else:
            pdf.set_font("Arial", size=12)  # Regular font for content
            pdf.multi_cell(0, 10, line)
    pdf_path = os.path.join(app.root_path, "itinerary.pdf")
    pdf.output(pdf_path)
    pdf.output("itinerary.pdf")
    return "itinerary.pdf"

@app.route('/generate_itinerary', methods=['POST'])
def generate_itinerary_api():
    data = request.json
    
    source = data.get("source", "")
    destination = data.get("destination", "")
    start_date = data.get("start_date", "")
    end_date = data.get("end_date", "")
    budget = data.get("budget", "")
    preferences = data.get("preferences", "")
    trip_type = data.get("trip_type", "")

    duration = calculate_duration(start_date, end_date)

    itinerary_text = generate_itinerary(source, destination, duration, budget, preferences, trip_type)
    
    
    pdf_path = save_to_pdf(itinerary_text)
    
    return jsonify({"itinerary_text": itinerary_text, "pdf_path": pdf_path})

@app.route('/download_pdf')
def download_pdf():
    pdf_path = os.path.join(app.root_path, "itinerary.pdf")
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
