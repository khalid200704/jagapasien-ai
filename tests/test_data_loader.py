from pathlib import Path

import pandas as pd
import pytest

from src.jagapasien.data_loader import choose_dataset_files, load_datasets


ROOT = Path(__file__).resolve().parents[1]


def test_choose_dataset_files_returns_expected_files():
    files = choose_dataset_files(ROOT)
    assert "candidate" in files
    assert "pairs" in files
    assert "patients" in files
    assert "visits" in files
    assert files["candidate"].name.endswith(".csv")


def test_load_datasets_reads_expected_tables():
    data = load_datasets(ROOT)
    assert isinstance(data.candidates, pd.DataFrame)
    assert isinstance(data.pairs, pd.DataFrame)
    assert isinstance(data.patients, pd.DataFrame)
    assert isinstance(data.visits, pd.DataFrame)
    assert len(data.candidates) > 0
    assert len(data.pairs) > 0
    assert len(data.patients) > 0
    assert len(data.visits) > 0


def test_missing_dataset_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_datasets(tmp_path)
