import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext
from pyspark.sql.functions import col, countDistinct, sum as spark_sum

# --------------------------------------------------------
# Initialize Glue Job
# --------------------------------------------------------
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# --------------------------------------------------------
# Read Curated Tables
# --------------------------------------------------------
order_items_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="curated_retailflow",
    table_name="order_items"
)

products_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="curated_retailflow",
    table_name="products"
)

order_items_df = order_items_dyf.toDF()
products_df = products_dyf.toDF()

print("order_items_df columns:", order_items_df.columns)
print("products_df columns:", products_df.columns)

# --------------------------------------------------------
# Join Order Items with Products
# --------------------------------------------------------
joined_df = (
    order_items_df.alias("o")
    .join(
        products_df.alias("p"),
        col("o.product_id") == col("p.product_id"),
        "inner"
    )
)

# --------------------------------------------------------
# Gold Aggregation
# --------------------------------------------------------
gold_df = (
    joined_df
    .groupBy(
        col("o.dt"),
        col("p.category")
    )
    .agg(
        countDistinct("o.order_id").alias("total_orders"),
        spark_sum("o.quantity").alias("total_quantity"),
        spark_sum("o.line_total").alias("total_revenue")
    )
)

# --------------------------------------------------------
# Rename Partition Column
# --------------------------------------------------------
gold_df = gold_df.withColumnRenamed("dt", "order_date")

# --------------------------------------------------------
# Convert to DynamicFrame
# --------------------------------------------------------
gold_dyf = DynamicFrame.fromDF(
    gold_df,
    glueContext,
    "gold_dyf"
)

# --------------------------------------------------------
# Write to S3 (Consumption Zone)
# --------------------------------------------------------
glueContext.write_dynamic_frame.from_options(
    frame=gold_dyf,
    connection_type="s3",
    connection_options={
        "path": "s3://retailflow-bucket/consumption/daily_category_revenue/",
        "partitionKeys": ["order_date"]
    },
    format="glueparquet"
)

print("Successfully wrote Gold data to S3.")

# --------------------------------------------------------
# Commit Job
# --------------------------------------------------------
job.commit()
