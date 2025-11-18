from pyspark.sql import SparkSession
from pyspark.sql.functions import date_format, current_timestamp
from pyspark.sql.types import StringType, StructType, StructField

PATH_CSV_FILE = "hdfs://masternode:9000/lakehouse/raw/br_companies/2025-10/cnpj.csv"
DATABASE_NAME = "bronze"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "company"

spark = SparkSession.builder.appName(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}").getOrCreate()

schema = StructType([    
    StructField("cnpj", StringType(), False),
    StructField("company_name", StringType(), True),
    StructField("legal_nature", StringType(), False),
    StructField("responsible_qualification", StringType(), False),
    StructField("share_capital", StringType(), True),
    StructField("company_size", StringType(), True),
    StructField("federative_entity", StringType(), True)
])

df = spark.read \
    .option("header", False) \
    .schema(schema) \
    .option("sep", ";") \
    .option("encoding", "UTF-8") \
    .csv(PATH_CSV_FILE)

df = df.na.fill({"company_size": "00"})

df = df \
    .withColumn("_partition_month", date_format(current_timestamp(), "yyyy-MM")) \
    .withColumn("_batch_timestamp", date_format(current_timestamp(), "yyyy-MM-dd HH:mm:ss")) 

hudi_options = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.recordkey.field": "cnpj",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.partitionpath.field": "_partition_month",
    "hoodie.clustering.plan.strategy.sort.columns": "cnpj"   
}

df.write.format("hudi") \
    .mode("overwrite") \
    .options(**hudi_options) \
    .saveAsTable(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")

df = spark.table(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")

df.show()
