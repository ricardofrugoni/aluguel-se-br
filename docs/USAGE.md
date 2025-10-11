# 📖 Usage Guide

## Dashboard Overview

The interactive dashboard provides:

- 🌍 **3D Globe**: Rotate and explore properties
- 📊 **Price Analysis**: Seasonal patterns and trends
- 🎯 **Property Details**: Click for detailed analysis
- 📈 **Comparisons**: City vs city, season vs season

## Getting Started

### 1. Launch Dashboard
```bash
streamlit run dashboard/globe_app.py
```

### 2. Navigate Interface

**Sidebar Controls:**
- 🏙️ **Cities**: Select São Paulo, Rio de Janeiro, or both
- 💰 **Price Range**: Filter by price (R$/night)
- 🏠 **Property Types**: Entire home, Private room, Shared room

**Main Interface:**
- 🌍 **3D Globe**: Interactive map with property locations
- 📊 **Price Distribution**: Histogram of prices
- 📅 **Seasonal Analysis**: Detailed temporal patterns

### 3. Explore Properties

**Globe Interaction:**
- 🖱️ **Drag**: Rotate the globe
- 🔍 **Scroll**: Zoom in/out
- 👆 **Click**: Select property for analysis

**Property Analysis:**
- 📈 **Seasonal Chart**: Price variations by month
- 💡 **Insights**: Recommendations and patterns
- 🎯 **Metrics**: High season vs regular season

## Features

### 🌍 3D Globe
- **Rotation**: 360° view of properties
- **Zoom**: Focus on specific areas
- **Colors**: Price-based color coding
- **Hover**: Quick property preview

### 📊 Price Analysis
- **Seasonal Patterns**: Monthly price variations
- **Percentages**: Relative changes from base price
- **Discrepancy Flags**: High/Moderate/Low seasonality
- **Savings Calculator**: Potential savings by avoiding high season

### 🎯 Property Selection
- **Random Selection**: Discover new properties
- **Detailed Metrics**: Comprehensive property information
- **Seasonal Insights**: When to book for best prices
- **Recommendations**: Smart booking advice

## Data Interpretation

### Price Categories
- 🟢 **Budget**: < R$150/night
- 🟡 **Mid-Range**: R$150-300/night
- 🟠 **High-End**: R$300-500/night
- 🔴 **Luxury**: > R$500/night

### Seasonality Levels
- 🔥🔥🔥 **EXTREME**: >50% price variation
- 🔥🔥 **HIGH**: 30-50% variation
- 🔥 **MODERATE**: 15-30% variation
- ✅ **LOW**: <15% variation

### Seasonal Patterns

**Rio de Janeiro:**
- **Peak**: December-February (Summer + Holidays)
- **Events**: Carnival (+60% premium)
- **Low**: June-August (Winter)
- **Best Value**: May, September

**São Paulo:**
- **Peak**: January, July, December (Holidays)
- **Stable**: Less seasonal variation
- **Low**: March-June, August-October
- **Best Value**: April, October

## Tips for Best Experience

### 🎯 Property Selection
1. **Use Filters**: Narrow down by city, price, type
2. **Random Discovery**: Click "🎲 Random Property"
3. **Compare Cities**: Toggle between SP and RJ
4. **Price Ranges**: Explore different budget levels

### 📊 Analysis Deep Dive
1. **Seasonal Charts**: Look for patterns
2. **Discrepancy Flags**: Identify high-variation properties
3. **Savings Calculator**: Find potential deals
4. **Monthly Breakdown**: Plan optimal booking times

### 🔍 Globe Navigation
1. **Start Centered**: Default view shows both cities
2. **Zoom In**: Focus on specific neighborhoods
3. **Color Coding**: Green = cheap, Red = expensive
4. **Click Points**: Get detailed property analysis

## Advanced Usage

### Custom Analysis
- **Export Data**: Download filtered results
- **Custom Filters**: Modify price ranges and types
- **Seasonal Comparison**: Compare high vs regular season
- **City Comparison**: SP vs RJ patterns

### Integration
- **API Access**: Use data processing modules
- **Custom Models**: Train on your own data
- **Extensions**: Add new features and visualizations

## Troubleshooting

### Common Issues

**Dashboard Won't Load:**
```bash
# Check if Streamlit is running
streamlit --version

# Restart dashboard
streamlit run dashboard/globe_app.py
```

**No Data Showing:**
```bash
# Check if sample data exists
ls data/processed/sample_data.csv

# Recreate samples
python scripts/prepare_sample.py
```

**Performance Issues:**
- Reduce sample size in filters
- Close other applications
- Use sample data only

## Support

- 📧 **Email**: ricardo@example.com
- 🐛 **Issues**: GitHub Issues
- 📖 **Documentation**: [Full Docs](docs/)
- 💬 **Discussions**: GitHub Discussions
