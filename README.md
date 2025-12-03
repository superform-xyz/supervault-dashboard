# SuperVault Manager Dashboard

Internal monitoring and metrics dashboard for SuperVaults, built on top of the Superman Pricing API.

## Features

- **PPS Monitoring**: Real-time Price Per Share tracking with staleness indicators and expiration alerts
- **Allocation Breakdown**: Visual breakdown of assets across yield sources (active vs idle)
- **Vault Details**: Comprehensive vault information including addresses, assets, and status
- **Fee Tracking**: Performance fees, management fees, HWM PPS, and unrealized profit
- **Upkeep Monitoring**: UP token balance status for automation payments
- **Multi-chain Support**: Switch between Ethereum and Base networks

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/superform-xyz/supervault-dashboard.git
cd supervault-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the environment example and configure:
```bash
cp .env.example .env
```

4. Run the application:
```bash
python app.py
```

5. Open your web browser and navigate to `http://localhost:8050`

## Project Structure

```
supervault-dashboard/
├── app.py                  # Main application entry point
├── requirements.txt        # Dependencies
├── .env.example            # Environment configuration template
│
├── assets/                 # Static assets
│   ├── custom.css          # Custom styling
│   └── clipboard.js        # Copy-to-clipboard functionality
│
├── components/             # Reusable Dash components
│   ├── pps_chart.py        # PPS visualization with health status
│   ├── vault_details.py    # Vault details card
│   ├── tvl_breakdown.py    # Allocation breakdown chart and table
│   └── status_cards.py     # Fees and upkeep cards
│
├── api/                    # API client code
│   └── client.py           # Superman Pricing API wrapper with caching
│
├── layouts/                # Page layouts
│   └── dashboard.py        # Main dashboard layout and callbacks
│
└── utils/                  # Utility functions
    ├── formatters.py       # Data formatting helpers
    ├── constants.py        # App constants and explorer URLs
    └── config.py           # Environment configuration
```

## API Endpoints

The dashboard consumes the Superman Pricing API:

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/vaults` | List all SuperVaults (addresses, names, symbols) |
| `GET /api/v1/vault/{address}` | Comprehensive vault details (PPS, TVL, fees, status, etc.) |
| `GET /api/v1/pps` | PPS data for validator network (separate endpoint for speed) |
| `GET /health` | Health check |

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment mode | `development` |
| `CACHE_TTL` | API cache TTL in seconds | `60` |
| `REFRESH_INTERVAL` | Auto-refresh interval in seconds | `60` |

## License

MIT License - see LICENSE file for details.