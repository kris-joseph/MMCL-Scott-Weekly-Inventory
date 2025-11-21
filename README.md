# MMCL Weekly Equipment Inventory Report

Automated weekly inventory report generator for York University's Making & Media Creation Lab (MMCL). This script fetches equipment data from LibCal's API, merges availability status, and generates Excel and CSV reports.

The automatially-scheduled should will create datestamped files in the `output/` directory.

## Features

- 🤖 **Automated Weekly Reports**: Runs every Friday at 9:00 AM EST via GitHub Actions
- 📊 **Dual Format Output**: Generates both Excel (.xlsx) and CSV files
- 🔄 **Checkout Status Tracking**: Shows which items are checked out vs. available
- 🧹 **Automatic Cleanup**: Deletes reports older than 3 months
- 🔒 **Secure Credentials**: Uses GitHub Secrets for API credentials

## How It Works

### Schedule

The workflow runs automatically:
- **Every Friday at 9:00 AM EST** (1:00 PM UTC)
- Can also be triggered manually from the Actions tab

### Process

1. **Authentication**: Connects to LibCal API using OAuth credentials
2. **Data Collection**: 
   - Fetches complete equipment list from `/equipment/items/{id}`
   - Fetches checkout status from `/equipment/items/status/{id}`
3. **Data Merge**: Combines both datasets using equipment ID and barcode
4. **Report Generation**: Creates formatted Excel and CSV files
5. **Cleanup**: Removes reports older than 90 days
6. **Commit**: Pushes reports to the repository

### Output Files

Reports are saved in the `output/` directory with filenames like:
- `2024-11-22_Loanable_Inventory.xlsx`
- `2024-11-22_Loanable_Inventory.csv`

Each report includes:
- Item Name
- Barcode Number
- Asset Number
- Serial Number
- **Checkout Status** (CHECKED OUT / Available)
- DSA Notes (empty column for manual annotation)
- Current Notes on Damage

## Local Development

To run the script locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export LIBCAL_CLIENT_ID="your_client_id"
export LIBCAL_CLIENT_SECRET="your_client_secret"
export LIBCAL_LOCATION_ID="2632"

# Run the script
python generate_inventory.py
```

## Troubleshooting

### Workflow Not Running

1. Check that GitHub Actions is enabled for your repository
2. Verify the workflow file is in `.github/workflows/`
3. Check the Actions tab for any error messages

### Authentication Errors

1. Verify your secrets are set correctly in repository settings
2. Ensure the client ID and secret are valid and active in LibCal
3. Check that the API credentials haven't expired

### Missing Data

1. Verify the `LIBCAL_LOCATION_ID` matches your LibCal location
2. Check that the API account has appropriate permissions
3. Review the workflow logs in the Actions tab for specific errors

### No Files Committed

The workflow only commits files if there are changes. If the inventory hasn't changed since the last run, no new commit will be created. The reports are still generated and available as workflow artifacts.

## Customization

### Change Schedule

Edit the cron expression in `.github/workflows/weekly-inventory.yml`:

```yaml
schedule:
  - cron: '0 13 * * 5'  # Current: Friday at 1:00 PM UTC
```

Cron format: `minute hour day-of-month month day-of-week`

Examples:
- `0 13 * * 1`: Monday at 1:00 PM UTC
- `0 13 * * 1,5`: Monday and Friday at 1:00 PM UTC
- `30 14 * * 5`: Friday at 2:30 PM UTC

### Change Retention Period

Modify the `days_threshold` parameter in `generate_inventory.py`:

```python
cleanup_old_files(output_dir, days_threshold=90)  # Change 90 to desired days
```

### Change Location

Update the `LIBCAL_LOCATION_ID` variable in your repository settings, or modify the default in the script.

## API Documentation

This project uses Springshare's LibCal API 1.1:
- Equipment Items: `/equipment/items/{id}`
- Equipment Status: `/equipment/items/status/{id}`

For more information, see the LibCal API documentation in your LibCal admin interface.

## Support

For issues or questions:
1. Check the Actions tab for workflow run logs
2. Review the troubleshooting section above
3. Consult LibCal API documentation
4. Contact MMCL technical staff

## License

Internal use for York University Libraries' Making & Media Creation Lab.
