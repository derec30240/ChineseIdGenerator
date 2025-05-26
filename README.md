<div align="center">
  <h1>Chinese ID Generator</h1>

  <p>
    A Python script for batch generating Chinese ID numbers.
  </p>
</div>

## Table of Contents

<details>
  <summary>
    Click me to Open/Close the directory listing
  </summary>

  - [Introductions](#introductions)
  - [Features](#features)
  - [File Structure](#file-structure)
  - [Requirements](#requirements)
  - [Usage](#usage)
  - [Example](#example)
    - [Input](#input)
    - [Output](#output)
  - [Notes](#notes)
</details>

## Introductions

This project is a **Chinese ID Number Generator** that supports batch generation of all valid Chinese ID numbers conforming to the national standard (GB 11643-1999) based on user input patterns with wildcards.

- Supports efficient parallel/multiprocessing generation, suitable for large-scale completion, testing, and other scenarios.
- Administrative region codes are based on the Ministry of Civil Affairs 2022 data, with whitelist filtering.
- Generated ID numbers are automatically validated with the check digit to ensure compliance.

## Features

- **Wildcard Support:** `-` can appear in any position, representing any digit (or X, only for the check digit).
- **Efficient Parallelism:** Automatically utilizes multi-core CPUs for parallel generation, supporting large-scale data completion.
- **Smart Date Estimation:** Automatically recognizes leap years and valid date ranges, avoiding invalid dates.
- **Automatic Check Digit Calculation:** Strictly calculates the check digit according to the national standard, ensuring every number is valid.
- **Region Code Filtering:** Only generates IDs for valid administrative regions.

## File Structure

```
├── README.md
├── chinese_id_generator.py
└── region_codes.json
```

- `chinese_id_generator.py`: Main program and core class `ChineseIdGenerator`
- `region_codes.json`: Administrative region code data file (format: `{code: region name}`)

## Requirements

- Python 3.7+
- Dependency: `tqdm`

Install dependencies:

```sh
pip install tqdm
```

## Usage

1. Prepare region data

  Ensure `region_codes.json` is present in the same directory as the script.

2. Run the generator

  ```sh
  python chinese_id_generator.py
  ```

3. Input Pattern

  When prompted, enter an 18-digit ID number pattern, using `-` for unknown positions. For example:

  - `11010119900101----`: Beijing Dongcheng District, January 1, 1990, any sequence code and check digit
  - `44----1998-------X`: Any region in Guangdong Province, any date in 1998, check digit is X

4. Output

  - The program displays generation progress and total combinations.
  - All valid results are automatically saved to a `YYYYMMDD_HHMMSS.txt` file in the current directory.
  - The console shows a sample ID and its corresponding region.

## Example

### Input

```
行政区划编码来自民政部2022年数据，部分可能具有时效性，请注意辨别
==========
请输入需要补全的18位身份号码，缺失处用'-'代替
11010119900101----
```

### Output

```
正在生成有效的身份号码...
生成进度: 100%|██████████| 1000/1000 [00:01<00:00, 550.57comb/s]

共找到 1000 个有效号码
完整结果已保存至文件：20250526_202720.txt
示例号码: 110101199001010007
所属地区: 北京市 东城区
```

## Notes

- Administrative region code data may change over time. It is recommended to update region_codes.json regularly.
- For testing, data completion, and educational purposes only. Strictly prohibited for illegal use.
