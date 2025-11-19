# GMC Demand Tool - Technical Architecture

## Overview

This tool implements a machine learning approach to reverse-engineer the Global Management Challenge demand formula from historical data, then uses the learned model to forecast future demand and optimize decisions.

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                   GMC DEMAND ANALYZER                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐ │
│  │ Data Loader │───▶│   Feature    │───▶│   Elasticity   │ │
│  │             │    │  Engineer    │    │   Estimator    │ │
│  └─────────────┘    └──────────────┘    └────────────────┘ │
│         │                   │                     │          │
│         ▼                   ▼                     ▼          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Historical Database                     │    │
│  │  • 5-6 periods × 9 product-markets                  │    │
│  │  • Your decisions + Results                          │    │
│  │  • Competitor data (prices, quality, market share)   │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                 │
│                            ▼                                 │
│                   ┌────────────────┐                        │
│                   │    Demand      │                        │
│                   │   Predictor    │                        │
│                   └────────────────┘                        │
│                            │                                 │
│                            ▼                                 │
│              ┌──────────────────────────┐                   │
│              │  Outputs                  │                   │
│              │  • Forecasts              │                   │
│              │  • Elasticities           │                   │
│              │  • Scenarios              │                   │
│              └──────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## Methodology

### 1. Data Loading (`data_loader.py`)

**Input**: Excel files with GMC management reports (W sheet format)

**Process**:
- Parses cells A1-A856 from each report
- Extracts:
  - Your decisions (A7-A94)
  - Results (A108-A320)
  - Group data (A332-A856):
    - All 8 companies' market shares
    - Competitor prices, quality ratings
    - Financial metrics

**Output**: Structured DataFrame with all historical periods

### 2. Feature Engineering (`feature_engineering.py`)

**Purpose**: Calculate derived metrics that aren't directly in reports

**Key Calculations**:

#### Quality Scores
```python
Quality = Base (60-200+)
        + MINOR implementations (×6 each)
        + MAJOR implementations (×26 each)
        + Assembly time effect (% × 0.00315)
        + Premium materials (% × 0.0016)
        - Aging (4-10 per period depending on current quality)

Stars = ceil((Quality - 60) / 20)
```

#### Cumulative Effects
```python
# Management Budget: Simple cumulative
MgmtBudget_cum[t] = sum(MgmtBudget[1:t])

# Training: 30% carry-over
Training_cum[t] = Training[t] + 0.3 × Training_cum[t-1]

# Image Advertising: 60% carry-over
ImgAd_cum[t] = ImgAd[t] + 0.6 × ImgAd_cum[t-1]

# Direct Advertising: 30% carry-over
DirAd_cum[t] = DirAd[t] + 0.3 × DirAd_cum[t-1]
```

#### Market Saturation
```python
Saturation[product,market] = sum(MarketShare[company=1:8])
# Affects elasticity: as saturation → 100%, all elasticities → 0
```

### 3. Elasticity Estimation (`elasticity_estimator.py`)

**Core Idea**: The GMC demand formula is multiplicative:
```
Demand = Base × Seasonality × ∏(Factor_Effects)
```

Taking logarithms linearizes it:
```
log(Demand) = log(Base) + log(Seasonality) + Σ(log(Factor_Effects))
```

This becomes a **linear regression problem**!

#### Feature Preparation

For each product-market combination, we create features:

1. **Price Effect** (power law):
   ```
   X_price = elasticity × log(Price / Reference_Price)
   ```

2. **Quality Effect** (logarithmic):
   ```
   X_quality = elasticity × log(Quality)
   ```

3. **Linear Effects** (advertising, management, etc.):
   ```
   X_factor = coefficient × Value
   ```

4. **Market Saturation** (modifier):
   ```
   Effective_Elasticity = Base_Elasticity × (1 - Saturation/100)
   ```

#### Regression Model

```python
# Target variable (log-transformed)
y = log(Actual_Demand + 1)

# Feature matrix
X = [
    log(Price_Ratio),
    log(Quality),
    ImgAd_Cumulative,
    DirAd_Cumulative,
    MgmtBudget_Cumulative,
    Training_Cumulative,
    Premium_Materials_Pct,
    Assembly_Time_Excess,
    Agents_Count,
    Commission_Pct,
    Internet_Ports,
    Website_Dev,
    Backlog_Previous,
    Market_Saturation,
    log(Competitor_Avg_Price)
]

# Fit with regularization to prevent overfitting
model = Ridge(alpha=1.0)
model.fit(X, y)

# Extract coefficients
elasticities = model.coef_
base_demand = exp(model.intercept_)
```

#### Seasonality Extraction

```python
# Residuals in log space = seasonality effect
residuals = y_actual - y_predicted

# Group by quarter
seasonality[quarter] = exp(mean(residuals[quarter]))
```

#### Model Quality

We use **R² (coefficient of determination)** to measure fit:
- R² > 0.9: Excellent (predictions very accurate)
- R² > 0.7: Good (predictions reliable)
- R² > 0.5: Fair (use with caution)
- R² < 0.5: Poor (need more data or different features)

### 4. Demand Prediction (`demand_predictor.py`)

**Input**: 
- Learned elasticities from Step 3
- Current period's historical data
- Your planned decisions for next period

**Process**:

```python
# Start with base
demand = base_demand[product, market]

# Apply seasonality
quarter = (period - 1) % 4 + 1
demand *= seasonality[quarter]

# Apply price effect
price_ratio = your_price / reference_price
price_effect = exp(elasticity_price × log(price_ratio))
demand *= price_effect

# Apply quality effect
quality_effect = exp(elasticity_quality × log(quality))
demand *= quality_effect

# Apply advertising (cumulative with decay)
current_img_ad_cum = current_value + 0.6 × previous_cumulative
img_ad_effect = exp(coefficient × current_img_ad_cum)
demand *= img_ad_effect

# ... repeat for all factors ...

# Apply market saturation adjustment
saturation_penalty = 1 - (market_saturation / 100)
adjusted_elasticities = base_elasticities × saturation_penalty

# Final prediction
predicted_demand = base × seasonality × ∏(all_effects)
```

**Output**: Predicted orders for each of 9 product-market combinations

### 5. Scenario Analysis

**Purpose**: Test "what-if" scenarios

**Method**:
1. Define base case (your current plan)
2. Create variations:
   ```python
   scenarios = {
       'price_minus_5': base with 5% lower prices,
       'high_advertising': base with 99 image ads,
       'premium_quality': base with +20 quality,
   }
   ```
3. Predict demand for each scenario
4. Compare results side-by-side

## Key Formulas from Documentation

### Price Elasticity
```
Demand_change% = Elasticity × Price_change%

Typical values:
- EAEC: -3.2 to -6.4
- EU: -5.0 to -6.4
- Internet: -2.2 to -3.8

More negative = More price-sensitive
```

### Quality (R&D)
```
Quality_Points = 60 (base)
                + 6 × MINOR_count
                + 26 × MAJOR_count (6 on receipt + 20 on implementation)
                - Aging (4-10 per period)

Effect on demand: logarithmic
Each +10 quality points ≈ +2-3% demand
```

### Image Advertising
```
Effect on demand = Coefficient × Cumulative_Spending

Cumulative[t] = Current[t] + 0.6 × Cumulative[t-1]

Coefficients (typical):
- EAEC: 0.0014
- EU: 0.0014
- Internet: 0.0028 (2× effect)

60% of previous period's spending continues to work
```

### Direct Advertising
```
Effect on demand = Coefficient × Cumulative_Spending

Cumulative[t] = Current[t] + 0.3 × Cumulative[t-1]

Coefficient: ~0.0056 (same for all markets)

30% carry-over effect
```

### Management Budget
```
Effect: Power function (diminishing returns)

Cumulative[t] = sum(Spending[1:t])

Effect saturates around 180-200 per period
Strong cumulative benefit
```

### Training
```
Effect: Power function

Cumulative[t] = Current[t] + 0.3 × Cumulative[t-1]

Reduces defects, improves hiring
30% carry-over
```

### Premium Materials
```
Effect: Linear

Demand_change% = Coefficient × Material_Pct

Coefficients vary by product-market:
- Strongest on EU market
- Weakest on Internet
- Product 1 > Product 3 > Product 2
```

### Assembly Time
```
Effect: Power function (diminishing returns)

Assembly_Pct = (Actual_Time / Standard_300min) × 100

Optimal range: 110-125%
Beyond 130%: Diminishing returns
Cost: Assembler wages × extra time
```

### Market Saturation
```
Saturation = sum(Market_Share[all_8_companies])

Elasticity_Adjustment = Base_Elasticity × (1 - Saturation/100)

As saturation → 100%, all elasticities → 0
Market becomes "full" and unresponsive to changes
```

## Validation Strategy

### Holdout Testing
1. Remove last historical period
2. Train on periods 1-4
3. Predict period 5
4. Compare predictions to actual results
5. Calculate accuracy metrics

### Cross-Validation
1. Train on periods 1-3, test on period 4
2. Train on periods 1-4, test on period 5
3. Average accuracy across tests

### Good Predictions Should Have:
- R² > 0.7 in training
- Predictions within ±15% of actual
- Correct directional effects (price ↓ → demand ↑)

## Limitations & Assumptions

### Assumptions
1. **Elasticities are stable** across periods within same scenario
2. **Linear relationships** in log space (multiplicative in normal space)
3. **Competitors don't react** strategically to your decisions
4. **No structural breaks** (game rules don't change mid-game)

### Limitations
1. **Need historical data**: Minimum 3 periods, ideally 5-6
2. **Scenario-specific**: Elasticities learned from one scenario may not apply to another
3. **No R&D tracking**: Can't see hidden MAJOR implementations in history
4. **Competitor uncertainty**: Don't know their future decisions

### Edge Cases
1. **New product launches**: No historical data
2. **Market disruptions**: Competitors dumping inventory
3. **Extreme decisions**: Outside range of historical data
4. **Collusion**: Coordinated competitor actions

## Performance Optimization

### For Speed
- Cache loaded data between runs
- Vectorize calculations (NumPy operations)
- Parallel processing for 9 product-markets

### For Accuracy
- More historical periods (5-6 optimal)
- Diverse decision patterns in history
- Track R&D implementations manually if needed
- Account for competitor behavior patterns

## Future Enhancements

### Planned Features
1. **Price Optimizer**: Find profit-maximizing prices given constraints
2. **Goodwill Optimizer**: Optimize for investment attractiveness
3. **Production Planner**: Match production to predicted demand
4. **Competitor Predictor**: Forecast competitor actions
5. **Monte Carlo Simulation**: Confidence intervals for predictions

### Advanced Analytics
- Time series forecasting (ARIMA/Prophet)
- Neural networks for non-linear effects
- Bayesian optimization for decision search
- Multi-objective optimization (profit + market share + goodwill)

---

**Built for GMC Finals 2025** 🏆
