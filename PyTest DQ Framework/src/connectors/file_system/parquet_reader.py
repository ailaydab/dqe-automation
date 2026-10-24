import pandas as pd
import glob
import os
 
class ParquetReader:
    def __init__(self):
        pass
        
    def process(self, file_path: str, include_subfolders: bool = True) -> pd.DataFrame:
        return pd.read_parquet(file_path)