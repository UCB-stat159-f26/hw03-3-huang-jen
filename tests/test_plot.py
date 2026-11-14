import matplotlib.pyplot as plt
import pandas as pd
import pytest

from tennis_career import plot_career

def _sample_data():
    return pd.DataFrame({
        "player_age": [18.0, 30.0],
        "age_difference": [-4.0, 5.0],
        "result": ["W", "L"],
        "player_name": ["Test Player", "Test Player"],
    })

def test_plot_points_and_save(tmp_path):
    ax = plot_career(_sample_data())
    assert ax.collections[0].get_offsets().tolist() == [[18.0, -4.0]]
    assert ax.collections[1].get_offsets().tolist() == [[30.0, 5.0]]
    assert list(ax.lines[0].get_ydata()) == [0, 0]
    assert "Test Player" in ax.get_title()
    assert len(ax.texts) == 0
    ax.figure.savefig(tmp_path / "career.png")
    assert (tmp_path / "career.png").is_file()
    plt.close(ax.figure)

def test_empty_data():
    empty = _sample_data().iloc[:0]
    with pytest.raises(ValueError, match="no matches"):
        plot_career(empty)