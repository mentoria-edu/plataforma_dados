from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.column import Column
from pyspark.sql.functions import col, when

COMPANY_SIZE_NOT_INFORMED = 0
COMPANY_SIZE_MICRO = 1
COMPANY_SIZE_SMALL = 3
COMPANY_SIZE_OTHERS = 5

DATABASE_NAME = "gold"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "company"
SOURCE_DATABASE = "silver"
GOLD_TABLE_NAME = f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}"

HUDI_OPTIONS = {
    "hoodie.table.name": f"{TABLE_NAME}",
    "hoodie.datasource.write.keygenerator.class": (
        "org.apache.hudi.keygen.ComplexKeyGenerator"
    ),
    "hoodie.datasource.write.recordkey.field": ("cnpj,_attribute_change_hash"),
    "hoodie.datasource.write.partitionpath.field": "_partition_month",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.precombine.field": "_batch_timestamp",
    "hoodie.datasource.hive_sync.enable": "false",
    "hoodie.spark.sql.merge.into.partial.updates": "false",
    "hoodie.cleaner.policy.failed.writes": "LAZY",
}


def get_company_size_description(column: Column) -> Column:
    """
    Maps a company size code column to a human-readable
    company size description.

    Args:
        column (Column): Spark Column containing the company size code.

    Returns:
        Column: Spark Column with the corresponding company size description.
    """
    return (
        when(column == COMPANY_SIZE_NOT_INFORMED, "NOT INFORMED")
        .when(column == COMPANY_SIZE_MICRO, "MICRO COMPANY")
        .when(column == COMPANY_SIZE_SMALL, "SMALL COMPANY")
        .when(column == COMPANY_SIZE_OTHERS, "OTHERS")
        .otherwise(None)
    )


def write_hudi_table(spark: SparkSession, df: DataFrame) -> None:
    """Write DataFrame to Hudi table in gold layer.
    Args:
        spark: Active Spark session.
        df: DataFrame to write.
    Returns:
        None
    """
    if spark.catalog.tableExists(GOLD_TABLE_NAME):
        df.write.format("hudi").mode("overwrite").options(
            **HUDI_OPTIONS
        ).insertInto(GOLD_TABLE_NAME)
        return

    df.write.format("hudi").mode("overwrite").options(**HUDI_OPTIONS).option(
        "hoodie.datasource.write.operation", "bulk_insert"
    ).saveAsTable(GOLD_TABLE_NAME)


def main() -> None:
    spark = SparkSession.builder.appName(
        f"{DATABASE_NAME}_{TABLE_NAME}"
    ).getOrCreate()

    source_df = spark.table(f"{SOURCE_DATABASE}.{SCHEMA_NAME}__{TABLE_NAME}")

    df = source_df.withColumn(
        "company_size_description",
        get_company_size_description(col("company_size")),
    )

    df = df.select(
        "cnpj",
        "company_name",
        "legal_nature",
        "responsible_qualification",
        "share_capital",
        "company_size",
        "company_size_description",
        "federative_entity",
        "_attribute_change_hash",
        "_is_current",
        "_batch_timestamp",
        "_partition_month",
    )

    write_hudi_table(spark, df)


if __name__ == "__main__":
    main()
