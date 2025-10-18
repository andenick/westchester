# Namecheap Domain Setup Guide
## Complete Step-by-Step Instructions for Westchester County Data Platform

**Last Updated**: October 17, 2025
**Estimated Time**: 30 minutes (including domain purchase)

---

## Part 1: Purchase Your Domain (10 minutes)

### Step 1: Go to Namecheap
1. Open your web browser
2. Navigate to: **https://www.namecheap.com**
3. Click "Sign Up" (top right) if you don't have an account
   - Enter email address, username, password
   - Verify email address

### Step 2: Search for Your Domain
1. In the search box on homepage, type your desired domain name
   - Examples:
     - `westchester-data.com`
     - `westchesterdata.org`
     - `wcdata.net`
     - `westchester-platform.com`

2. Click "Search" button

3. Review available domains:
   - ✅ Green checkmark = Available
   - ❌ Red X = Taken (try different name or extension)

### Step 3: Select Your Domain
1. Click "Add to Cart" next to your chosen domain
   - **Recommended**: `.com` domains ($12-15/year)
   - **Alternative**: `.org` for non-profit appearance ($14-16/year)
   - **Avoid**: Unusual extensions (.xyz, .info) - less professional

2. Review cart:
   - Domain name: __________________ (write it down!)
   - Price: ~$12-15 for first year
   - Auto-renew: ✅ Enabled (recommended to avoid losing domain)

### Step 4: Domain Privacy (IMPORTANT)
1. Look for "WhoisGuard" or "Domain Privacy"
   - **FREE** for first year on most `.com` domains
   - ✅ **Enable This!** - Protects your personal info from public WHOIS database

2. What it does:
   - Hides your name, address, phone, email from public searches
   - Shows Namecheap's info instead
   - Required by law in EU (GDPR), recommended everywhere

### Step 5: Complete Purchase
1. Click "Confirm Order"
2. Create account or log in
3. Enter payment information:
   - Credit card (Visa, Mastercard, AmEx)
   - PayPal (if preferred)
4. Review total cost:
   - Domain: ~$12-15
   - WhoisGuard: $0 (first year free)
   - **Total**: ~$12-15

5. Click "Continue" or "Pay Now"

6. **IMPORTANT**: Save your receipt email!

---

## Part 2: Initial Domain Configuration (5 minutes)

### Step 6: Access Domain Dashboard
1. After purchase, you'll be redirected to "Domain List"
   - Or go to: **https://ap.www.namecheap.com/domains/list/**

2. Find your new domain in the list

3. Click "Manage" button next to your domain

### Step 7: Verify Domain Settings
1. On domain management page, check:
   - **Auto-Renew**: Should be ON (green)
   - **Domain Lock**: Should be ON (prevents unauthorized transfers)
   - **WhoisGuard**: Should be ENABLED (protecting your privacy)

2. If any are off, click to enable them

### Step 8: Set Nameservers (DO THIS LATER)
**IMPORTANT**: Do NOT change nameservers yet!

We'll configure DNS records in Part 3 after Netlify and Render are set up.

Current nameservers should be:
- `dns1.registrar-servers.com`
- `dns2.registrar-servers.com`

Leave these for now. We'll update DNS records, not nameservers.

---

## Part 3: DNS Configuration (15 minutes)
**⚠️ COMPLETE THIS AFTER NETLIFY AND RENDER DEPLOYMENT**

### When to Do This
After you've completed:
- ✅ Render backend deployed (you have: westchester-api.onrender.com)
- ✅ Netlify frontend deployed (you have: random-name.netlify.app)

### Step 9: Access DNS Management
1. In Namecheap domain dashboard, click "Advanced DNS" tab

2. You'll see DNS records table with columns:
   - Type
   - Host
   - Value
   - TTL (Time To Live)

### Step 10: Add Netlify DNS Records
These records point your domain to Netlify frontend.

#### Record 1: A Record (Main Domain)
1. Click "Add New Record"
2. Select "A Record" from dropdown
3. Fill in:
   - **Type**: A Record
   - **Host**: `@` (this means your root domain)
   - **Value**: `75.2.60.5` ← Netlify's load balancer IP
     - ⚠️ **Important**: Get actual IP from Netlify dashboard
     - This IP may change - verify in Netlify docs or dashboard
   - **TTL**: Automatic (or 1 min for testing, 30 min for production)

4. Click green checkmark to save

#### Record 2: CNAME Record (www Subdomain)
1. Click "Add New Record"
2. Select "CNAME Record" from dropdown
3. Fill in:
   - **Type**: CNAME Record
   - **Host**: `www`
   - **Value**: `your-site-name.netlify.app` ← Your Netlify subdomain
     - Example: `westchester-platform.netlify.app`
     - Find this in Netlify dashboard: Site settings → Domain management
   - **TTL**: Automatic

4. Click green checkmark to save

### Step 11: Add Render DNS Record (API Subdomain)
This record points api.your-domain.com to your Render backend.

#### Record 3: CNAME Record (API Subdomain)
1. Click "Add New Record"
2. Select "CNAME Record" from dropdown
3. Fill in:
   - **Type**: CNAME Record
   - **Host**: `api`
   - **Value**: `your-app-name.onrender.com` ← Your Render service URL
     - Example: `westchester-api.onrender.com`
     - Find this in Render dashboard: Service → Settings
   - **TTL**: Automatic

4. Click green checkmark to save

### Step 12: Remove Default Records (If Needed)
Namecheap may have pre-configured some parking page records.

**Remove these if present**:
- Any A records pointing to `192.64.119.x` (parking page)
- Any CNAME records for `@` (conflicts with A record)

**How to remove**:
- Click trash can icon next to unwanted record
- Confirm deletion

### Final DNS Configuration Should Look Like:
```
Type    Host    Value                           TTL
A       @       75.2.60.5                       Automatic
CNAME   www     your-site.netlify.app           Automatic
CNAME   api     your-app.onrender.com           Automatic
```

### Step 13: Save All Changes
1. Review all three records are correct
2. Click "Save All Changes" button (bottom of page)
3. You'll see "Changes saved successfully" message

---

## Part 4: DNS Propagation & Verification (Wait Time)

### Step 14: Understand DNS Propagation
After saving DNS records, changes need to propagate across internet:
- **Minimum**: 5-10 minutes
- **Typical**: 30 minutes to 2 hours
- **Maximum**: Up to 48 hours (rare)

**Why it takes time**:
- DNS servers worldwide cache old records
- They need to refresh with your new records
- TTL (Time To Live) controls cache duration

### Step 15: Check DNS Propagation
Use these tools to monitor propagation:

**Option 1: DNS Checker** (Recommended)
1. Go to: **https://dnschecker.org**
2. Enter your domain: `your-domain.com`
3. Select "A" record type
4. Click "Search"
5. Map shows where your domain resolves:
   - ✅ Green checkmarks = Propagated
   - ❌ Red X = Not yet propagated
6. Wait until most locations show green

**Option 2: Command Line**
```bash
# Windows Command Prompt or PowerShell
nslookup your-domain.com

# Should eventually show:
# Address: 75.2.60.5 (Netlify IP)
```

**Option 3: What's My DNS**
1. Go to: **https://www.whatsmydns.net**
2. Enter your domain
3. Select "A" record
4. Click "Search"
5. View results from servers worldwide

### Step 16: Test Your Domain
Once DNS propagates, test your domain:

**Test Main Domain**:
1. Open browser
2. Go to: `http://your-domain.com`
3. Should redirect to HTTPS and show your site

**Test www Subdomain**:
1. Go to: `http://www.your-domain.com`
2. Should also show your site

**Test API Subdomain**:
1. Go to: `https://api.your-domain.com/api/health`
2. Should show API health check response:
   ```json
   {"status": "healthy", "version": "1.0.0"}
   ```

---

## Part 5: SSL Certificate Setup (Automatic)

### Step 17: Netlify Auto-SSL
**Good news**: Netlify automatically provisions SSL certificates!

1. In Netlify dashboard: Site settings → Domain management → HTTPS
2. After DNS propagates (30 min - 2 hours):
   - Status changes to "Certificate active"
   - HTTPS automatically enabled
   - HTTP → HTTPS redirect enabled

3. If SSL doesn't auto-provision after 4 hours:
   - Click "Verify DNS configuration"
   - Click "Renew certificate"
   - Contact Netlify support if still issues

### Step 18: Render Auto-SSL
**Good news**: Render also automatically provisions SSL!

1. In Render dashboard: Service → Settings → Custom Domain
2. After adding `api.your-domain.com`:
   - SSL status shows "Pending"
   - After DNS propagates: "Active"
   - HTTPS automatically enabled

3. Verify SSL:
   - Go to: `https://api.your-domain.com/api/health`
   - Look for green lock icon in browser address bar
   - Click lock → "Certificate" → Should show Let's Encrypt

---

## Part 6: Domain Email Configuration (Optional)

### Step 19: Email Forwarding (Free)
If you want email@your-domain.com to work:

1. In Namecheap: Domain management → "Email Forwarding" tab
2. Click "Add Forwarder"
3. Set up forwarding:
   - **Alias**: `info` (creates info@your-domain.com)
   - **Forward To**: your-personal-email@gmail.com
   - Click "Add Forwarder"

4. Repeat for other aliases:
   - `contact@your-domain.com`
   - `support@your-domain.com`
   - `admin@your-domain.com`

5. **Limit**: 100 email forwarders per domain (plenty!)

### Step 20: Professional Email (Paid)
For full email hosting (send & receive):

**Option 1: Namecheap Private Email** ($12/year per mailbox)
- Basic email hosting
- 3 GB storage per mailbox
- Webmail + IMAP/SMTP

**Option 2: Google Workspace** ($6/month per user)
- Gmail with your domain
- Google Drive, Calendar, Docs
- 30 GB storage minimum

**Option 3: ProtonMail** ($4-8/month)
- Privacy-focused email
- End-to-end encryption
- 10-50 GB storage

---

## Part 7: Domain Management Best Practices

### Security Settings

**Enable Two-Factor Authentication (2FA)**:
1. Namecheap account → Security → Two-Step Verification
2. Enable using:
   - SMS (phone number)
   - Authenticator app (Google Authenticator, Authy)
   - U2F security key (YubiKey, etc.)
3. Save backup codes in safe place

**Domain Lock**:
- Already enabled by default
- Prevents unauthorized domain transfers
- Disable only when you want to transfer domain

**WhoisGuard**:
- Renews annually (free first year, $3-5/year after)
- Keep enabled to protect privacy

### Renewal Settings

**Auto-Renew**:
- ✅ Keep enabled (avoid accidental domain loss)
- Domain expires if not renewed → website goes down
- Namecheap sends renewal reminders 30, 15, 7, 1 day before

**Renewal Price**:
- Year 1: ~$12-15 (often discounted)
- Year 2+: ~$12-15 (regular price)
- Price locked for duration you prepay

**Prepay for Multiple Years** (Optional):
- Lock in current price
- Avoid future price increases
- Renew for 2-5 years at once

### Backup & Documentation

**Record Important Info**:
```
Domain Name: ___________________________
Registrar: Namecheap
Purchase Date: _________________________
Expiration Date: _______________________
Auto-Renew: [✓] Enabled [ ] Disabled
WhoisGuard: [✓] Enabled [ ] Disabled
Nameservers: dns1.registrar-servers.com, dns2.registrar-servers.com
```

**Save These Credentials Securely**:
- Namecheap username/password
- 2FA backup codes
- Domain transfer authorization code (EPP code)

**Use Password Manager**:
- LastPass, 1Password, Bitwarden, Dashlane
- Store all domain credentials
- Enable 2FA on password manager too

---

## Troubleshooting

### Issue: "Domain not resolving after 24 hours"

**Check**:
1. Verify DNS records in Namecheap:
   - Correct type (A vs CNAME)
   - Correct host (@, www, api)
   - Correct values (IPs, subdomains)

2. Clear DNS cache:
   ```bash
   # Windows
   ipconfig /flushdns

   # Mac/Linux
   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
   ```

3. Check TTL:
   - If set to "Automatic", Namecheap uses 30 minutes
   - If set to high value (1 day), old records cached longer

4. Contact Namecheap support:
   - Live chat available 24/7
   - Usually resolve DNS issues quickly

### Issue: "SSL certificate not provisioning"

**Solutions**:
1. Verify DNS fully propagated (use dnschecker.org)
2. SSL won't provision until DNS resolves correctly
3. In Netlify: "Verify DNS configuration" button
4. In Render: Remove and re-add custom domain
5. Wait 4-6 hours total before worrying

### Issue: "Website shows Namecheap parking page"

**Cause**: DNS records not configured or propagating

**Fix**:
1. Check Advanced DNS tab - records present?
2. Wait for propagation (30 min - 2 hours)
3. Clear browser cache (Ctrl+Shift+Delete)
4. Try incognito/private browsing mode

### Issue: "www works but root domain doesn't" (or vice versa)

**Cause**: Missing A record or CNAME record

**Fix**:
1. Verify BOTH records present:
   - A record for @ (root domain)
   - CNAME for www
2. Both should point to Netlify
3. Save changes and wait for propagation

### Issue: "api subdomain shows error"

**Cause**: Incorrect CNAME value or CORS issue

**Fix**:
1. Verify CNAME record:
   - Host: `api`
   - Value: `your-app.onrender.com` (exact URL from Render)
2. Check Render environment variables include your domain in CORS_ORIGINS
3. Test API directly: `https://your-app.onrender.com/api/health`

---

## Cost Summary

### Year 1 Costs
- Domain registration: $12-15
- WhoisGuard (privacy): **FREE** (first year)
- SSL certificate: **FREE** (via Netlify & Render)
- Email forwarding: **FREE** (unlimited forwarders)
- **Total Year 1**: $12-15

### Ongoing Costs (Year 2+)
- Domain renewal: $12-15/year
- WhoisGuard renewal: $3-5/year
- SSL certificate: **FREE** (always via Let's Encrypt)
- Email forwarding: **FREE**
- **Total Year 2+**: $15-20/year

### Optional Costs
- Private Email (Namecheap): +$12/year per mailbox
- Google Workspace: +$72/year per user
- Domain privacy alternatives: $8-12/year
- Premium DNS: $5-10/year (not needed)

---

## Next Steps

### After Domain Setup
1. ✅ Domain purchased and configured
2. ✅ DNS records added (after Netlify/Render deployed)
3. ✅ SSL certificates active
4. → Proceed to: `RENDER_BACKEND_SETUP_GUIDE.md`
5. → Then: `NETLIFY_FRONTEND_SETUP_GUIDE.md`
6. → Finally: Return here to configure DNS (Part 3)

### Quick Reference

**Namecheap Dashboard**: https://ap.www.namecheap.com
**Domain List**: https://ap.www.namecheap.com/domains/list/
**DNS Management**: Domain List → Manage → Advanced DNS

**Support**:
- Live Chat: 24/7 available in dashboard
- Knowledge Base: https://www.namecheap.com/support/knowledgebase/
- Community Forum: https://community.namecheap.com/

---

**Guide Version**: 1.0
**Last Updated**: October 17, 2025
**For**: Westchester County Data Platform
**Next Guide**: RENDER_BACKEND_SETUP_GUIDE.md
