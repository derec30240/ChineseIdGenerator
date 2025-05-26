"""
FilePath: chinese_id_generator.py
Author: Dr_Kee
Email: derec30240@163.com
Date: 2025-02-13 18:41:06
LastEditors: Dr_Kee
LastEditTime: 2025-05-26 19:34:18
Copyright (c) 2025 by Dr_Kee. All Rights Reserved.
Description: 
  本模块提供身份证号码生成功能，支持通配符输入和高效并行生成。
  生成的身份证号码符合国家标准（GB 11643-1999）的校验规则。
  行政区划代码基于民政部2022年数据，支持白名单过滤。
"""
import calendar
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import itertools
import json
from multiprocessing import Pool, cpu_count
import re
from tqdm import tqdm


class ChineseIdGenerator:
    """身份证号码生成器核心类"""

    def __init__(self, region_file="region_codes.json"):
        """初始化生成器
        
        Args:
            region_file (str): 行政区划代码JSON文件路径，格式为 {代码: 地区名称}
        """
        # 校验位计算参数（GB 11643-1999标准）
        self.weights = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
        self.check_codes = '10X98765432'

        # 加载行政区划代码白名单
        with open(region_file, "r", encoding="utf-8") as f:
            self.regions = json.load(f)
        self.valid_regions = set(self.regions.keys())  # 有效地区代码集合

    def parallel_generate(self, input_id, processes=None):
        """并行生成主入口
        
        Args:
            input_id (str): 18位输入模式
            processes (int): 进程数（默认使用全部核心）
        
        Returns:
            list: 所有有效身份证号列表
        """
        pattern = self.parse_pattern(input_id)
        check_char = pattern['check']

        # 初始化进度条（尝试预估总数）
        try:
            total = self.estimate_total(pattern)
        except:
            total = None  # 无法预估时显示动态进度

        with tqdm(total=total, desc="生成进度", unit="comb") as pbar:
            with Pool(processes or cpu_count()) as pool:
                chunks = self.generate_components(pattern)
                results = []

                # 分块处理（避免内存不足）
                chunk_size = 100000  # 每批处理10万组合
                while True:
                    batch = list(itertools.islice(chunks, chunk_size))
                    if not batch:
                        break

                    # 并行计算校验码
                    validated = pool.imap_unordered(self.process_batch, batch)
                    for id_list in validated:
                        # 过滤校验位匹配项
                        valid = [
                            id_num for id_num in id_list
                            if check_char in ('-', id_num[-1])
                        ]
                        results.extend(valid)
                        pbar.update(len(id_list))  # 更新进度条

                # 去重并保留顺序
                seen = set()
                final = []
                for id_num in results:
                    if id_num not in seen:
                        seen.add(id_num)
                        final.append(id_num)
                return final

    def parse_pattern(self, pattern):
        """解析18位身份证模式字符串
        
        Args:
            pattern (str): 包含通配符的18位模式（'-'表示任意字符）
        
        Returns:
            dict: 分解后的各部分模式字典
        """
        return {
            'region': pattern[0:6],
            'year': pattern[6:10],
            'month': pattern[10:12],
            'day': pattern[12:14],
            'sequence': pattern[14:17],
            'check': pattern[17]
        }

    def estimate_total(self, pattern):
        """预估总组合数（用于进度条显示）
        
        Args:
            pattern (dict): 解析后的模式字典
        
        Returns:
            int: 预估的候选组合总数
        """
        # 地区码可能性 = 匹配的行政区划代码数量
        region_count = len(self.filter_regions(pattern['region']))
        # 日期可能性 = 智能日期估算引擎计算结果
        date_count = self.estimate_dates(pattern)
        # 顺序码可能性 = 10的（通配符数量）次方
        seq_count = 10**pattern['sequence'].count('-')

        return region_count * date_count * seq_count

    def filter_regions(self, pattern):
        """根据正则表达式过滤有效行政区划代码
        
        Args:
            pattern (str): 行政区划代码模式（支持正则表达式）
        
        Returns:
            list: 匹配的行政区划代码列表
        """
        regex = re.compile(pattern.replace('-', '.'))
        return [code for code in self.valid_regions if regex.match(code)]

    def estimate_dates(self, pattern):
        """日期组合估算引擎（核心优化算法）
        
        采用分治策略：
        1. 按年份分组处理
        2. 按月份并行计算
        3. 根据日期模式选择快速估算或精确计算
        
        Args:
            pattern (dict): 包含年月日模式的分段字典
        
        Returns:
            int: 有效的日期组合总数
        """

        def _estimate_wildcard_days(month, common_max, leap_max, leap_count,
                                    total_years):
            """全通配符快速估算（适用于类似--的日期模式）
            
            Args:
                month (int): 目标月份（1-12）
                common_max (int): 非闰年该月最大天数
                leap_max (int): 闰年该月最大天数（仅2月不同）
                leap_count (int): 闰年总数
                total_years (int): 总年份数
            
            Returns:
                int: 估算的天数组合
            """
            if month != 2:
                # 非二月月份直接取最大值（如--模式在1月表示31天）
                return total_years * common_max
            else:
                # 二月特殊处理：闰年29天 + 非闰年28天
                return leap_count * leap_max + (total_years -
                                                leap_count) * common_max

        def _calculate_exact_days(years, month, day_pattern, common_max,
                                  leap_max):
            """精确日期模式计算（适用于混合模式如1-、-5等）
            
            采用多线程加速：
            1. 将年份分为闰年组和非闰年组
            2. 并行计算两组的天数可能性
            3. 汇总结果
            
            Args:
                years (list): 候选年份列表
                month (int): 目标月份
                day_pattern (str): 日期模式字符串
                common_max (int): 非闰年最大天数
                leap_max (int): 闰年最大天数
            
            Returns:
                int: 精确的天数组合
            """
            count = 0
            year_groups = {
                'leap': [y for y in years if _is_leap_year(y)],
                'common': [y for y in years if not _is_leap_year(y)]
            }

            # 使用线程池并行处理两组计算（提升计算密集型任务效率）
            with ThreadPoolExecutor() as executor:
                futures = []
                for key in ['leap', 'common']:
                    # 确定该组的二月最大天数（仅当月份为2时生效）
                    max_day = leap_max if key == 'leap' and month == 2 else common_max
                    futures.append(
                        executor.submit(_calc_group_days, year_groups[key],
                                        day_pattern, max_day))
                # 汇总各线程结果
                for f in futures:
                    count += f.result()
            return count

        def _calc_group_days(years, day_pattern, max_day):
            """分组天数计算（核心匹配逻辑）
            
            实现细节：
            1. 生成日期候选范围
            2. 使用正则表达式进行模式匹配
            3. 有效天数 × 年数 = 总组合数
            
            Args:
                years (list): 同类型年份列表（全闰年或全非闰年）
                day_pattern (str): 日期模式（如1-、-5）
                max_day (int): 该组最大天数
            
            Returns:
                int: 该年份组的天数组合数
            """
            if not years:
                return 0

            # 解析日期模式长度（始终为2位）
            day_length = len(day_pattern)

            # 计算日期范围（考虑模式约束）
            lower = int(day_pattern.replace('-', '0').ljust(day_length, '0'))
            upper = int(day_pattern.replace('-', '9').ljust(day_length, '9'))
            start = max(1, lower)
            end = min(max_day, upper)

            if start > end:  # 无效范围（如指定2月30日）
                return 0

            # 构建正则表达式（将-替换为.通配符，实现模式匹配）
            regex = re.compile(day_pattern.replace('-', '.'))

            # 统计有效天数（正则匹配优化）
            valid_days = sum(1 for d in range(start, end + 1)
                             if regex.match(f"{d:0{day_length}d}"))

            return len(years) * valid_days

        def _is_leap_year(year):
            """优化的闰年判断算法
            
            规则：
            1. 能被4整除
            2. 且不能被100整除，除非能被400整除
            
            Args:
                year (int): 待判断年份
            
            Returns:
                bool: 是否为闰年
            """
            return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

        # 主逻辑开始----------------------------------------------------
        year_part = pattern['year']
        month_part = pattern['month']
        day_part = pattern['day']

        # 步骤1：生成候选年份（1900-2999之间）
        years = list(self.generate_numbers(year_part, 1900, 2999))
        if not years:
            return 0

        # 步骤2：统计闰年特征
        leap_years = sum(1 for y in years if _is_leap_year(y))
        total_years = len(years)

        # 步骤3：生成候选月份（1-12月）
        months = list(self.generate_numbers(month_part, 1, 12))
        if not months:
            return 0

        # 步骤4：分析日期模式特征
        day_wildcards = day_part.count('-')
        is_special_day = any(c.isdigit() for c in day_part)

        total = 0
        for month in months:
            # 获取基准天数（2001为非闰年）
            common_max_day = calendar.monthrange(2001, month)[1]  # 非闰年
            leap_max_day = 29 if month == 2 else common_max_day

            # 模式决策：全通配符使用快速估算，否则精确计算
            if not is_special_day and day_wildcards > 0:
                total += _estimate_wildcard_days(month, common_max_day,
                                                 leap_max_day, leap_years,
                                                 total_years)
            else:
                total += _calculate_exact_days(years, month, day_part,
                                               common_max_day, leap_max_day)

        return total

    def generate_numbers(self, pattern, min_val, max_val):
        """数值生成核心方法
        
        Args:
            pattern (str): 数字模式（如"199-")
            min_val (int): 最小值
            max_val (int): 最大值
        
        Yields:
            int: 符合要求的数值
        """
        # 处理无通配符情况
        if '-' not in pattern:
            num = int(pattern)
            if min_val <= num <= max_val:
                yield num
            return

        # 计算有效范围（如"199-" → 1990-1999）
        length = len(pattern)
        lower = int(pattern.replace('-', '0').ljust(length, '0'))
        upper = int(pattern.replace('-', '9').ljust(length, '9'))
        start = max(min_val, lower)
        end = min(max_val, upper)

        # 生成候选并过滤（保证模式匹配）
        fmt_str = f"{{:0{length}d}}"
        for num in range(start, end + 1):
            candidate = fmt_str.format(num)
            if all(c == '-' or c == o for c, o in zip(pattern, candidate)):
                yield num

    def generate_components(self, pattern):
        """生成候选组件笛卡尔积
        
        Args:
            pattern (dict): 解析后的模式字典
        
        Returns:
            itertools.product: 候选组件的笛卡尔积生成器
        """
        # 1. 处理行政区划代码
        valid_regions = self.filter_regions(pattern['region'])
        if not valid_regions:
            raise ValueError("无匹配的行政区划代码")

        # 2. 生成有效日期列表
        date_gen = self.generate_dates(pattern['year'], pattern['month'],
                                       pattern['day'])
        dates = list(date_gen)

        # 3. 生成顺序码候选
        seq_gen = self.generate_sequence(pattern['sequence'])

        # 返回三者的笛卡尔积（地区码 × 日期 × 顺序码）
        return itertools.product(valid_regions, dates, seq_gen)

    def generate_dates(self, year_pattern, month_pattern, day_pattern):
        """生成有效日期（YYYYMMDD格式）
        
        采用惰性生成器模式，避免内存爆炸
        
        Args:
            year_pattern (str): 年份模式（如"199-")
            month_pattern (str): 月份模式
            day_pattern (str): 日期模式
        
        Yields:
            str: 符合要求的日期字符串
        """
        # 生成候选年份（1900-2999年）
        for year in self.generate_numbers(year_pattern, 1900, 2999):
            # 生成候选月份（1-12月）
            for month in self.generate_numbers(month_pattern, 1, 12):
                try:
                    # 获取当月最大天数（考虑闰年）
                    max_day = calendar.monthrange(year, month)[1]
                    # 生成候选日期
                    for day in self.generate_numbers(day_pattern, 1, max_day):
                        yield f"{year:04d}{month:02d}{day:02d}"
                except:  # 处理非法月份（如2月30日）
                    continue

    def generate_sequence(self, pattern):
        """生成顺序码候选（3位数字）
        
        Args:
            pattern (str): 顺序码模式（如"01-")
        
        Returns:
            generator: 所有可能的顺序码组合
        """
        wild_count = pattern.count('-')
        if wild_count == 0:  # 无通配符直接返回
            return [pattern]

        # 构建通配符组合（如"01-" → ["010"..."019"]）
        parts = []
        for c in pattern:
            parts.append('0123456789' if c == '-' else c)
        return (''.join(p) for p in itertools.product(*parts))

    def process_batch(self, args):
        """批量生成身份证号并计算校验码（多进程工作单元）
        
        功能说明：
          将行政区划码、日期码、顺序码组合成前17位身份证号，计算校验码后返回完整18位身份证号。
          该函数设计为多进程池的工作单元，需保持无状态且可序列化。
        
        Args:
            args (tuple): 包含以下元素的元组
                - region (str): 6位行政区划代码（如"110101"）
                - date_str (str): 8位出生日期字符串（格式YYYYMMDD）
                - seq (str): 3位顺序码（如"001"）
        
        Returns:
            list[str]: 包含单个有效身份证号的列表（保持返回类型统一以便结果合并）
        """
        # 解包输入参数
        region, date_str, seq = args
        # 组合前17位身份证号
        id_17 = region + date_str + seq
        # 计算校验位（第18位）
        check_code = self.calculate_check_code(id_17)
        # 返回完整身份证号（列表形式保持多进程接口统一）
        return [id_17 + check_code]

    def calculate_check_code(self, id_17):
        """计算校验码（第18位）
        
        Args:
            id_17 (str): 前17位身份证号
        
        Returns:
            str: 校验码（0-9或X）
        """
        total = sum(int(c) * w for c, w in zip(id_17, self.weights))
        return self.check_codes[total % 11]


# 使用示例
if __name__ == "__main__":
    generator = ChineseIdGenerator(region_file="region_codes.json")
    print("行政区划编码来自民政部2022年数据，部分可能具有时效性，请注意辨别")
    while True:
        print("=" * 10)
        input_id = input("请输入需要补全的18位身份号码，缺失处用'-'代替\n")
        # 输入验证
        if len(input_id) != 18 or not all(
                char.isdigit() or char == '-' or char == 'X'
                for char in input_id):
            print("无效的输入格式！")
            continue

        print("正在生成有效的身份号码...")
        results = generator.parallel_generate(input_id)
        print(f"\n共找到 {len(results)} 个有效号码")

        if results:
            # 结果保存
            file_name = datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"
            with open(file_name, "w") as f:
                for id in results:
                    f.write(id + "\n")
            print("完整结果已保存至文件：" + file_name)
            print("示例号码:", results[0])
            print("所属地区:", generator.regions.get(results[0][:6], "未知"))
