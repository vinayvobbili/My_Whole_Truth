from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytz
from matplotlib import transforms

from config import get_config
from services.xsoar import IncidentFetcher

eastern = pytz.timezone('US/Eastern')

CONFIG = get_config()

ROOT_DIRECTORY = Path(__file__).parent.parent.parent
OUTPUT_PATH = ROOT_DIRECTORY / "web" / "static" / "charts" / "Vectra Efficacy.png"


def generate_chart(tickets):
    # Extract creation dates and convert to datetime objects
    creation_dates = [datetime.fromisoformat(ticket['created']) for ticket in tickets]

    # Create a DataFrame with the creation dates
    df = pd.DataFrame({'Creation Date': creation_dates})

    # Group tickets by day
    df['Date'] = df['Creation Date'].dt.date
    daily_counts = df.groupby('Date').size().reset_index(name='Ticket Count')

    # Create the bar chart
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(14, 8))
    plt.bar(daily_counts['Date'], daily_counts['Ticket Count'], color='skyblue')

    # Customize the chart
    plt.title('Vectra Detections Over Time', fontsize=14, fontweight='bold')
    plt.xlabel('Detection Date', fontsize=10, fontweight='bold', labelpad=10)
    plt.ylabel('Number of Detections', fontsize=10, fontweight='bold', labelpad=10)
    plt.xticks(rotation=90)

    # Add a thin black border around the figure
    fig.patch.set_edgecolor('black')
    fig.patch.set_linewidth(5)

    # Add the current time to the chart
    now_eastern = datetime.now(eastern).strftime('%m/%d/%Y %I:%M %p %Z')
    trans = transforms.blended_transform_factory(fig.transFigure, fig.transFigure)
    plt.text(0.05, 0.01, now_eastern, ha='left', va='bottom', fontsize=10, transform=trans)

    plt.tight_layout()

    # Save the chart
    plt.savefig(OUTPUT_PATH)
    plt.close()


def make_chart(months_back=3, save_chart=True):
    """
    Fetch tickets and generate a chart

    Args:
        months_back: Number of months to look back for data
        save_chart: Whether to save the chart to file
    """
    try:
        query = f'type:"{CONFIG.ticket_type_prefix} Vectra Detection"'
        period = {"byTo": "months", "toValue": None, "byFrom": "months", "fromValue": months_back}

        incident_fetcher = IncidentFetcher()
        tickets = incident_fetcher.get_tickets(query, period)

        print(f"Retrieved {len(tickets)} tickets")
        generate_chart(tickets)

    except Exception as e:
        print(f"Error fetching tickets or generating chart: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    make_chart()
