/**
 * AIIR Pricing Calculator — Google Sheets Setup Script
 *
 * HOW TO USE:
 * 1. Create a new Google Sheet named "AIIR Pricing Calculator"
 * 2. Open Extensions > Apps Script
 * 3. Paste this entire script
 * 4. Run setupAIIRPricingCalculator()
 * 5. Note the Sheet ID from the URL (between /d/ and /edit)
 *    → This is your AIIR_PRICING_SHEET_ID
 */

function setupAIIRPricingCalculator() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // ─── SHEET 1: Calculator ───────────────────────────────────────────────────
  let calcSheet = ss.getSheetByName('Calculator');
  if (!calcSheet) calcSheet = ss.insertSheet('Calculator');
  calcSheet.clearContents();
  calcSheet.clearFormats();

  // Headers / Labels
  const labels = [
    // Row 1: Title
    ['A1', 'AIIR Pricing Calculator'],
    ['A2', 'Selected Tier'],         ['B2', 'IGNITE'],   // n8n writes tier here
    ['A3', 'Engagement Date'],       ['B3', ''],

    // ─── IGNITE TIER (rows 37–50) ───────────────────────────────────────────
    ['A35', '── IGNITE TIER ──'],
    ['A36', 'Session'],              ['B36', 'Hours'],   ['E36', 'Fee / Months'],
    ['A37', 'Initial Coaching Session'],  ['B37', 0.5],  ['C37', 'fixed'],
    ['A38', 'Stakeholder 1: ASM'],        ['B38', 1.0],
    ['A39', 'Dev History Interview'],     ['B39', 2.0],
    ['A40', 'Interview-Based 360°'],      ['B40', 6.0],  ['E40', 'hours'],
    ['A41', 'Assessment Feedback'],       ['B41', 2.0],
    ['A42', 'Dev Planning Session'],      ['B42', 1.0],
    ['A43', 'Stakeholder 2: SDP'],        ['B43', 1.0],
    ['A44', 'Implementation Sessions'],   ['B44', 8.0],
    ['A45', 'Stakeholder 3: Midpoint'],   ['B45', 1.0],
    ['A46', 'Stakeholder 4: Wrap-Up'],    ['B46', 1.0],

    // CZ fee row
    ['A37', 'Initial Coaching Session'],
    ['D37', 'CZ Fee (months)'],      ['E37', 9],  // n8n writes 7-9
    ['D38', 'CZ Rate/mo (IGNITE)'],  ['F38', 75], // CORRECT rate $75 (not $50)

    // Totals (formulas)
    ['A47', 'Total Coaching Hours'], // B47 = SUM
    ['A48', 'Total Coach Cost'],     // B48 = hours * rate
    ['A49', 'PM Fee (12%)'],         // B49 = coach cost * 0.12
    ['A50', 'Total Services'],       // B50 = coach + PM

    // Input parameters
    ['A13', '── PRICING INPUTS ──'],
    ['A14', 'Tier'],                 ['B14', 'IGNITE'],
    ['A15', 'Coaching Bill Rate'],   ['B15', 350],   // n8n writes market+seniority rate
    ['A16', 'Margin'],               ['B16', 0.65],  // ALWAYS 0.65 — n8n enforces this
    ['A17', 'CZ Rate IGNITE'],       ['B17', 75],    // CORRECT: $75 not $50
    ['A18', 'CZ Rate ASCENT/VISTA'], ['B18', 50],

    // Output section
    ['G44', 'CZ Fee'],                                    // H44 = CZ months * rate
    ['G45', 'LD12 Assessment Fee'],    ['H45', 150],      // Fixed: $150 per participant
    ['G46', 'Hogan Insight Fee'],      ['H46', 300],      // Fixed: $300 per participant
    ['G47', 'Services incl. Margin'],                     // H47
    ['G48', 'Total per Participant'],                     // H48 = H44+H45+H46+H47
    ['G49', 'Number of Participants'], ['H49', ''],       // n8n writes here (FIRST)
    ['G50', 'TOTAL ENGAGEMENT PRICE'],                    // H50 ← THE FINAL PRICE
  ];

  // Write all labels
  labels.forEach(([cellRef, value]) => {
    if (value !== undefined && value !== '') {
      calcSheet.getRange(cellRef).setValue(value);
    }
  });

  // ─── IGNITE FORMULAS ──────────────────────────────────────────────────────
  // Total coaching hours (sum B37:B46)
  calcSheet.getRange('B47').setFormula('=SUM(B37:B46)');
  // Total coach cost
  calcSheet.getRange('B48').setFormula('=B47*B15');
  // PM fee 12%
  calcSheet.getRange('B49').setFormula('=B48*0.12');
  // Total services (coach + PM)
  calcSheet.getRange('B50').setFormula('=B48+B49');
  // CZ fee total
  calcSheet.getRange('H44').setFormula('=E37*F38');   // CZ months * CZ rate
  // H45 = LD12 fee ($150, fixed) — set as value in labels above
  // H46 = Hogan Insight fee ($300, fixed) — set as value in labels above
  // Services including margin
  calcSheet.getRange('H47').setFormula('=B50/(1-B16)');
  // Total per participant (CZ + LD12 + Hogan + services with margin)
  calcSheet.getRange('H48').setFormula('=H44+H45+H46+H47');
  // TOTAL ENGAGEMENT PRICE
  calcSheet.getRange('H50').setFormula('=IF(H49="",H48,H48*H49)');

  // ─── ROADMAP TIER (rows 21–34) ────────────────────────────────────────────
  const roadmapStartRow = 21;
  calcSheet.getRange(`A${roadmapStartRow - 1}`).setValue('── ROADMAP TIER ──');
  calcSheet.getRange(`A${roadmapStartRow}`).setValue('Session');
  calcSheet.getRange(`B${roadmapStartRow}`).setValue('Hours');

  const roadmapSessions = [
    ['Initial Coaching Session', 0.5],
    ['Stakeholder 1: ASM', 1.0],
    ['Dev History Interview', 2.0],
    ['Interview-Based 360°', 3.75],
    ['Assessment Feedback', 2.0],
    ['Dev Planning Session', 1.0],
    ['Stakeholder 2: SDP', 1.0],
    ['Implementation Sessions', 5.0],
    ['Stakeholder 3: Midpoint', 1.0],
    ['Stakeholder 4: Wrap-Up', 1.0],
  ];
  roadmapSessions.forEach(([name, hours], i) => {
    const row = roadmapStartRow + 1 + i;
    calcSheet.getRange(`A${row}`).setValue(name);
    calcSheet.getRange(`B${row}`).setValue(hours);
  });
  const roadmapLastRow = roadmapStartRow + 1 + roadmapSessions.length;
  calcSheet.getRange(`A${roadmapLastRow}`).setValue('Total Hours (ROADMAP)');
  calcSheet.getRange(`B${roadmapLastRow}`).setFormula(`=SUM(B${roadmapStartRow + 1}:B${roadmapLastRow - 1})`);
  calcSheet.getRange(`D${roadmapStartRow + 4}`).setValue('CZ Fee (months)');
  calcSheet.getRange(`E${roadmapStartRow + 4}`).setValue(6); // ROADMAP = 6 months

  // ─── ASCENT TIER (rows 55–70) ─────────────────────────────────────────────
  const ascentStartRow = 55;
  calcSheet.getRange(`A${ascentStartRow - 1}`).setValue('── ASCENT TIER ──');
  const ascentSessions = [
    ['Initial Coaching Session', 0.5],
    ['Stakeholder 1: ASM', 1.0],
    ['Dev History Interview', 2.0],
    ['Interview-Based 360°', 9.0],   // 12 interviews * 45min
    ['Assessment Feedback', 2.0],
    ['Dev Planning Session', 1.0],
    ['Stakeholder 2: SDP', 1.0],
    ['Implementation Sessions', 12.0],
    ['Stakeholder 3: Midpoint', 1.0],
    ['Stakeholder 4: Wrap-Up', 1.0],
  ];
  ascentSessions.forEach(([name, hours], i) => {
    const row = ascentStartRow + i;
    calcSheet.getRange(`A${row}`).setValue(name);
    calcSheet.getRange(`B${row}`).setValue(hours);
  });
  calcSheet.getRange(`D${ascentStartRow + 5}`).setValue('CZ Fee (months)');
  calcSheet.getRange(`E${ascentStartRow + 5}`).setValue(12); // ASCENT = 12 months

  // ─── SPARK I TIER (rows 73–85) ────────────────────────────────────────────
  const spark1StartRow = 73;
  calcSheet.getRange(`A${spark1StartRow - 1}`).setValue('── SPARK I TIER ──');
  const spark1Sessions = [
    ['Initial Coaching Session', 0.5],
    ['Stakeholder 1: ASM', 1.0],
    ['Dev History (Survey $60)', 0], // NO Dev History Interview in SPARK I — survey instead
    ['Interview-Based 360°', 3.75],
    ['Assessment Feedback', 2.0],
    ['Dev Planning Session', 1.0],
    ['Stakeholder 2: SDP', 1.0],
    ['Implementation Sessions', 4.0],
    ['Stakeholder 3: Midpoint', 1.0],
    ['Stakeholder 4: Wrap-Up', 1.0],
  ];
  spark1Sessions.forEach(([name, hours], i) => {
    const row = spark1StartRow + i;
    calcSheet.getRange(`A${row}`).setValue(name);
    calcSheet.getRange(`B${row}`).setValue(hours);
  });
  calcSheet.getRange(`D${spark1StartRow + 5}`).setValue('CZ Fee (months)');
  calcSheet.getRange(`E${spark1StartRow + 5}`).setValue(4); // SPARK I = 4 months
  // Note: SPARK I uses $60 survey instead of Dev History session
  calcSheet.getRange(`C${spark1StartRow + 2}`).setValue('Uses $60 survey instead');

  // ─── SPARK II TIER (rows 91–103) ─────────────────────────────────────────
  const spark2StartRow = 91;
  calcSheet.getRange(`A${spark2StartRow - 1}`).setValue('── SPARK II TIER ──');
  const spark2Sessions = [
    ['Initial Coaching Session', 0.5],
    ['Stakeholder 1: ASM', 1.0],
    ['Dev History Interview', 2.0],
    ['Interview-Based 360°', 3.75],
    ['Assessment Feedback', 2.0],
    ['Dev Planning Session', 1.0],
    ['Stakeholder 2: SDP', 1.0],
    ['Implementation Sessions', 5.0],
    ['Stakeholder 3: Midpoint', 1.0],
    ['Stakeholder 4: Wrap-Up', 1.0],
  ];
  spark2Sessions.forEach(([name, hours], i) => {
    const row = spark2StartRow + i;
    calcSheet.getRange(`A${row}`).setValue(name);
    calcSheet.getRange(`B${row}`).setValue(hours);
  });
  calcSheet.getRange(`D${spark2StartRow + 5}`).setValue('CZ Fee (months)');
  calcSheet.getRange(`E${spark2StartRow + 5}`).setValue(5); // SPARK II = 5 months

  // ─── AIIR VISTA TIER (rows 107–125) ──────────────────────────────────────
  const vistaStartRow = 107;
  calcSheet.getRange(`A${vistaStartRow - 1}`).setValue('── AIIR VISTA TIER ──');
  const vistaSessions = [
    ['Initial Coaching Session', 0.5],
    ['Stakeholder 1: ASM', 1.0],
    ['Dev History Interview', 2.0],
    ['Interview-Based 360°', 6.0],
    ['Assessment Feedback', 2.0],
    ['Dev Planning Session', 1.0],
    ['Stakeholder 2: SDP', 1.0],
    ['Implementation Sessions', 10.0],
    ['Stakeholder 3: Midpoint', 1.0],
    ['Stakeholder 4: Wrap-Up', 1.0],
  ];
  vistaSessions.forEach(([name, hours], i) => {
    const row = vistaStartRow + i;
    calcSheet.getRange(`A${row}`).setValue(name);
    calcSheet.getRange(`B${row}`).setValue(hours);
  });
  calcSheet.getRange(`D${vistaStartRow + 5}`).setValue('CZ Fee (months)');
  calcSheet.getRange(`E${vistaStartRow + 5}`).setValue(12); // VISTA = 12 months

  // ─── FORMATTING ───────────────────────────────────────────────────────────
  // Bold headers
  calcSheet.getRange('A1').setFontWeight('bold').setFontSize(14);
  calcSheet.getRange('H50').setFontWeight('bold').setBackground('#FFFF00').setFontSize(12);
  calcSheet.getRange('G50').setFontWeight('bold');
  calcSheet.getRange('A13:A18').setFontWeight('bold');
  calcSheet.getRange('B16').setBackground('#FFE0E0'); // Highlight margin cell — always 0.65
  calcSheet.getRange('B15').setBackground('#E0F0FF'); // Highlight bill rate

  // Protection note on B16
  calcSheet.getRange('C16').setValue('← ALWAYS 0.65 — do not change');
  calcSheet.getRange('C16').setFontColor('#CC0000').setFontStyle('italic');

  // Freeze top rows
  calcSheet.setFrozenRows(3);
  calcSheet.setFrozenColumns(1);

  // Auto-resize columns
  calcSheet.autoResizeColumns(1, 10);

  SpreadsheetApp.flush();
  Logger.log('Calculator sheet setup complete.');

  // ─── SHEET 2: Tracker ─────────────────────────────────────────────────────
  let trackerSheet = ss.getSheetByName('Tracker');
  if (!trackerSheet) trackerSheet = ss.insertSheet('Tracker');
  trackerSheet.clearContents();

  const trackerHeaders = [
    'engagement_id',      // A
    'created_at',          // B
    'transcript_filename', // C
    'client_company',      // D
    'coachee_name',        // E
    'hubspot_deal_id',     // F
    'coach_name',          // G
    'tier',                // H
    'bill_rate',           // I
    'num_participants',    // J
    'price_per_participant', // K
    'total_engagement_price', // L
    'payment_structure',   // M
    'net_days',            // N
    'pricing_approval_status', // O  (PENDING / APPROVED / ADJUSTED)
    'pricing_approved_by', // P
    'pricing_approved_at', // Q
    'rationale_doc_url',   // R
    'calculator_url',      // S
    'sow_doc_url',         // T
    'sow_approval_status', // U  (PENDING / APPROVED)
    'sow_approved_by',     // V
    'sow_approved_at',     // W
    'client_email',        // X
    'sent_at',             // Y
    'archive_folder_url',  // Z
    'full_variables_json'  // AA
  ];

  trackerSheet.getRange(1, 1, 1, trackerHeaders.length).setValues([trackerHeaders]);

  // Format tracker header row
  const headerRange = trackerSheet.getRange(1, 1, 1, trackerHeaders.length);
  headerRange.setFontWeight('bold').setBackground('#1a73e8').setFontColor('white');
  trackerSheet.setFrozenRows(1);
  trackerSheet.setColumnWidth(trackerHeaders.length, 400); // AA — wide for JSON

  // Conditional formatting for approval status
  const pricingStatusRange = trackerSheet.getRange('O2:O1000');
  const sowStatusRange = trackerSheet.getRange('U2:U1000');

  // Green for APPROVED, red for PENDING
  [pricingStatusRange, sowStatusRange].forEach(range => {
    const rules = trackerSheet.getConditionalFormatRules();
    rules.push(
      SpreadsheetApp.newConditionalFormatRule()
        .whenTextEqualTo('APPROVED')
        .setBackground('#d9ead3')
        .setRanges([range])
        .build()
    );
    rules.push(
      SpreadsheetApp.newConditionalFormatRule()
        .whenTextEqualTo('PENDING')
        .setBackground('#fce5cd')
        .setRanges([range])
        .build()
    );
    trackerSheet.setConditionalFormatRules(rules);
  });

  trackerSheet.autoResizeColumns(1, 26);
  SpreadsheetApp.flush();

  Logger.log('Tracker sheet setup complete.');
  Logger.log('=== SETUP COMPLETE ===');
  Logger.log('Sheet ID: ' + ss.getId());
  Logger.log('Copy this ID as your AIIR_PRICING_SHEET_ID variable in n8n.');

  // Show confirmation
  SpreadsheetApp.getUi().alert(
    '✅ AIIR Pricing Calculator Setup Complete!\n\n' +
    'Sheet ID (copy this for n8n):\n' +
    ss.getId() + '\n\n' +
    'Next steps:\n' +
    '1. Set this as AIIR_PRICING_SHEET_ID in your n8n workflows\n' +
    '2. Verify B16 = 0.65 (Margin) on Calculator sheet\n' +
    '3. Verify F38 = 75 (IGNITE CZ Rate)'
  );
}
