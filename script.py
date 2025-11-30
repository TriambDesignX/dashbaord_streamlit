import pandas as pd
import numpy as np

EXCEL_FILE = 'Environment dummy data.xlsx' 

def safe_read(sheet, header, cols, col_names):
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, header=header)
        df_clean = df.iloc[:, cols].copy()
        df_clean.columns = col_names
        df_clean['Month'] = pd.to_datetime(df_clean['Month'], errors='coerce')
        return df_clean.dropna(subset=['Month'])
    except Exception as e:
        print(f"Skipping {sheet}: {e}")
        return pd.DataFrame()

def main():
    print("Processing all sheets...")
    
    # 1. Load Data Components
    # Production (Row 3 header)
    df_prod = safe_read('Production ', 2, [0, 1], ['Month', 'Production_Pcs'])
    
    # Electricity (Row 4 header) -> Month, Total, Renewable, DG, Bill, DG Cost
    df_elec = safe_read('Electrcity Data', 3, [1, 6, 4, 5, 10, 11], 
                        ['Month', 'Elec_Total_kWh', 'Elec_Renewable_kWh', 'Elec_DG_kWh', 'Cost_Grid', 'Cost_DG'])
    
    # Water (Header Row 5 roughly) -> Month, Fresh, Recycled, Washing
    df_water = pd.read_excel(EXCEL_FILE, sheet_name='Water Data', header=None, skiprows=4)
    df_water = df_water.iloc[:, [0, 4, 7, 8]]
    df_water.columns = ['Month', 'Water_Fresh_KL', 'Water_Recycled_KL', 'Water_Washing_KL']
    df_water['Month'] = pd.to_datetime(df_water['Month'], errors='coerce')
    df_water = df_water.dropna(subset=['Month'])

    # Washing Details (For L/kg metric)
    df_wash = safe_read('Washing Details', 3, [0, 4], ['Month', 'Washing_Kg'])

    # Boilers (Row 3 header)
    df_boiler = safe_read('Boilers', 2, [1, 3, 4, 19], ['Month', 'Fuel_Wood_Kg', 'Fuel_Briquette_Kg', 'Cost_Boiler'])

    # 2. Merge Everything
    print("Merging...")
    df_master = df_prod.merge(df_elec, on='Month', how='outer') \
                       .merge(df_water, on='Month', how='outer') \
                       .merge(df_wash, on='Month', how='outer') \
                       .merge(df_boiler, on='Month', how='outer')

    # 3. Clean Numbers (Fill NaNs with 0)
    num_cols = df_master.columns.drop('Month')
    df_master[num_cols] = df_master[num_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # 4. Calculate Critical KPIs
    # Efficiency
    df_master['KPI_Energy_Pc'] = df_master['Elec_Total_kWh'] / df_master['Production_Pcs']
    df_master['KPI_Water_Pc'] = (df_master['Water_Fresh_KL'] * 1000) / df_master['Production_Pcs']
    
    # Washing Efficiency (Liters / kg of fabric)
    df_master['KPI_Wash_L_kg'] = np.where(df_master['Washing_Kg'] > 0, 
                                          (df_master['Water_Washing_KL'] * 1000) / df_master['Washing_Kg'], 0)

    # Financials
    df_master['Total_Cost'] = df_master['Cost_Grid'] + df_master['Cost_DG'] + df_master['Cost_Boiler']

    # Save
    df_master.sort_values('Month', inplace=True)
    df_master.to_csv('processed_environment_data.csv', index=False)
    print("Done! 'processed_environment_data.csv' created.")

if __name__ == "__main__":
    main()