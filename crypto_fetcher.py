import requests
import pandas as pd
import os
import time
from datetime import datetime

def fetch_crypto_data(max_retries=3):
    """
    Fetch cryptocurrency data from CoinGecko API with retry mechanism
    """
    API_URL = "https://api.coingecko.com/api/v3/coins/markets"
    PARAMS = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    
    for attempt in range(max_retries):
        try:
            print(f"API fetch attempt {attempt+1}/{max_retries}")
            response = requests.get(API_URL, params=PARAMS)
            print(f"API Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Successfully fetched data for {len(data)} cryptocurrencies")
                return data
            elif response.status_code == 429:
                print("Rate limit exceeded, waiting before retry...")
                time.sleep(60)  # Wait a minute before retrying
            else:
                print(f"Error fetching data: {response.status_code}")
                print(f"Response content: {response.text[:200]}...")  # Print first 200 chars
                time.sleep(5)  # Brief pause before retry
        except Exception as e:
            print(f"Exception during API fetch: {str(e)}")
            time.sleep(5)  # Brief pause before retry
    
    print("All API fetch attempts failed")
    return None

def save_to_excel(data, directory="data"):
    """
    Save cryptocurrency data to Excel with date in filename
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Get current date for filename
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"crypto_data_{today}.xlsx"
        file_path = os.path.join(directory, filename)
        
        print(f"Preparing to save data to {file_path}")
        
        # Create DataFrame and select relevant columns
        df = pd.DataFrame(data)
        columns_to_keep = [
            'id', 'symbol', 'name', 'current_price', 'market_cap', 
            'total_volume', 'price_change_percentage_24h'
        ]
        
        # Make sure all required columns exist in the data
        for col in columns_to_keep:
            if col not in df.columns:
                print(f"Warning: Column '{col}' not found in API response")
                columns_to_keep.remove(col)
        
        df = df[columns_to_keep]
        
        # Add timestamp column
        df['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to Excel
        df.to_excel(file_path, index=False)
        
        # Verify file was created
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ Excel file created successfully: {file_path} ({file_size} bytes)")
            return file_path
        else:
            print(f"❌ Failed to create Excel file at {file_path}")
            return None
    except Exception as e:
        print(f"❌ Error saving to Excel: {str(e)}")
        return None

def main():
    """
    Main function to fetch and save cryptocurrency data
    """
    print("🚀 Starting cryptocurrency data fetching process...")
    
    # Fetch data from API
    data = fetch_crypto_data()
    
    if not data or len(data) == 0:
        print("❌ No data retrieved from API. Exiting.")
        return
    
    # Save data to Excel
    excel_path = save_to_excel(data)
    
    if excel_path:
        print(f"✅ Process completed successfully. Data saved to {excel_path}")
    else:
        print("❌ Process failed to save data.")

if __name__ == "__main__":
    main()
