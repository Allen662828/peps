#!/usr/bin/env python3

"""

Blakkbox Tuning - Offline CLI Data Entry App

Save as: blakkbox_cli.py

Run:    python3 blakkbox_cli.py

"""

import sqlite3

import os

import datetime

import textwrap


DB_PATH = os.path.expanduser("~/.blakkbox_tuning.db")

RECEIPT_DIR = os.path.expanduser("~/blakkbox_receipts")


os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

os.makedirs(RECEIPT_DIR, exist_ok=True)


# Initialize DB

conn = sqlite3.connect(DB_PATH)

c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS forms (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    form_base TEXT,

    client_suffix TEXT,

    date_iso TEXT,

    time TEXT,

    name TEXT,

    address TEXT,

    contact TEXT,

    plate TEXT,

    car TEXT,

    make TEXT,

    model TEXT,

    transmission TEXT,

    sw_id TEXT,

    hw_id TEXT,

    service TEXT,

    total_price TEXT,

    technician TEXT

)""")

conn.commit()


BRAND = "BLAKKBOX TUNING"

ADDR = "Poblacion, Tuba, Benguet"

PHONE = "+639386350507"

SEPARATOR = "=" * 51

DASH = "-" * 51


def next_form_base():
    # form_base like 001-A, 002-A, ...

    c.execute("SELECT form_base FROM forms ORDER BY id DESC LIMIT 1")

    row = c.fetchone()

    if row and row[0]:
        try:
            num = int(row[0].split("-")[0])

            num += 1

        except:
            num = 1

    else:
        num = 5  # start at 005 to match your sample; change if you want

    return f"{num:03d}-A"


def input_with_default(prompt, default=""):
    if default:
        i = input(f"{prompt} [{default}]: ").strip()

        return i if i else default

    else:
        i = input(f"{prompt}: ").strip()

        return i


def format_receipt(record, copy_type="CLIENT"):
    """

    record: dict with fields

    copy_type: "CLIENT" or "SHOP"

    For client copy we'll append a client_suffix: /DD-MM-YY

    """

    lines = []

    lines.append(SEPARATOR)

    lines.append(BRAND)

    lines.append(ADDR)

    lines.append(PHONE)

    lines.append(SEPARATOR)

    title = (
        "CLIENT DATA FORM - CLIENT COPY"
        if copy_type == "CLIENT"
        else "CLIENT DATA FORM - SHOP COPY"
    )

    lines.append(title)

    lines.append(SEPARATOR)

    if copy_type == "CLIENT":
        form_number = f"{record['form_base']}/{record['client_suffix']}"

    else:
        form_number = record["form_base"]

    lines.append(f"Form Number : {form_number}")

    lines.append(f"Date : {record['date_iso']}")

    lines.append(f"Time : {record['time']}")

    lines.append(DASH)

    lines.append(f"Name : {record['name']}")

    lines.append(f"Address : {record['address']}")

    lines.append(f"Contact : {record['contact']}")

    lines.append(f"Plate # : {record['plate']}")

    lines.append(f"Car : {record['car']}")

    lines.append(f"Make : {record['make']}")

    lines.append(f"Model : {record['model']}")

    lines.append(f"Transmission: {record['transmission']}")

    lines.append(f"SW ID : {record['sw_id']}")

    lines.append(f"HW ID : {record['hw_id']}")

    lines.append(f"Service : {record['service']}")

    lines.append(f"Total Price : {record['total_price']}")

    lines.append(DASH)

    lines.append("Client Signature: ______________________")

    lines.append(
        f"Technician : {record.get('technician', '') or '______________________'}"
    )

    lines.append("")

    lines.append("Terms")

    lines.append("")

    terms = [
        "1. Payment must be settled in full upon service completion.",
        "2. Blakkbox Tuning not liable for pre-existing defects.",
        "3. Warranty applies only to tuning performed.",
        "4. Client acknowledges risks of performance mods.",
        "5. This form serves as proof of agreement.",
    ]

    for t in terms:
        lines.append(t)

    lines.append(SEPARATOR)

    return "\n".join(lines)


def save_record_to_db(record):
    c.execute(
        """INSERT INTO forms (

        form_base, client_suffix, date_iso, time, name, address, contact, plate, car, make,

        model, transmission, sw_id, hw_id, service, total_price, technician

    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            record["form_base"],
            record["client_suffix"],
            record["date_iso"],
            record["time"],
            record["name"],
            record["address"],
            record["contact"],
            record["plate"],
            record["car"],
            record["make"],
            record["model"],
            record["transmission"],
            record["sw_id"],
            record["hw_id"],
            record["service"],
            record["total_price"],
            record.get("technician", ""),
        ),
    )

    conn.commit()

    return c.lastrowid


def export_text_file(form_id, client_text, shop_text):
    fname = os.path.join(RECEIPT_DIR, f"form_{form_id:05d}.txt")

    with open(fname, "w", encoding="utf-8") as f:
        f.write(client_text)

        f.write("\n\n")

        f.write(shop_text)

    return fname


def main():
    print()

    print("==== BLAKKBOX TUNING - Offline CLI Data Entry ====")

    print("Location:", ADDR, "| Phone:", PHONE)

    print("DB:", DB_PATH)

    print()

    # Pre-fill defaults from last record if exists

    c.execute(
        "SELECT name,address,contact,plate,car,make,model,transmission,sw_id,hw_id,service,total_price,technician FROM forms ORDER BY id DESC LIMIT 1"
    )

    last = c.fetchone()

    defaults = {}

    if last:
        keys = [
            "name",
            "address",
            "contact",
            "plate",
            "car",
            "make",
            "model",
            "transmission",
            "sw_id",
            "hw_id",
            "service",
            "total_price",
            "technician",
        ]

        defaults = dict(zip(keys, last))

    # interactive input

    form_base = next_form_base()

    now = datetime.datetime.now()

    date_iso = now.strftime("%a %d-%m-%Y")  # e.g., Fri 10-03-2025 to look like sample

    time_str = now.strftime("%H:%M:%S")

    client_suffix = now.strftime("%d-%m-%y")  # appended to client copy: /DD-MM-YY

    print(f"Auto Form Base -> {form_base}")

    print(f"Auto Date -> {date_iso}    Time -> {time_str}")

    print()

    name = input_with_default("Name", defaults.get("name", "NAPOLEON TYRONE CAEL"))

    address = input_with_default("Address", defaults.get("address", "KM3 L.T.B."))

    contact = input_with_default("Contact", defaults.get("contact", "09070457154"))

    plate = input_with_default("Plate #", defaults.get("plate", "UID277"))

    car = input_with_default("Car", defaults.get("car", "HILUX"))

    make = input_with_default("Make", defaults.get("make", "TOYOTA"))

    model = input_with_default("Model", defaults.get("model", "2012"))

    transmission = input_with_default(
        "Transmission", defaults.get("transmission", "M/T")
    )

    sw_id = input_with_default("SW ID", defaults.get("sw_id", "89663-0KN51"))

    hw_id = input_with_default("HW ID", defaults.get("hw_id", "89661"))

    service = input_with_default("Service", defaults.get("service", "STANDARD TUNNING"))

    total_price = input_with_default(
        "Total Price (₱)", defaults.get("total_price", "₱10.000")
    )

    technician = input_with_default(
        "Technician (optional)", defaults.get("technician", "")
    )

    record = {
        "form_base": form_base,
        "client_suffix": client_suffix,
        "date_iso": date_iso,
        "time": time_str,
        "name": name,
        "address": address,
        "contact": contact,
        "plate": plate,
        "car": car,
        "make": make,
        "model": model,
        "transmission": transmission,
        "sw_id": sw_id,
        "hw_id": hw_id,
        "service": service,
        "total_price": total_price,
        "technician": technician,
    }

    # Save

    rowid = save_record_to_db(record)

    # Prepare receipts

    client_text = format_receipt(record, copy_type="CLIENT")

    shop_text = format_receipt(record, copy_type="SHOP")

    # Print to terminal

    print()

    print("---- CLIENT COPY ----")

    print(client_text)

    print()

    print("---- SHOP COPY ----")

    print(shop_text)

    print()

    # Export to text file

    fname = export_text_file(rowid, client_text, shop_text)

    print(f"Saved record id {rowid}  -> {fname}")

    print()

    print(
        "You can print the saved file with `lp` (Linux/mac) or open it in a text editor."
    )

    print("Example: lp", fname)

    print()

    print("Done. New form base will increment next run.")

    print()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nAborted by user.")

    finally:
        conn.close()
