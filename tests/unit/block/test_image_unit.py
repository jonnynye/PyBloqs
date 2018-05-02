import matplotlib.pyplot as plt
import pandas as pd
import pytest
from pybloqs.block.image import PlotBlock, PlotlyPlotBlock
from mock import patch


def test_create_PlotBlock():
    f = plt.figure()
    b = PlotBlock(f)
    assert len(b._img_data) > 0
    assert b._mime_type == 'png'


def test_create_PlotBlock_with_bbox_inches_tight():
    f = plt.figure()
    b = PlotBlock(f, box_inches='tight')
    assert len(b._img_data) > 0
    assert b._mime_type == 'png'


def test_create_PlotBlock_with_bbox_inches_none():
    f = plt.figure()
    b = PlotBlock(f, bbox_inches=None)
    assert len(b._img_data) > 0
    assert b._mime_type == 'png'


def test_create_Plotly_with_invalid_data():
    with pytest.raises(ValueError):
        PlotlyPlotBlock(pd.Series([1, 2, 3]).plot())


def test_create_Bokeh_with_invalid_data():
    with pytest.raises(ValueError):
        PlotlyPlotBlock(pd.Series([1, 2, 3]).plot())


def test_missing_matplotlib_raises_error():
    with patch.dict('sys.modules', {'matplotlib.pyplot': None}):
        with pytest.raises(ImportError):
            import pybloqs.block.image


def test_missing_plotly_does_not_raise_error():
    with patch.dict('sys.modules', {'plotly': None}):
        import pybloqs.block.image


def test_missing_bokeh_does_not_raise_error():
    with patch.dict('sys.modules', {'bokeh': None}):
        import pybloqs.block.image
