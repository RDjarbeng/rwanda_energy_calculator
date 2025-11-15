# Rwanda Energy Calculator

A web application for calculating electricity costs and units according to Rwanda Energy Group (REG) tariffs, with a detailed breakdown by tier.

Built with FastHTML. App is deployed with Onrender [here](https://rwanda-energy-calculator.onrender.com/)

## Features

- **Calculate Units from Cost:**  
  Enter the amount (RWF) you wish to spend on electricity and get the corresponding kilowatt-hours (kWh) you will receive, including an optional field for any initial amount already paid.
- **Calculate Cost from Units:**  
  Enter the number of units (kWh) consumed to estimate the total cost (RWF), with a detailed breakdown by tariff tier.
- **Tiered Breakdown:**  
  See how your payment or usage is distributed across REG tariff tiers (Tier 1, 2, 3) and VAT.
- **Live Calculation:**  
  Instant results and breakdown as you type, powered by FastHTML and HTMX.
- **Static HTML Build:**  
  Generates static pages for deployment (e.g., Netlify).

## REG Tariffs (as implemented)

- **Tier 1:** Up to 15 kWh @ 89 RWF/kWh
- **Tier 2:** 16–35 kWh @ 212 RWF/kWh
- **Tier 3:** Above 35 kWh @ 249 RWF/kWh
- **VAT:** 18% applied to all charges

[View Official REG Tariffs](https://www.reg.rw/customer-service/tariffs/)

## Usage

### 1. Online

Visit the deployed site (if available) or run locally.

### 2. Local Development

**Requirements:**
- Python 3
- [fasthtml](https://github.com/AnswerDotAI/fasthtml) package 
`pip install python-fasthtml`
  

**Recommended Environment:**
If you use Anaconda, it is recommended to create a separate environment for this project and activate it before running any commands:
```bash
conda create -n rwanda-energy python=3.11
conda activate rwanda-energy
```

**Run locally:**
```bash
python main.py
```
or (if using Netlify/Serverless)
```bash
python netlify/functions/app.py
```

**Build static HTML:**
```bash
python build.py
```
The output will be in the `dist/` directory.

## How It Works

- Enter your payment amount to see how many units you will get, with an optional field for initial payment (useful for monthly purchases).
- Enter number of units consumed to see the cost and how it falls into REG's tiered pricing.
- The results are shown instantly, with full breakdown tables for transparency.

## Example

- **Calculate Units:**  
  - Amount: `10,000 RWF`  
  - Initial payment (optional): `2,000 RWF`  
  - Result: `X kWh` (details per tier shown)

- **Calculate Cost:**  
  - Units: `30 kWh`  
  - Result: `Y RWF` (details per tier shown)

## Tech Stack

- Python (serverless functions or standalone)
- FastHTML (UI rendering)
- HTMX (live updates)
- Pico CSS (simple, clean styling)
- Netlify (optional, for deployment)

## Project Structure

```
main.py                  # Main app logic (routes, calculations)
build.py                 # Script to build static HTML pages
netlify/functions/app.py # Netlify function for serverless deployment
requirements.txt         # Python dependencies (if present)
dist/                    # Output directory for static HTML
```
## Announcement
Link to announcement by [RURA on change to energy tariffs on Richard's blog](https://rdjarbeng.com/rura-announces-revised-electricity-end-user-tariffs-effective-october-2025/)
## License

This project is open source. See the LICENSE file for details.

## Author

Created by [RDjarbeng](https://github.com/RDjarbeng)
Initial programming logic by [Ian Akotey](https://github.com/ianakotey)

---

Feel free to open issues or pull requests for improvements, bug fixes, or new features!
