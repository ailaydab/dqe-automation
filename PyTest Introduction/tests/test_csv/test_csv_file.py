import pytest
import re
import pathlib

def test_file_not_empty(csv_data):
    assert (
        pathlib.Path(csv_data["file_path"]).stat().st_size > 0
    ), "CSV file is empty, please check the path."
    assert not csv_data["df"].empty, "DataFrame is empty, please check the CSV file."


@pytest.mark.validate_csv
@pytest.mark.xfail(reason="There are duplicates.")
def test_duplicates(csv_data):
    assert not csv_data["df"].duplicated().any(), "There are duplicates in the CSV file, please check data."

@pytest.mark.validate_csv
def test_validate_schema(csv_data, expected_schema):
    actual_schema = list(csv_data["df"].columns)
    assert (actual_schema == expected_schema), f"Schema mismatch. Expected: {expected_schema}, Actual: {actual_schema}"

@pytest.mark.validate_csv
@pytest.mark.skip(reason="Temporarily skipped")
def test_age_column_valid(csv_data):
    for age in csv_data["df"]["age"]:
        assert 0 <= age <= 100, f"Invalid age value: {age} (Valid age values 0-100)"

@pytest.mark.validate_csv
def test_email_column_valid(csv_data):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    for email in csv_data["df"]["email"]:
        assert bool(re.match(email_pattern, email)), f"Invalid email value: {email} (Valid email format: example@domain.com)"


@pytest.mark.parametrize(
    "target_id, expected_is_active",[(1, False),(2, True)],
)
def test_active_players(csv_data, target_id, expected_is_active):
    row = csv_data["df"][csv_data["df"]["id"] == target_id]
    assert not row.empty, f"No data found for id: {target_id}"
    assert row["is_active"].values[0] == expected_is_active


def test_active_player(csv_data):
    row = csv_data["df"][csv_data["df"]["id"] == 2]
    assert not row.empty, "No data found for id: 2"
    assert row["is_active"].values[0] == True or row["is_active"].values[0] == True