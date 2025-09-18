from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StringType, DoubleType

PATH_CSV_FILE = "/data_bureau/raw/br_companies/companies.csv"
DATABASE_NAME = "bronze"
SCHEMA_NAME = "br_companies"
TABLE_NAME = "companies"

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
    "_c0": "cnpj",
    "_c1": "company_name",
    "_c2": "legal_nature",
    "_c3": "responsible_qualification",
    "_c4": "share_capital",
    "_c5": "company_size",
    "_c6": "federative_entity"
})

df = df.na.fill({"company_size": "00"})

df = df \
    .withColumn("cnpj", col("cnpj").cast(StringType())) \
    .withColumn("company_name", col("company_name").cast(StringType())) \
    .withColumn("legal_nature", col("legal_nature").cast(StringType())) \
    .withColumn("responsible_qualification", col("responsible_qualification").cast(StringType())) \
    .withColumn("share_capital", col("share_capital").cast(DoubleType())) \
    .withColumn("company_size", col("company_size").cast(StringType())) \
    .withColumn("federative_entity", col("federative_entity").cast(StringType()))

hudi_options = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.recordkey.field": "cnpj",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.clustering.plan.strategy.sort.columns": "cnpj",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
}

df.write.format("hudi") \
    .mode("append") \
    .options(**hudi_options) \
    .saveAsTable(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")