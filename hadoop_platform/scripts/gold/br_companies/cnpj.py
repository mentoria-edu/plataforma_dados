from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from pyspark.sql.types import StringType, LongType, DoubleType, BooleanType, TimestampType

TABLE_NAME = "company"
DATABASE_NAME = "gold"
SCHEMA_NAME = "br_companies"

spark = SparkSession.builder.appName(f"{DATABASE_NAME}_{TABLE_NAME}").getOrCreate()

main_table = f"silver.{SCHEMA_NAME}__{TABLE_NAME}"
legal_nature_table = f"silver.{SCHEMA_NAME}__legal_nature"
qualification_table = f"silver.{SCHEMA_NAME}__qualification"

company_size_description = when(col("company.company_size") == "00", "NOT INFORMED") \
    .when(col("company.company_size") == "01", "MICRO COMPANY") \
    .when(col("company.company_size") == "03", "SMALL COMPANY") \
    .when(col("company.company_size") == "05", "OTHERS")

df_main = spark.table(main_table).alias("company")
df_legal_nature = spark.table(legal_nature_table).alias("legal_nature")
df_qualification = spark.table(qualification_table).alias("qualification")

result_df = df_main \
    .join(
        df_legal_nature,
        (col("company.legal_nature") == col("legal_nature.id_legal_nature")) &
        (col("company._batch_timestamp") == col("legal_nature._batch_timestamp")),
        "left"
    ) \
    .join(
        df_qualification,
        (col("company.responsible_qualification") == col("qualification.id_qualification")) &
        (col("company._batch_timestamp") == col("qualification._batch_timestamp")),
        "left"
    ) \
    .select(
        col("company.cnpj").cast(LongType()),
        col("company.company_name").cast(StringType()),
        df_legal_nature["description"].alias("description_legal_nature").cast(StringType()),
        df_qualification["description"].alias("description_responsible_qualification").cast(StringType()),
        col("company.share_capital").cast(DoubleType()),
        company_size_description.alias("company_size").cast(StringType()),
        col("company.federative_entity").cast(StringType()),
        col("company._hash").cast(StringType()),
        col("company._is_current").cast(BooleanType()),
        col("company._partition_month").cast(StringType()),
        col("company._batch_timestamp").cast(TimestampType())
    )

hudi_options = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.recordkey.field": "cnpj",
    "hoodie.datasource.write.precombine.field": "_batch_timestamp",
    "hoodie.table.precombine.field": "_batch_timestamp",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.partitionpath.field": "_partition_month"  
}

result_df.write.format("hudi") \
    .mode("overwrite") \
    .options(**hudi_options) \
    .saveAsTable(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")

df = spark.table(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")

df.printSchema()

df.show()
