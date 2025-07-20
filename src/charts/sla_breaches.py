from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import sys

import matplotlib.transforms as transforms
import numpy as np
from matplotlib import pyplot as plt
from pytz import timezone

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config import get_config
from services.xsoar import TicketHandler

eastern = timezone('US/Eastern')
config = get_config()

root_directory = Path(__file__).parent.parent.parent


@dataclass
class SlaBreachCounts:
    total_ticket_count: int = 0
    response_sla_breach_count: int = 0
    containment_sla_breach_count: int = 0


def get_tickets_by_periods(tickets):
    current_date = datetime.now()

    # Calculate reference dates
    yesterday = (current_date - timedelta(days=1)).date()
    seven_days_ago = (current_date - timedelta(days=7)).date()
    thirty_days_ago = (current_date - timedelta(days=30)).date()

    # Initialize data structure for sla_breach_counts_by_periods
    sla_breach_counts_by_periods = {
        'Yesterday': SlaBreachCounts(),
        'Past 7 days': SlaBreachCounts(),
        'Past 30 days': SlaBreachCounts()
    }

    # Process each ticket
    for ticket in tickets:
        custom_fields = ticket['CustomFields']
        response_sla_status = custom_fields.get('timetorespond', {}).get('slaStatus', custom_fields.get('responsesla', {}).get('slaStatus'))
        containment_sla_status = custom_fields.get('timetocontain', {}).get('slaStatus', custom_fields.get('containmentsla', {}).get('slaStatus'))

        incident_date = datetime.strptime(
            ticket['created'],
            '%Y-%m-%dT%H:%M:%S.%fZ' if '.' in ticket['created'] else '%Y-%m-%dT%H:%M:%SZ'
        ).date()

        # Update metrics for each time period
        if incident_date == yesterday:
            sla_breach_counts_by_periods['Yesterday'].total_ticket_count += 1

            if response_sla_status == 2:
                sla_breach_counts_by_periods['Yesterday'].response_sla_breach_count += 1
            if containment_sla_status == 2:
                sla_breach_counts_by_periods['Yesterday'].containment_sla_breach_count += 1

        if seven_days_ago <= incident_date <= current_date.date():
            sla_breach_counts_by_periods['Past 7 days'].total_ticket_count += 1

            if response_sla_status == 2:
                sla_breach_counts_by_periods['Past 7 days'].response_sla_breach_count += 1
            if containment_sla_status == 2:
                sla_breach_counts_by_periods['Past 7 days'].containment_sla_breach_count += 1

        if thirty_days_ago <= incident_date <= current_date.date():
            sla_breach_counts_by_periods['Past 30 days'].total_ticket_count += 1

            if response_sla_status == 2:
                sla_breach_counts_by_periods['Past 30 days'].response_sla_breach_count += 1
            if containment_sla_status == 2:
                sla_breach_counts_by_periods['Past 30 days'].containment_sla_breach_count += 1

    return sla_breach_counts_by_periods


def save_sla_breaches_chart(ticket_slas_by_periods):
    # Set up enhanced plot style without grids
    plt.style.use('default')

    # Configure matplotlib fonts
    import matplotlib
    matplotlib.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Arial']

    thirty_days_ticket_count = ticket_slas_by_periods['Past 30 days'].total_ticket_count
    seven_days_ticket_count = ticket_slas_by_periods['Past 7 days'].total_ticket_count
    yesterday_ticket_count = ticket_slas_by_periods['Yesterday'].total_ticket_count

    metrics = {
        'Response SLA Breaches': {
            'Yesterday': ticket_slas_by_periods['Yesterday'].response_sla_breach_count,
            'Past 7 days': ticket_slas_by_periods['Past 7 days'].response_sla_breach_count,
            'Past 30 days': ticket_slas_by_periods['Past 30 days'].response_sla_breach_count
        },
        'Containment SLA Breaches': {
            'Yesterday': ticket_slas_by_periods['Yesterday'].containment_sla_breach_count,
            'Past 7 days': ticket_slas_by_periods['Past 7 days'].containment_sla_breach_count,
            'Past 30 days': ticket_slas_by_periods['Past 30 days'].containment_sla_breach_count
        }
    }

    # Enhanced figure with better proportions and styling
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='#f8f9fa')
    fig.patch.set_facecolor('#f8f9fa')

    # Width of each bar and positions of the bars
    width = 0.15  # Reduced from 0.25 to make bars narrower
    x = np.array([0, 0.8])  # Reduced gap from 1.2 to 0.8 to bring groups closer

    # Professional color palette (matching MTTR/MTTC chart)
    colors = {
        '30days': '#4CAF50',  # Muted Green for 30 days
        '7days': '#FF6B40',   # Orange for 7 days
        'yesterday': '#4080FF' # Blue for yesterday
    }

    # Create bars and store their container objects
    response_breaches_yesterday = metrics['Response SLA Breaches']['Yesterday']
    response_breaches_7days = metrics['Response SLA Breaches']['Past 7 days']
    response_breaches_30days = metrics['Response SLA Breaches']['Past 30 days']
    containment_breaches_yesterday = metrics['Containment SLA Breaches']['Yesterday']
    containment_breaches_7days = metrics['Containment SLA Breaches']['Past 7 days']
    containment_breaches_30days = metrics['Containment SLA Breaches']['Past 30 days']

    bar1 = ax.bar(x - width, [response_breaches_30days, containment_breaches_30days], width,
                  label=f'Past 30 days ({thirty_days_ticket_count})',
                  color=colors['30days'], edgecolor='white', linewidth=1.5, alpha=0.95)
    bar2 = ax.bar(x, [response_breaches_7days, containment_breaches_7days], width,
                  label=f'Past 7 days ({seven_days_ticket_count})',
                  color=colors['7days'], edgecolor='white', linewidth=1.5, alpha=0.95)
    bar3 = ax.bar(x + width, [response_breaches_yesterday, containment_breaches_yesterday], width,
                  label=f'Yesterday ({yesterday_ticket_count})',
                  color=colors['yesterday'], edgecolor='white', linewidth=1.5, alpha=0.95)

    # Enhanced axes styling
    ax.set_facecolor('#ffffff')
    ax.grid(False)  # Explicitly disable grid
    ax.set_axisbelow(True)

    # Style the spines
    for spine in ax.spines.values():
        spine.set_color('#CCCCCC')
        spine.set_linewidth(1.5)

    # Enhanced border
    border_width = 4
    fig.patch.set_edgecolor('#1A237E')
    fig.patch.set_linewidth(border_width)

    # Enhanced timestamp with modern styling
    trans = transforms.blended_transform_factory(fig.transFigure, fig.transFigure)
    now_eastern = datetime.now(eastern).strftime('%m/%d/%Y %I:%M %p %Z')

    plt.text(0.02, 0.02, f"Generated@ {now_eastern}",
             transform=trans, ha='left', va='bottom',
             fontsize=10, color='#1A237E', fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.4", facecolor='white', alpha=0.9, edgecolor='#1A237E', linewidth=1.5))

    # Enhanced titles and labels
    plt.suptitle('SLA Breaches by Response & Containment',
                 fontsize=20, fontweight='bold', color='#1A237E', y=0.95)

    # Customize the plot
    ax.set_ylabel('Breach Count', fontsize=14, fontweight='bold', color='#1A237E')
    ax.set_xticks(x)
    ax.set_xticklabels(['Response', 'Containment'], fontsize=12, fontweight='bold', color='#1A237E')

    # Enhanced legend - moved to upper left to avoid crowding with bars
    legend = ax.legend(title='Period (Ticket Count)', loc='upper left',
                      frameon=True, fancybox=True, shadow=True,
                      title_fontsize=12, fontsize=10)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(0.95)
    legend.get_frame().set_edgecolor('#1A237E')
    legend.get_frame().set_linewidth(2)

    # Enhanced value labels with black circles
    for bars in [bar1, bar2, bar3]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                # Circle label in middle
                ax.text(bar.get_x() + bar.get_width() / 2., height / 2,
                       f'{int(height)}',
                       ha='center', va='center',
                       fontsize=12, color='white', fontweight='bold',
                       bbox=dict(boxstyle="circle,pad=0.2", facecolor='black', alpha=0.8, edgecolor='white', linewidth=1))

    # Add GS-DnR watermark
    fig.text(0.99, 0.01, 'GS-DnR',
             ha='right', va='bottom', fontsize=10,
             alpha=0.7, color='#3F51B5', style='italic', fontweight='bold')

    # Add explanatory note
    plt.text(0.02, 0.08, '(*) Ticket counts for that period',
             transform=trans, ha='left', va='bottom',
             fontsize=9, color='#666666', style='italic')

    # Enhanced layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.88, bottom=0.15, left=0.08, right=0.92)

    today_date = datetime.now().strftime('%m-%d-%Y')
    OUTPUT_PATH = root_directory / "web" / "static" / "charts" / today_date / "SLA Breaches.png"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT_PATH)
    plt.close(fig)


def make_chart():
    query = f'type:{config.team_name} -owner:""'
    period = {
        "byTo": "months",
        "toValue": None,
        "byFrom": "months",
        "fromValue": 1
    }

    incident_fetcher = TicketHandler()
    tickets = incident_fetcher.get_tickets(query=query, period=period)
    tickets_by_periods = get_tickets_by_periods(tickets)
    save_sla_breaches_chart(tickets_by_periods)


if __name__ == '__main__':
    make_chart()
