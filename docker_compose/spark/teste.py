from pyspark.sql import SparkSession

# Inicializa a sessão Spark
spark = SparkSession.builder.appName("SimplesTesteDataFrame").getOrCreate()

# # Obtém o diretório warehouse configurado
# warehouse_dir = spark.conf.get("spark.sql.warehouse.dir")
# print(f"Diretório warehouse: {warehouse_dir}")

# Cria um DataFrame simples
dados = [(1, "Ana"), (2, "Pedro"), (3, "Maria")]
df = spark.createDataFrame(dados, ["id", "nome"])

# Salva o DataFrame no warehouse
df.write.mode("overwrite").saveAsTable("teste_simples")

spark.stop()