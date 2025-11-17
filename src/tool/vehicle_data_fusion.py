"""
Vehicle Data Fusion Tool

This tool provides functionality to merge two Excel datasets with different naming conventions.
It uses fuzzy matching to align column names and entity names (vehicle models, brands, series).

Use Case:
- Merge sales data with configuration data
- Handle inconsistent naming conventions across different data sources
- Support for vehicle model, brand, and manufacturer series matching
"""

from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from src.tool.base import BaseTool, ToolResult


class VehicleDataFusionTool(BaseTool):
    """Tool for merging vehicle sales and configuration data with fuzzy matching."""

    name: str = "vehicle_data_fusion"
    description: str = """
    Merge two Excel files containing vehicle data with different naming conventions.
    Uses fuzzy matching to align column names and entity names (vehicle models, brands, series).
    
    Parameters:
    - sales_file_path: Path to the sales data Excel file
    - config_file_path: Path to the configuration data Excel file
    - output_file_path: Path where the merged result will be saved
    - sales_key_columns: List of column names in sales data to use for matching (e.g., ['车型', '品牌', '厂商车系'])
    - config_key_columns: List of column names in config data to use for matching (e.g., ['车型名称', '品牌名', '车系'])
    - similarity_threshold: Minimum similarity score (0-1) for matching, default 0.8
    - match_method: Matching method - 'fuzzy' (default) or 'exact'
    """

    parameters: dict = {
        "type": "object",
        "properties": {
            "sales_file_path": {
                "type": "string",
                "description": "Path to the sales data Excel file",
            },
            "config_file_path": {
                "type": "string",
                "description": "Path to the configuration data Excel file",
            },
            "output_file_path": {
                "type": "string",
                "description": "Path where the merged result will be saved",
            },
            "sales_key_columns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of column names in sales data to use for matching",
            },
            "config_key_columns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of column names in config data to use for matching",
            },
            "similarity_threshold": {
                "type": "number",
                "description": "Minimum similarity score (0-1) for matching, default 0.8",
                "default": 0.8,
            },
            "match_method": {
                "type": "string",
                "enum": ["fuzzy", "exact"],
                "description": "Matching method - 'fuzzy' (default) or 'exact'",
                "default": "fuzzy",
            },
        },
        "required": [
            "sales_file_path",
            "config_file_path",
            "output_file_path",
            "sales_key_columns",
            "config_key_columns",
        ],
    }

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using SequenceMatcher.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score between 0 and 1
        """
        if not str1 or not str2:
            return 0.0

        # Normalize strings: convert to lowercase and strip whitespace
        str1_normalized = str(str1).lower().strip()
        str2_normalized = str(str2).lower().strip()

        return SequenceMatcher(None, str1_normalized, str2_normalized).ratio()

    def _find_best_match(
        self, target: str, candidates: List[str], threshold: float = 0.8
    ) -> Optional[Tuple[str, float]]:
        """
        Find the best matching string from candidates.

        Args:
            target: String to match
            candidates: List of candidate strings
            threshold: Minimum similarity threshold

        Returns:
            Tuple of (best_match, score) or None if no match above threshold
        """
        best_match = None
        best_score = 0.0

        for candidate in candidates:
            score = self._calculate_similarity(target, candidate)
            if score > best_score:
                best_score = score
                best_match = candidate

        if best_score >= threshold:
            return (best_match, best_score)
        return None

    def _align_column_names(
        self,
        sales_columns: List[str],
        config_columns: List[str],
        threshold: float = 0.7,
    ) -> Dict[str, str]:
        """
        Create a mapping between sales and config column names using fuzzy matching.

        Args:
            sales_columns: Column names from sales data
            config_columns: Column names from config data
            threshold: Similarity threshold for matching

        Returns:
            Dictionary mapping sales columns to config columns
        """
        column_mapping = {}

        for sales_col in sales_columns:
            match_result = self._find_best_match(sales_col, config_columns, threshold)
            if match_result:
                config_col, score = match_result
                column_mapping[sales_col] = config_col

        return column_mapping

    def _create_composite_key(self, row: pd.Series, columns: List[str]) -> str:
        """
        Create a composite key from multiple columns.

        Args:
            row: DataFrame row
            columns: List of column names to combine

        Returns:
            Composite key string
        """
        values = [str(row.get(col, "")).strip() for col in columns]
        return "||".join(values)

    def _fuzzy_merge_dataframes(
        self,
        sales_df: pd.DataFrame,
        config_df: pd.DataFrame,
        sales_keys: List[str],
        config_keys: List[str],
        threshold: float = 0.8,
    ) -> pd.DataFrame:
        """
        Merge two dataframes using fuzzy matching on key columns.

        Args:
            sales_df: Sales data DataFrame
            config_df: Configuration data DataFrame
            sales_keys: Key columns in sales data
            config_keys: Key columns in config data
            threshold: Similarity threshold for matching

        Returns:
            Merged DataFrame
        """
        # Create composite keys
        sales_df["_composite_key"] = sales_df.apply(
            lambda row: self._create_composite_key(row, sales_keys), axis=1
        )
        config_df["_composite_key"] = config_df.apply(
            lambda row: self._create_composite_key(row, config_keys), axis=1
        )

        # Store all config composite keys for matching
        config_keys_list = config_df["_composite_key"].tolist()

        # Create mapping from sales to config indices
        match_mapping = []
        for idx, sales_key in enumerate(sales_df["_composite_key"]):
            match_result = self._find_best_match(sales_key, config_keys_list, threshold)
            if match_result:
                matched_key, score = match_result
                config_idx = config_df[
                    config_df["_composite_key"] == matched_key
                ].index[0]
                match_mapping.append(
                    {"sales_idx": idx, "config_idx": config_idx, "match_score": score}
                )

        # Perform the merge based on the mapping
        merged_rows = []
        for mapping in match_mapping:
            sales_row = sales_df.iloc[mapping["sales_idx"]].to_dict()
            config_row = config_df.iloc[mapping["config_idx"]].to_dict()

            # Combine rows, prefixing config columns to avoid conflicts
            merged_row = sales_row.copy()
            for key, value in config_row.items():
                if key not in merged_row and key != "_composite_key":
                    merged_row[f"config_{key}"] = value

            merged_row["match_score"] = mapping["match_score"]
            merged_rows.append(merged_row)

        result_df = pd.DataFrame(merged_rows)

        # Remove temporary composite key columns
        if "_composite_key" in result_df.columns:
            result_df = result_df.drop(columns=["_composite_key"])
        if "config__composite_key" in result_df.columns:
            result_df = result_df.drop(columns=["config__composite_key"])

        return result_df

    async def execute(
        self,
        sales_file_path: str,
        config_file_path: str,
        output_file_path: str,
        sales_key_columns: List[str],
        config_key_columns: List[str],
        similarity_threshold: float = 0.8,
        match_method: str = "fuzzy",
    ) -> ToolResult:
        """
        Execute the vehicle data fusion.

        Args:
            sales_file_path: Path to sales Excel file
            config_file_path: Path to config Excel file
            output_file_path: Path for output merged file
            sales_key_columns: Key columns in sales data for matching
            config_key_columns: Key columns in config data for matching
            similarity_threshold: Minimum similarity score for matching
            match_method: 'fuzzy' or 'exact' matching method

        Returns:
            ToolResult with merge statistics
        """
        try:
            # Read Excel files
            sales_df = pd.read_excel(sales_file_path)
            config_df = pd.read_excel(config_file_path)

            # Validate key columns exist
            for col in sales_key_columns:
                if col not in sales_df.columns:
                    return ToolResult(
                        error=f"Sales key column '{col}' not found in sales data. Available columns: {list(sales_df.columns)}"
                    )

            for col in config_key_columns:
                if col not in config_df.columns:
                    return ToolResult(
                        error=f"Config key column '{col}' not found in config data. Available columns: {list(config_df.columns)}"
                    )

            # Perform merge based on method
            if match_method == "exact":
                # For exact matching, we need to align column names first
                if len(sales_key_columns) != len(config_key_columns):
                    return ToolResult(
                        error=f"For exact matching, sales_key_columns and config_key_columns must have the same length"
                    )

                # Rename config columns to match sales columns
                rename_dict = {
                    config_key_columns[i]: sales_key_columns[i]
                    for i in range(len(sales_key_columns))
                }
                config_df_renamed = config_df.rename(columns=rename_dict)

                # Perform exact merge
                merged_df = pd.merge(
                    sales_df,
                    config_df_renamed,
                    on=sales_key_columns,
                    how="left",
                    suffixes=("", "_config"),
                )
            else:
                # Fuzzy matching
                merged_df = self._fuzzy_merge_dataframes(
                    sales_df,
                    config_df,
                    sales_key_columns,
                    config_key_columns,
                    similarity_threshold,
                )

            # Save merged result
            merged_df.to_excel(output_file_path, index=False)

            # Generate statistics
            total_sales_records = len(sales_df)
            total_config_records = len(config_df)
            total_merged_records = len(merged_df)
            match_rate = (
                (total_merged_records / total_sales_records * 100)
                if total_sales_records > 0
                else 0
            )

            stats = {
                "method": match_method,
                "similarity_threshold": similarity_threshold,
                "sales_records": total_sales_records,
                "config_records": total_config_records,
                "merged_records": total_merged_records,
                "match_rate_percent": round(match_rate, 2),
                "output_file": output_file_path,
                "sales_columns": list(sales_df.columns),
                "config_columns": list(config_df.columns),
                "merged_columns": list(merged_df.columns),
            }

            output_message = f"""
数据融合完成！

融合方法: {match_method}
相似度阈值: {similarity_threshold}

数据统计:
- 销量数据记录数: {total_sales_records}
- 配置数据记录数: {total_config_records}
- 成功融合记录数: {total_merged_records}
- 匹配率: {match_rate:.2f}%

输出文件: {output_file_path}
            """

            return ToolResult(output=output_message)

        except FileNotFoundError as e:
            return ToolResult(error=f"文件未找到: {str(e)}")
        except Exception as e:
            return ToolResult(error=f"数据融合失败: {str(e)}")


# Convenience function for easy import
async def merge_vehicle_data(
    sales_file: str,
    config_file: str,
    output_file: str,
    sales_keys: List[str],
    config_keys: List[str],
    threshold: float = 0.8,
    method: str = "fuzzy",
) -> Dict[str, Any]:
    """
    Convenience function to merge vehicle data.

    Args:
        sales_file: Path to sales Excel file
        config_file: Path to config Excel file
        output_file: Path for output file
        sales_keys: Key columns in sales data
        config_keys: Key columns in config data
        threshold: Similarity threshold (0-1)
        method: 'fuzzy' or 'exact'

    Returns:
        Dictionary with merge results
    """
    tool = VehicleDataFusionTool()
    result = await tool.execute(
        sales_file_path=sales_file,
        config_file_path=config_file,
        output_file_path=output_file,
        sales_key_columns=sales_keys,
        config_key_columns=config_keys,
        similarity_threshold=threshold,
        match_method=method,
    )
    return result
