# QUICK SETUP GUIDE

## 📦 Installation (5 minutes)

### Option 1: Using pip (Recommended)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Verify installation
python -c "import pandas, numpy, sklearn; print('✅ All packages installed!')"
```

### Option 2: Using conda

```bash
# 1. Create environment
conda create -n gmc python=3.10
conda activate gmc

# 2. Install packages
pip install -r requirements.txt
```

## 📁 Data Preparation (2 minutes)

1. **Export your GMC reports** to Excel format
   - Go to your GMC dashboard
   - Download management reports for each period
   - Save as `.xlsx` files

2. **Place files** in `data/historical/` folder:
   ```
   data/historical/
   ├── period_1.xlsx
   ├── period_2.xlsx
   ├── period_3.xlsx
   ├── period_4.xlsx
   └── period_5.xlsx
   ```

3. **Minimum requirement**: 3 periods
   **Recommended**: 5-6 periods for accurate predictions

## 🚀 Running the Tool

### Method 1: Jupyter Notebook (Visual, Interactive)

```bash
# Start Jupyter
jupyter notebook

# Open gmc_analyzer.ipynb
# Run all cells (Cell → Run All)
```

### Method 2: Command Line (Fast, Automated)

```bash
# Run the script
python run_analysis.py

# Results appear in output/ folder
```

## 📊 What You'll Get

After running, check the `output/` folder:

1. **elasticities.xlsx**
   - Learned demand coefficients
   - Shows which factors matter most
   - Model quality (R² scores)

2. **demand_forecast.xlsx**
   - Predicted orders for next period
   - Broken down by product and market
   - Shows impact of each factor

3. **scenario_analysis.xlsx**
   - Compare different strategies
   - Price variations
   - Advertising levels

## 🎯 First Time Usage

### Step 1: Learn from History
```bash
python run_analysis.py
```

### Step 2: Review Elasticities
Open `output/elasticities.xlsx` and look for:
- **High R²** (>0.8) = Good model ✅
- **Price elasticity** (-2 to -4 is typical)
- **Strong factors** (high absolute values)

### Step 3: Adjust Decisions
Edit in `run_analysis.py` or Jupyter notebook:
```python
next_period_decisions['price_p1_eaec'] = 1100  # Your strategy
next_period_decisions['mgmt_budget'] = 180
# ... etc
```

### Step 4: Re-run & Compare
```bash
python run_analysis.py
```

## 🔧 Customization

### Change Decisions
Edit `get_default_decisions()` in `run_analysis.py`:
```python
def get_default_decisions(current_period):
    decisions = current_period.copy()
    
    # Your custom strategy here
    decisions['price_p1_eaec'] = 1050  # Lower price
    decisions['img_ad_eaec'] = 90       # More advertising
    
    return decisions
```

### Add Scenarios
Edit the `scenarios` dictionary:
```python
scenarios = {
    'aggressive': {
        'price_p1_eaec': 950,
        'img_ad_eaec': 99,
    },
    'conservative': {
        'price_p1_eaec': 1200,
        'img_ad_eaec': 50,
    },
}
```

## ❓ Troubleshooting

### "No Excel files found"
➜ Put your `.xlsx` reports in `data/historical/` folder

### "Module not found"
➜ Run: `pip install -r requirements.txt`

### "Low R² scores"
➜ Need more historical data (aim for 5+ periods)

### "Predictions seem wrong"
➜ Validate on known period first:
1. Remove last period from `data/historical/`
2. Run analysis
3. Compare predictions to actual results
4. If good match, your model is working!

## 📚 Next Steps

1. ✅ Install packages
2. ✅ Add historical data (3-5 periods minimum)
3. ✅ Run first analysis
4. ✅ Review elasticities
5. ✅ Adjust decisions
6. ✅ Test scenarios
7. ✅ Use in finals!

## 🆘 Need Help?

1. Check `README.md` for detailed documentation
2. Review Jupyter notebook comments
3. Look at example outputs in screenshots
4. Validate data format matches documentation

---

**Ready to analyze! Good luck! 🚀**
