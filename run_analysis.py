#!/usr/bin/env python3
"""
GMC Demand Forecasting Tool - Command Line Version
Run this script instead of the Jupyter notebook if you prefer CLI

Usage:
    python run_analysis.py
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Import our modules
sys.path.append('modules')
from data_loader import GMCReportLoader
from feature_engineering import GMCFeatureEngineer
from elasticity_estimator import ElasticityEstimator
from demand_predictor import DemandPredictor


def main():
    """Main analysis pipeline"""
    
    print("="*80)
    print("GMC DEMAND FORECASTING TOOL")
    print("="*80)
    
    # Setup paths
    DATA_DIR = Path('data/historical')
    OUTPUT_DIR = Path('output')
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Step 1: Load data
    print("\n[1/5] Loading historical data...")
    print("-" * 80)
    
    if not DATA_DIR.exists() or not list(DATA_DIR.glob('*.xlsx')):
        print("❌ ERROR: No Excel files found in data/historical/")
        print("   Please place your GMC reports there and try again.")
        return
    
    loader = GMCReportLoader()
    df_raw = loader.load_multiple_reports(DATA_DIR)
    
    print(f"\n✅ Loaded {len(df_raw)} periods")
    print(f"   Periods: {df_raw['period'].tolist()}")
    
    # Step 2: Engineer features
    print("\n[2/5] Engineering features...")
    print("-" * 80)
    
    engineer = GMCFeatureEngineer()
    df = engineer.engineer_features(df_raw)
    
    print(f"✅ Calculated derived metrics")
    print(f"   Total features: {len(df.columns)}")
    
    # Step 3: Estimate elasticities
    print("\n[3/5] Estimating elasticities...")
    print("-" * 80)
    
    estimator = ElasticityEstimator()
    elasticity_results = estimator.estimate_all(df)
    
    output_file = OUTPUT_DIR / 'elasticities.xlsx'
    estimator.save_results(elasticity_results, str(output_file))
    
    # Step 4: Make predictions
    print("\n[4/5] Predicting demand for next period...")
    print("-" * 80)
    
    current_period = df.iloc[-1]
    next_period_number = int(current_period['period']) + 1
    
    print(f"\nPredicting Period {next_period_number}")
    print(f"Based on data from Period {int(current_period['period'])}")
    
    # Use current period's decisions as baseline
    next_period_decisions = get_default_decisions(current_period)
    
    predictor = DemandPredictor(elasticity_results)
    predictions = predictor.predict_demand(
        current_period,
        next_period_decisions,
        next_period_number
    )
    
    # Display predictions
    print("\n📈 DEMAND FORECAST:\n")
    display_cols = ['product', 'market', 'predicted_demand', 'seasonality_factor', 
                    'price_effect']
    print(predictions[display_cols].to_string(index=False))
    
    # Save predictions
    output_file = OUTPUT_DIR / 'demand_forecast.xlsx'
    predictions.to_excel(output_file, index=False)
    print(f"\n✅ Forecast saved to {output_file}")
    
    # Step 5: Scenario analysis
    print("\n[5/5] Running scenario analysis...")
    print("-" * 80)
    
    scenarios = {
        'price_minus_5pct': {
            'price_p1_eaec': next_period_decisions['price_p1_eaec'] * 0.95,
            'price_p1_eu': next_period_decisions['price_p1_eu'] * 0.95,
            'price_p1_internet': next_period_decisions['price_p1_internet'] * 0.95,
        },
        'price_plus_5pct': {
            'price_p1_eaec': next_period_decisions['price_p1_eaec'] * 1.05,
            'price_p1_eu': next_period_decisions['price_p1_eu'] * 1.05,
            'price_p1_internet': next_period_decisions['price_p1_internet'] * 1.05,
        },
    }
    
    scenario_results = predictor.predict_with_scenarios(
        current_period,
        next_period_decisions,
        scenarios,
        next_period_number
    )
    
    # Show scenario comparison for P1
    print("\n📊 SCENARIO COMPARISON - Product 1:\n")
    p1_scenarios = scenario_results[scenario_results['product'] == 'p1']
    pivot = p1_scenarios.pivot_table(
        index='market',
        columns='scenario',
        values='predicted_demand',
        aggfunc='first'
    )
    print(pivot.to_string())
    
    # Save scenario analysis
    output_file = OUTPUT_DIR / 'scenario_analysis.xlsx'
    scenario_results.to_excel(output_file, index=False)
    print(f"\n✅ Scenario analysis saved to {output_file}")
    
    # Summary
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print("\nOutputs saved to 'output/' folder:")
    print("  • elasticities.xlsx      - Learned coefficients")
    print("  • demand_forecast.xlsx   - Demand predictions")
    print("  • scenario_analysis.xlsx - Sensitivity analysis")
    print("\nNext steps:")
    print("  1. Review elasticities to understand key drivers")
    print("  2. Adjust decisions in get_default_decisions() function")
    print("  3. Re-run analysis to test different strategies")
    print("\n")


def get_default_decisions(current_period: pd.Series) -> pd.Series:
    """
    Define default decisions for next period
    
    Modify these values to test different strategies!
    """
    
    # Start with current period's decisions as baseline
    decisions = current_period.copy()
    
    # Override with your planned changes
    # Example: Adjust prices
    decisions['price_p1_eaec'] = 1100
    decisions['price_p1_eu'] = 1150
    decisions['price_p1_internet'] = 1080
    
    # Example: Adjust advertising
    decisions['img_ad_eaec'] = 75
    decisions['img_ad_eu'] = 75
    decisions['img_ad_internet'] = 80
    
    # Example: Adjust management
    decisions['mgmt_budget'] = 180
    decisions['training_days'] = 35
    
    return decisions


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Analysis interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
