#!/usr/bin/env python
"""
Script to generate demo data directly without going through the API.
Usage: python generate_demo_data_en.py
"""

import os
import sys
import django
import yaml
import zipfile
import io
from datetime import datetime

# Django configuration
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fundraising_generator.services.generator import FundraisingDataGenerator

def main():
    print("🚀 Generating demo data...")
    print("=" * 60)
    import sys
    sys.stdout.flush()
    
    # Load configuration
    config_path = 'demo_config_en.yml'
    if not os.path.exists(config_path):
        print(f"❌ Error: {config_path} not found")
        sys.exit(1)
    
    print(f"📄 Loading configuration: {config_path}")
    sys.stdout.flush()
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    print("   ✓ Configuration loaded")
    sys.stdout.flush()
    
    # Generate data
    print("\n🔄 Generating...")
    print("   → Initializing generator...")
    sys.stdout.flush()
    generator = FundraisingDataGenerator(config_data)
    print("   ✓ Generator initialized")
    print("   → Starting data generation (this may take a few minutes)...")
    sys.stdout.flush()
    transactions, contacts = generator.generate()
    print("   ✓ Data generation completed")
    sys.stdout.flush()
    
    print(f"✓ {len(transactions):,} transactions generated")
    print(f"✓ {len(contacts):,} contacts generated")
    
    # Create output directory with timestamp
    print("\n📦 Creating output directory...")
    current_ts = datetime.now()
    timestamp_label = current_ts.strftime('%Y-%m-%d %H:%M')
    timestamp_safe = current_ts.strftime('%Y-%m-%d_%H-%M')
    output_dir = os.path.join('demo_output', timestamp_safe)
    os.makedirs(output_dir, exist_ok=True)
    print(f"✓ Output directory created: {output_dir}")
    
    # Create ZIP file
    print("\n📦 Creating ZIP file...")
    zip_filename = os.path.join(output_dir, f'demo_data_en_{timestamp_safe}.zip')
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Import Salesforce mapper
        from fundraising_generator.services.salesforce_mapper import export_to_salesforce_format
        
        # Add transactions (Salesforce NPC format)
        transactions_sf = export_to_salesforce_format(transactions, data_type='transactions')
        transactions_csv = transactions_sf.to_csv(index=False).encode('utf-8')
        zip_file.writestr(f'Gift_Transaction_{timestamp_safe}.csv', transactions_csv)
        
        # Add contacts (Salesforce NPC format)
        contacts_sf = export_to_salesforce_format(contacts, data_type='contacts')
        contacts_csv = contacts_sf.to_csv(index=False).encode('utf-8')
        zip_file.writestr(f'Contact_{timestamp_safe}.csv', contacts_csv)
        
        # Also include original format for backward compatibility
        transactions_csv_orig = transactions.to_csv(index=False).encode('utf-8')
        zip_file.writestr(f'transactions_{timestamp_safe}.csv', transactions_csv_orig)
        
        contacts_csv_orig = contacts.to_csv(index=False).encode('utf-8')
        zip_file.writestr(f'contacts_{timestamp_safe}.csv', contacts_csv_orig)
    
    # Save ZIP file
    with open(zip_filename, 'wb') as f:
        f.write(zip_buffer.getvalue())
    
    print(f"✓ File created: {zip_filename}")
    print(f"✓ Size: {os.path.getsize(zip_filename) / 1024:.1f} KB")
    
    # Create symbolic link for easier use (in root directory)
    root_link = 'demo_data_en.zip'
    # Use lexists to detect broken symlinks as well
    if os.path.lexists(root_link):
        os.remove(root_link)
    os.symlink(os.path.abspath(zip_filename), root_link)
    print(f"✓ Link created: {root_link} -> {zip_filename}")
    
    print("\n✅ Generation complete!")
    print(f"\n📊 You can now analyze the data with:")
    print(f"   python demo_analysis_en.py {zip_filename}")
    print(f"   or")
    print(f"   python demo_analysis_en.py {root_link}")
    
    return zip_filename, timestamp_label, timestamp_safe

if __name__ == '__main__':
    zip_filename, timestamp_label, timestamp_safe = main()
    # Print timestamp for use by other scripts
    print(f"\n📅 Timestamp: {timestamp_label} (folder: {timestamp_safe})")

