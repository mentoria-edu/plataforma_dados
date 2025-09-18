from pyspark.sql import SparkSession
from pyspark.sql.functions import col

TABLE_NAME = "companies"
DATABASE_NAME = "gold"
SCHEMA_NAME = "br_companies"

spark = SparkSession.builder.appName(f"{TABLE_NAME}_{DATABASE_NAME}").getOrCreate()

main_table = f"silver.{SCHEMA_NAME}__{TABLE_NAME}"
legal_nature_table = f"silver.{SCHEMA_NAME}__legal_nature"
qualifications_table = f"silver.{SCHEMA_NAME}__qualifications"

df_main = spark.table(main_table)
df_legal_nature = spark.table(legal_nature_table)
df_qualifications = spark.table(qualifications_table)

result_df = df_main \
    .join(df_legal_nature, col("legal_nature") == col("id_legal_nature"), "left") \
    .join(df_qualifications, col("responsible_qualification") == col("id_qualification"), "left") \
    .select(
        col("cnpj"),
        col("company_name"),
        col("legal_nature").alias("id_legal_nature"),
        df_legal_nature["description"].alias("description_legal_nature"),
        col("responsible_qualification").alias("id_responsible_qualification"),
        df_qualifications["description"].alias("description_responsible_qualification"),
        col("share_capital"),
        col("company_size"),
        col("federative_entity")
    )

hudi_options = {
    "hoodie.table.name": TABLE_NAME,
    "hoodie.datasource.write.recordkey.field": "cnpj",
    "hoodie.datasource.write.operation": "insert",
    "hoodie.clustering.plan.strategy.sort.columns": "cnpj",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
}

result_df.write.format("hudi") \
    .mode("overwrite") \
    .options(**hudi_options) \
    .saveAsTable(f"{DATABASE_NAME}.{SCHEMA_NAME}__{TABLE_NAME}")