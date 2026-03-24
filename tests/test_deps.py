import pandas as pd
from PySide6.QtWidgets import QApplication

def test_pyside6():
    app = QApplication([])
    assert app is not None

def test_pandas():
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    assert df.shape == (2, 2)