import pandas as pd
import re

df = pd.read_excel('bills.xlsx')

def extract_fields(text):
    text = str(text).replace('\n', ' ')

    # 1. Vendor Name
    vendor = None
    vendor_match = re.search(r'(?:SPEED PRINTER SOLUTIONS|M\. A\. STONEX|co OPiutTigons|S\.T\.LOKHAND SURAT WALA|S\.T\. LOKHANDWALA)', text, re.IGNORECASE)
    if vendor_match:
        vendor = vendor_match.group(0).strip()
    else:
        potential_vendor = re.search(r'\b([A-Z][A-Z\s\.\&]{5,50})\b', text)
        if potential_vendor:
            val = potential_vendor.group(1).strip()
            if "GSTIN" not in val and "INVOICE" not in val and "TAX" not in val and len(val) > 5:
                vendor = val

    # 2. GSTIN
    gstin_match = re.search(r'GSTIN[\s:.-]*([0-9A-Z]{15})', text, re.IGNORECASE)
    if not gstin_match:
         gstin_match = re.search(r'\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})\b', text)
    gstin = gstin_match.group(1) if gstin_match else None

    # 3. Invoice Number
    inv_match = re.search(r'(?:Invoice|Inv|Bill|Numbhar)[.\s]*(?:No|Number|#)[\s:]*([A-Za-z0-9-]+)', text, re.IGNORECASE)
    invoice_number = inv_match.group(1) if inv_match else None

    # 4. Date
    date_match = re.search(r'(?:Date)[\s:]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})', text, re.IGNORECASE)
    if not date_match:
        date_match = re.search(r'\b([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})\b', text)
    date = date_match.group(1) if date_match else None

    # 5. Total Price / Amount
    amounts = re.findall(r'(?:Total|Amount|Payable|Grand Total)[\s:=-]+([\d,]+\.\d{2})', text, re.IGNORECASE)
    if not amounts:
        amounts = re.findall(r'₹?\s*([\d,]+\.\d{2})', text)
    total = None
    if amounts:
        try:
            numeric_amounts = [float(a.replace(',', '')) for a in amounts]
            total = max(numeric_amounts)
        except:
            pass

    # 6. Customer Name
    billed_to_match = re.search(r'(?:Bill To|Billed To|Party Name|SHED)[\s:]*([A-Za-z0-9\s,.-]+?)(?:Invoice|Date|GSTIN|Mo:|Total|\bMo\b)', text, re.IGNORECASE)
    billed_to = None
    if billed_to_match:
        billed_to = billed_to_match.group(1).strip()
    else:
        # Check for Yogesh Natwarlal Shah (HUF) which appears often in the sample
        if "Yogesh Natwarlal Shah" in text:
            billed_to = "Yogesh Natwarlal Shah (HUF)"
        elif "SHED" in text:
            billed_to = "SHED"

    return {
        'Vendor Name': vendor,
        'Customer Name': billed_to,
        'Invoice Number': invoice_number,
        'Date': date,
        'Total Price': total,
        'GSTIN': gstin
    }

parsed_data = df['Extracted Text'].apply(extract_fields)
parsed_df = pd.DataFrame(parsed_data.tolist())

# Reorder columns
final_df = pd.concat([df['Image File'], parsed_df, df['Extracted Text']], axis=1)
final_df.to_excel('structured_bills.xlsx', index=False)
