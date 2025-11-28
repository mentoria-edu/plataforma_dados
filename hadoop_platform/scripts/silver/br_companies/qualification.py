from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, trim, lit
from pyspark.sql.types import TimestampType

TARGET_DATABASE_NAME = "silver"
SOURCE_DATABASE_NAME = "bronze"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "qualification"

SILVER_TABLE = f"{TARGET_DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}"
BRONZE_TABLE = f"{SOURCE_DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}"

HUDI_CONFIGS = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.keygenerator.class": "org.apache.hudi.keygen.ComplexKeyGenerator",
    "hoodie.datasource.write.recordkey.field": "id_qualification,description",
    "hoodie.datasource.write.partitionpath.field": "_partition_month",
    "hoodie.datasource.write.operation": "upsert",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.precombine.field": "_batch_timestamp",
    "hoodie.table.precombine.field": "_batch_timestamp",
    "hoodie.datasource.hive_sync.enable": "false",
}


def clean_bronze_qualification(spark: SparkSession, table: str) -> DataFrame:
    """Clean and normalize input data from the bronze layer.

    Args:
        spark (SparkSession): Spark session.
        table (str): Full path to the bronze table.

    Returns:
        DataFrame: Data cleaned, normalized and ready for SCD2 processing.
    """
    df = spark.table(table)

    df = df.select(
        col("id_qualification"),
        col("description"),
        col("_batch_timestamp"),
        col("_partition_month")
    )

    df = df.withColumn("id_qualification", trim(col("id_qualification")))
    df = df.withColumn("description", trim(col("description")))

    df = df.withColumn("_batch_timestamp", col("_batch_timestamp").cast(TimestampType()))

    df = df.withColumn("_is_current", lit(True))

    return df


def get_changes_qualification(
    spark: SparkSession,
    path_target_table: str,
    source_df: DataFrame
) -> DataFrame:
    """Identify expired rows and new versions for SCD2 processing.

    Args:
        spark (SparkSession): Spark session.
        path_target_table (str): Path of the silver table.
        source_df (DataFrame): Cleaned source DataFrame.

    Returns:
        DataFrame: Expired records (is_current=False) + new versions.
    """
    target_df = spark.table(path_target_table)

    join_cond = [
        target_df.id_qualification == source_df.id_qualification,
        target_df._is_current == True
    ]

    expired_records = target_df.join(source_df, join_cond, "inner")
    expired_records = expired_records.filter(target_df.description != source_df.description)

    expired_records = expired_records.select(
        target_df.id_qualification,
        target_df.description,
        target_df._batch_timestamp,
        target_df._partition_month,
    )

    expired_records = expired_records.withColumn("_is_current", lit(False))

    new_versions = source_df.select(
        "id_qualification",
        "description",
        "_batch_timestamp",
        "_partition_month",
        "_is_current"
    )

    return expired_records.unionByName(new_versions)


def main() -> None:
    """Apply SCD2 logic and write results into Hudi silver table."""
    spark = (
        SparkSession.builder
        .appName("silver_qualification_scd2")
        .enableHiveSupport()
        .config("spark.sql.catalogImplementation", "hive")
        .getOrCreate()
    )

    df_source_cleaned = clean_bronze_qualification(spark, BRONZE_TABLE)

    if spark.catalog.tableExists(SILVER_TABLE):
        df_changes = get_changes_qualification(
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