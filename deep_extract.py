import pandas as pd
import re
import json

df = pd.read_excel('bills.xlsx')

def enhanced_extract(text):
    text = str(text).replace('\n', ' ')

    vendor = None
    customer = None
    gstin = None
    date = None
    invoice = None
    total = None

    # Vendor extraction - look at first parts of the document
    # Very often the first capitalized string is the vendor.
    match_vendor = re.search(r'^\s*([^\|\[\]\(\)\:]{3,50})(?:\n|GSTIN|Mob|Phone|Address|No\.)', text, re.IGNORECASE)
    if match_vendor:
        vendor = match_vendor.group(1).strip()
        if "Invoice" in vendor or "Bill" in vendor or "GSTIN" in vendor:
            vendor = None

    if not vendor:
        # Known patterns
        if "SPEED PRINTER SOLUTIONS" in text: vendor = "SPEED PRINTER SOLUTIONS"
        elif "M. A. STONEX" in text: vendor = "M. A. STONEX"
        elif "S.T.LOKHAND" in text or "S.T. LOKHAND" in text: vendor = "S.T. LOKHANDWALA"
        elif "OPiutTigons" in text: vendor = "co OPiutTigons"
        else:
            m = re.search(r'([A-Z][A-Z\s\.\&]{5,40})\b', text)
            if m: vendor = m.group(1).strip()

    # Customer Name
    customer_match = re.search(r'(?:Bill To|Billed To|Party Name|Buyer)[\s:]*([A-Za-z0-9\s,.-]+?)(?:Invoice|Date|GSTIN|Mo:|Total|Address|\bMo\b)', text, re.IGNORECASE)
    if customer_match:
        customer = customer_match.group(1).strip()
    else:
        if "Yogesh Natwarlal Shah" in text: customer = "Yogesh Natwarlal Shah (HUF)"
        elif "SHED" in text: customer = "SHED"

    # GSTIN
    gstin_match = re.search(r'([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})', text)
    if gstin_match:
        gstin = gstin_match.group(1)

    # Invoice Number
    inv_match = re.search(r'(?:Invoice|Inv|Bill|Numbhar)[.\s]*(?:No|Number|#)[\s:]*([A-Za-z0-9-/]+)', text, re.IGNORECASE)
    if inv_match:
        invoice = inv_match.group(1).strip()
        if invoice.upper() == "DATE": invoice = None

    # Date
    date_match = re.search(r'\b([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})\b', text)
    if date_match:
        date = date_match.group(1)

    # Total Amount
    # Find all decimal amounts
    amounts = re.findall(r'([\d,]+\.\d{2})', text)
    if amounts:
        numeric_amounts = []
        for a in amounts:
            try:
                numeric_amounts.append(float(a.replace(',', '')))
            except:
                pass
        if numeric_amounts:
            total = max(numeric_amounts)

    # Try finding items list if possible (Product / Qty / Rate / Amount)
    items = []

    # A very naive extraction for items since it's unstructured text from OCR
    # We look for lines that have a number, some text, another number (rate), and another number (amount)

    return {
        'Vendor Name': vendor,
        'Customer Name': customer,
        'GSTIN': gstin,
        'Invoice Number': invoice,
        'Date': date,
        'Total Price': total
    }

parsed_data = df['Extracted Text'].apply(enhanced_extract)
parsed_df = pd.DataFrame(parsed_data.tolist())

final_df = pd.concat([df['Image File'], parsed_df, df['Extracted Text']], axis=1)
final_df.to_excel('structured_bills_detailed.xlsx', index=False)
final_df.to_csv('structured_bills_detailed.csv', index=False)
