import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

class GoLiveToAbillityMapper:
    """Transforms raw Salesforce Go Live exports into strict Abillity import CSVs."""
    def __init__(self, mapping_dictionary_path: str):
        # Mock load dictionary
        self.sku_map = {"SF-VOIP-01": "AB-VOIP-CORE", "SF-DATA-100": "AB-FIBER-100"}

    def reconcile_data(self, sf_df: pd.DataFrame) -> pd.DataFrame:
        logging.info(f"Ingested {len(sf_df)} Go Live records. Processing...")
        
        abillity_df = pd.DataFrame()
        abillity_df['Customer_ID'] = sf_df['Account_Number'].astype(str).str.zfill(8)
        abillity_df['Billing_SKU'] = sf_df['SF_Product_Code'].map(self.sku_map)
        abillity_df['Activation_Date'] = pd.to_datetime(sf_df['Go_Live_Date']).dt.strftime('%Y-%m-%d')
        abillity_df['Monthly_Charge'] = sf_df['Contract_Value'] / sf_df['Term_Months']

        # Zero-fault validation
        unmapped = abillity_df['Billing_SKU'].isna().sum()
        if unmapped > 0:
            missing_skus = sf_df[abillity_df['Billing_SKU'].isna()]['SF_Product_Code'].unique()
            logging.error(f"Critical Mapping Failure: {unmapped} records unmapped. SKUs: {missing_skus}")
            raise ValueError("Reconciliation failed. Update mapping dictionary.")
            
        logging.info("Reconciliation successful. Ready for Abillity import.")
        return abillity_df

if __name__ == "__main__":
    mock_sf_data = pd.DataFrame({
        "Account_Number": [10293, 40192],
        "SF_Product_Code": ["SF-VOIP-01", "SF-DATA-100"],
        "Go_Live_Date": ["2026-09-01", "2026-09-15"],
        "Contract_Value": [1200, 2400],
        "Term_Months": [12, 24]
    })
    mapper = GoLiveToAbillityMapper("map.json")
    final_csv = mapper.reconcile_data(mock_sf_data)
    print(final_csv.head())
