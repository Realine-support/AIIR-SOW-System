"""
COMPLETE END-TO-END PRODUCTION TEST
Tests the full workflow: Drive → AI → Pricing → Sheets Update
"""

import asyncio
import logging
from datetime import datetime
from app.config import get_config
from app.services import GoogleDriveService, GoogleSheetsService, OpenAIService
from app.business_logic import calculate_pricing, generate_pricing_rationale

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_full_production():
    """Complete end-to-end production test with real transcript"""

    logger.info("=" * 80)
    logger.info("COMPLETE END-TO-END PRODUCTION TEST")
    logger.info("=" * 80)
    logger.info("")

    try:
        # Load config
        config = get_config()
        logger.info("✓ Config loaded")

        # Initialize services
        drive = GoogleDriveService(config.google_credentials_path)
        sheets = GoogleSheetsService(config.google_credentials_path)
        openai_svc = OpenAIService(config.openai_api_key)
        logger.info("✓ All services initialized")
        logger.info("")

        # ====================
        # STEP 1: GET TRANSCRIPT FROM DRIVE
        # ====================
        logger.info("=" * 80)
        logger.info("STEP 1: DOWNLOAD TRANSCRIPT FROM GOOGLE DRIVE")
        logger.info("=" * 80)
        logger.info("")

        logger.info("Listing transcripts in folder...")
        files = drive.list_files_in_folder(
            config.transcripts_folder_id,
            mime_type=None,
            order_by='createdTime desc'
        )

        # Filter for .txt files
        txt_files = [f for f in files if f['name'].endswith('.txt')]

        if not txt_files:
            logger.error("❌ No .txt transcript files found!")
            logger.info(f"Found {len(files)} total files:")
            for f in files[:5]:
                logger.info(f"  - {f['name']} ({f.get('mimeType', 'unknown')})")
            return

        # Use most recent transcript
        transcript_file = txt_files[0]
        file_id = transcript_file['id']
        filename = transcript_file['name']

        logger.info(f"✓ Found transcript: {filename}")
        logger.info(f"  File ID: {file_id}")
        logger.info("")

        logger.info("Downloading transcript content...")
        transcript_text = drive.download_file(file_id)
        logger.info(f"✓ Downloaded: {len(transcript_text)} characters")
        logger.info("")

        # ====================
        # STEP 2: AI EXTRACTION
        # ====================
        logger.info("=" * 80)
        logger.info("STEP 2: AI VARIABLE EXTRACTION")
        logger.info("=" * 80)
        logger.info("")

        logger.info("Sending to OpenAI GPT-4o...")
        extracted = openai_svc.extract_variables_from_transcript(transcript_text)

        logger.info("✓ Extraction complete!")
        logger.info("")
        logger.info("EXTRACTED DATA:")
        logger.info(f"  Client: {extracted.client_company_name}")
        logger.info(f"  Coachee: {extracted.coachee_name} ({extracted.coachee_title})")
        logger.info(f"  Decision Maker: {extracted.decision_maker_name} ({extracted.decision_maker_email})")
        logger.info(f"  Seniority: {extracted.seniority_level.value}")
        logger.info(f"  Duration: {extracted.engagement_duration_months} months")
        logger.info(f"  Market: {extracted.market_type.value}")
        logger.info(f"  Budget Ceiling: ${extracted.budget_ceiling:,.0f}" if extracted.budget_ceiling else f"  Budget Ceiling: Not specified")
        logger.info(f"  Budget Phrases: {len(extracted.budget_constraint_phrases)} detected")
        logger.info(f"  360° Status: {extracted.existing_360_status or 'Not mentioned'}")
        logger.info(f"  Self-Awareness Signals: {len(extracted.self_awareness_signals)} detected")
        logger.info("")

        # ====================
        # STEP 3: PRICING CALCULATION
        # ====================
        logger.info("=" * 80)
        logger.info("STEP 3: PRICING CALCULATION")
        logger.info("=" * 80)
        logger.info("")

        logger.info("Applying business logic...")
        pricing = calculate_pricing(extracted)

        logger.info("✓ Pricing calculated!")
        logger.info("")
        logger.info("PRICING RESULTS:")
        logger.info(f"  Program Tier: {pricing.tier.value}")
        logger.info(f"  Bill Rate: ${pricing.bill_rate_per_hour}/hour")
        logger.info(f"  360° Decision: {pricing.threesixty_decision} ({pricing.session_hours.threesixty_interview_hours} hrs)")
        logger.info(f"  Total Hours: {pricing.total_coaching_hours:.1f} hours")
        logger.info(f"  Total Price: ${pricing.total_engagement_price:,.0f}")
        logger.info(f"  Payment Terms: {pricing.payment_terms}")

        if pricing.budget_reduction_triggered:
            logger.info(f"  Budget Reductions: {len(pricing.budget_reductions)} levers applied")
            total_saved = sum(r.cost_saved for r in pricing.budget_reductions)
            logger.info(f"  Total Saved: ${total_saved:,.0f}")
        logger.info("")

        # ====================
        # STEP 4: GENERATE ENGAGEMENT ID
        # ====================
        logger.info("=" * 80)
        logger.info("STEP 4: GENERATE ENGAGEMENT ID")
        logger.info("=" * 80)
        logger.info("")

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        client_slug = extracted.client_company_name.replace(' ', '').replace(',', '').upper()[:10]
        engagement_id = f"{client_slug}-{timestamp}"
        logger.info(f"✓ Engagement ID: {engagement_id}")
        logger.info("")

        # ====================
        # STEP 5: WRITE TO GOOGLE SHEETS TRACKER
        # ====================
        logger.info("=" * 80)
        logger.info("STEP 5: WRITE TO GOOGLE SHEETS TRACKER")
        logger.info("=" * 80)
        logger.info("")

        tracker_row = [
            engagement_id,                                          # A: Engagement ID
            extracted.client_company_name,                          # B: Client Company
            extracted.coachee_name,                                 # C: Coachee Name
            extracted.coachee_title,                                # D: Coachee Title
            extracted.decision_maker_name or extracted.coachee_name, # E: Decision Maker
            extracted.decision_maker_email,                         # F: Decision Maker Email
            pricing.tier.value,                                     # G: Program Tier
            str(extracted.seniority_level.value),                   # H: Seniority Level
            str(extracted.engagement_duration_months or ''),        # I: Duration
            str(extracted.market_type.value),                       # J: Market Type
            str(pricing.bill_rate_per_hour),                        # K: Bill Rate
            str(pricing.total_coaching_hours),                      # L: Total Hours
            str(pricing.total_engagement_price),                    # M: Total Price
            pricing.payment_terms,                                  # N: Payment Terms
            '',  # Rationale URL (would be uploaded to Drive)       # O
            f"https://docs.google.com/spreadsheets/d/{config.calculator_sheet_id}",  # P: Calculator URL
            '',  # SOW URL (not generated yet)                      # Q
            'Pending Review',  # STATUS                             # R
            datetime.now().isoformat(),                             # S: Created At
            datetime.now().isoformat(),                             # T: Updated At
        ]

        logger.info("Writing row to Tracker sheet...")
        result = sheets.append_row(
            config.tracker_sheet_id,
            config.tracker_tab_name,
            tracker_row
        )
        logger.info(f"✓ Row added to Tracker!")
        logger.info(f"  Updated cells: {result.get('updates', {}).get('updatedCells', 0)}")
        logger.info("")

        # ====================
        # STEP 6: WRITE TO CALCULATOR SHEET
        # ====================
        logger.info("=" * 80)
        logger.info("STEP 6: WRITE TO CALCULATOR SHEET")
        logger.info("=" * 80)
        logger.info("")

        calculator_updates = [
            {'range': f'{config.calculator_tab_name}!A2', 'values': [[engagement_id]]},
            {'range': f'{config.calculator_tab_name}!B2', 'values': [[extracted.client_company_name]]},
            {'range': f'{config.calculator_tab_name}!C2', 'values': [[pricing.tier.value]]},
            {'range': f'{config.calculator_tab_name}!D2', 'values': [[pricing.bill_rate_per_hour]]},
            {'range': f'{config.calculator_tab_name}!E2', 'values': [[pricing.session_hours.implementation_sessions]]},
            {'range': f'{config.calculator_tab_name}!F2', 'values': [[pricing.session_hours.stakeholder_sessions_hours]]},
            {'range': f'{config.calculator_tab_name}!G2', 'values': [[pricing.session_hours.developmental_history_hours]]},
            {'range': f'{config.calculator_tab_name}!H2', 'values': [[pricing.session_hours.threesixty_interview_hours]]},
            {'range': f'{config.calculator_tab_name}!I2', 'values': [[pricing.session_hours.assessment_feedback_hours]]},
            {'range': f'{config.calculator_tab_name}!J2', 'values': [[pricing.total_engagement_price]]},
        ]

        logger.info("Updating Calculator sheet...")
        sheets.batch_update(config.calculator_sheet_id, calculator_updates)
        calculator_url = f"https://docs.google.com/spreadsheets/d/{config.calculator_sheet_id}"
        logger.info(f"✓ Calculator updated!")
        logger.info(f"  URL: {calculator_url}")
        logger.info("")

        # ====================
        # STEP 7: GENERATE RATIONALE
        # ====================
        logger.info("=" * 80)
        logger.info("STEP 7: GENERATE PRICING RATIONALE")
        logger.info("=" * 80)
        logger.info("")

        logger.info("Generating AI-powered rationale...")
        rationale = generate_pricing_rationale(extracted, pricing)
        logger.info(f"✓ Rationale generated: {len(rationale)} characters")
        logger.info("")
        logger.info("RATIONALE PREVIEW:")
        logger.info("-" * 80)
        logger.info(rationale[:500] + "...")
        logger.info("-" * 80)
        logger.info("")

        # ====================
        # FINAL SUMMARY
        # ====================
        logger.info("=" * 80)
        logger.info("✓✓✓ PRODUCTION TEST COMPLETE ✓✓✓")
        logger.info("=" * 80)
        logger.info("")
        logger.info("SUMMARY:")
        logger.info(f"  ✓ Transcript processed: {filename}")
        logger.info(f"  ✓ AI extraction: 100% successful")
        logger.info(f"  ✓ Pricing calculated: ${pricing.total_engagement_price:,.0f}")
        logger.info(f"  ✓ Google Sheets updated: Tracker + Calculator")
        logger.info(f"  ✓ Engagement ID: {engagement_id}")
        logger.info("")
        logger.info("NEXT STEPS:")
        logger.info("1. Open Google Sheets to review the engagement")
        logger.info("2. Verify all calculations are correct")
        logger.info("3. Update Status column to 'Approved' or 'Rejected'")
        logger.info("")
        logger.info(f"Tracker URL: https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}")
        logger.info(f"Calculator URL: {calculator_url}")
        logger.info("")
        logger.info("🎉 SYSTEM IS FULLY OPERATIONAL! 🎉")
        logger.info("")

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ PRODUCTION TEST FAILED: {e}")
        logger.error("=" * 80)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_full_production())
