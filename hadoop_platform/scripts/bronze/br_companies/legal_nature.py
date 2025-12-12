from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col,
    current_timestamp,
    from_utc_timestamp,
    lit,
    xxhash64
)
from pyspark.sql.types import StringType, StructField, StructType
from datetime import datetime

DATABASE_NAME = "bronze"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "legal_nature"
BRONZE_TABLE_NAME = f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}"

HUDI_OPTIONS = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.keygenerator.class": "org.apache.hudi.keygen.ComplexKeyGenerator",
    "hoodie.datasource.write.recordkey.field": "id_legal_nature,_attribute_change_hash",
    "hoodie.datasource.write.partitionpath.field": "_partition_month",
    "hoodie.datasource.write.operation": "insert_overwrite",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.precombine.field": "_batch_timestamp",
    "hoodie.datasource.hive_sync.enable": "false",
    "hoodie.spark.sql.merge.into.partial.updates": "false",
    "hoodie.cleaner.policy.failed.writes": "LAZY"
}

SCHEMA = StructType([
    StructField("id_legal_nature", StringType(), True),
    StructField("description", StringType(), True),
])


def transform_date(batch_month: str) -> int:
    """Convert batch month string to integer partition format.

    Args:
        batch_month: Date string in YYYY-MM format.

    Returns:
        int: Partition month in YYYYMM format.

    Raises:
        ValueError: If batch_month is not in YYYY-MM format.
    """
    try:
        datetime.strptime(batch_month, "%Y-%m")
        return int(batch_month.replace("-", ""))
    except Exception:
        raise ValueError(
            f"Invalid date format. Expected ISO pattern YYYY-MM but received: {batch_month}"
        )


def read_csv_file(spark: SparkSession, path: str, schema: StructType) -> DataFrame:
    """Read CSV file into a DataFrame.

    Args:
        spark: Active Spark session.
        path: Path to the CSV file.
        schema: Schema definition for the CSV data.

    Returns:
        DataFrame: Raw CSV data as DataFrame.
    """
    df = (
        spark.read.format("csv")
        .options(
            sep=";",
            header="false",
            encoding="UTF-8",
        )
        .schema(schema)
        .load(path)
    )
    return df


def add_columns_hash(df: DataFrame) -> DataFrame:
    """Add attribute change hash column to DataFrame.

    Args:
        df: Source DataFrame.

    Returns:
        DataFrame: DataFrame with _attribute_change_hash column added.
    """
    business_cols = [c for c in df.columns if not c.startswith("_")]

    df = df.withColumn(
        "_attribute_change_hash",
        xxhash64(*[col(c) for c in business_cols])
    )
    return df


def add_date_columns(df: DataFrame, partition_month_int: int) -> DataFrame:
    """Add batch timestamp and partition month columns to DataFrame.

    Args:
        df: Source DataFrame.
        partition_month_int: Partition month in YYYYMM format.

    Returns:
        DataFrame: DataFrame with _batch_timestamp and _partition_month columns added.
    """
    df = (
        df.withColumn(
            "_batch_timestamp",
            from_utc_timestamp(current_timestamp(), "America/Sao_Paulo"),
        )
        .withColumn(
            "_partition_month", lit(partition_month_int)
        )
    )
    return df


def write_hudi_table(spark: SparkSession, df: DataFrame) -> None:
    """Write DataFrame to Hudi table in bronze layer.

    Args:
        spark: Active Spark session.
        df: DataFrame to write.

    Returns:
        None
    """
    if spark.catalog.tableExists(BRONZE_TABLE_NAME):
        df.write.format("hudi")\
            .mode("append")\
            .options(**HUDI_OPTIONS)\
            .insertInto(BRONZE_TABLE_NAME)
        return

    df.write.format("hudi")\
        .mode("overwrite")\
        .options(**HUDI_OPTIONS)\
        .option("hoodie.datasource.write.operation", "bulk_insert")\
        .saveAsTable(BRONZE_TABLE_NAME)


def main() -> None:
    """Execute bronze layer ingestion pipeline for legal nature data.

    Returns:
        None
    """
    spark = SparkSession.builder.appName(f"{DATABASE_NAME}_{TABLE_NAME}").getOrCreate()

    PATH_CSV_FILE = spark.conf.get("spark.csv.path")
    BATCH_MONTH = spark.conf.get("spark.input.date")

    partition_month_int = transform_date(BATCH_MONTH)

    df = read_csv_file(spark, PATH_CSV_FILE, SCHEMA)
    df = add_columns_hash(df)
    df = add_date_columns(df, partition_month_int)
    df = df.withColumn("_is_current", lit(True))

    write_hudi_table(spark, df)

if __name__ == "__main__":
    main()