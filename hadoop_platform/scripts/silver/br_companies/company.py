from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, trim, concat_ws, coalesce, lit, xxhash64
from pyspark.sql.types import DoubleType

TARGET_DATABASE_NAME = "silver"
SOURCE_DATABASE_NAME = "bronze"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "company"

TARGET_TABLE = f"{TARGET_DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}"
BATCH_TABLE = f"{SOURCE_DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}"

HUDI_CONFIGS = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.keygenerator.class": "org.apache.hudi.keygen.ComplexKeyGenerator",
    "hoodie.datasource.write.recordkey.field": "cnpj,_attribute_change_hash",
    "hoodie.datasource.write.partitionpath.field": "_partition_month",
    "hoodie.datasource.write.operation": "upsert",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.precombine.field": "_batch_timestamp",
    "hoodie.table.precombine.field": "_batch_timestamp",
    "hoodie.datasource.hive_sync.enable": "false",
    "hoodie.spark.sql.merge.into.partial.updates": "false",
    "hoodie.cleaner.policy.failed.writes": "LAZY"
}

def prepare_bronze_data(spark: SparkSession, table: str) -> DataFrame:
    """Clean data from the bronze layer.

    Args:
        spark (SparkSession): Active Spark session.
        table (str): Full table path in the bronze layer.

    Returns:
        DataFrame: Cleaned and normalized bronze data with hash and control fields.
    """
    df = spark.table(table)


    df = df.select(
        col("cnpj"),
        col("company_name"),
        col("legal_nature"),
        col("responsible_qualification"),
        col("share_capital"),
        col("company_size"),
        col("federative_entity"),
        col("_batch_timestamp"),
        col("_partition_month")
    )

    df = df.withColumn("cnpj", trim(col("cnpj")))
    df = df.withColumn("company_name", trim(col("company_name")))
    df = df.withColumn("legal_nature", trim(col("legal_nature")))
    df = df.withColumn("responsible_qualification", trim(col("responsible_qualification")))
    df = df.withColumn("company_size", trim(col("company_size")))
    df = df.withColumn("federative_entity", trim(col("federative_entity")))

    df = df.withColumn("share_capital", col("share_capital").cast(DoubleType()))
    df = df.withColumn("_batch_timestamp", col("_batch_timestamp").cast("timestamp"))

    df = df.withColumn("company_size", coalesce(col("company_size"), lit("00")))

    business_cols = [c for c in df.columns if not c.startswith("_")]

    df = df.withColumn(
        "_attribute_change_hash",
        xxhash64(*[col(c) for c in business_cols])
    )

    df = df.withColumn("_is_current", lit(True))
    return df


def get_data_to_update(
    spark: SparkSession,
    path_target_table: str,
    source_df: DataFrame
) -> DataFrame:
    """Identify updated rows for SCD2 processing.

    Args:
        spark (SparkSession): Active Spark session.
        path_target_table (str): Full path of the target silver table.
        source_df (DataFrame): Processed source DataFrame from bronze.

    Returns:
        DataFrame: Union of expired old records and new versions for upsert.
    """
    target_df = spark.table(path_target_table)

    join_cond = [
        target_df._is_current == True,
        target_df.cnpj == source_df.cnpj
    ]

    changed_target = target_df.join(source_df, join_cond, "inner")
    changed_target = changed_target.filter(target_df._attribute_change_hash != source_df._attribute_change_hash)

    changed_target = changed_target.select(
            target_df.cnpj,
            target_df.company_name,
            target_df.legal_nature,
            target_df.responsible_qualification,
            target_df.share_capital,
            target_df.company_size,
            target_df.federative_entity,
            target_df._batch_timestamp,
            target_df._partition_month,
            target_df._attribute_change_hash,
        )

    changed_target = changed_target.withColumn("_is_current", lit(False))

    data_update_df = changed_target.unionByName(
        source_df.select(
            "cnpj",
            "company_name",
            "legal_nature",
            "responsible_qualification",
            "share_capital",
            "company_size",
            "federative_entity",
            "_batch_timestamp",
            "_partition_month",
            "_attribute_change_hash",
            "_is_current"
        )
    )

    return data_update_df


def main() -> None:
    """Execute cleaning and SCD2 upsert logic into a Hudi silver table.

    Returns:
        None
    """
    spark = (
        SparkSession.builder
        .appName("silver_pyspark")
        .enableHiveSupport()
        .getOrCreate()
    )

    df_source_cleaned = prepare_bronze_data(spark, BATCH_TABLE)

    if spark.catalog.tableExists(TARGET_TABLE):
        df_data_to_update = get_data_to_update(
            spark,
            TARGET_TABLE,
            df_source_cleaned
        )

        df_merged_data = df_source_cleaned.unionByName(df_data_to_update)
        df_merged_data.write.format("hudi").mode("append").options(**HUDI_CONFIGS).insertInto(TARGET_TABLE)
        return

    df_source_cleaned.write.format("hudi").mode("insert").options(**HUDI_CONFIGS).saveAsTable(TARGET_TABLE)

if __name__ == "__main__":
    main()