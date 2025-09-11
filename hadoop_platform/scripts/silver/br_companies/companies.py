from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim

TABLE_NAME_BRONZE = "bronze.br_companies__companies"
DATABASE_NAME = "silver"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "companies"

spark = SparkSession.builder.appName(f"{TABLE_NAME}_{DATABASE_NAME}").getOrCreate()

df = spark.read.table(TABLE_NAME_BRONZE)

df = df \
    .withColumn("cnpj", trim(col("cnpj"))) \
    .withColumn("company_name", trim(col("company_name"))) \
    .withColumn("company_size", trim(col("company_size")))

hudi_options = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.recordkey.field": "cnpj",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.clustering.plan.strategy.sort.columns": "cnpj",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
}

spark.sql(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")

df.write.format("hudi") \
    .mode("overwrite") \
    .options(**hudi_options) \
    .saveAsTable(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")