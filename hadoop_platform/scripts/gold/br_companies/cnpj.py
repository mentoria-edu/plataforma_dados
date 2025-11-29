from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, broadcast
from pyspark.sql.column import Column
from pyspark.sql.types import StringType, LongType, DoubleType, BooleanType, TimestampType

TABLE_NAME = "company"
DATABASE_NAME = "gold"
SCHEMA_NAME = "br_companies"

HUDI_CONFIGS = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.recordkey.field": "cnpj",
    "hoodie.datasource.write.precombine.field": "_batch_timestamp",
    "hoodie.table.precombine.field": "_batch_timestamp",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.partitionpath.field": "_partition_month"  
}


def get_company_size_description(col_name: str) -> Column:
    """
    Map a company_size code column to a human-readable description.

    Args:
        col_name (str): Nome da coluna com o código de tamanho da empresa.

    Returns:
        Column: Expressão Spark contendo a descrição correspondente.
    """
    return (
        when(col(col_name) == "00", "NOT INFORMED")
        .when(col(col_name) == "01", "MICRO COMPANY")
        .when(col(col_name) == "03", "SMALL COMPANY")
        .when(col(col_name) == "05", "OTHERS")
        .otherwise(None)
    )


def main() -> None:

    spark = SparkSession.builder.appName(f"{DATABASE_NAME}_{TABLE_NAME}").getOrCreate()

    main_table = f"silver.{SCHEMA_NAME}__{TABLE_NAME}"
    legal_nature_table = f"silver.{SCHEMA_NAME}__legal_nature"
    qualification_table = f"silver.{SCHEMA_NAME}__qualification"

    df_main = spark.table(main_table).alias("company")
    df_legal_nature = spark.table(legal_nature_table).alias("legal_nature")
    df_qualification = spark.table(qualification_table).alias("qualification")

    df_joined = (
        df_main
            .join(
                broadcast(df_legal_nature),
                (
                    (col("company.legal_nature") == col("legal_nature.id_legal_nature")) &
                    (col("company._batch_timestamp") == col("legal_nature._batch_timestamp"))
                ),
                "left"
            )
            .join(
                broadcast(df_qualification),
                (
                    (col("company.responsible_qualification") == col("qualification.id_qualification")) &
                    (col("company._batch_timestamp") == col("qualification._batch_timestamp"))
                ),
                "left"
            )
    )
    

    company_size_description = get_company_size_description("company.company_size").alias("size_description")


    result_df = (
        df_joined.select(
            col("company.cnpj").cast(LongType()).alias("cnpj"),
            col("company.company_name").cast(StringType()).alias("company_name"),
            col("legal_nature.description").alias("description_legal_nature"),
            col("qualification.description").alias("description_responsible_qualification"),
            col("company.share_capital").cast(DoubleType()).alias("share_capital"),
            company_size_description,
            col("company.federative_entity"),
            col("company._attribute_change_hash"),
            col("company._is_current"),
            col("company._batch_timestamp"),
            col("company._partition_month")
        )
    )     

    result_df = (
        result_df
            .withColumn("cnpj", col("cnpj").cast(LongType()))
            .withColumn("company_name", col("company_name").cast(StringType()))
            .withColumn("description_legal_nature", col("description_legal_nature").cast(StringType()))
            .withColumn("description_responsible_qualification", col("description_responsible_qualification").cast(StringType()))
            .withColumn("share_capital", col("share_capital").cast(DoubleType()))
            .withColumn("size_description", col("size_description").cast(StringType()))
            .withColumn("federative_entity", col("federative_entity").cast(DoubleType()))            
            .withColumn("size_description", col("size_description").cast(StringType()))
            .withColumn("_attribute_change_hash", col("_attribute_change_hash").cast(StringType()))
            .withColumn("_is_current", col("_is_current").cast(BooleanType()))
            .withColumn("_batch_timestamp", col("_batch_timestamp").cast(TimestampType()))
            .withColumn("_partition_month", col("_partition_month").cast(StringType()))
    )

    result_df.write.format("hudi").mode("overwrite").options(**HUDI_CONFIGS).saveAsTable(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")
    

if __name__ == "__main__":
    main()
