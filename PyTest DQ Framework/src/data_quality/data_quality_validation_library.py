import pandas as pd

class DataQualityLibrary:
    """
    A library of static methods for performing data quality checks on pandas DataFrames.

    This class is intended to be used in a PyTest-based testing framework to validate
    the quality of data in DataFrames. Each method performs a specific data quality
    check and uses assertions to ensure that the data meets the expected conditions.
    """

    @staticmethod
    def check_duplicates(df, column_names=None):
        if column_names:
            duplicates_count = df.duplicated(subset=column_names).sum()
            assert duplicates_count == 0, f"DQ Fail - Found {duplicates_count} duplicate rows based on columns: {column_names}"
        else:
            duplicates_count = df.duplicated().sum()
            assert duplicates_count == 0, f"DQ Fail - Found {duplicates_count} duplicate rows in the DataFrame"

    @staticmethod
    def check_count(df1, df2):
        count1 = len(df1)
        count2 = len(df2)
        assert count1 == count2, f"DQ Fail - Count mismatch: {count1} (df1) vs {count2} (df2)"

    @staticmethod
    def check_data_full_data_set(df1, df2):
        pd.testing.assert_frame_equal(df1,df2,checklike=True)

    @staticmethod
    def check_dataset_is_not_empty(df):
        assert not df.empty, "DQ Fail - DataFrame is empty!!!"

    @staticmethod
    def check_not_null_values(df, column_names=None):
        if column_names:
            for column in column_names:
                null_count = df[column].isnull().sum()
                assert null_count == 0, f"DQ Fail - Found {null_count} null values in column: {column}"
        else:
            null_count = df.isnull().sum().sum()
            assert null_count == 0, f"DQ Fail - Found {null_count} null values in the DataFrame"

@staticmethod
def check_completeness(df, expected_columns):
    missing_columns = [col for col in expected_columns if col not in df.columns]
    assert not missing_columns, f"DQ Fail - Missing expected columns: {missing_columns}"