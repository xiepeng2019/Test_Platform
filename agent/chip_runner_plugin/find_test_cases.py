#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通过用例编号查找匹配的测试用例路径。
"""

import os
import ast
import argparse
import sys


def extract_case_id_from_function(func_node):
    """
    从函数的文档字符串中提取用例编号。
    假设用例编号在文档字符串的第一行，并且以特定格式存在。
    例如: "测试用例编号：BW_CPU_SYS_FUNC_TC0001" 或 "测试编号: BW_CPU_SYS_FUNC_TC0001" 或 "BW_CPU_SYS_FUNC_TC0001"
    """
    if not func_node.body or not isinstance(func_node.body[0], ast.Expr):
        return None

    docstring_node = func_node.body[0].value
    if not isinstance(docstring_node, ast.Constant) or not isinstance(docstring_node.value, str):
        return None

    docstring = docstring_node.value.strip()
    if not docstring:
        return None

    # 尝试从文档字符串中提取用例编号
    lines = docstring.split('\n')
    first_line = lines[0]
    case_id = None
    if '：' in first_line:
        case_id = first_line.split('：', 1)[1].strip()
    elif ':' in first_line:
        case_id = first_line.split(':', 1)[1].strip()
    else:
        case_id = first_line.strip()
    return case_id



def find_test_methods_in_file(file_path):
    """
    在指定的文件中查找所有以 'test_' 开头的函数，并提取其用例编号。
    """
    test_methods = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content, filename=file_path)
    except SyntaxError as e:
        print(f"⚠️  文件 {file_path} 存在语法错误: {e}", file=sys.stderr)
        return test_methods
    except Exception as e:
        print(f"⚠️  读取文件 {file_path} 时出错: {e}", file=sys.stderr)
        return test_methods

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            case_id = extract_case_id_from_function(node)
            if case_id:
                test_methods.append({
                    'file_path': file_path,
                    'function_name': node.name,
                    'case_id': case_id
                })
    return test_methods


def scan_project_for_test_cases(project_root, case_ids):
    """
    扫描项目目录，查找匹配指定用例编号的测试用例。
    """
    matched_cases = []

    for root, _, files in os.walk(project_root):
        # 跳过一些常见的非测试目录
        if any(part in root for part in ['.git', '__pycache__', '.pytest_cache', 'TestLog']):
            continue
            
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                file_path = os.path.join(root, file)
                test_methods = find_test_methods_in_file(file_path)
                for method_info in test_methods:
                    if method_info['case_id'] in case_ids:
                        matched_cases.append(method_info)

    return matched_cases


def main():
    import time
    import subprocess
    st = time.time()
    parser = argparse.ArgumentParser(description='通过用例编号查找匹配的测试用例路径。')
    parser.add_argument('case_ids', metavar='CASE_ID', type=str, nargs='+',
                        help='要查找的用例编号')
    parser.add_argument('--project-root', type=str, default='.',
                        help='项目根目录 (默认: 当前目录)')
    parser.add_argument('--run', action='store_true',
                        help='执行pytest测试')
    parser.add_argument('--pytest-args', type=str, default='',
                        help='传递给pytest的额外参数')

    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    if not os.path.isdir(project_root):
        print(f"❌ 项目根目录不存在: {project_root}", file=sys.stderr)
        sys.exit(1)

    # print(f"🔍 正在扫描项目目录: {project_root}")
    # print(f"🔍 查找用例编号: {args.case_ids}")

    matched_cases = scan_project_for_test_cases(project_root, args.case_ids)

    if not matched_cases:
        print("❌ 未找到匹配的测试用例。")
        sys.exit(1)

    # print(f"✅ 找到 {len(matched_cases)} 个匹配的测试用例:")
    path_list = []
    for case in matched_cases:
        # 输出格式可以是 pytest 可识别的格式
        nodeid = f"{case['file_path']}"
        path_list.append(nodeid)

    if args.run:
        # 构造pytest命令
        pytest_cmd = ["pytest", "-sv", "-p", "test_runner_plugin"] + path_list
        if args.pytest_args:
            pytest_cmd += args.pytest_args.split()
        print(f"🚀 执行命令: {' '.join(pytest_cmd)}")
        # 执行pytest命令
        result = subprocess.run(pytest_cmd)
        sys.exit(result.returncode)
    else:
        print(' '.join(path_list))
    # print(f"✅ 耗时: {time.time() - st} 秒")

if __name__ == '__main__':
    main()
