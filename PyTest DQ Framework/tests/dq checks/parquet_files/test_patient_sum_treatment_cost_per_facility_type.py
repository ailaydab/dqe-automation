import pytest
 
@pytest.mark.parquet_data
def test_smoke_and_not_empty(parquet_reader, data_quality_library):
    target_path =  "/workspaces/dqe-automation/parquet_data/patient_sum_treatment_cost_per_facility_type"
    target_data = parquet_reader.process(target_path)
    data_quality_library.check_dataset_is_not_empty(target_data)
 
@pytest.mark.parquet_data
def test_completeness(parquet_reader, data_quality_library):
    target_path =  "/workspaces/dqe-automation/parquet_data/patient_sum_treatment_cost_per_facility_type"
    target_data = parquet_reader.process(target_path)
    expected_columns = ["facility_type", "full_name", "sum_treatment_cost"]
    data_quality_library.check_completeness(target_data, expected_columns=expected_columns)
 
@pytest.mark.parquet_data
def test_count(db_connection, parquet_reader, data_quality_library):
    source_query = """
        SELECT
            f.facility_type,
            CONCAT(p.last_name, ' ', p.first_name) AS full_name,
            SUM(v.treatment_cost) AS sum_treatment_cost
        FROM visits v
        JOIN facilities f ON v.facility_id = f.id
        JOIN patients p ON v.patient_id = p.id
        GROUP BY f.facility_type, p.last_name, p.first_name
    """
    source_data = db_connection.get_data_sql(source_query)
    target_path =  "/workspaces/dqe-automation/parquet_data/patient_sum_treatment_cost_per_facility_type"
    target_data = parquet_reader.process(target_path)
    data_quality_library.check_count(source_data, target_data)
 
@pytest.mark.parquet_data
def test_uniqueness(parquet_reader, data_quality_library):
    target_path =  "/workspaces/dqe-automation/parquet_data/patient_sum_treatment_cost_per_facility_type"
    target_data = parquet_reader.process(target_path)
    data_quality_library.check_duplicates(target_data, column_names=["facility_type", "full_name"])
 
@pytest.mark.parquet_data
def test_not_null_values(parquet_reader, data_quality_library):
    target_path =  "/workspaces/dqe-automation/parquet_data/patient_sum_treatment_cost_per_facility_type"
    target_data = parquet_reader.process(target_path)
    not_null_columns = ["facility_type", "full_name", "sum_treatment_cost"]
    data_quality_library.check_not_null_values(target_data, column_names=not_null_columns)