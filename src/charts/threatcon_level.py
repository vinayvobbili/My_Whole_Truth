import json
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrow

THREAT_CON_FILE = "../../data/transient/secOps/threatcon.json"


def gauge(threatcon_details):
    """
    Creates a gauge chart representing the threat level.

    Args:
        threatcon_details (json): The color representing the threat level ('red', 'orange', 'yellow', 'green'). And the reason for that color

    Returns:
        matplotlib.figure.Figure: The generated gauge chart figure.
    """

    threatcon_color = threatcon_details['level']
    reason = threatcon_details['reason']

    # Create figure and axis
    rad_angle = 0
    fig, ax = plt.subplots(figsize=(8, 6))

    # Set the gauge range
    angles = np.linspace(0, 180)

    # Create color ranges
    red = angles <= 45
    orange = (angles > 45) & (angles <= 90)
    yellow = (angles > 90) & (angles <= 135)
    green = angles > 135

    # Plot the colored arcs
    radius = 1
    # Plot the colored arcs with darker colors
    ax.plot(radius * np.cos(np.radians(angles[red])),
            radius * np.sin(np.radians(angles[red])),
            color='#8B0000', linewidth=20, zorder=1)  # Dark red
    ax.plot(radius * np.cos(np.radians(angles[orange])),
            radius * np.sin(np.radians(angles[orange])),
            color='#FF8C00', linewidth=20, zorder=1)  # Dark orange
    ax.plot(radius * np.cos(np.radians(angles[yellow])),
            radius * np.sin(np.radians(angles[yellow])),
            color='#FFD700', linewidth=20, zorder=1)  # Dark yellow
    ax.plot(radius * np.cos(np.radians(angles[green])),
            radius * np.sin(np.radians(angles[green])),
            color='#006400', linewidth=20, zorder=1)  # Dark green

    # Add the arrow (needle)
    if threatcon_color == 'red':
        rad_angle = np.radians(22.5)
    elif threatcon_color == 'orange':
        rad_angle = np.radians(67.5)
    elif threatcon_color == 'yellow':
        rad_angle = np.radians(112.5)
    elif threatcon_color == 'green':
        rad_angle = np.radians(157.5)

    arrow_length = 0.80
    arrow_width = 0.04
    arrow = FancyArrow(0, 0,
                       arrow_length * np.cos(rad_angle),
                       arrow_length * np.sin(rad_angle),
                       width=arrow_width,
                       color='black', zorder=3)  # set zorder to 3
    ax.add_patch(arrow)

    # Add a center dot
    ax.plot(0, 0, 'ko', markersize=20, zorder=2)  # set zorder to 2

    # Add a black line along the top edge of the gauge
    outer_radius = 1.04  # Adjust this value to move the line outward
    ax.plot(outer_radius * np.cos(np.radians(angles)),
            outer_radius * np.sin(np.radians(angles)),
            color='black', linewidth=1, zorder=2)  # set zorder to 2

    # Add a horizontal black line at the bottom of the gauge
    ax.plot([-outer_radius, outer_radius], [0, 0], color='black', linewidth=1, zorder=2)  # set zorder to 2

    # Set title with a nice font
    ax.text(0, 1.2, f'Threatcon Level - {datetime.today().strftime("%m/%d/%Y")}',
            ha='center', va='center', fontsize=14, fontweight='bold',
            fontname='Arial')

    # Configure plot
    ax.set_aspect('equal')
    ax.set_ylim(bottom=0)
    ax.set_xlim([-1.1, 1.1])
    ax.axis('off')
    plt.tight_layout()

    if threatcon_color != 'green':
        # Add Reason section on top of the gauge
        reason_text = f"Reason: \n{reason}"
        reason_font_color = 'black'
        if threatcon_color == 'yellow':
            reason_font_color = '#FFD700'
        elif threatcon_color == 'orange':
            reason_font_color = '#FF8C00'
        elif threatcon_color == 'red':
            reason_font_color = '#8B0000'

        fig.text(0.2, 0.4, reason_text, ha='left', va='center', fontsize=10, color=reason_font_color,
                 bbox=dict(facecolor='gray', edgecolor='black', boxstyle='round,pad=0.5', linewidth=1))

    # Define the threat level details
    threat_details = [
        ["Level", "Description"],
        ["GREEN", "No known significant threats or on-going attacks"],
        ["YELLOW", "There are global threats and/or non-specific threats which could affect MetLife"],
        ["ORANGE", "There are known threats which are specifically targeting MetLife"],
        ["RED", "There is an ongoing attack confirmed to be targeting MetLife"]
    ]

    # Create a table at the bottom of the chart
    definitions_table = plt.table(
        cellText=threat_details[1:],  # Skip the header row for cell text
        colLabels=threat_details[0],  # Use the header row for column labels
        loc='bottom',
        bbox=[0.05, -0.5, 0.9, 0.3],  # Adjust position and size as needed
        colWidths=[0.15, 0.85]  # Set the column widths - 12% for Level, 88% for Description
    )

    # Style the table
    definitions_table.auto_set_font_size(False)
    definitions_table.set_fontsize(10)

    # Apply colors to the cells
    definitions_table.get_celld()[(0, 0)].set_facecolor('#3366CC')  # Header background
    definitions_table.get_celld()[(0, 1)].set_facecolor('#3366CC')  # Header background
    definitions_table.get_celld()[(0, 0)].set_text_props(color='white')  # Header text color
    definitions_table.get_celld()[(0, 1)].set_text_props(color='white')  # Header text color

    # Color the level cells according to the threat level
    definitions_table.get_celld()[(1, 0)].set_facecolor('#006400')  # Dark GREEN
    definitions_table.get_celld()[(2, 0)].set_facecolor('#FFD700')  # Dark YELLOW
    definitions_table.get_celld()[(3, 0)].set_facecolor('#FF8C00')  # Dark ORANGE
    definitions_table.get_celld()[(4, 0)].set_facecolor('#8B0000')  # Dark RED

    # Set the description cell backgrounds
    definitions_table.get_celld()[(1, 1)].set_facecolor('#B3FFB3')  # Light green
    definitions_table.get_celld()[(2, 1)].set_facecolor('#FFFFB3')  # Light yellow
    definitions_table.get_celld()[(3, 1)].set_facecolor('#FFCC99')  # Light orange
    definitions_table.get_celld()[(4, 1)].set_facecolor('#FFB3B3')  # Light red

    # Explicitly set cell alignment for each cell
    for i in range(1, 5):
        # Set Level column to center
        definitions_table.get_celld()[(i, 0)].set_text_props(ha='left')
        # Set Description column to left align with minimal padding
        definitions_table.get_celld()[(i, 1)].set_text_props(ha='left')
        # Add specific padding control for description column
        definitions_table.get_celld()[(i, 1)].PAD = 0.02

    # Also set header alignment
    definitions_table.get_celld()[(0, 0)].set_text_props(ha='center')
    definitions_table.get_celld()[(0, 1)].set_text_props(ha='center')  # Keep header centered

    # Adjust the table scale
    definitions_table.scale(1, 1.5)

    return fig


def make_chart():
    """
    Generates the threat level gauge chart with the text table and saves it as an image.
    """
    with open(THREAT_CON_FILE, "r") as file:
        threatcon_details = json.loads(file.read())

    fig = gauge(threatcon_details)

    # Add a thin black border around the figure
    fig.patch.set_edgecolor('black')
    fig.patch.set_linewidth(5)

    fig.savefig('../../web/static/charts/Threatcon Level.png', format='png', bbox_inches='tight', pad_inches=0.2, dpi=300)
    plt.close()


if __name__ == '__main__':
    make_chart()
