import pytest
import pandas as pd
import pathlib

# Fixture to read the CSV file
@pytest.fixture(scope="session")
def csv_data():
    base_path = pathlib.Path(__file__).parent.parent
    file_path = base_path / "src" / "data" / "data.csv"
    df = pd.read_csv(file_path)
    return {"df": df, "file_path": str(file_path)}

# Fixture to validate the schema of the file
@pytest.fixture(scope="session")
def expected_schema():
    return ["id","name","age","email","is_active"]

# Pytest hook to mark unmarked tests with a custom mark
def pytest_collection_modifyitems(items):
    for item in items:
        if not list(item.iter_markers()):
            item.add_marker(pytest.mark.unmarked)