from pyspark.sql import SparkSession, DataFrame

DATABASE_NAME = "gold"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "qualification"
SOURCE_DATABASE = "silver"
GOLD_TABLE_NAME = f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}"

HUDI_OPTIONS = {
    "hoodie.table.name": f"{TABLE_NAME}",
    "hoodie.datasource.write.keygenerator.class": (
       "org.apache.hudi.keygen.ComplexKeyGenerator"
    ),
    "hoodie.datasource.write.recordkey.field": (
        "id_qualification,_attribute_change_hash"
    ),
    "hoodie.datasource.write.partitionpath.field": "_partition_month",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.precombine.field": "_batch_timestamp",
    "hoodie.datasource.hive_sync.enable": "false",
    "hoodie.spark.sql.merge.into.partial.updates": "false",
    "hoodie.cleaner.policy.failed.writes": "LAZY"
}


def write_hudi_table(spark: SparkSession, df: DataFrame) -> None:
    """Write DataFrame to Hudi table in gold layer.
    Args:
        spark: Active Spark session.
        df: DataFrame to write.
    Returns:
        None
    """
    if spark.catalog.tableExists(GOLD_TABLE_NAME):
        df.write.format("hudi")\
            .mode("overwrite")\
            .options(**HUDI_OPTIONS)\
            .insertInto(GOLD_TABLE_NAME)
        return

    df.write.format("hudi")\
        .mode("overwrite")\
        .options(**HUDI_OPTIONS)\
        .option("hoodie.datasource.write.operation", "bulk_insert")\
        .saveAsTable(GOLD_TABLE_NAME)


def main() -> None:

    spark = SparkSession.builder.appName(
        f"{DATABASE_NAME}_{TABLE_NAME}"
    ).getOrCreate()

    source_df = spark.table(
        f"{SOURCE_DATABASE}.{SCHEMA_NAME}__{TABLE_NAME}"
    )

    df = source_df


    write_hudi_table(spark, df)

if __name__ == "__main__":
    main()
