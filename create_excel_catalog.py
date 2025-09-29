"""
Create a sample Excel file with product catalog data
This can be imported directly into Google Sheets
"""

import csv
import json

# Read the CSV data
csv_file = 'sample_product_catalog.csv'
json_file = 'sample_product_catalog.json'

products = []

with open(csv_file, 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        # Convert numeric fields
        product = {
            'ID': row['ID'],
            'Model': row['Model'],
            'Brand': row['Brand'],
            'Airflow_Min': float(row['Airflow Min']),
            'Airflow_Max': float(row['Airflow Max']),
            'Pressure_Min': float(row['Pressure Min']),
            'Pressure_Max': float(row['Pressure Max']),
            'Power': float(row['Power']),
            'Price': float(row['Price']),
            'Currency': row['Currency'],
            'Stock_Status': row['Stock Status'],
            'Delivery_Days': int(row['Delivery Days']),
            'Description': row['Description'],
            'Warranty_Years': int(row['Warranty Years']),
            'Efficiency_Rating': row['Efficiency Rating'],
            'Noise_Level': float(row['Noise Level']),
            'Last_Updated': row['Last Updated']
        }
        products.append(product)

# Save as JSON for easy viewing
with open(json_file, 'w') as file:
    json.dump(products, file, indent=2)

print(f"Created {csv_file} with {len(products)} products")
print(f"Created {json_file} for easy viewing")
print("\nColumn structure:")
print("- ID: Unique product identifier")
print("- Model: Full model name")
print("- Brand: Manufacturer")
print("- Airflow Min/Max: m³/hr capacity range")
print("- Pressure Min/Max: mbar pressure range")
print("- Power: kW rating")
print("- Price: ZAR price")
print("- Currency: Currency code")
print("- Stock Status: in_stock/low_stock/on_order")
print("- Delivery Days: Lead time")
print("- Description: Product description")
print("- Warranty Years: Warranty period")
print("- Efficiency Rating: IE2/IE3/IE4")
print("- Noise Level: dB rating")
print("- Last Updated: Date of last update")
print("\nTo use:")
print("1. Open Google Sheets")
print("2. File → Import → Upload sample_product_catalog.csv")
print("3. Or copy/paste the data directly")