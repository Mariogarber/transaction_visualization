# 💰 Transaction Visualization Dashboard

An interactive web-based dashboard for analyzing financial transaction patterns, detecting suspicious activities, and visualizing money flows across countries and industries.

![Dashboard](https://img.shields.io/badge/Dashboard-Dash-blue.svg) ![Python](https://img.shields.io/badge/Python-3.8+-green.svg) ![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

##  Quick Start

### Docker Deployment (Recommended)
```bash
# Build the Docker image
docker build -t transaction-dashboard .

# Run the container
docker run -d -p 8080:8080 --name transaction-dashboard transaction-dashboard
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start the dashboard
python app.py
```

Access the dashboard at: **http://localhost:8080**

---

##  Overview

The **Transaction Visualization Dashboard** is a comprehensive analytics platform designed for financial crime investigation and transaction pattern analysis. It provides interactive visualizations across multiple domains:

###  Key Features
- **Statistical Analysis**: Transaction distributions, amounts, and temporal patterns
- **Geographical Mapping**: Interactive maps showing transaction flows between countries
- **Industrial Analysis**: Sector-wise transaction breakdown and trends over time
- **Risk Assessment**: Suspicious transaction detection and risk scoring

###  Use Cases
- Financial crime investigation
- Anti-money laundering (AML) analysis
- Transaction pattern discovery
- Cross-border payment monitoring
- Industry sector compliance analysis

---

##  Architecture

The project follows a modular architecture for maintainability and scalability:

```
transaction_visualization/
├── app.py                    # Application entry point
├── core/                     # Core application logic
│   ├── app_factory.py       # Dash app initialization
│   └── config.py            # Configuration settings
├── data/                     # Data management
│   ├── data_manager.py      # Data processing and filtering
│   └── cache/               # Cached datasets
├── layouts/                  # UI page layouts
│   ├── base_layout.py       # Common layout components
│   ├── statistical_layout.py
│   ├── geographical_layout.py
│   ├── industrial_layout.py
│   └── risk_analysis_layout.py
├── callbacks/                # Interactive behavior
│   ├── navigation_callbacks.py
│   ├── statistical_callbacks.py
│   ├── geographical_callbacks.py
│   ├── industrial_callbacks.py
│   └── risk_analysis_callbacks.py
└── visualizations/           # Chart generation
    ├── statistical_plots.py
    ├── geographical_plots.py
    ├── industrial_plots.py
    └── risk_analysis_plots.py
```

---

##  Dashboard Sections

### 1.  Statistical Analysis
- **Transaction Overview**: Volume, amounts, and distribution analysis
- **Temporal Patterns**: Time-based transaction trends
- **Source Analysis**: Legal vs illegal transaction breakdown
- **Interactive Filters**: Date ranges, countries, and transaction types

### 2.  Geographical Analysis
- **Interactive World Map**: Folium-powered geographical visualization
- **Country Markers**: Click for detailed transaction information with pie charts
- **Transaction Flow Maps**: Arrows showing money movement between countries
- **Risk Choropleth**: Color-coded risk assessment by region

### 3.  Industrial Analysis
- **Sector Breakdown**: Transaction analysis by industry
- **Stacked Bar Charts**: Legal vs illegal transactions per industry
- **Time Series Analysis**: Industrial trends over time
- **Normalization Options**: Percentage and absolute value views

### 4.  Risk Analysis
- **Risk Distribution**: Statistical analysis of risk scores
- **Shell Company Detection**: Suspicious entity identification
- **Tax Haven Analysis**: Flow analysis to high-risk jurisdictions
- **Trend Analysis**: Risk pattern evolution over time

---

##  Data Structure

The dashboard processes transaction data with the following schema:

| Column | Type | Description |
|---------|------|-------------|
| `Transaction_ID` | string | Unique transaction identifier |
| `Date` | datetime | Transaction date |
| `Amount (USD)` | float | Transaction amount in USD |
| `Country` | string | Origin country |
| `Destination Country` | string | Destination country |
| `Industry` | string | Industry sector |
| `Transaction Type` | string | Type of transaction |
| `Source of Money` | string | Legal/Illegal classification |
| `Reported by Authority` | boolean | Authority reporting status |
| `Risk_Score` | float | Calculated risk assessment |
| `Latitude/Longitude` | float | Geographical coordinates |

### Data Sources
- Geographical data: World countries GeoJSON with ISO codes
- Transaction records: Processed CSV format
- Risk assessments: Calculated metrics and authority reports

---

##  Technologies

### Backend
- **Python 3.8+**: Core programming language
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **GeoPandas**: Geographical data handling
- **Shapely**: Geometric operations

### Frontend & Visualization
- **Dash**: Web application framework
- **Plotly**: Interactive charts and graphs
- **Folium**: Geographical mapping with markers and popups
- **Dash Bootstrap Components**: Modern UI styling
- **Matplotlib**: Chart generation for embedded visualizations

### Data Processing
- **Caching System**: Improved performance with data caching
- **Multi-format Support**: CSV, GeoJSON data processing
- **Real-time Filtering**: Dynamic data filtering and aggregation

---

##  Features

### Interactive Components
- **Dynamic Navigation**: Multi-section navigation bar
- **Date Range Pickers**: Temporal filtering across all sections
- **Multi-select Dropdowns**: Country and industry filtering
- **Responsive Charts**: Auto-resizing visualizations
- **Loading Indicators**: User feedback during data processing

### Advanced Visualizations
- **Choropleth Maps**: Color-coded geographical analysis
- **Stacked Bar Charts**: Comparative analysis with normalization
- **Time Series Plots**: Temporal trend analysis with moving averages
- **Interactive Legends**: Show/hide data series
- **Popup Charts**: Embedded pie charts in map markers

---

##  Configuration

### Environment Setup
The application supports flexible configuration:
- Port settings (default: 8080)
- Debug mode toggle
- Data directory paths
- Cache management

### Performance Optimization
- **Data Caching**: Automatic caching of processed datasets
- **Lazy Loading**: On-demand data processing
- **Memory Management**: Efficient data structure handling

---

##  Error Handling

The dashboard includes comprehensive error handling:
- **Data Validation**: Schema validation for input data
- **Graceful Degradation**: Fallback options for missing data
- **User Feedback**: Clear error messages and loading states
- **Callback Protection**: Prevention of circular callback dependencies

---

##  Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Kill process on port 8080 (Windows)
netstat -ano | findstr :8080
taskkill /PID <process_id> /F

# Kill process on port 8080 (Linux/Mac)
sudo lsof -ti:8080 | xargs kill -9
```

**Dependencies Issues**
```bash
# Clean install
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

**Data Loading Problems**
- Ensure CSV files match the expected schema
- Check geographical data files are present in data directory
- Verify column names match the DataManager expectations

**Map Display Issues**
- Check Folium HTML generation
- Verify base64 encoding is working for embedded charts
- Ensure popup content is properly formatted

---

## Performance

### Optimization Features
- **Modular Architecture**: Separated concerns for better maintainability
- **Efficient Callbacks**: Minimized unnecessary updates
- **Data Caching**: Reduced processing time for repeated operations
- **Responsive Design**: Optimized for different screen sizes

### Scalability
- **Plugin Architecture**: Easy addition of new analysis modules
- **Configurable Components**: Customizable chart parameters
- **Extensible Data Sources**: Support for multiple data formats

---

##  Migration Notes

This project has been migrated from a monolithic structure to a modular architecture:
- **Version 1.0**: Single `dashboard.py` file
- **Version 2.0**: Modular structure with separated components

### Legacy Files (Deprecated)
- `dashboard.py` - Old monolithic implementation
- `functions/` - Legacy function directory
- `utils/` - Old utility modules
- `refactor.py` - Migration script

---

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---

##  Support

For questions or issues, please open an issue on the repository or contact the development team.

**Dashboard URL**: http://localhost:8080  
**Documentation**: See inline code documentation  
**Version**: 2.0 (Modular Architecture)  
**Last Updated**: January 2026