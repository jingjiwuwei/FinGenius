#!/usr/bin/env python3
"""
Quick Data Fusion Script - 快速数据融合脚本

A simple command-line tool for merging vehicle Excel data files.
用于合并车辆 Excel 数据文件的简单命令行工具。

Usage / 用法:
    python quick_fusion.py sales.xlsx config.xlsx output.xlsx

Example / 示例:
    python quick_fusion.py \
        examples/data/sample_sales_data.xlsx \
        examples/data/sample_config_data.xlsx \
        merged_result.xlsx \
        --sales-keys 车型 品牌 厂商车系 \
        --config-keys 车型名称 品牌名 车系 \
        --threshold 0.7
"""

import argparse
import asyncio
import sys
from pathlib import Path


# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tool.vehicle_data_fusion import VehicleDataFusionTool


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Quick Vehicle Data Fusion Tool - 快速车辆数据融合工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples / 示例:

1. Basic fuzzy merge / 基本模糊匹配:
   python quick_fusion.py sales.xlsx config.xlsx output.xlsx \\
       --sales-keys 车型 品牌 --config-keys 车型名称 品牌名

2. Exact merge / 精确匹配:
   python quick_fusion.py sales.xlsx config.xlsx output.xlsx \\
       --sales-keys 车型 品牌 --config-keys 车型名称 品牌名 \\
       --method exact

3. Strict fuzzy merge / 严格模糊匹配:
   python quick_fusion.py sales.xlsx config.xlsx output.xlsx \\
       --sales-keys 车型 品牌 厂商车系 \\
       --config-keys 车型名称 品牌名 车系 \\
       --threshold 0.9
        """,
    )

    parser.add_argument(
        "sales_file", help="Path to sales data Excel file / 销量数据 Excel 文件路径"
    )

    parser.add_argument(
        "config_file",
        help="Path to configuration data Excel file / 配置数据 Excel 文件路径",
    )

    parser.add_argument(
        "output_file", help="Path for merged output Excel file / 输出文件路径"
    )

    parser.add_argument(
        "--sales-keys",
        nargs="+",
        required=True,
        help="Key columns in sales data / 销量数据关键列",
    )

    parser.add_argument(
        "--config-keys",
        nargs="+",
        required=True,
        help="Key columns in config data / 配置数据关键列",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="Similarity threshold (0-1), default 0.8 / 相似度阈值 (0-1)，默认 0.8",
    )

    parser.add_argument(
        "--method",
        choices=["fuzzy", "exact"],
        default="fuzzy",
        help="Matching method: fuzzy or exact, default fuzzy / 匹配方法：模糊或精确，默认模糊",
    )

    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()

    # Validate threshold
    if not 0 <= args.threshold <= 1:
        print("❌ 错误: 相似度阈值必须在 0 到 1 之间")
        print("❌ Error: Similarity threshold must be between 0 and 1")
        return 1

    # Validate key columns count for exact matching
    if args.method == "exact" and len(args.sales_keys) != len(args.config_keys):
        print("❌ 错误: 精确匹配时销量数据和配置数据的关键列数量必须相同")
        print(
            "❌ Error: For exact matching, sales and config must have same number of key columns"
        )
        return 1

    # Validate files exist
    if not Path(args.sales_file).exists():
        print(f"❌ 错误: 销量数据文件不存在: {args.sales_file}")
        print(f"❌ Error: Sales file not found: {args.sales_file}")
        return 1

    if not Path(args.config_file).exists():
        print(f"❌ 错误: 配置数据文件不存在: {args.config_file}")
        print(f"❌ Error: Config file not found: {args.config_file}")
        return 1

    # Display configuration
    print("\n" + "=" * 70)
    print("🚗 车辆数据融合工具 / Vehicle Data Fusion Tool")
    print("=" * 70)
    print(f"\n📥 输入文件 / Input Files:")
    print(f"   销量数据 / Sales:  {args.sales_file}")
    print(f"   配置数据 / Config: {args.config_file}")
    print(f"\n📤 输出文件 / Output File:")
    print(f"   {args.output_file}")
    print(f"\n🔑 关键列 / Key Columns:")
    print(f"   销量 / Sales:  {args.sales_keys}")
    print(f"   配置 / Config: {args.config_keys}")
    print(f"\n⚙️  设置 / Settings:")
    print(f"   匹配方法 / Method:    {args.method}")
    print(f"   相似度阈值 / Threshold: {args.threshold}")
    print("\n" + "-" * 70)
    print("⏳ 处理中... / Processing...")
    print("-" * 70 + "\n")

    # Create tool and execute
    tool = VehicleDataFusionTool()

    try:
        result = await tool.execute(
            sales_file_path=args.sales_file,
            config_file_path=args.config_file,
            output_file_path=args.output_file,
            sales_key_columns=args.sales_keys,
            config_key_columns=args.config_keys,
            similarity_threshold=args.threshold,
            match_method=args.method,
        )

        if result.error:
            print(f"❌ 错误 / Error: {result.error}")
            return 1

        print(result.output)
        print("\n" + "=" * 70)
        print("✅ 完成! / Done!")
        print("=" * 70 + "\n")
        return 0

    except Exception as e:
        print(f"\n❌ 发生错误 / Error occurred: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
