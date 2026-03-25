from docx import Document

doc = Document(r"D:\AIIR\AIIR_IGNITE_SOW_Template.docx")
full = "\n".join(p.text for p in doc.paragraphs)

checks = ["{{HUBSPOT_ID}}", "{{CLIENT_COMPANY}}", "{{COACH_NAME}}", "{{TOTAL_PRICE}}", "{{NET_DAYS}}", "{{STAKEHOLDER_COUNT}}", "{{PAYMENT_STRUCTURE_1}}"]
print("--- Placeholders ---")
for c in checks:
    print(f"{c}: {'FOUND' if c in full else 'MISSING'}")

bad = ["Jonathan Bailey", "Jonathan Kirschner", "$27,445", "395830485039589", "Client A"]
print("--- Leftover client data ---")
for b in bad:
    print(f"{b}: {'STILL PRESENT' if b in full else 'cleaned'}")
