# IndieHackers Data Collector 🚀

A lightweight, professional Python-based CLI tool to collect public SaaS product data from [IndieHackers.com](https://www.indiehackers.com/products). This tool uses the internal Algolia API for high-performance extraction without the need for heavy browser automation.

## ✨ Features

- **Fast & Efficient**: Direct API calls to Algolia (the search engine powering IH).
- **Customizable Filters**: Filter by Revenue, Tech Skills (Founders Code), and more.
- **CSV Export**: Automatically saves data to a clean, structured CSV file.
- **Professional Setup**: Includes `.env` support, logging, and CLI arguments.

## 🛠️ Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/indiehackers-collector.git
   cd indiehackers-collector
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   - Copy the example file: `cp .env.example .env` (or manually rename it).
   - Open `.env` and fill in your Algolia credentials.
   
   > [!TIP]
   > You can find these keys by inspecting the network traffic in your browser while visiting the IndieHackers products page. Look for requests to `*.algolia.net`.

## 🚀 Usage

Run the script with default settings (Founders Code, Min Revenue $1):
```bash
python collector.py
```

### Advanced Usage (CLI Arguments)

You can customize the collection process using flags:

```bash
# Filter for high revenue products (> $1000/mo) and fetch 3 pages
python collector.py --revenue 1000 --pages 3 --output high_revenue.csv

# Include products from non-coders
python collector.py --no-code --pages 1
```

**Available Flags:**
- `--revenue [number]`: Minimum monthly revenue (Default: 1)
- `--no-code`: Disable the "Founders Code" only filter.
- `--pages [number]`: Maximum number of pages to fetch (100 items per page).
- `--output [filename]`: Custom output filename (Default: `products.csv`).

## ⚖️ Legal & Ethical Note

This tool is designed for **personal market research only**. It respects the site's data structure by using polite delays and only accessing publicly available data. 

> [!WARNING]
> Do not use this tool for commercial data resale or aggressive scraping. Always respect IndieHackers' Terms of Service and `robots.txt`.
