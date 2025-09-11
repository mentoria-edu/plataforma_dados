from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp
from pyspark.sql.types import StringType, TimestampType

PATH_CSV_FILE = "/raw/br_companies/qualifications.csv"
DATABASE_NAME = "bronze"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "qualifications"

spark = SparkSession.builder.appName(f"{TABLE_NAME}_{DATABASE_NAME}").getOrCreate()

df = spark.read.csv(
    PATH_CSV_FILE,
    sep=";",
    header=False,
    inferSchema=False
)

df = df.withColumnsRenamed({
    "_c0": "id_qualification",
    "_c1": "description"
})

df = df.withColumn("created_at", current_timestamp())

df = df \
    .withColumn("id_qualification", col("id_qualification").cast(StringType())) \
    .withColumn("description", col("description").cast(StringType())) \
    .withColumn("created_at", col("created_at").cast(TimestampType()))

hudi_options = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.recordkey.field": "id_qualification",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.clustering.plan.strategy.sort.columns": "id_qualification",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
}

spark.sql(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")

df.write.format("hudi") \
    .mode("append") \
    .options(**hudi_options) \
    .saveAsTable(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")