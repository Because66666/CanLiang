import os
import shutil
from bs4 import BeautifulSoup  # 需要安装：pip install beautifulsoup4

def flatten_files(target_dir):
    """
    扁平化目标文件夹的文件结构
    :param target_dir: 目标文件夹路径（如 'output'）
    """
    # 步骤1：收集所有文件的路径映射（原相对路径 → 根目录文件名）
    file_mapping = {}  # key: 原相对路径(如 '_next/static/main.js'), value: 根目录文件名(如 'main.js')
    all_files = []

    # 遍历所有子目录，收集文件
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            # 计算文件相对于目标文件夹的相对路径
            rel_path = os.path.relpath(os.path.join(root, file), target_dir)
            # 替换路径分隔符为统一的 '/'（处理Windows系统）
            rel_path = rel_path.replace(os.sep, '/')
            all_files.append(rel_path)

    # 步骤2：处理文件名冲突，生成目标文件名
    for rel_path in all_files:
        file_name = os.path.basename(rel_path)
        # 检查根目录是否已存在同名文件
        target_path = os.path.join(target_dir, file_name)
        counter = 1
        # 若冲突则添加序号（如 main.js → main_1.js）
        while os.path.exists(target_path):
            name, ext = os.path.splitext(file_name)
            file_name = f"{name}_{counter}{ext}"
            target_path = os.path.join(target_dir, file_name)
            counter += 1
        file_mapping[rel_path] = file_name

    # 步骤3：移动所有文件到根目录
    for rel_path, target_name in file_mapping.items():
        source_path = os.path.join(target_dir, rel_path.replace('/', os.sep))  # 转换为系统路径格式
        target_path = os.path.join(target_dir, target_name)
        # 移动文件
        shutil.move(source_path, target_path)
        print(f"移动文件: {rel_path} → {target_name}")

    # 步骤4：删除空文件夹（从最深层开始删除）
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):  # 检查文件夹是否为空
                os.rmdir(dir_path)
                print(f"删除空文件夹: {dir_path}")

    # 步骤5：修正HTML文件中的资源引用路径
    fix_html_references(target_dir, file_mapping)


def fix_html_references(target_dir, file_mapping):
    """修正HTML文件中的资源引用路径"""
    # 遍历根目录下所有HTML文件
    for file in os.listdir(target_dir):
        if file.endswith('.html'):
            html_path = os.path.join(target_dir, file)
            with open(html_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')

            # 修正script标签的src属性
            for script in soup.find_all('script', src=True):
                src = script['src']
                corrected_src = get_corrected_path(src, file_mapping)
                if corrected_src:
                    script['src'] = corrected_src

            # 修正link标签的href属性（CSS等）
            for link in soup.find_all('link', href=True):
                href = link['href']
                corrected_href = get_corrected_path(href, file_mapping)
                if corrected_href:
                    link['href'] = corrected_href

            # 修正img/video/source等标签的src属性
            for tag in soup.find_all(['img', 'video', 'source'], src=True):
                src = tag['src']
                corrected_src = get_corrected_path(src, file_mapping)
                if corrected_src:
                    tag['src'] = corrected_src

            # 保存修正后的HTML
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"修正HTML路径: {file}")


def get_corrected_path(original_path, file_mapping):
    """根据文件映射修正资源路径"""
    # 处理绝对路径（如 '/_next/static/main.js' → 取 '_next/static/main.js'）
    if original_path.startswith('/'):
        original_path = original_path[1:]
    # 处理相对路径（如 '../_next/main.js' 转换为绝对相对路径）
    # 简化处理：直接匹配映射表中的键（忽略上级目录标识，适用于大部分场景）
    for rel_path in file_mapping:
        if original_path.endswith(rel_path) or rel_path.endswith(original_path):
            return file_mapping[rel_path]
    return None  # 未找到映射则不修改


if __name__ == "__main__":
    # 配置目标文件夹（与next.config.js中的distDir一致，默认为'output'）
    TARGET_DIRECTORY = "output"

    # 检查目标文件夹是否存在
    if not os.path.exists(TARGET_DIRECTORY):
        print(f"错误：目标文件夹 '{TARGET_DIRECTORY}' 不存在！")
        exit(1)

    # 执行扁平化操作
    flatten_files(TARGET_DIRECTORY)
    print("文件结构扁平化完成！")