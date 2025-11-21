import requests
import datetime
import pandas as pd
import os
from pathlib import Path

def cleanup_old_files(output_dir, days_threshold=90):
    """
    Delete files older than the specified number of days.
    
    Args:
        output_dir: Path to the output directory
        days_threshold: Number of days (default 90 for 3 months)
    """
    print(f"\nChecking for files older than {days_threshold} days...")
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_threshold)
    files_deleted = 0
    
    for file_path in output_dir.glob('*'):
        if file_path.is_file():
            file_modified = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_modified < cutoff_date:
                print(f"Deleting old file: {file_path.name} (modified: {file_modified.strftime('%Y-%m-%d')})")
                file_path.unlink()
                files_deleted += 1
    
    if files_deleted == 0:
        print("No old files found to delete.")
    else:
        print(f"Deleted {files_deleted} old file(s).")


def fetch_equipment_data(location_id, access_token, endpoint_type='items'):
    """
    Fetch equipment data from LibCal API with pagination.
    
    Args:
        location_id: LibCal location ID
        access_token: OAuth access token
        endpoint_type: Either 'items' or 'status'
    
    Returns:
        List of equipment records
    """
    if endpoint_type == 'items':
        url = f'https://yorku.libcal.com/1.1/equipment/items/{location_id}'
    else:
        url = f'https://yorku.libcal.com/1.1/equipment/items/status/{location_id}'
    
    headers = {'Authorization': f'Bearer {access_token}'}
    page_index = 0
    all_items = []
    
    while True:
        params = {
            'pageSize': 100,
            'visibility': 'admin_only',
            'pageIndex': page_index
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        items = response.json()
        all_items.extend(items)
        
        if len(items) < 100:
            break
        
        page_index += 1
    
    return all_items


def generate_inventory_report():
    """Main function to generate the weekly inventory report."""
    
    # Get configuration from environment variables
    location_id = int(os.environ.get('LIBCAL_LOCATION_ID', '2632'))
    client_id = os.environ.get('LIBCAL_CLIENT_ID')
    client_secret = os.environ.get('LIBCAL_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise ValueError("LIBCAL_CLIENT_ID and LIBCAL_CLIENT_SECRET must be set as environment variables")
    
    # Create output directory if it doesn't exist
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Get today's date for filename
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    print("=" * 80)
    print(f"MMCL Weekly Equipment Inventory Report - {today}")
    print("=" * 80)
    
    # Step 1: Authenticate with LibCal API
    print("\nAuthenticating with LibCal API...")
    auth_url = 'https://yorku.libcal.com/1.1/oauth/token'
    auth_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    
    auth_response = requests.post(auth_url, data=auth_data)
    auth_response.raise_for_status()
    access_token = auth_response.json()['access_token']
    print("Authentication successful!")
    
    # Step 2: Fetch equipment items data
    print("\nFetching equipment items data...")
    items_data = fetch_equipment_data(location_id, access_token, 'items')
    print(f"Retrieved {len(items_data)} items from equipment/items endpoint")
    
    # Step 3: Fetch equipment status data
    print("\nFetching equipment checkout status data...")
    status_data = fetch_equipment_data(location_id, access_token, 'status')
    print(f"Retrieved {len(status_data)} items from equipment/items/status endpoint")
    
    # Step 4: Merge the datasets
    print("\nMerging datasets...")
    
    inventory_df = pd.DataFrame(items_data)
    status_df = pd.DataFrame(status_data)
    
    # Keep only needed columns from status data and rename eid to id
    status_columns = ['eid', 'barcode', 'is_checked_out']
    status_df = status_df[status_columns].copy()
    status_df.rename(columns={'eid': 'id'}, inplace=True)
    
    # Merge on equipment ID
    inventory_df = inventory_df.merge(
        status_df[['id', 'is_checked_out']], 
        on='id', 
        how='left'
    )
    
    # Handle items that didn't match by ID - try barcode match
    missing_status = inventory_df['is_checked_out'].isna()
    if missing_status.any():
        print(f"Warning: {missing_status.sum()} items did not match by ID, attempting barcode match...")
        barcode_status = status_df[['barcode', 'is_checked_out']].copy()
        barcode_status.rename(columns={'is_checked_out': 'is_checked_out_barcode'}, inplace=True)
        
        inventory_df = inventory_df.merge(barcode_status, on='barcode', how='left')
        inventory_df.loc[missing_status, 'is_checked_out'] = inventory_df.loc[missing_status, 'is_checked_out_barcode']
        inventory_df.drop('is_checked_out_barcode', axis=1, inplace=True)
    
    # Fill remaining NaN values with False
    inventory_df['is_checked_out'] = inventory_df['is_checked_out'].fillna(False)
    
    # Convert to readable format
    inventory_df['checkout_status'] = inventory_df['is_checked_out'].apply(
        lambda x: 'CHECKED OUT' if x else 'Available'
    )
    
    print(f"Merge complete. Final inventory has {len(inventory_df)} items")
    print(f"Items checked out: {(inventory_df['is_checked_out'] == True).sum()}")
    print(f"Items available: {(inventory_df['is_checked_out'] == False).sum()}")
    
    # Step 5: Clean up data
    # Drop unnecessary columns
    columns_to_drop = ['created', 'bookId', 'fromDate', 'instructions', 'value', 
                       'replacement_cost', 'formid', 'groupId', 'groupTermsAndConditions', 
                       'locationTermsAndConditions', 'groupName', 'model', 'is_checked_out']
    inventory_df.drop(columns_to_drop, axis=1, inplace=True, errors='ignore')
    
    # Remove HTML tags from damage notes
    inventory_df['damage_notes'] = inventory_df['damage_notes'].replace(r'<[^<>]*>', '', regex=True)
    inventory_df['damage_notes'] = inventory_df['damage_notes'].replace(r'[\r\n|\r|\n|\t]', ' ', regex=True)
    
    # Add DSA Notes column
    inventory_df['DSA_Notes'] = ""
    
    # Select and order final columns
    final_columns = ['name', 'barcode', 'asset_number', 'serial_number', 
                     'checkout_status', 'DSA_Notes', 'damage_notes']
    final_df = inventory_df[final_columns].copy()
    
    # Step 6: Save outputs
    base_filename = f"{today}_Loanable_Inventory"
    
    # Save as CSV
    csv_path = output_dir / f"{base_filename}.csv"
    print(f"\nSaving CSV file: {csv_path}")
    final_df.to_csv(csv_path, index=False)
    
    # Save as Excel with formatting
    excel_path = output_dir / f"{base_filename}.xlsx"
    print(f"Saving Excel file: {excel_path}")
    
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        final_df.to_excel(writer, sheet_name=today, index=False, freeze_panes=(1, 2))
        
        worksheet = writer.sheets[today]
        workbook = writer.book
        
        # Create header format
        header_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'bold': True
        })
        
        # Define column headers
        col_headers = [
            "Item Name",
            "Barcode Number",
            "Asset#",
            "Serial#",
            "Checkout Status",
            "Add Notes Here for Any Issues Found",
            "Current Notes on Damage"
        ]
        
        # Add formatted table
        worksheet.add_table(0, 0, len(final_df), len(col_headers) - 1, {
            'columns': [{'header': header} for header in col_headers],
            'style': 'Table Style Medium 2'
        })
        
        # Apply header formatting
        for i, header in enumerate(col_headers):
            worksheet.write(0, i, header, header_format)
        
        # Auto-fit columns
        worksheet.autofit()
    
    print("\nFiles saved successfully!")
    
    # Step 7: Clean up old files
    cleanup_old_files(output_dir, days_threshold=90)
    
    print("\n" + "=" * 80)
    print("Report generation complete!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        generate_inventory_report()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        raise
