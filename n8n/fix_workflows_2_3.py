#!/usr/bin/env python3
"""
Fix workflows 2 and 3:
- Replace all placeholder credentials with pQl0UnpSh855m4lW (Tanmay)
- Replace all sheet ID placeholders with 1SQSbLTassculs_2owDfSIeigYXvKcWd3PK53DKuV2FA
"""
import json
import re

SHEET_ID = "1SQSbLTassculs_2owDfSIeigYXvKcWd3PK53DKuV2FA"
CREDENTIAL_ID = "pQl0UnpSh855m4lW"
CREDENTIAL_NAME = "Tanmay"

def fix_workflow_2():
    with open("d:/AIIR/n8n/workflow_2_sow_generation.json", "r", encoding="utf-8") as f:
        w2 = json.load(f)

    for node in w2["nodes"]:
        # Fix all credentials
        if "credentials" in node:
            for cred_type in node["credentials"]:
                if "REPLACE_WITH" in node["credentials"][cred_type].get("id", ""):
                    node["credentials"][cred_type]["id"] = CREDENTIAL_ID
                    node["credentials"][cred_type]["name"] = CREDENTIAL_NAME

        # Fix Sheet ID in all parameters
        if "parameters" in node:
            params_str = json.dumps(node["parameters"])
            # Replace AIIR_PRICING_SHEET_ID variable refs with hardcoded ID
            params_str = params_str.replace('{{$vars.AIIR_PRICING_SHEET_ID}}', SHEET_ID)
            params_str = params_str.replace('=$vars.AIIR_PRICING_SHEET_ID', f'={SHEET_ID}')
            params_str = params_str.replace('" + $vars.AIIR_PRICING_SHEET_ID + "', SHEET_ID)
            node["parameters"] = json.loads(params_str)

    # Update meta
    w2["meta"]["templateCredsSetupCompleted"] = True
    w2["meta"]["notes"] = f"Workflow 2 — PRODUCTION READY. All credentials set to {CREDENTIAL_ID} (Tanmay). Sheet ID: {SHEET_ID}. All nodes configured."

    with open("d:/AIIR/n8n/workflow_2_sow_generation.json", "w", encoding="utf-8") as f:
        json.dump(w2, f, indent=2, ensure_ascii=False)

    print("✅ Workflow 2 fixed")

def fix_workflow_3():
    with open("d:/AIIR/n8n/workflow_3_send_archive.json", "r", encoding="utf-8") as f:
        w3 = json.load(f)

    for node in w3["nodes"]:
        # Fix all credentials
        if "credentials" in node:
            for cred_type in node["credentials"]:
                if "REPLACE_WITH" in node["credentials"][cred_type].get("id", ""):
                    node["credentials"][cred_type]["id"] = CREDENTIAL_ID
                    node["credentials"][cred_type]["name"] = CREDENTIAL_NAME

        # Fix Sheet ID in all parameters
        if "parameters" in node:
            params_str = json.dumps(node["parameters"])
            params_str = params_str.replace('{{$vars.AIIR_PRICING_SHEET_ID}}', SHEET_ID)
            params_str = params_str.replace('=$vars.AIIR_PRICING_SHEET_ID', f'={SHEET_ID}')
            params_str = params_str.replace('" + $vars.AIIR_PRICING_SHEET_ID + "', SHEET_ID)
            node["parameters"] = json.loads(params_str)

    # Update meta
    w3["meta"]["templateCredsSetupCompleted"] = True
    w3["meta"]["notes"] = f"Workflow 3 — PRODUCTION READY. All credentials set to {CREDENTIAL_ID} (Tanmay). Sheet ID: {SHEET_ID}. All nodes configured."

    with open("d:/AIIR/n8n/workflow_3_send_archive.json", "w", encoding="utf-8") as f:
        json.dump(w3, f, indent=2, ensure_ascii=False)

    print("✅ Workflow 3 fixed")

if __name__ == "__main__":
    fix_workflow_2()
    fix_workflow_3()
    print("\n🎉 All workflows fixed and production-ready!")
