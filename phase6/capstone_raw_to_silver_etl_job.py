import sys
import datetime
import boto3

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsgluedq.transforms import EvaluateDataQuality

# ---------------------------------------------------------------------------
# 0. Initialize Glue Contexts
# ---------------------------------------------------------------------------
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

namespace = "RetailFlowDQMetrics"
if "--cw_namespace" in sys.argv:
    namespace = getResolvedOptions(sys.argv, ['cw_namespace'])['cw_namespace']

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

curated_path = "s3://retailflow-bucket/curated/"
quarantine_path = "s3://retailflow-bucket/quarantine/"

# ---------------------------------------------------------------------------
# 1. Read Raw Data from Glue Catalog
# ---------------------------------------------------------------------------

orders_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="retailflow_raw",
    table_name="orders",
    transformation_ctx="orders_source"
)
print("Orders schema:")
orders_dyf.printSchema()

print("Orders count:", orders_dyf.count())

order_items_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="retailflow_raw",
    table_name="order_items",
    transformation_ctx="order_items_source"
)
#print("Order_items schema:")
#order_items_dyf.printSchema()

#print("Order_items count:", order_items_dyf.count())

print(f"[Bookmark] Orders records processed this run: {orders_dyf.count()}")
print(f"[Bookmark] OrderItems records processed this run: {order_items_dyf.count()}")

customers_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="retailflow_raw",
    table_name="customers",
    transformation_ctx="customers_source"
)
#print("customers schema:")
#customers_dyf.printSchema()

#print("customers count:", customers_dyf.count())

products_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="retailflow_raw",
    table_name="products",
    transformation_ctx="products_source"
)

#print("products schema:")
#products_dyf.printSchema()

#print("products count:", products_dyf.count())


# ---------------------------------------------------------------------------
# 2. Define DQDL Rulesets (Completeness only for order_items)
# ---------------------------------------------------------------------------
orders_rules = """
Rules = [
    IsComplete "order_id",
    IsComplete "customer_id",
    IsComplete "status",
    IsUnique "order_id"
]
"""

order_items_rules = """
Rules = [
    IsComplete "order_id",
    IsComplete "product_id",
    IsComplete "quantity",
    IsComplete "unit_price",
    IsComplete "line_total"
]
"""

customers_rules = """
Rules = [
    IsComplete "customer_id",
    IsComplete "customer_name",
    IsUnique "customer_id"
]
"""

products_rules = """
Rules = [
    IsComplete "product_id",
    IsComplete "product_name",
    IsUnique "product_id"
]
"""

# ---------------------------------------------------------------------------
# 3. Apply Data Quality Evaluation (DQDL Completeness/Uniqueness)
# ---------------------------------------------------------------------------
orders_eval = EvaluateDataQuality().process_rows(
    frame=orders_dyf, ruleset=orders_rules,
    publishing_options={"dataQualityEvaluationContext": "orders_quality_eval",
                        "enableDataQualityCloudWatchMetrics": True,
                        "enableDataQualityResultsPublishing": True}
)

order_items_eval = EvaluateDataQuality().process_rows(
    frame=order_items_dyf, ruleset=order_items_rules,
    publishing_options={"dataQualityEvaluationContext": "order_items_quality_eval",
                        "enableDataQualityCloudWatchMetrics": True,
                        "enableDataQualityResultsPublishing": True}
)

customers_eval = EvaluateDataQuality().process_rows(
    frame=customers_dyf, ruleset=customers_rules,
    publishing_options={"dataQualityEvaluationContext": "customers_quality_eval",
                        "enableDataQualityCloudWatchMetrics": True,
                        "enableDataQualityResultsPublishing": True}
)

products_eval = EvaluateDataQuality().process_rows(
    frame=products_dyf, ruleset=products_rules,
    publishing_options={"dataQualityEvaluationContext": "products_quality_eval",
                        "enableDataQualityCloudWatchMetrics": True,
                        "enableDataQualityResultsPublishing": True}
)

# ---------------------------------------------------------------------------
# 4. Referential Integrity check in PySpark (order_items vs products)
# ---------------------------------------------------------------------------
order_items_df = order_items_dyf.toDF()
products_df = products_dyf.toDF()


print("order_items_df columns:", order_items_df.columns)
print("products_df columns:", products_df.columns)

invalid_order_items = order_items_df.join(
    products_df.select("product_id"),
    on="product_id",
    how="left_anti"
)

valid_order_items = order_items_df.join(
    products_df.select("product_id"),
    on="product_id",
    how="left_semi"
)

valid_order_items_dyf = DynamicFrame.fromDF(valid_order_items, glueContext, "valid_order_items_dyf")
invalid_order_items_dyf = DynamicFrame.fromDF(invalid_order_items, glueContext, "invalid_order_items_dyf")

# ---------------------------------------------------------------------------
# 5. Route Records to Curated / Quarantine
# ---------------------------------------------------------------------------
# Orders (split passed vs failed records)

orders_outcomes = orders_eval.select("rowLevelOutcomes")

orders_outcomes_df = orders_outcomes.toDF()
orders_outcomes_dyf = DynamicFrame.fromDF(
    orders_outcomes_df,
    glueContext,
    "orders_outcomes"
)

orders_good = Filter.apply(
    frame=orders_outcomes_dyf,
    f=lambda x: x["DataQualityEvaluationResult"] == "Passed"
)

orders_bad = Filter.apply(
    frame=orders_outcomes_dyf,
    f=lambda x: x["DataQualityEvaluationResult"] == "Failed"
)

if orders_good.count() > 0:
    glueContext.write_dynamic_frame.from_options(
        frame=orders_good,
        connection_type="s3",
        format="glueparquet",
        connection_options={"path": curated_path + "orders/","partitionKeys": ["dt"]
        },
        transformation_ctx="orders_curated"
    )

if orders_bad.count() > 0:
    glueContext.write_dynamic_frame.from_options(
        frame=orders_bad,
        connection_type="s3",
        format="glueparquet",
        connection_options={"path": quarantine_path + "orders/","partitionKeys": ["dt"]
        },
        transformation_ctx="orders_quarantine"
    )


# Order Items (partition by dt)
if valid_order_items_dyf.count() > 0:
    glueContext.write_dynamic_frame.from_options(
        frame=valid_order_items_dyf,
        connection_type="s3",
        format="glueparquet",
        connection_options={"path": curated_path + "order_items/", "partitionKeys": ["dt"]
            
        },
        transformation_ctx="order_items_curated"
    )

if invalid_order_items_dyf.count() > 0:
    glueContext.write_dynamic_frame.from_options(
        frame=invalid_order_items_dyf,
        connection_type="s3",
        format="glueparquet",
        connection_options={"path": quarantine_path + "order_items/", "partitionKeys": ["dt"]
            
        },
        transformation_ctx="order_items_quarantine"
    )

# Customers
glueContext.write_dynamic_frame.from_options(
    frame=customers_dyf, connection_type="s3", format="glueparquet",
    connection_options={"path": curated_path + "customers/"},
    transformation_ctx="customers_curated"
)

# Products
glueContext.write_dynamic_frame.from_options(
    frame=products_dyf, connection_type="s3", format="glueparquet",
    connection_options={"path": curated_path + "products/"},
    transformation_ctx="products_curated"
)

# ---------------------------------------------------------------------------
# 6. Publish Data Quality Metrics to CloudWatch
# ---------------------------------------------------------------------------
cw = boto3.client("cloudwatch", region_name="us-east-1")

items_total = valid_order_items_dyf.count() + invalid_order_items_dyf.count()
items_score = (valid_order_items_dyf.count() / items_total * 100) if items_total > 0 else 100.0

cw.put_metric_data(
    Namespace=namespace,
    MetricData=[
        {"MetricName": "OrderItemsDataQualityScore","Dimensions":[{"Name":"JobName","Value":args["JOB_NAME"]}],
         "Timestamp": datetime.datetime.utcnow(),"Value": items_score,"Unit":"Percent"},
        {"MetricName": "OrderItemsQuarantinedRowCount","Dimensions":[{"Name":"JobName","Value":args["JOB_NAME"]}],
         "Timestamp": datetime.datetime.utcnow(),"Value": float(invalid_order_items_dyf.count()),"Unit":"Count"},
        {"MetricName": "OrdersQuarantinedRowCount","Dimensions":[{"Name":"JobName","Value":args["JOB_NAME"]}],
         "Timestamp": datetime.datetime.utcnow(),"Value": float(orders_bad.count()),"Unit":"Count"}
    ]
)

print(f"[CloudWatch] published ItemsScore={items_score}% "
      f"QuarantinedItems={invalid_order_items_dyf.count()} "
      f"QuarantinedOrders={orders_bad.count()} to namespace {namespace}")

# ---------------------------------------------------------------------------
# 7. Commit Job
# ---------------------------------------------------------------------------
job.commit()
