# Chinese ID Generator

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
![Static Badge](https://img.shields.io/badge/license-MIT-blue)
![Static Badge](https://img.shields.io/badge/Python-3.7%2B-yellow)

Batch generating Chinese ID numbers

[English](README.md) | [简体中文](README.zh-CN.md)

Support the batch generation of all valid Chinese identity numbers that comply with national standards ([GB 11643-1999](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=080D6FBF2BB468F9007657F26D60013E)) based on the wildcard patterns input by users.

This project has the following characteristics:

- **Wildcard support** : `-` can appear in any position and represent any number (or X, only used for check codes).
- **Efficient Parallelism** : Automatically utilizes multi-core CPUs for parallel generation, suitable for large-scale completion, testing and other scenarios.
- **Intelligent Date Estimation** : Automatically identify leap years and valid date ranges to avoid invalid dates.
- **Automatic check bit calculation:** Check codes are calculated strictly in accordance with national standards to ensure compliance.
- **Area code filtering:** The address code is based on [the data of the Ministry of Civil Affairs in 2022](https://www.mca.gov.cn/mzsj/xzqh/2022/202201xzqh.html) and supports custom whitelist filtering.

> [!CAUTION]
> This project is only for testing, data completion and educational purposes. Illegal use is strictly prohibited.

## Table of Contents

- [Install](#install)
  - [Prerequisite](#prerequisite)
  - [Installation Steps](#installation-steps)
- [Usage](#usage)
- [Example](#example)
- [File Structure](#file-structure)
- [Maintainers](#maintainers)
- [Contributing](#contributing)
- [License](#license)

## Install

### Prerequisite

- [Python 3.7+](https://www.python.org/)
- [pip](https://pypi.org/project/pip/)

### Installation Steps

1. Clone the repository to local

   ```sh
   git clone https://github.com/your_username/ChineseIdGenerator.git
   ```

2. Install dependencies

   ```sh
   pip install tqdm
   ```

## Usage

1. Prepare the address code

   Make sure that `region_codes.json` is in the same directory as the script.

2. Run the generator

   ```sh
   python chinese_id_generator.py
   ```

3. Input pattern

   When prompted, enter an 18-digit ID number pattern, using `-` for unknown positions. For example:

   - `11010119900101----`: Beijing Dongcheng District, January 1, 1990, any sequence code and check digit
   - `44----1998-------X`: Any region in Guangdong Province, any date in 1998, any sequence code, check digit is X

4. Output

   During the generation process, the progress bar and the total number of combinations will be displayed.

   After the generation is completed, all valid results will be automatically saved to `YYYYMMDD_HHMMSS.txt` in the same directory. One of the sample numbers will be displayed together with its corresponding administrative division.

## Example

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

## File Structure

```
├── chinese_id_generator.py
└── region_codes.json
```

The project mainly includes the following two documents:

- `chinese_id_generator.py`: Main program and core class `ChineseIdGenerator`
- `region_codes.json`: Administrative region code data file (format: `{code: region name}`)

## Maintainers

[@Dr_Kee](https://github.com/derec30240)

## Contributing

[Open an issue](https://github.com/derec30240/ChineseIdGenerator/issues/new) or submit PRs.

> [!NOTE]
> If editing the README，please conform to the [standard-readme](https://github.com/RichardLitt/standard-readme) specification.

## License

[MIT](LICENSE) © Dr_Kee
