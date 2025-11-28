from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, trim, lit
from pyspark.sql.types import TimestampType

TARGET_DATABASE_NAME = "silver"
SOURCE_DATABASE_NAME = "bronze"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "legal_nature"

SILVER_TABLE = f"{TARGET_DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}"
BRONZE_TABLE = f"{SOURCE_DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}"

HUDI_CONFIGS = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.keygenerator.class": "org.apache.hudi.keygen.ComplexKeyGenerator",
    "hoodie.datasource.write.recordkey.field": "id_legal_nature,description",
    "hoodie.datasource.write.partitionpath.field": "_partition_month",
    "hoodie.datasource.write.operation": "upsert",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.precombine.field": "_batch_timestamp",
    "hoodie.table.precombine.field": "_batch_timestamp",
    "hoodie.datasource.hive_sync.enable": "false",
}


def prepare_bronze_legal_nature(spark: SparkSession, table: str) -> DataFrame:
    """Clean and normalize input data from the bronze layer.

    Args:
        spark (SparkSession): Spark session.
        table (str): Full path to the bronze table.

    Returns:
        DataFrame: Data cleaned, normalized and ready for SCD2 processing.
    """
    df = spark.table(table)

    df = df.select(
        col("id_legal_nature"),
        col("description"),
        col("_batch_timestamp"),
        col("_partition_month")
    )

    df = df.withColumn("id_legal_nature", trim(col("id_legal_nature")))
    df = df.withColumn("description", trim(col("description")))

    df = df.withColumn("_batch_timestamp", col("_batch_timestamp").cast(TimestampType()))

    df = df.withColumn("_is_current", lit(True))

    return df


def get_changes_legal_nature(
    spark: SparkSession,
    path_target_table: str,
    source_df: DataFrame
) -> DataFrame:
    """Identify expired rows and new rows for a SCD2 upsert.

    Args:
        spark (SparkSession): Spark session.
        path_target_table (str): Full table path in the silver layer.
        source_df (DataFrame): Cleaned source DataFrame from bronze.

    Returns:
        DataFrame: Records with expired versions plus new versions.
    """
    target_df = spark.table(path_target_table)

    join_cond = [
        target_df.id_legal_nature == source_df.id_legal_nature,
        target_df._is_current == True
    ]

    expired_records = target_df.join(source_df, join_cond, "inner")
    expired_records = expired_records.filter(target_df.description != source_df.description)

    expired_records = expired_records.select(
        target_df.id_legal_nature,
        target_df.description,
        target_df._batch_timestamp,
        target_df._partition_month,
    )

    expired_records = expired_records.withColumn("_is_current", lit(False))

    new_versions = source_df.select(
        "id_legal_nature",
        "description",
        "_batch_timestamp",
        "_partition_month",
        "_is_current"
    )

    return expired_records.unionByName(new_versions)


def main() -> None:
    """Process SCD2 logic and write results to a Hudi silver table."""
    spark = (
        SparkSession.builder
        .appName("silver_legal_nature_scd2")
        .enableHiveSupport()
        .getOrCreate()
    )

    df_source_cleaned = prepare_bronze_legal_nature(spark, BRONZE_TABLE)

    if spark.catalog.tableExists(SILVER_TABLE):
        df_changes = get_changes_legal_nature(
            spark,
            SILVER_TABLE,
            df_source_cleaned
        )

        df_final = df_source_cleaned.unionByName(df_changes)

        df_final.write.format("hudi") \
            .mode("append") \
            .options(**HUDI_CONFIGS) \
            .insertInto(SILVER_TABLE)

        return

    df_source_cleaned.write.format("hudi") \
        .mode("insert") \
        .options(**HUDI_CONFIGS) \
        .saveAsTable(SILVER_TABLE)

if __name__ == "__main__":
    main()