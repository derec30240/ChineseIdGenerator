# 中国身份号码生成器

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
![Static Badge](https://img.shields.io/badge/license-MIT-blue)
![Static Badge](https://img.shields.io/badge/Python-3.7%2B-yellow)

批量生成中国大陆公民身份号码

*英文版参见[这里](README.md)。*

支持根据用户输入的带有通配符的模式，批量生成所有符合国家标准（[GB 11643-1999](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=080D6FBF2BB468F9007657F26D60013E)）的有效中国身份号码。

本项目具有以下特点：

- **通配符支持：** `-` 可以出现在任何位置，代表任何数字（或X，仅用于校验码）。
- **高效并行：** 自动利用多核CPU进行并行生成，适合大规模补全、测试等场景。
- **智能日期估计：** 自动识别闰年和有效日期范围，避免无效日期。
- **自动校验位计算：** 严格按照国家标准计算校验码，确保合规性。
- **地区代码过滤：** 地址码基于[民政部2022年数据](https://www.mca.gov.cn/mzsj/xzqh/2022/202201xzqh.html)，支持自定义白名单过滤。

> [!CAUTION]
> 本项目仅用于测试、数据补全和教育目的。严禁非法使用。

## 目录

- [安装](#安装)
  - [前置要求](#前置要求)
  - [安装步骤](#安装步骤)
- [用法](#用法)
- [示例](#示例)
- [项目结构](#项目结构)
- [维护者](#维护者)
- [如何贡献](#如何贡献)
- [使用许可](#使用许可)

## 安装

### 前置要求

- [Python 3.7+](https://www.python.org/)
- [pip](https://pypi.org/project/pip/)

### 安装步骤

1. 克隆本仓库到本地

   ```sh
   git clone https://github.com/你的用户名/ChineseIdGenerator.git
   ```

2. 安装依赖项

   ```sh
   pip install tqdm
   ```

## 用法

1. 准备地址码

   确保`region_codes.json`与脚本位于同一目录下。

2. 运行生成器

   ```sh
   python chinese_id_generator.py
   ```

3. 输入格式

   出现提示时，输入一个18位的身份号码，用`-`表示未知位。例如：

   - `11010119900101----`：北京市东城区，1990年1月1日，任意顺序码与校验码
   - `44----1998-------X`：广东省任意地区，1998年任意时间，任意顺序码，校验码为X

4. 输出

   生成过程中会显示进度条与总的组合个数。

   生成完毕后，所有有效结果将自动保存至同一目录下的`YYYYMMDD_HHMMSS.txt`。程序将展示其中一个示例号码与其对应的行政区划。

## 示例

```
行政区划编码来自民政部2022年数据，部分可能具有时效性，请注意辨别
==========
请输入需要补全的18位身份号码，缺失处用'-'代替
1101011999
无效的输入格式！
==========
请输入需要补全的18位身份号码，缺失处用'-'代替
11010119900101----
正在生成有效的身份号码...
生成进度: 100%|██████████| 1000/1000 [00:01<00:00, 550.57comb/s]

共找到 1000 个有效号码
完整结果已保存至文件：20250526_202720.txt
示例号码: 110101199001010007
所属地区: 北京市 东城区
==========
请输入需要补全的18位身份号码，缺失处用'-'代替
```

## 项目结构

```
├── chinese_id_generator.py
└── region_codes.json
```

项目主要包括以下2个文件：

- `chinese_id_generator.py`：主程序与核心类`ChineseIdGenerator`
- `region_codes.json`：官方地址码数据集（格式：`{地址码: 行政区划名称}`）

## 维护者

[@Dr_Kee](https://github.com/derec30240)

## 如何贡献

[提一个Issue](https://github.com/derec30240/ChineseIdGenerator/issues/new)或者提交Pull Requests。

> [!NOTE]
> 如果要编辑README，请遵循[standard-readme](https://github.com/RichardLitt/standard-readme)规范。

## 使用许可

[MIT](LICENSE) © Dr_Kee
