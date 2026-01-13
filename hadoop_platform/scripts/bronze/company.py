from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import upper, trim, regexp_replace, col
from pyspark.sql.types import StringType, StructField, StructType
from typing import Dict
from base_bronze_pipeline import BaseBronzePipeline


class CompanyPipeline(BaseBronzePipeline):
    """Pipeline for company data ingestion with custom transformations."""
    
    def define_schema(self) -> StructType:
        """Define schema for company CSV data.
        
        Returns:
            StructType: Schema with company identification and classification columns.
        """
        return StructType([
            StructField("cnpj", StringType(), True),
            StructField("company_name", StringType(), True),
            StructField("legal_nature", StringType(), True),
            StructField("responsible_qualification", StringType(), True),
            StructField("share_capital", StringType(), True),
            StructField("company_size", StringType(), True),
            StructField("federative_entity", StringType(), True),
        ])
    
    def primary_key_column(self) -> str:
        """Return primary key column name.
        
        Returns:
            str: Primary key column 'cnpj'.
        """
        return "cnpj"
    
    def configure_csv_options(self) -> Dict[str, str]:
        """Configure custom CSV options for company data.
        
        Returns:
            Dict[str, str]: CSV reading options with comma separator.
        """
        return {
            "sep": ",",
            "header": "false",
            "encoding": "UTF-8",
        }


def main() -> None:
    """Execute company pipeline from Spark configuration."""
    spark = SparkSession.builder.appName("bronze_company").getOrCreate()
    
    csv_path = spark.conf.get("spark.csv.path")
    batch_month = spark.conf.get("spark.input.date")
    
    pipeline = CompanyPipeline(
        spark=spark,
        schema_name="br_companies",
        table_name="company"
    )
    
    pipeline.run(csv_path, batch_month)
    spark.stop()


if __name__ == "__main__":
    main()