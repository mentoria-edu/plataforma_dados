from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import date_format, current_timestamp
from pyspark.sql.types import StringType, StructType, StructField

PATH_CSV_FILE = "hdfs://masternode:9000/lakehouse/raw/br_companies/2025-10/cnpj.csv"
DATABASE_NAME = "bronze"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "company"

HUDI_CONFIGS = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.recordkey.field": "cnpj",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.partitionpath.field": "_partition_month",
    "hoodie.clustering.plan.strategy.sort.columns": "cnpj"   
}

def build_string_schema(col_names: list[str]) -> StructType:
    """
    Create a StructType schema where all fields are StringType.

    Args:
        col_names (list[str]): List of column names.

    Returns:
        StructType: Schema with all fields as StringType.
    """
    return StructType([
        StructField(col_name, StringType(), True) for col_name in col_names
    ])

def add_meta_columns(df: DataFrame) -> DataFrame:
    """
    Add control metadata columns to the DataFrame.

    Adds:
        - _partition_month  (yyyy-MM)
        - _batch_timestamp  (yyyy-MM-dd HH:mm:ss)

    Args:
        df (DataFrame): Input DataFrame.

    Returns:
        DataFrame: DataFrame with metadata fields added.
    """
    return (
        df.withColumn("_partition_month", date_format(current_timestamp(), "yyyy-MM"))
          .withColumn("_batch_timestamp", date_format(current_timestamp(), "yyyy-MM-dd HH:mm:ss"))
    )

def main() -> None:

    spark = SparkSession.builder.appName(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}").getOrCreate()

    table_columns = [
        "cnpj",
        "company_name",
        "legal_nature",
        "responsible_qualification",
        "share_capital",
        "company_size",
        "federative_entity"
    ]

    schema = build_string_schema(table_columns)

    df = (
        spark.read 
            .option("header", False) 
            .schema(schema) 
            .option("sep", ";") 
            .option("encoding", "UTF-8")
            .csv(PATH_CSV_FILE)
    )

    df = add_meta_columns(df)   

    df.write.format("hudi").mode("overwrite").options(**HUDI_CONFIGS ).saveAsTable(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")

if __name__ == "__main__":
    main()
