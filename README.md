# GMC Demand Forecasting Tool

A sophisticated tool to analyze Global Management Challenge reports, learn demand elasticities, and predict future demand.

## 🎯 What It Does

1. **Learns from your history** - Analyzes 5-6 historical periods to reverse-engineer the demand formula
2. **Predicts demand** - Forecasts orders for next period based on your planned decisions
3. **Tests scenarios** - Compare different strategies (price changes, advertising levels, etc.)
4. **Provides insights** - Shows which factors drive demand in your specific scenario

## 📁 Project Structure

```
gmc_tool/
├── gmc_analyzer.ipynb          # Main notebook (START HERE)
├── modules/
│   ├── data_loader.py          # Parses Excel reports
│   ├── feature_engineering.py  # Calculates derived metrics
│   ├── elasticity_estimator.py # Learns elasticities via regression
│   └── demand_predictor.py     # Forecasts demand
├── data/
│   └── historical/             # PUT YOUR EXCEL REPORTS HERE
│       ├── period_1.xlsx
│       ├── period_2.xlsx
│       └── ...
└── output/                     # Results saved here
    ├── elasticities.xlsx
    ├── demand_forecast.xlsx
    └── scenario_analysis.xlsx
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pandas numpy openpyxl scikit-learn matplotlib seaborn jupyter
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

### 2. Prepare Your Data

- Export your GMC management reports to Excel format
- Place them in `data/historical/` folder
- Name them clearly (e.g., `period_1.xlsx`, `period_2.xlsx`, etc.)
- **You need at least 3-5 historical periods for good results**

### 3. Run the Notebook

```bash
jupyter notebook gmc_analyzer.ipynb
```

Then run all cells (Cell → Run All)

## 📊 Understanding the Output

### Elasticities Sheet
Shows how demand responds to each factor:
- **Negative price effect** = Lower price → Higher demand ✅
- **Positive quality effect** = Better quality → Higher demand ✅
- **R²** = Model fit quality (0.7+ is good, 0.9+ is excellent)

### Demand Forecast
Predictions for next period broken down by:
- Base demand (inherent market size)
- Seasonality factor (quarterly variations)
- Price effect (your price vs. optimal)
- Quality effect (R&D impact)
- Advertising effect (image + direct)
- Total predicted orders

### Scenario Analysis
Compare different strategies side-by-side:
- Base case (your planned decisions)
- Price variations (±5%, ±10%)
- Advertising variations (high/low)
- Custom scenarios you define

## 🎓 How It Works

### The Demand Formula

Based on GMC documentation, demand follows this structure:

```
Demand = Base_Demand × Seasonality × ∏(Factor_Effects)

Where factors include:
- Prices (power law with elasticity)
- Quality / R&D (logarithmic)
- Advertising (linear with cumulative effects)
- Management budget (cumulative)
- Training (30% carry-over)
- Premium materials
- Assembly time
- Agents & Distributors
- Internet infrastructure
- Market saturation (reduces all elasticities)
```

### Learning Process

1. **Feature Engineering**: Calculate all derived metrics
   - Cumulative advertising (60% image, 30% direct carry-over)
   - Quality scores from R&D implementations
   - Market saturation levels

2. **Regression**: Use multi-variable regression to find coefficients
   - Log-transform to linearize multiplicative effects
   - Ridge regularization to prevent overfitting
   - Separate model for each product-market (9 total)

3. **Validation**: Check R² scores
   - R² > 0.7 = Good model
   - R² > 0.9 = Excellent model
   - R² < 0.5 = Need more data or different factors

## 💡 Tips for Best Results

### Data Quality
- ✅ **DO**: Include diverse decision variations in history
- ✅ **DO**: Have at least 5 periods of data
- ❌ **DON'T**: Use periods with major R&D implementations without tracking them
- ❌ **DON'T**: Mix different scenarios in the same dataset

### Interpreting Results
- **High price elasticity** (-2.0 to -4.0) = Very price-sensitive market
- **Low price elasticity** (-0.5 to -1.0) = Price doesn't matter as much
- **Strong advertising effect** = Invest more in ads
- **Weak advertising effect** = Focus on price/quality instead

### Decision Making
1. Start with base predictions
2. Test ±10% price variations
3. Look for "sweet spots" where profit is maximized
4. Consider competitor reactions (prices from group data)
5. Account for production constraints

## 🔧 Customization

### Modify Decisions (Step 4 in notebook)
Edit the `next_period_decisions` dictionary:
```python
next_period_decisions = pd.Series({
    'price_p1_eaec': 1100,  # Change prices
    'img_ad_eaec': 75,      # Change advertising
    'mgmt_budget': 180,     # Change management budget
    # ... etc
})
```

### Add Custom Scenarios (Step 5)
```python
scenarios = {
    'aggressive_pricing': {
        'price_p1_eaec': 950,
        'price_p1_eu': 1000,
    },
    'premium_strategy': {
        'price_p1_eaec': 1300,
        'quality_p1': 150,  # Assumes R&D investment
    }
}
```

## 🐛 Troubleshooting

### "No data available for orders_pX_market"
- Check that your Excel files have values in cells A131-A139
- Verify files are in correct format (W sheet structure)

### Low R² scores (< 0.5)
- Need more historical periods (aim for 5-6)
- Check if there are missing values in key cells
- Verify data quality (no corrupted files)

### Predictions seem off
- Validate against known period: Input historical decisions, compare to actual
- Check seasonality factors (should vary by quarter)
- Verify cumulative effects are calculating correctly

### Module import errors
```bash
# Make sure you're in the correct directory
cd gmc_tool
jupyter notebook gmc_analyzer.ipynb
```

## 📝 Adding New Periods

After each game period:

1. Export new period report to Excel
2. Add to `data/historical/` folder
3. Re-run the notebook
4. Elasticities will update automatically with new data

## 🎯 Finals Strategy

### Before Finals
1. Run tool on all available practice data
2. Document learned elasticities
3. Test predictions against holdout period
4. Prepare decision templates for each period

### During Finals
1. Quick analysis after each period result
2. Update forecasts for next period
3. Run scenario analysis for key decisions
4. Focus on factors with highest elasticities

## 📚 Advanced Features

### Price Optimization (Coming Soon)
Find optimal prices that:
- Maximize profit given production capacity
- Match target sales volume
- Consider competitor reactions

### Goodwill Optimization (Coming Soon)
Optimize decisions for:
- Investment attractiveness
- All 8 goodwill factors
- Financial strategy (dividends, shares)

## 🤝 Support

For issues or questions:
1. Check troubleshooting section
2. Review cell outputs for error messages
3. Verify data format matches documentation

## 📄 License

This tool is for educational and competitive use in Global Management Challenge.

---

**Good luck in the finals! 🏆**
