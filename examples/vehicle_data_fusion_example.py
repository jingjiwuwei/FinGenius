"""
Example script demonstrating how to use the Vehicle Data Fusion Tool.

This script shows how to merge two Excel files with vehicle sales and configuration data
that have different naming conventions.
"""

import asyncio
import os
import sys


# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd

from src.tool.vehicle_data_fusion import VehicleDataFusionTool, merge_vehicle_data


def create_sample_data():
    """Create sample sales and configuration data for demonstration."""

    # Sample sales data with Chinese column names
    sales_data = {
        "车型": [
            "红旗H5 2023款 1.5T 智联旗享版",
            "红旗H5 2023款 1.8T 豪华版",
            "比亚迪秦PLUS 2023款 DM-i 55KM",
            "比亚迪秦PLUS 2023款 DM-i 120KM",
        ],
        "品牌": ["红旗", "红旗", "比亚迪", "比亚迪"],
        "厂商车系": ["红旗H5", "红旗H5", "秦PLUS", "秦PLUS"],
        "销量": [1250, 980, 5600, 4200],
        "月份": ["2023-10", "2023-10", "2023-10", "2023-10"],
    }

    # Sample configuration data with slightly different naming (simulating different source)
    config_data = {
        "车型名称": [
            "红旗 H5 2023款 1.5T智联 旗享版",
            "红旗 H5 2023 1.8T 豪华型",
            "比亚迪 秦Plus 2023 DM-i 55km",
            "比亚迪 秦Plus DM-i 120km 2023",
        ],
        "品牌名": ["一汽红旗", "一汽红旗", "BYD比亚迪", "BYD比亚迪"],
        "车系": ["H5系列", "H5系列", "秦Plus系列", "秦Plus系列"],
        "发动机": ["1.5T", "1.8T", "DM-i", "DM-i"],
        "变速箱": ["7速双离合", "7速双离合", "E-CVT", "E-CVT"],
        "驱动方式": ["前驱", "前驱", "前驱", "前驱"],
        "座位数": [5, 5, 5, 5],
    }

    # Create DataFrames
    sales_df = pd.DataFrame(sales_data)
    config_df = pd.DataFrame(config_data)

    # Create example directory if not exists
    os.makedirs("examples/data", exist_ok=True)

    # Save to Excel files
    sales_file = "examples/data/sample_sales_data.xlsx"
    config_file = "examples/data/sample_config_data.xlsx"

    sales_df.to_excel(sales_file, index=False)
    config_df.to_excel(config_file, index=False)

    print(f"✓ Created sample sales data: {sales_file}")
    print(f"  Columns: {list(sales_df.columns)}")
    print(f"  Records: {len(sales_df)}\n")

    print(f"✓ Created sample config data: {config_file}")
    print(f"  Columns: {list(config_df.columns)}")
    print(f"  Records: {len(config_df)}\n")

    return sales_file, config_file


async def example_fuzzy_merge():
    """Example of fuzzy matching merge."""
    print("=" * 60)
    print("示例 1: 使用模糊匹配融合数据")
    print("=" * 60 + "\n")

    # Create sample data
    sales_file, config_file = create_sample_data()

    # Define output file
    output_file = "examples/data/merged_vehicle_data_fuzzy.xlsx"

    # Define key columns for matching
    sales_keys = ["车型", "品牌", "厂商车系"]
    config_keys = ["车型名称", "品牌名", "车系"]

    print(f"销量数据关键列: {sales_keys}")
    print(f"配置数据关键列: {config_keys}")
    print(f"相似度阈值: 0.7")
    print(f"匹配方法: 模糊匹配\n")

    # Use the convenience function
    result = await merge_vehicle_data(
        sales_file=sales_file,
        config_file=config_file,
        output_file=output_file,
        sales_keys=sales_keys,
        config_keys=config_keys,
        threshold=0.7,
        method="fuzzy",
    )

    if result.error:
        print(f"❌ 错误: {result.error}")
    else:
        print(result.output)

        # Show a preview of the merged data
        merged_df = pd.read_excel(output_file)
        print("\n合并后的数据预览 (前3行):")
        print(merged_df.head(3).to_string())


async def example_exact_merge():
    """Example of exact matching merge."""
    print("\n" + "=" * 60)
    print("示例 2: 使用精确匹配融合数据")
    print("=" * 60 + "\n")

    # Create sample data with exact matching
    sales_data = {
        "车型": ["ModelA", "ModelB", "ModelC"],
        "品牌": ["BrandX", "BrandY", "BrandX"],
        "销量": [100, 200, 150],
    }

    config_data = {
        "车型名": ["ModelA", "ModelB", "ModelC"],
        "品牌名": ["BrandX", "BrandY", "BrandX"],
        "配置": ["Standard", "Deluxe", "Premium"],
    }

    os.makedirs("examples/data", exist_ok=True)

    sales_file = "examples/data/exact_sales_data.xlsx"
    config_file = "examples/data/exact_config_data.xlsx"

    pd.DataFrame(sales_data).to_excel(sales_file, index=False)
    pd.DataFrame(config_data).to_excel(config_file, index=False)

    output_file = "examples/data/merged_vehicle_data_exact.xlsx"

    # Use exact matching
    tool = VehicleDataFusionTool()
    result = await tool.execute(
        sales_file_path=sales_file,
        config_file_path=config_file,
        output_file_path=output_file,
        sales_key_columns=["车型", "品牌"],
        config_key_columns=["车型名", "品牌名"],
        similarity_threshold=1.0,
        match_method="exact",
    )

    if result.error:
        print(f"❌ 错误: {result.error}")
    else:
        print(result.output)

        # Show merged data
        merged_df = pd.read_excel(output_file)
        print("\n合并后的数据:")
        print(merged_df.to_string())


async def example_with_tool_instance():
    """Example using tool instance directly."""
    print("\n" + "=" * 60)
    print("示例 3: 直接使用工具实例")
    print("=" * 60 + "\n")

    # Create sample data
    sales_file, config_file = create_sample_data()
    output_file = "examples/data/merged_vehicle_data_instance.xlsx"

    # Create tool instance
    tool = VehicleDataFusionTool()

    print(f"工具名称: {tool.name}")
    print(f"工具描述: {tool.description}\n")

    # Execute with custom threshold
    result = await tool.execute(
        sales_file_path=sales_file,
        config_file_path=config_file,
        output_file_path=output_file,
        sales_key_columns=["车型", "品牌"],
        config_key_columns=["车型名称", "品牌名"],
        similarity_threshold=0.6,  # Lower threshold for more lenient matching
        match_method="fuzzy",
    )

    if result.error:
        print(f"❌ 错误: {result.error}")
    else:
        print(result.output)


async def main():
    """Run all examples."""
    print("\n" + "🚗 " * 20)
    print(" " * 15 + "车辆数据融合工具示例")
    print("🚗 " * 20 + "\n")

    # Run examples
    await example_fuzzy_merge()
    await example_exact_merge()
    await example_with_tool_instance()

    print("\n" + "=" * 60)
    print("✓ 所有示例运行完成!")
    print("=" * 60)
    print("\n查看输出文件:")
    print("  - examples/data/merged_vehicle_data_fuzzy.xlsx")
    print("  - examples/data/merged_vehicle_data_exact.xlsx")
    print("  - examples/data/merged_vehicle_data_instance.xlsx\n")


if __name__ == "__main__":
    asyncio.run(main())
