import pandas as pd
from data_loader import load_actigraphy_series
actigraphy_df = load_actigraphy_series("child-mind-institute-problematic-internet-use/series_train.parquet")
sample_df = actigraphy_df.head(1000).to_pandas()

print(sample_df.columns)
print(sample_df.info())