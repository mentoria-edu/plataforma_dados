from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StringType

PATH_CSV_FILE = "/data_bureau/raw/br_companies/qualifications.csv"
DATABASE_NAME = "bronze"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "qualifications"

spark = SparkSession.builder.appName(f"{DATABASE_NAME}_{TABLE_NAME}").getOrCreate()

df = spark.read.format("csv") \
    .options(
        sep=";",
        header="false", 
        inferSchema="false",
        encoding="UTF-8",
        multiline="true",
    ) \
    .load(PATH_CSV_FILE)

df = df.withColumnsRenamed({
    "_c0": "id_qualification",
    "_c1": "description"
})

df = df \
    .withColumn("id_qualification", col("id_qualification").cast(StringType())) \
    .withColumn("description", col("description").cast(StringType()))

hudi_options = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.recordkey.field": "id_qualification",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.clustering.plan.strategy.sort.columns": "id_qualification",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
}

df.write.format("hudi") \
    .mode("append") \
    .options(**hudi_options) \
    .saveAsTable(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")