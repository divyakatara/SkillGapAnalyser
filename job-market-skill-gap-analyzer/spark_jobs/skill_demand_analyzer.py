"""
PySpark job for analyzing skill demand at scale.
Processes job descriptions and computes aggregated skill metrics.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, explode, count, desc, lit, round as spark_round, collect_list
)
from pyspark.sql.types import StringType, ArrayType
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillDemandAnalyzer:
    """PySpark-based analyzer for computing skill demand metrics."""
    
    def __init__(self, app_name: str = "JobMarketSkillAnalyzer"):
        """Initialize Spark session."""
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .master("local[*]") \
            .config("spark.driver.memory", "2g") \
            .config("spark.executor.memory", "2g") \
            .config("spark.sql.shuffle.partitions", "4") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info(f"Spark session created: {app_name}")
    
    def load_jobs_with_skills(self, jobs_csv_path: str) -> "DataFrame":
        """
        Load jobs CSV with skills column.
        
        Args:
            jobs_csv_path: Path to jobs CSV file with 'skills' column
            
        Returns:
            Spark DataFrame
        """
        logger.info(f"Loading jobs from {jobs_csv_path}")
        
        df = self.spark.read.csv(
            jobs_csv_path,
            header=True,
            inferSchema=True,
            escape='"'
        )
        
        # Parse skills column (assuming it's stored as JSON string or Python list string)
        @udf(ArrayType(StringType()))
        def parse_skills(skills_str):
            if not skills_str:
                return []
            try:
                # Try JSON parsing first
                return json.loads(skills_str)
            except:
                # Fallback: parse Python list string
                import ast
                try:
                    return ast.literal_eval(skills_str)
                except:
                    return []
        
        from pyspark.sql.functions import udf
        parse_skills_udf = udf(parse_skills, ArrayType(StringType()))
        
        df = df.withColumn("skills_parsed", parse_skills_udf(col("skills")))
        
        total_jobs = df.count()
        logger.info(f"Loaded {total_jobs} jobs")
        
        return df
    
    def compute_skill_demand(self, jobs_df: "DataFrame") -> "DataFrame":
        """
        Compute skill demand metrics using PySpark.
        
        Args:
            jobs_df: Spark DataFrame with skills
            
        Returns:
            DataFrame with skill demand statistics
        """
        logger.info("Computing skill demand metrics")
        
        total_jobs = jobs_df.count()
        
        # Explode skills array to individual rows
        skills_exploded = jobs_df.select(
            col("job_id"),
            explode(col("skills_parsed")).alias("skill")
        )
        
        # Aggregate skill counts
        skill_demand = skills_exploded.groupBy("skill") \
            .agg(count("*").alias("job_count")) \
            .withColumn("total_jobs", lit(total_jobs)) \
            .withColumn("percentage", 
                       spark_round((col("job_count") / col("total_jobs") * 100), 2)) \
            .orderBy(desc("job_count"))
        
        # Add demand category
        skill_demand = skill_demand.withColumn(
            "demand_level",
            when(col("percentage") >= 30, "High")
            .when(col("percentage") >= 10, "Medium")
            .otherwise("Low")
        )
        
        unique_skills = skill_demand.count()
        logger.info(f"Found {unique_skills} unique skills")
        
        return skill_demand
    
    def compute_skill_cooccurrence(self, jobs_df: "DataFrame", min_support: int = 5) -> "DataFrame":
        """
        Find skills that frequently appear together.
        
        Args:
            jobs_df: Spark DataFrame with skills
            min_support: Minimum number of jobs for a skill pair
            
        Returns:
            DataFrame with skill pairs and co-occurrence counts
        """
        from pyspark.sql.functions import array_sort, size
        
        logger.info("Computing skill co-occurrence patterns")
        
        # Filter jobs with at least 2 skills
        jobs_with_skills = jobs_df.filter(size(col("skills_parsed")) >= 2)
        
        # Create pairs of skills per job
        from pyspark.sql.functions import expr
        
        skill_pairs = jobs_with_skills.select(
            col("job_id"),
            explode(
                expr("transform(skills_parsed, (x, i) -> transform(filter(skills_parsed, (y, j) -> j > i), y -> struct(x as skill1, y as skill2)))")
            ).alias("pair_struct")
        ).select(
            col("job_id"),
            col("pair_struct.skill1"),
            col("pair_struct.skill2")
        )
        
        # Alternative simpler approach using self-join
        skills_exploded = jobs_with_skills.select(
            col("job_id"),
            explode(col("skills_parsed")).alias("skill")
        )
        
        # Self join to create pairs
        skill_pairs_simple = skills_exploded.alias("a").join(
            skills_exploded.alias("b"),
            (col("a.job_id") == col("b.job_id")) & (col("a.skill") < col("b.skill"))
        ).select(
            col("a.job_id"),
            col("a.skill").alias("skill1"),
            col("b.skill").alias("skill2")
        )
        
        # Count co-occurrences
        cooccurrence = skill_pairs_simple.groupBy("skill1", "skill2") \
            .agg(count("*").alias("cooccurrence_count")) \
            .filter(col("cooccurrence_count") >= min_support) \
            .orderBy(desc("cooccurrence_count"))
        
        logger.info(f"Found {cooccurrence.count()} skill pairs")
        
        return cooccurrence
    
    def aggregate_by_category(self, skill_demand_df: "DataFrame", 
                              skill_dict_path: str = "nlp/skill_dictionary.json") -> "DataFrame":
        """
        Aggregate skills by category.
        
        Args:
            skill_demand_df: DataFrame with skill demand
            skill_dict_path: Path to skill dictionary
            
        Returns:
            DataFrame with category-level aggregation
        """
        logger.info("Aggregating skills by category")
        
        # Load skill dictionary
        with open(skill_dict_path, 'r') as f:
            skill_dict = json.load(f)
        
        # Create skill to category mapping
        skill_to_category = {}
        for category, skills in skill_dict.items():
            for skill in skills:
                skill_to_category[skill] = category
        
        # Broadcast the mapping
        category_map = self.spark.sparkContext.broadcast(skill_to_category)
        
        @udf(StringType())
        def get_category(skill):
            return category_map.value.get(skill, "other")
        
        from pyspark.sql.functions import udf
        get_category_udf = udf(get_category, StringType())
        
        # Add category and aggregate
        categorized = skill_demand_df.withColumn(
            "category",
            get_category_udf(col("skill"))
        )
        
        category_demand = categorized.groupBy("category") \
            .agg(
                count("*").alias("unique_skills"),
                sum("job_count").alias("total_mentions"),
                spark_round(avg("percentage"), 2).alias("avg_percentage")
            ) \
            .orderBy(desc("total_mentions"))
        
        return category_demand
    
    def save_results(self, df: "DataFrame", output_path: str, format: str = "csv"):
        """
        Save results to file.
        
        Args:
            df: Spark DataFrame to save
            output_path: Output file path
            format: Output format ('csv', 'json', 'parquet')
        """
        logger.info(f"Saving results to {output_path}")
        
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if format == "csv":
            # Coalesce to single file for easier consumption
            df.coalesce(1).write.mode("overwrite") \
                .option("header", "true") \
                .csv(str(output_path))
        elif format == "json":
            df.coalesce(1).write.mode("overwrite").json(str(output_path))
        elif format == "parquet":
            df.write.mode("overwrite").parquet(str(output_path))
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Results saved successfully")
    
    def stop(self):
        """Stop Spark session."""
        self.spark.stop()
        logger.info("Spark session stopped")


from pyspark.sql.functions import udf, when, sum, avg


def main():
    """Main execution function."""
    analyzer = SkillDemandAnalyzer()
    
    try:
        # Configuration
        input_path = "data/processed/jobs_with_skills.csv"
        output_dir = "data/processed"
        
        # Check if input exists
        if not Path(input_path).exists():
            logger.warning(f"Input file not found: {input_path}")
            logger.info("Run scraper and NLP extraction first")
            return
        
        # Load jobs
        jobs_df = analyzer.load_jobs_with_skills(input_path)
        
        # Compute skill demand
        skill_demand = analyzer.compute_skill_demand(jobs_df)
        skill_demand.show(20, truncate=False)
        
        # Save skill demand
        analyzer.save_results(
            skill_demand,
            f"{output_dir}/skill_demand",
            format="csv"
        )
        
        # Compute co-occurrence
        cooccurrence = analyzer.compute_skill_cooccurrence(jobs_df)
        cooccurrence.show(10, truncate=False)
        
        # Save co-occurrence
        analyzer.save_results(
            cooccurrence,
            f"{output_dir}/skill_cooccurrence",
            format="csv"
        )
        
        # Category aggregation
        category_demand = analyzer.aggregate_by_category(skill_demand)
        category_demand.show(truncate=False)
        
        # Save category demand
        analyzer.save_results(
            category_demand,
            f"{output_dir}/category_demand",
            format="csv"
        )
        
        print("\n" + "="*60)
        print("Spark Analysis Complete")
        print("="*60)
        print(f"Total unique skills: {skill_demand.count()}")
        print(f"Skill pairs analyzed: {cooccurrence.count()}")
        print(f"Categories: {category_demand.count()}")
        print("="*60 + "\n")
        
    finally:
        analyzer.stop()


if __name__ == "__main__":
    main()
