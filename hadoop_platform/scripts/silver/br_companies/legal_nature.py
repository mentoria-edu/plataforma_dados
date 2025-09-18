from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim

TABLE_NAME_BRONZE = "bronze.br_companies__legal_nature"
DATABASE_NAME = "silver"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "legal_nature"

spark = SparkSession.builder.appName(f"{DATABASE_NAME}_{TABLE_NAME}").getOrCreate()

df = spark.read.table(TABLE_NAME_BRONZE)

df = df \
    .withColumn("id_legal_nature", trim(col("id_legal_nature"))) \
    .withColumn("description", trim(col("description")))

df = df.filter(
    col("description").isNotNull() & 
    (col("description") != "")
)

df = df.dropDuplicates(["id_legal_nature"])

hudi_options = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.recordkey.field": "id_legal_nature",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.clustering.plan.strategy.sort.columns": "id_legal_nature",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
}

df.write.format("hudi") \
    .mode("overwrite") \
    .options(**hudi_options) \
    .saveAsTable(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")