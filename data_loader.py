# data_loader.py

import polars as pl
import os


def load_train_data(path: str) -> pl.DataFrame:
    df = pl.read_csv(path)
    df = df.with_columns([
        pl.col("Basic_Demos-Age").alias("age"),
        pl.col("Basic_Demos-Sex").alias("sex"),
        pl.when(pl.col("PCIAT-PCIAT_Total") <= 30).then(0)
         .when(pl.col("PCIAT-PCIAT_Total") <= 49).then(1)
         .when(pl.col("PCIAT-PCIAT_Total") <= 79).then(2)
         .otherwise(3).alias("sii")
    ])
    return df


def load_actigraphy_series(directory: str) -> pl.DataFrame:
    id_folders = [f.name for f in os.scandir(directory) if f.is_dir() and f.name.startswith("id=")]
    all_series = []

    for id_folder in id_folders:
        id_val = id_folder.split("=")[-1]
        file_path = os.path.join(directory, id_folder, "part-0.parquet")
        if os.path.exists(file_path):
            df = pl.read_parquet(file_path).with_columns(pl.lit(id_val).alias("id"))
            all_series.append(df)

    return pl.concat(all_series) if all_series else pl.DataFrame()



def preprocess_actigraphy_daily_features(df: pl.DataFrame) -> pl.DataFrame:
    print(f"[DEBUG] Received DataFrame type: {type(df)}")
    print(f"[DEBUG] Schema: {df.schema if hasattr(df, 'schema') else 'N/A'}")
    
    df = df.with_columns([
        (pl.col("time_of_day") / 1e9).alias("seconds"),
        ((pl.col("time_of_day") / 1e9) / 3600).alias("hour"),
        pl.col("relative_date_PCIAT").alias("day"),
    ])

    df = df.filter(pl.col("non-wear_flag") == 0)

    df = df.with_columns([
        pl.when((pl.col("hour") >= 22) | (pl.col("hour") < 7)).then(1).otherwise(0).alias("is_night")
    ])

    grouped = df.group_by(["id", "day"]).agg([
        pl.mean("enmo").alias("mean_enmo"),
        pl.sum("enmo").alias("total_enmo"),
        pl.mean("light").alias("mean_light"),
        pl.max("light").alias("max_light"),
        pl.mean("anglez").alias("mean_anglez"),
        pl.count().alias("total_samples"),
        pl.sum("is_night").alias("night_samples")
    ])

    return grouped.with_columns([
        (pl.col("night_samples") / pl.col("total_samples")).alias("percent_night_activity")
    ])



def batch_process_actigraphy_features(directory: str) -> pl.DataFrame:
    id_folders = [f.name for f in os.scandir(directory) if f.is_dir() and f.name.startswith("id=")]
    all_features = []

    for id_folder in id_folders:
        id_val = id_folder.split("=")[-1]
        file_path = os.path.join(directory, id_folder, "part-0.parquet")

        if os.path.exists(file_path):
            try:
                raw_df = pl.read_parquet(file_path)
                if not isinstance(raw_df, pl.DataFrame):
                    raw_df = pl.DataFrame(raw_df)
                df = raw_df.with_columns(pl.lit(id_val).alias("id"))
                features = preprocess_actigraphy_daily_features(df)
                all_features.append(features)
            except Exception as e:
                print(f"❌ Failed to process {id_val}: {type(raw_df).__name__} — {e}")

    if all_features:
        return pl.concat(all_features, how="vertical")
    else:
        return pl.DataFrame()

