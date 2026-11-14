import matplotlib.pyplot as plt

def _style_axes(ax, player_name):
    ax.axhline(0, color="gray", linewidth=1)
    ax.set_xlabel(f"{player_name}'s age (years)")
    ax.set_ylabel("Age difference in years (Player's age - opponent's age)")
    ax.set_title(f"{player_name}'s career matches", pad=65)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("bottom")
    ax.grid(color="lightgray", linewidth=0.7)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

def plot_career(data):
    """Return a NYT-style plot with the cleaned data from get_career_data."""
    if data.empty:
        raise ValueError("There are no matches to plot.")
    wins = data[data["result"] == "W"]
    losses = data[data["result"] == "L"]
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.scatter(wins["player_age"], wins["age_difference"], color="deepskyblue", alpha=0.6, s=12, label="Match won")
    ax.scatter(losses["player_age"], losses["age_difference"], color="purple", alpha=0.6, s=12, label="Match lost")
    _style_axes(ax, data["player_name"].iloc[0])
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.08), ncol=2, frameon=False, markerscale=1.5)
    fig.tight_layout()
    return ax