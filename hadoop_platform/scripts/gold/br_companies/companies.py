from pyspark.sql import SparkSession

TABLE_NAME = "companies"
DATABASE_NAME = "gold"
SCHEMA_NAME = "br_companies"

spark = SparkSession.builder.appName(f"{TABLE_NAME}_{DATABASE_NAME}").getOrCreate()

query = f'''
SELECT 
    silver.{SCHEMA_NAME}__{TABLE_NAME}.cnpj,
    silver.{SCHEMA_NAME}__{TABLE_NAME}.company_name, 
    silver.{SCHEMA_NAME}__{TABLE_NAME}.legal_nature AS id_legal_nature,
    silver.{SCHEMA_NAME}__legal_nature.description AS description_legal_nature,
    silver.{SCHEMA_NAME}__{TABLE_NAME}.responsible_qualification AS id_responsible_qualification,
    silver.{SCHEMA_NAME}__qualifications.description AS description_responsible_qualification,
    silver.{SCHEMA_NAME}__{TABLE_NAME}.share_capital,
    silver.{SCHEMA_NAME}__{TABLE_NAME}.company_size,
    silver.{SCHEMA_NAME}__{TABLE_NAME}.federative_entity
FROM
    silver.{SCHEMA_NAME}__{TABLE_NAME}
LEFT JOIN
    silver.{SCHEMA_NAME}__legal_nature
ON
    silver.{SCHEMA_NAME}__{TABLE_NAME}.legal_nature = silver.{SCHEMA_NAME}__legal_nature.id_legal_nature
LEFT JOIN
    silver.{SCHEMA_NAME}__qualifications
ON
    silver.{SCHEMA_NAME}__{TABLE_NAME}.responsible_qualification = silver.{SCHEMA_NAME}__qualifications.id_qualification;
'''

table = spark.sql(query)

hudi_options = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.recordkey.field": "cnpj",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.clustering.plan.strategy.sort.columns": "cnpj",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
}

spark.sql(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")

table.write.format("hudi") \
    .mode("append") \
    .options(**hudi_options) \
    .saveAsTable(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")