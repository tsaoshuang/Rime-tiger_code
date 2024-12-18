#
# python 04-gen_moss_tiger_dict.py ../dicts/moss.basic.dict.yaml --dict data/moran.basic.dict.yaml
# python 04-gen_moss_tiger_dict.py ../dicts/moss.phrase.dict.yaml --dict data/phrase.dict.yaml
# python 04-gen_moss_tiger_dict.py ../dicts/moss.words.dict.yaml --dict data/moran.words.dict.yaml
# python 04-gen_moss_tiger_dict.py ../dicts/moss.tencent.dict.yaml --dict data/moran.tencent.dict.yaml
# python 04-gen_moss_tiger_dict.py ../dicts/moss.computer.dict.yaml --dict data/moran.computer.dict.yaml
# python 04-gen_moss_tiger_dict.py ../dicts/moss.moe.dict.yaml --dict data/moran.moe.dict.yaml

import argparse
import os
from datetime import datetime

def load_char_codes(moss_dict_path):
    """加载单字编码表"""
    char_codes = {}  # {字符: (编码, 权重)}
    
    with open(moss_dict_path, 'r', encoding='utf-8') as f:
        # 跳过文件头
        for line in f:
            if line.strip() == '...':
                break
                
        # 读取编码
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('\t')
            if len(parts) >= 3:
                char, code, weight = parts[0], parts[1], int(parts[2])
                # 只有当字符不存在,或新的权重更大时才更新
                if char not in char_codes or weight > char_codes[char][1]:
                    char_codes[char] = (code, weight)
    
    return char_codes

def format_code(code):
    """格式化编码，确保']'后的部分长度为2"""
    if ']' in code:
        prefix, suffix = code.split(']')
        # 如果']'后只有一个字符，补0
        if len(suffix) == 1:
            return f"{prefix}]{suffix}0"
    return code

def process_dict_dict(dict_dict_path, char_codes):
    """处理词典，如果没有权重则默认为1，并格式化编码"""
    entries = []
    
    with open(dict_dict_path, 'r', encoding='utf-8') as f:
        # 跳过文件头
        for line in f:
            if line.strip() == '...':
                break
                
        # 处理每个词条
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # 解析原始词条
            parts = line.split('\t')
            if not parts:
                continue
                
            word = parts[0]
            try:
                weight = int(parts[-1])
            except (ValueError, IndexError):
                weight = 1
            
            # 获取每个字的编码
            codes = []
            valid = True
            
            for char in word:
                if char in char_codes:
                    code = char_codes[char][0]  # 获取编码
                    code = format_code(code)    # 格式化编码
                    codes.append(code)
                else:
                    valid = False
                    break
            
            if valid:
                code_str = ' '.join(codes)
                entries.append((word, code_str, weight))
    
    return entries

def get_dict_name(dict_path):
    """从词典路径中提取名称"""
    # 获取文件名(不含路径和扩展名)
    base_name = os.path.splitext(os.path.basename(dict_path))[0]
    # 去掉 .dict 后缀（如果存在）
    if base_name.endswith('.dict'):
        base_name = base_name[:-5]  # 去掉 '.dict' 后缀
    # 提取最后一个点后面的部分作为核心名称
    core_name = base_name.split('.')[-1]
    # 添加 moss. 前缀
    return f'moss.{core_name}'

def write_output(output_path, entries, dict_name):
    """写入输出文件，包含完整的文件头信息，并按权重排序"""
    # 按权重降序排序（权重大的排在前面）
    sorted_entries = sorted(entries, key=lambda x: x[2], reverse=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # 写入文件头
        f.write('# Rime dictionary\n')
        f.write('# encoding: utf-8\n')
        f.write('# Generated by Hertz Hwang <https://github.com/hertz-hwang>\n\n')
        
        f.write('---\n')
        f.write(f'name: {dict_name}\n')
        f.write(f'version: "{datetime.now().strftime("%Y.%m.%d")}"\n')
        f.write('sort: by_weight\n')
        f.write('use_preset_vocabulary: false\n')
        f.write('columns:\n')
        f.write('  - text\n')
        f.write('  - code\n')
        f.write('  - weight\n')
        f.write('...\n\n')
        
        # 写入排序后的词条
        for word, codes, weight in sorted_entries:
            f.write(f'{word}\t{codes}\t{weight}\n')

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='生成词典的编码')
    parser.add_argument('output', help='输出文件路径')
    parser.add_argument('--moss', default='../dicts/moss.base.dict.yaml', help='单字码表路径 (默认: ../dicts/moss.dict.yaml)')
    parser.add_argument('--dict', help='要处理的词典路径')
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.moss):
        print(f'错误: 单字码表文件不存在: {args.moss}')
        return
    if not os.path.exists(args.dict):
        print(f'错误: 词典文件不存在: {args.dict}')
        return
        
    # 创建输出目录(如果不存在)
    output_dir = os.path.dirname(args.output)
    if output_dir:  # 只在有目录部分时创建
        os.makedirs(output_dir, exist_ok=True)
    
    # 处理流程
    char_codes = load_char_codes(args.moss)
    entries = process_dict_dict(args.dict, char_codes)
    dict_name = get_dict_name(args.dict)
    write_output(args.output, entries, dict_name)
    
    print(f'处理完成! 输出文件: {args.output}')

if __name__ == '__main__':
    main()
