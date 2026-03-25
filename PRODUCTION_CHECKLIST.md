# AIIR SOW System - Production Deployment Checklist

**Date**: March 25, 2026
**Status**: ✅ System Tested & Ready for Deployment

---

## Pre-Deployment (Complete Before Going Live)

### 1. Environment Setup
- [ ] Create Railway account (https://railway.app)
- [ ] Connect GitHub repository to Railway
- [ ] Upload Google credentials JSON to Railway
- [ ] Set all environment variables in Railway dashboard

### 2. Configuration Changes
- [ ] Update CORS settings in [`api/index.py:30`](api/index.py#L30) to restrict origins
- [ ] Change `ENVIRONMENT=production` in Railway env vars
- [ ] Set `DEBUG=false` in Railway env vars
- [ ] Update `GOOGLE_CREDENTIALS_PATH=/app/credentials.json`

### 3. Railway Deployment
- [ ] Deploy to Railway
- [ ] Verify deployment succeeded (check Railway logs)
- [ ] Note production URL: `https://________.up.railway.app`
- [ ] Test health endpoint: `GET https://YOUR-URL/health`

---

## n8n Webhook Updates

### Workflow 1: Google Drive Trigger
- [ ] Open n8n workflow 1
- [ ] Update HTTP Request node URL to: `https://YOUR-URL/webhooks/google-drive-file-added`
- [ ] Save and activate workflow
- [ ] Test with sample transcript upload

### Workflow 2: Sheets Trigger
- [ ] Open n8n workflow 2
- [ ] Update HTTP Request node URL to: `https://YOUR-URL/webhooks/pricing-model-approved?engagement_id={{ $json['Engagement ID'] }}`
- [ ] Save and activate workflow
- [ ] Test with manual Column U approval

---

## Production Testing

### Test 1: End-to-End Workflow 1
- [ ] Upload test transcript to Google Drive transcripts folder
- [ ] Wait for n8n workflow 1 to trigger
- [ ] Verify engagement created in Tracker sheet
- [ ] Check Calculator sheet populated correctly
- [ ] Verify pricing rationale document created
- [ ] Confirm email notification received

### Test 2: End-to-End Workflow 2
- [ ] Manually change Column U to "Approved" in Tracker
- [ ] Wait for n8n workflow 2 to trigger
- [ ] Verify SOW document created in Google Drive
- [ ] Check all 14 placeholders filled correctly
- [ ] Verify Column K updated with SOW URL
- [ ] Confirm email notification received

### Test 3: Edge Cases
- [ ] Test transcript without decision maker email
- [ ] Test transcript with special characters
- [ ] Test concurrent uploads (2+ transcripts at once)
- [ ] Verify error logging in Railway dashboard

---

## Monitoring Setup

### Railway Dashboard
- [ ] Bookmark Railway project dashboard
- [ ] Enable email notifications for deployment failures
- [ ] Check "Metrics" tab for CPU/memory usage

### Log Monitoring
- [ ] Test error logging by triggering intentional failure
- [ ] Verify logs appear in Railway dashboard
- [ ] Set up log retention (Railway default: 7 days)

### Optional: Advanced Monitoring
- [ ] Set up Sentry account (https://sentry.io)
- [ ] Add Sentry SDK to project
- [ ] Configure Sentry alerts for errors

---

## Post-Deployment

### Immediate (Day 1)
- [ ] Monitor first 5-10 real transcript uploads
- [ ] Check Railway logs for any errors
- [ ] Verify Google API quota usage (Drive/Sheets/Docs)
- [ ] Test from different networks to ensure accessibility

### Week 1
- [ ] Review OpenAI API usage and costs
- [ ] Check Railway billing usage
- [ ] Gather user feedback on SOW quality
- [ ] Document any new issues in GitHub Issues

### Ongoing
- [ ] Weekly check of error logs
- [ ] Monthly review of API costs
- [ ] Quarterly security audit (rotate API keys)

---

## Rollback Plan (If Issues Occur)

1. **Immediate Rollback**:
   - [ ] Revert n8n webhooks to local ngrok URL
   - [ ] Restart local server + ngrok
   - [ ] System operational within 5 minutes

2. **Debug Production**:
   - [ ] Check Railway logs for errors
   - [ ] Verify environment variables set correctly
   - [ ] Test health endpoint
   - [ ] Check Google credentials permissions

3. **Re-deploy**:
   - [ ] Fix issues locally
   - [ ] Test thoroughly
   - [ ] Re-deploy to Railway
   - [ ] Update n8n webhooks again

---

## Success Criteria

System is considered successfully deployed when:

- ✅ Health endpoint returns 200 OK
- ✅ At least 3 test transcripts processed successfully
- ✅ Both workflows (1 & 2) completing without errors
- ✅ All 14 SOW placeholders filling correctly
- ✅ Email notifications sending properly
- ✅ Railway logs show no critical errors
- ✅ Response time <30 seconds per workflow

---

## Important URLs

### Railway
- Dashboard: https://railway.app/dashboard
- Docs: https://docs.railway.app

### Production Endpoints
- Health Check: `https://YOUR-URL/health`
- Workflow 1: `POST https://YOUR-URL/webhooks/google-drive-file-added`
- Workflow 2: `POST https://YOUR-URL/webhooks/pricing-model-approved?engagement_id=XXX`

### Google Drive Folders
- Transcripts: https://drive.google.com/drive/folders/1JX0QUdZtxSn-1kEJrB1rwenJL9gjrWpu
- Client Documents: https://drive.google.com/drive/folders/1wiW8A9j7BTavRObjrXFQan2mMv1ElaS2
- Rationales: https://drive.google.com/drive/folders/1IFEtmm73v3QkCfploTrt5ox9rn898kra

### Google Sheets
- Tracker: https://docs.google.com/spreadsheets/d/1_9faJK4jCs-jhbKyI1HuF01CCzY6H3DlzUQKuhSUYtU
- Calculator Template: https://docs.google.com/spreadsheets/d/1YpiNSVidnsp8fMQ0DOxE4SxC-NdjxwtksJz-9jYd0QM

---

## Emergency Contacts

**Developer**: kapurkartanmay@gmail.com
**System Owner**: AIIR Consulting
**Railway Support**: https://railway.app/help

---

## Notes

- Railway free trial provides $5 credit
- Production plan: ~$5-10/month for this workload
- OpenAI costs: ~$0.10 per transcript
- Google APIs: Free within generous quotas
- No database required (using Google Sheets as data store)

---

**Last Updated**: March 25, 2026
**System Version**: 1.0.0
**Deployment Status**: ⏳ READY TO DEPLOY

---

*Deployment time estimate: 30-45 minutes*
*Recommended deployment window: During business hours for immediate monitoring*
