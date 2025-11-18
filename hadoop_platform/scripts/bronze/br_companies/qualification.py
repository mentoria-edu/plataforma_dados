from pyspark.sql import SparkSession
from pyspark.sql.functions import date_format, current_timestamp
from pyspark.sql.types import StringType, StructType, StructField

PATH_CSV_FILE = "hdfs://masternode:9000/lakehouse/raw/br_companies/2025-10/qualification.csv"
DATABASE_NAME = "bronze"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "qualification"

spark = SparkSession.builder.appName(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}").getOrCreate()

schema = StructType([
    StructField("id_qualification", StringType(), False),
    StructField("description", StringType(), False),
])

df = spark.read \
    .option("header", False) \
    .schema(schema) \
    .option("sep", ";") \
    .option("encoding", "UTF-8") \
    .csv(PATH_CSV_FILE)

df = df \
    .withColumn("_partition_month", date_format(current_timestamp(), "yyyy-MM")) \
    .withColumn("_batch_timestamp", date_format(current_timestamp(), "yyyy-MM-dd HH:mm:ss")) 

hudi_options = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.recordkey.field": "id_qualification",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
    "hoodie.clustering.plan.strategy.sort.columns": "id_qualification",
    "hoodie.datasource.write.partitionpath.field": "_partition_month"
}

df.write.format("hudi") \
    .mode("overwrite") \
    .options(**hudi_options) \
    .saveAsTable(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")

df = spark.table(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")

df.show()
