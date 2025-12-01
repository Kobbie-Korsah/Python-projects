
import os
from fastf1_utils import fetch_fastf1_data, save_to_csv
from api_utils import fetch_jolpica_data

def print_separator(title):
    """Print a formatted section separator"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def main():
    """Main function to orchestrate F1 data fetching and display"""
    
    print_separator("F1 DASHBOARD BETA 1 - CONSOLE VERSION")
    
    # Configuration - Modify these values to fetch different data
    SEASON = 2024
    RACE_NUMBER = 1  # 1 = Bahrain GP (first race of 2024)
    DRIVER_CODE = 'VER'  # Max Verstappen
    
    print(f"\n[CONFIG] Configuration:")
    print(f"   Season: {SEASON}")
    print(f"   Race: Round {RACE_NUMBER}")
    print(f"   Driver: {DRIVER_CODE}")
    
    # Create output directory for CSV files
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"\n[OK] Created output directory: {output_dir}/")
    
    # ========== PART 1: FastF1 Data Fetching ==========
    print_separator("PART 1: FASTF1 TELEMETRY DATA")
    
    try:
        # Fetch session and fastest lap data using FastF1
        fastest_lap_data = fetch_fastf1_data(SEASON, RACE_NUMBER, DRIVER_CODE)
        
        if fastest_lap_data:
            print(f"\n[FASTEST_LAP] Fastest Lap Information:")
            print(f"   Driver: {fastest_lap_data['Driver']}")
            print(f"   Team: {fastest_lap_data['Team']}")
            print(f"   Lap Time: {fastest_lap_data['LapTime']}")
            print(f"   Lap Number: {fastest_lap_data['LapNumber']}")
            print(f"   Speed (I1): {fastest_lap_data['SpeedI1']} km/h")
            print(f"   Speed (I2): {fastest_lap_data['SpeedI2']} km/h")
            print(f"   Speed (FL): {fastest_lap_data['SpeedFL']} km/h")
            print(f"   Speed (ST): {fastest_lap_data['SpeedST']} km/h")
            
            # Save FastF1 data to CSV
            csv_filename = f"{output_dir}/fastf1_{SEASON}_r{RACE_NUMBER}_{DRIVER_CODE}.csv"
            save_to_csv(fastest_lap_data, csv_filename)
            print(f"\n[OK] FastF1 data saved to: {csv_filename}")
        else:
            print("\n[ERROR] Failed to fetch FastF1 data")
    
    except Exception as e:
        print(f"\n[ERROR] Error fetching FastF1 data: {e}")
    
    # ========== PART 2: Jolpica-F1 API Data Fetching ==========
    print_separator("PART 2: JOLPICA-F1 API HISTORICAL DATA")
    
    try:
        # Fetch historical race results from Jolpica-F1 API
        race_results_df = fetch_jolpica_data(SEASON, RACE_NUMBER)
        
        if race_results_df is not None and not race_results_df.empty:
            print(f"\n[RESULTS] Race Results (Top 10):")
            print(f"\n{'Pos':<5} {'Driver':<25} {'Constructor':<20} {'Time/Status':<15}")
            print("-" * 70)
            
            # Display top 10 results in formatted table
            for idx, row in race_results_df.head(10).iterrows():
                print(f"{row['Position']:<5} {row['Driver']:<25} {row['Constructor']:<20} {row['Time']:<15}")
            
            # Save Jolpica API data to CSV
            csv_filename = f"{output_dir}/jolpica_{SEASON}_r{RACE_NUMBER}_results.csv"
            race_results_df.to_csv(csv_filename, index=False)
            print(f"\n[OK] Jolpica API data saved to: {csv_filename}")
            print(f"[OK] Total drivers: {len(race_results_df)}")
        else:
            print("\n[ERROR] Failed to fetch Jolpica API data")
    
    except Exception as e:
        print(f"\n[ERROR] Error fetching Jolpica API data: {e}")
    
    # ========== Summary ==========
    print_separator("DASHBOARD COMPLETE")
    print("\n[OK] Data fetching complete!")
    print(f"[OK] Check the '{output_dir}/' folder for CSV backups")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()