from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import services.azdo as azdo


def process_hunt_data(hunt_details):
    """Process raw hunt data into a structured DataFrame."""
    processed_data = []

    for hunt in hunt_details:
        created_date = datetime.strptime(hunt.fields['System.CreatedDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
        week = created_date.strftime('%m/%d/%y')
        priority = hunt.fields['Microsoft.VSTS.Common.Priority']

        # Map numeric priority to text labels
        priority_labels = {1: 'Critical', 2: 'High', 3: 'Medium', 4: 'Low'}
        priority_text = priority_labels.get(priority, 'Unknown')

        processed_data.append({
            'Week': week,
            'WeekDate': created_date,
            'Priority': priority_text,
            'Ticket': hunt.fields.get('System.Id', ''),
            'Title': hunt.fields.get('System.Title', ''),
            'XSOAR_Link': hunt.fields.get('XSOAR_Link', '')
        })

    return pd.DataFrame(processed_data)


def create_summary_data(df):
    """Create summary data for the bar chart."""
    # Group by week and priority, count occurrences
    summary = df.groupby(['Week', 'Priority']).size().unstack(fill_value=0)

    # Convert string dates to datetime objects for better plotting
    summary.index = pd.to_datetime(summary.index, format='%m/%d/%y')
    summary = summary.sort_index()

    # Ensure all priority columns exist
    for priority in ['Critical', 'High', 'Medium', 'Low']:
        if priority not in summary.columns:
            summary[priority] = 0

    # Calculate total hunts per week
    summary['Total'] = summary.sum(axis=1)

    return summary


def plot_stacked_bar(fig, summary_data, colors):
    """Create the stacked bar chart."""
    # Create chart area at the top 40% of the figure
    chart_ax = fig.add_axes([0.1, 0.55, 0.8, 0.35])  # [left, bottom, width, height]

    bottom = np.zeros(len(summary_data.index))

    # Plot each priority level - reversed order to match example (Low at bottom)
    for priority in ['Low', 'Medium', 'High', 'Critical']:
        if priority in summary_data.columns:
            chart_ax.bar(summary_data.index, summary_data[priority], bottom=bottom,
                         label=priority, color=colors[priority])
            bottom += np.array(summary_data[priority])

    # Format the x-axis with better date spacing
    chart_ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
    plt.setp(chart_ax.get_xticklabels(), rotation=45, ha='right')

    # Add data labels for total counts
    for i, (date, row) in enumerate(summary_data.iterrows()):
        if row['Total'] > 0:  # Only add label if there's data
            chart_ax.text(mdates.date2num(date), row['Total'] + 0.5, str(int(row['Total'])),
                          ha='center', va='bottom', fontweight='bold')

    # Add labels and title
    chart_ax.set_title('Weekly Threat Hunts by Priority', fontsize=16, fontweight='bold', pad=20)
    chart_ax.set_xlabel('Week', fontsize=12)
    chart_ax.set_ylabel('Number of Threat Hunts', fontsize=12)
    chart_ax.grid(axis='y', linestyle='-', alpha=0.2)

    # Add legend in upper left with vertical layout as in example
    chart_ax.legend(title='Priority', loc='upper left')

    # Add some padding at the top for the total labels
    y_max = max(summary_data['Total'].max() * 1.15, 4)  # At least 4, or 15% above max
    chart_ax.set_ylim(0, y_max)

    # Add stats box in upper right
    add_stats_textbox(fig, summary_data, colors)

    return chart_ax


def add_stats_textbox(fig, summary_data, colors):
    """Add statistics textbox to the figure in a better position."""
    # Calculate overall statistics
    total_hunts = summary_data['Total'].sum()

    # Create text for stats box
    stats_text = f"Total Threat Hunts: {int(total_hunts)}\n"

    for priority in ['Critical', 'High', 'Medium', 'Low']:
        if priority in summary_data.columns:
            count = summary_data[priority].sum()
            percentage = count / total_hunts * 100 if total_hunts > 0 else 0
            stats_text += f"{priority}: {int(count)} ({percentage:.1f}%)\n"

    # Add the text box to the upper right corner of the figure
    props = dict(boxstyle='round', facecolor='white', edgecolor='black', alpha=0.9)
    fig.text(0.87, 0.78, stats_text.strip(), fontsize=9,
             bbox=props, verticalalignment='top', horizontalalignment='center')


def create_details_table(fig, df, colors):
    """Create and style the details table matching the example layout."""
    # Add table title centered on page
    fig.text(0.5, 0.5, 'Threat Hunt Details', fontsize=14, fontweight='bold', ha='center')

    # Sort table data by date (newest first) and then by priority
    priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    df['Priority_Order'] = df['Priority'].map(priority_order)
    df = df.sort_values(['WeekDate', 'Priority_Order'], ascending=[False, True])

    # Create combined ticket and title column
    df['Hunt Details'] = df.apply(lambda row: f"#{row['Ticket']} {row['Title']}", axis=1)

    # Select and reorder columns for display
    display_df = df[['Week', 'Priority', 'Hunt Details', 'XSOAR_Link']]

    # Limit number of rows to what's shown in example (about 10)
    max_rows = min(12, len(display_df))
    display_df = display_df.head(max_rows)

    # Create table data for display
    table_data = display_df.values.tolist()
    column_headers = ['Week', 'Priority', 'Hunt Details', 'XSOAR Link']

    # Create axis for table at bottom portion of figure
    table_ax = fig.add_axes([0.1, 0.1, 0.8, 0.35])  # [left, bottom, width, height]
    table_ax.axis('off')

    # Create table with column widths matching example
    table = plt.table(
        cellText=table_data,
        colLabels=column_headers,
        loc='center',
        cellLoc='left',
        colWidths=[0.08, 0.08, 0.64, 0.2]
    )

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)  # Make rows slightly taller as in example

    # Style the header row with dark gray
    for j, cell in enumerate(table._cells[(0, j)] for j in range(len(column_headers))):
        cell.set_text_props(weight='bold', color='white')
        cell.set_facecolor('#4b5563')

    # Color code priority cells exactly like the example
    for i in range(len(table_data)):
        priority = table_data[i][1]
        if priority in colors:
            cell = table._cells[(i + 1, 1)]
            cell.set_facecolor(colors[priority])
            if priority in ['Critical', 'High']:
                cell.set_text_props(color='white')

    return table


def generate_threat_hunt_report(hunt_details, output_file='weekly_threat_hunts_with_details.png'):
    """Main function to generate the threat hunt report matching the example layout."""
    # Define priority colors to match the example
    colors = {
        'Critical': '#ef4444',  # Red
        'High': '#f97316',  # Orange
        'Medium': '#fbbf24',  # Yellow
        'Low': '#60a5fa'  # Blue
    }

    # Process data
    df = process_hunt_data(hunt_details)
    summary_data = create_summary_data(df)

    # Create figure with same proportions as example - more square
    fig = plt.figure(figsize=(10, 12))

    # Create chart and table
    plot_stacked_bar(fig, summary_data, colors)
    create_details_table(fig, df, colors)

    # Save with tight layout and display
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    # Get hunt details from Azure DevOps
    hunt_details = azdo.get_stories_from_area_path()

    # Generate the report
    generate_threat_hunt_report(hunt_details)
