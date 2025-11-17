# 车辆数据融合工具 (Vehicle Data Fusion Tool)

## 概述 (Overview)

车辆数据融合工具是为 FinGenius 平台开发的一个数据处理工具，用于解决来自不同数据源的车辆销量数据和配置数据融合问题。该工具特别适用于处理具有不同命名规范的数据集。

The Vehicle Data Fusion Tool is a data processing tool developed for the FinGenius platform to solve the problem of merging vehicle sales data and configuration data from different data sources, especially when they have different naming conventions.

## 问题背景 (Problem Background)

在汽车行业数据分析中，常常需要整合来自不同来源的数据：
- 一份数据包含按车型和车款分类的销量信息
- 另一份数据包含按车型和车款分类的配置信息

由于数据来源不同，对车型、品牌、厂商车系等字段的命名方式可能存在差异，例如：
- "红旗H5" vs "红旗 H5"
- "比亚迪" vs "BYD比亚迪"
- "秦PLUS" vs "秦Plus系列"

这使得简单的精确匹配难以完成数据融合。

## 解决方案 (Solution)

本工具提供了两种数据融合方法：

### 1. 模糊匹配 (Fuzzy Matching)
使用字符串相似度算法（基于 SequenceMatcher）来匹配不同命名规范的数据。可以处理：
- 大小写差异
- 空格差异
- 轻微的拼写差异
- 命名格式差异

### 2. 精确匹配 (Exact Matching)
传统的精确匹配方法，适用于数据格式统一的场景。

## 功能特性 (Features)

✅ **模糊匹配**: 基于相似度算法的智能匹配  
✅ **可配置阈值**: 自定义相似度阈值（0-1）  
✅ **多列匹配**: 支持多个关键列组合匹配  
✅ **Excel 支持**: 直接读写 Excel 文件  
✅ **匹配统计**: 提供详细的匹配率和统计信息  
✅ **匹配得分**: 在结果中包含每条记录的匹配得分  

## 安装 (Installation)

工具依赖已包含在 FinGenius 的 requirements.txt 中：
```bash
pip install -r requirements.txt
```

主要依赖：
- pandas: Excel 文件读写和数据处理
- openpyxl: Excel 文件格式支持

## 使用方法 (Usage)

### 方法 1: 使用便捷函数

```python
import asyncio
from src.tool.vehicle_data_fusion import merge_vehicle_data

async def main():
    result = await merge_vehicle_data(
        sales_file='data/sales.xlsx',
        config_file='data/config.xlsx',
        output_file='data/merged.xlsx',
        sales_keys=['车型', '品牌', '厂商车系'],
        config_keys=['车型名称', '品牌名', '车系'],
        threshold=0.7,
        method='fuzzy'
    )
    
    if result.error:
        print(f"错误: {result.error}")
    else:
        print(result.output)

asyncio.run(main())
```

### 方法 2: 使用工具类

```python
import asyncio
from src.tool.vehicle_data_fusion import VehicleDataFusionTool

async def main():
    tool = VehicleDataFusionTool()
    
    result = await tool.execute(
        sales_file_path='data/sales.xlsx',
        config_file_path='data/config.xlsx',
        output_file_path='data/merged.xlsx',
        sales_key_columns=['车型', '品牌'],
        config_key_columns=['车型名称', '品牌名'],
        similarity_threshold=0.8,
        match_method='fuzzy'
    )
    
    print(result.output if not result.error else result.error)

asyncio.run(main())
```

## 参数说明 (Parameters)

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `sales_file_path` | str | ✅ | 销量数据 Excel 文件路径 |
| `config_file_path` | str | ✅ | 配置数据 Excel 文件路径 |
| `output_file_path` | str | ✅ | 输出文件路径 |
| `sales_key_columns` | List[str] | ✅ | 销量数据中用于匹配的列名 |
| `config_key_columns` | List[str] | ✅ | 配置数据中用于匹配的列名 |
| `similarity_threshold` | float | ❌ | 相似度阈值（0-1），默认 0.8 |
| `match_method` | str | ❌ | 匹配方法：'fuzzy' 或 'exact'，默认 'fuzzy' |

## 运行示例 (Run Example)

项目包含完整的示例脚本：

```bash
cd /home/runner/work/FinGenius/FinGenius
python examples/vehicle_data_fusion_example.py
```

示例会：
1. 创建样例数据（销量数据和配置数据）
2. 演示模糊匹配融合
3. 演示精确匹配融合
4. 演示直接使用工具实例

运行后会在 `examples/data/` 目录下生成以下文件：
- `merged_vehicle_data_fuzzy.xlsx` - 模糊匹配结果
- `merged_vehicle_data_exact.xlsx` - 精确匹配结果
- `merged_vehicle_data_instance.xlsx` - 工具实例示例结果

## 输出说明 (Output)

融合后的 Excel 文件包含：
1. **原销量数据的所有列**
2. **配置数据的列**（添加 `config_` 前缀以避免冲突）
3. **match_score**（仅模糊匹配）：表示匹配置信度（0-1）

### 示例输出

```
数据融合完成！

融合方法: fuzzy
相似度阈值: 0.7

数据统计:
- 销量数据记录数: 4
- 配置数据记录数: 4
- 成功融合记录数: 4
- 匹配率: 100.00%

输出文件: examples/data/merged_vehicle_data_fuzzy.xlsx
```

## 最佳实践 (Best Practices)

### 1. 选择合适的相似度阈值

- **0.9-1.0**: 非常严格，适用于数据质量很高的场景
- **0.7-0.9**: 推荐值，适用于大多数场景
- **0.5-0.7**: 宽松匹配，适用于数据差异较大的场景
- **<0.5**: 不推荐，可能导致错误匹配

### 2. 选择关键列

选择能够唯一标识记录的列组合：
```python
# 好的选择
sales_keys = ['车型', '品牌', '厂商车系']
config_keys = ['车型名称', '品牌名', '车系']

# 可能不够
sales_keys = ['品牌']  # 单列可能不够唯一
```

### 3. 检查匹配结果

使用 `match_score` 列来审查匹配质量：
```python
import pandas as pd

# 读取结果
df = pd.read_excel('merged_output.xlsx')

# 查看低分匹配（可能需要人工检查）
low_score_matches = df[df['match_score'] < 0.8]
print(low_score_matches)
```

### 4. 处理未匹配数据

```python
# 读取原始销量数据和融合结果
sales_df = pd.read_excel('sales.xlsx')
merged_df = pd.read_excel('merged_output.xlsx')

# 找出未匹配的记录
unmatched_count = len(sales_df) - len(merged_df)
print(f"未匹配记录数: {unmatched_count}")
```

## 技术实现 (Technical Details)

### 相似度计算

使用 Python 标准库 `difflib.SequenceMatcher` 计算字符串相似度：

```python
from difflib import SequenceMatcher

def calculate_similarity(str1, str2):
    # 标准化字符串
    str1 = str1.lower().strip()
    str2 = str2.lower().strip()
    
    # 计算相似度
    return SequenceMatcher(None, str1, str2).ratio()
```

### 复合键匹配

对于多列匹配，工具会创建复合键：
```python
composite_key = f"{车型}||{品牌}||{厂商车系}"
```

然后对复合键进行相似度计算。

## 故障排除 (Troubleshooting)

### 问题 1: 匹配率过低

**原因**: 相似度阈值设置过高或数据差异太大

**解决方案**:
- 降低 `similarity_threshold` 参数
- 检查关键列选择是否合适
- 尝试减少用于匹配的列数

### 问题 2: 错误匹配

**原因**: 相似度阈值设置过低

**解决方案**:
- 提高 `similarity_threshold` 参数
- 增加更多关键列以提高匹配精度
- 考虑使用 `exact` 匹配方法

### 问题 3: 列名未找到错误

**原因**: 指定的列名在数据中不存在

**解决方案**:
```python
import pandas as pd

# 检查可用的列名
sales_df = pd.read_excel('sales.xlsx')
config_df = pd.read_excel('config.xlsx')

print("销量数据列:", list(sales_df.columns))
print("配置数据列:", list(config_df.columns))
```

## 性能考虑 (Performance Considerations)

- **小数据集** (<1000 条): 性能优秀，通常在秒级完成
- **中等数据集** (1000-10000 条): 需要数秒到数十秒
- **大数据集** (>10000 条): 可能需要分批处理

对于大数据集，建议：
1. 使用更严格的阈值减少计算量
2. 减少用于匹配的列数
3. 考虑先进行初步过滤

## 扩展和集成 (Extension and Integration)

### 集成到 FinGenius Agent

可以将此工具集成到 FinGenius 的 Agent 系统中：

```python
from src.agent.base import BaseAgent
from src.tool.vehicle_data_fusion import VehicleDataFusionTool

class DataFusionAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fusion_tool = VehicleDataFusionTool()
    
    async def process(self, sales_file, config_file):
        result = await self.fusion_tool.execute(
            sales_file_path=sales_file,
            config_file_path=config_file,
            output_file_path='output.xlsx',
            sales_key_columns=['车型', '品牌'],
            config_key_columns=['车型名称', '品牌名'],
            similarity_threshold=0.8,
            match_method='fuzzy'
        )
        return result
```

## 贡献 (Contributing)

欢迎提交问题和改进建议！可以通过以下方式参与：
1. 报告 Bug
2. 提出新功能建议
3. 提交 Pull Request

## 许可证 (License)

本工具遵循 FinGenius 项目的 GPL v3 许可证。

## 联系方式 (Contact)

如有问题或建议，请通过 GitHub Issues 联系我们。

---

**免责声明**: 本工具仅用于数据处理和分析，不构成任何投资建议。
