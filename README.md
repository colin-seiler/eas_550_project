# eas_550_project
Class project for EAS 550 at University at Buffalo

## Brazilian E-Commerce Dashboard
An interactive business intelligence dashboard built with Steamlit, visualizing Brazilian e-commerce order data across customers and sellers by geographic region.

**Live App:**  {NEEEEEED URL}

---

## Screenshots

### Full Dashboard
<img width="1855" height="873" alt="Screenshot 2026-05-13 223553" src="https://github.com/user-attachments/assets/865df8e4-598f-4cf4-814b-cd8e47bfc4c0" />

---

## Architecture

The app follows a modern data pipeline architecture:

1. **Source Data** — Raw Brazilian e-commerce CSVs (Olist dataset)

2. **Data Warehouse** — PostgreSQL database hosted on [Neon](https://neon.tech), modeled using dbt with a star schema

3. **Analytics Layer** — dbt models aggregate order data by customer and seller zip code

4. **Application** — Streamlit dashboard queries the live Neon database via connection pooling and renders interactive visualizations


### Star Schema

{Insert schema hereeeeeee}

---

## Features

- **Interactive Map** — Scatter plot of customer/seller locations across Brazil, sized by order volume
- **Customer & Seller Bar Charts** — Compare states across multiple metrics with a dropdown selector
- **Ship Days vs Delivery Days** — Scatter plot revealing the relationship between shipping speed and delivery time by state
- **Avg Freight vs Avg Order Price** — Scatter plot showing how freight costs relate to order value by state
- **Customer vs Seller Orders by State** — Side-by-side comparison of customer demand vs seller presence per state
- **State Filter** — Multi-select pills to filter all views by Brazilian state
- **Top N Slider** — Control how many zip codes appear on the map

---
 
## Setup Instructions

### Local Development
 
1. **Clone the repository**
   ```bash
   git clone https://github.com/colin-seiler/eas_550_project.git
   cd eas_550_project/app
   ```
 
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
 
3. **Create a `.env` file** in the `app/` folder
   ```
   DATABASE_URL=your_neon_connection_string_here
   ```
 
4. **Run the app**
   ```bash
   streamlit run app.py
   ```
 
The app will open automatically at `http://localhost:8501`.
 
---



