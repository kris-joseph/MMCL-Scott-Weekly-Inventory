# Quick Setup Guide for MMCL Weekly Inventory

## Prerequisites
- GitHub account with access to create repositories
- LibCal API credentials (client_id and client_secret)
- LibCal location ID (default: 2632 for Scott MCL)

## Step-by-Step Setup

### 1. Create GitHub Repository

```bash
# On GitHub.com, create a new repository named "mmcl-weekly-inventory"
# Clone it to your local machine
git clone https://github.com/YOUR-USERNAME/mmcl-weekly-inventory.git
cd mmcl-weekly-inventory
```

### 2. Add Project Files

Copy all files from this package into your repository:
- `generate_inventory.py`
- `requirements.txt`
- `README.md`
- `.gitignore`
- `.github/workflows/weekly-inventory.yml`

```bash
# Commit and push the files
git add .
git commit -m "Initial commit: Weekly inventory automation"
git push origin main
```

### 3. Configure Secrets and Variables

#### On GitHub.com:

1. Navigate to your repository
2. Click **Settings** → **Secrets and variables** → **Actions**

3. Add **Repository secrets**:
   - Click "New repository secret"
   - Name: `LIBCAL_CLIENT_ID`
   - Value: `193` (or your client ID)
   - Click "Add secret"
   
   - Click "New repository secret"
   - Name: `LIBCAL_CLIENT_SECRET`
   - Value: `your_secret_here`
   - Click "Add secret"

4. Add **Repository variable**:
   - Click on "Variables" tab
   - Click "New repository variable"
   - Name: `LIBCAL_LOCATION_ID`
   - Value: `2632` (or your location ID)
   - Click "Add variable"

### 4. Test the Workflow

1. Go to **Actions** tab in your repository
2. Click on "Weekly Equipment Inventory Report"
3. Click **Run workflow** dropdown
4. Click the green **Run workflow** button
5. Wait for the workflow to complete (usually 1-2 minutes)
6. Check the **output/** directory in your repository for the generated files

### 5. Verify Automation

The workflow will now run automatically every Friday at 9:00 AM EST.

You can check upcoming runs:
1. Go to **Actions** tab
2. Click on "Weekly Equipment Inventory Report"
3. View scheduled runs in the workflow history

## Troubleshooting

### Workflow fails with authentication error
- Double-check that secrets are spelled correctly (case-sensitive)
- Verify credentials work by testing locally
- Ensure API credentials haven't expired in LibCal

### No output files generated
- Check the workflow logs for Python errors
- Verify location ID is correct
- Ensure the LibCal API is accessible

### Files not appearing in repository
- The workflow commits files automatically
- If inventory hasn't changed, no new commit is made
- Check Actions artifacts for the generated files

### Need help?
- Review the detailed README.md
- Check workflow logs in the Actions tab
- Verify all prerequisites are met

## Next Steps

Once setup is complete:
- Monitor the first few automated runs
- Adjust schedule if needed (edit `.github/workflows/weekly-inventory.yml`)
- Customize retention period if desired (edit `generate_inventory.py`)
- Add additional maintainers to the repository

## Location IDs Reference

Common MMCL locations:
- Scott Library MCL: 2632
- Markham MCL: [add if needed]

To find your location ID:
1. Log into LibCal admin
2. Go to Equipment module
3. Location ID is visible in the admin interface URL or settings
