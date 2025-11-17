# Examples / 示例

This directory contains example scripts demonstrating how to use FinGenius tools.

本目录包含演示如何使用 FinGenius 工具的示例脚本。

## Vehicle Data Fusion / 车辆数据融合

### Quick Start / 快速开始

**Option 1: Quick Fusion Script / 快速融合脚本**

For quick command-line usage:

```bash
python examples/quick_fusion.py \
    sales.xlsx \
    config.xlsx \
    output.xlsx \
    --sales-keys 车型 品牌 厂商车系 \
    --config-keys 车型名称 品牌名 车系 \
    --threshold 0.7
```

**Option 2: Full Example Script / 完整示例脚本**

For comprehensive examples with sample data:

```bash
python examples/vehicle_data_fusion_example.py
```

This will:
- Create sample sales and configuration data
- Demonstrate fuzzy matching
- Demonstrate exact matching
- Show different usage patterns

### Files / 文件

- **`quick_fusion.py`**: Command-line tool for quick data fusion / 快速数据融合命令行工具
- **`vehicle_data_fusion_example.py`**: Comprehensive examples with sample data / 带示例数据的完整示例
- **`data/`**: Generated sample and output files (ignored by git) / 生成的示例和输出文件（被 git 忽略）

### Documentation / 文档

For detailed documentation, see:
- [Vehicle Data Fusion Guide](../docs/vehicle_data_fusion_guide.md)

详细文档请参见：
- [车辆数据融合指南](../docs/vehicle_data_fusion_guide.md)

## Requirements / 依赖

All examples require the FinGenius dependencies:

```bash
pip install -r requirements.txt
```

所有示例都需要安装 FinGenius 的依赖：

```bash
pip install -r requirements.txt
```
