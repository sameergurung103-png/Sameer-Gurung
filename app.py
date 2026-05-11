from flask import Flask, render_template, request, send_file
import csv
import os
from datetime import datetime
from collections import Counter

app = Flask(__name__)
CSV_FILE = "complaints.csv"


def create_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Complaint_ID", "Name", "Area",
                "Problem_Type", "Description", "Date_Time"
            ])


def get_complaint_id():
    with open(CSV_FILE, "r") as file:
        return len(list(csv.reader(file)))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    area = request.form.get("area")
    problem_type = request.form.get("problem_type")
    description = request.form.get("description")

    complaint_id = get_complaint_id()
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            complaint_id, name, area,
            problem_type, description, date_time
        ])

    return render_template("success.html", complaint_id=complaint_id)


@app.route("/dashboard")
def dashboard():
    area_counts = Counter()

    with open(CSV_FILE, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            area_counts[row["Area"]] += 1

    return render_template("dashboard.html", area_counts=area_counts)


@app.route("/search", methods=["GET", "POST"])
def search():
    complaints = []
    search_area = ""

    if request.method == "POST":
        search_area = request.form["area"]
        with open(CSV_FILE, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Area"].lower() == search_area.lower():
                    complaints.append(row)

    return render_template(
        "search.html",
        complaints=complaints,
        search_area=search_area
    )


@app.route("/export/<area>")
def export_area(area):
    export_file = f"{area}_report.csv"

    with open(CSV_FILE, "r") as file, open(export_file, "w", newline="") as out:
        reader = csv.DictReader(file)
        writer = csv.DictWriter(out, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            if row["Area"].lower() == area.lower():
                writer.writerow(row)

    return send_file(export_file, as_attachment=True)


if __name__ == "__main__":
    create_csv()
    app.run(debug=True)