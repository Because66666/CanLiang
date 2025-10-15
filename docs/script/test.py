import os
import shutil
from bs4 import BeautifulSoup  # 需安装：pip install beautifulsoup4

def merge_next_export(export_dir="output", keep_original=False):
    """
    合并Next.js静态导出内容为3个文件
    :param export_dir: Next.js导出目录（默认output）
    :param keep_original: 是否保留原始文件（默认不保留）
    """
    # 检查导出目录是否存在
    if not os.path.exists(export_dir):
        print(f"错误：导出目录 '{export_dir}' 不存在！")
        return

    # 步骤1：收集HTML中的资源引用顺序（确保加载顺序正确）
    html_path = os.path.join(export_dir, "index.html")
    if not os.path.exists(html_path):
        print(f"错误：未找到 {html_path}！")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # 收集CSS和JS的引用路径（按出现顺序）
    css_paths = []  # 存储CSS文件相对路径
    js_paths = []   # 存储JS文件相对路径

    # 提取link标签中的CSS
    for link in soup.find_all("link", rel="stylesheet"):
        if "href" in link.attrs:
            css_paths.append(link["href"])

    # 提取script标签中的JS（按出现顺序，确保执行顺序正确）
    for script in soup.find_all("script", src=True):
        if "src" in script.attrs:
            js_paths.append(script["src"])

    # 步骤2：合并所有CSS文件
    css_content = []
    for css_path in css_paths:
        # 处理绝对路径（如 '/_next/static/css/main.css' → '_next/static/css/main.css'）
        if css_path.startswith("/"):
            css_path = css_path[1:]
        full_path = os.path.join(export_dir, css_path.replace("/", os.sep))
        
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                css_content.append(f"/* 合并自：{css_path} */\n")
                css_content.append(f.read())
                css_content.append("\n\n")
        else:
            print(f"警告：未找到CSS文件 {full_path}，已跳过")

    # 保存合并后的CSS
    bundle_css = os.path.join(export_dir, "app.bundle.css")
    with open(bundle_css, "w", encoding="utf-8") as f:
        f.write("".join(css_content))
    print(f"已生成合并CSS：{bundle_css}")

    # 步骤3：合并所有JS文件
    js_content = []
    for js_path in js_paths:
        if js_path.startswith("/"):
            js_path = js_path[1:]
        full_path = os.path.join(export_dir, js_path.replace("/", os.sep))
        
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                js_content.append(f"/* 合并自：{js_path} */\n")
                js_content.append(f.read())
                js_content.append("\n\n")
        else:
            print(f"警告：未找到JS文件 {full_path}，已跳过")

    # 保存合并后的JS
    bundle_js = os.path.join(export_dir, "app.bundle.js")
    with open(bundle_js, "w", encoding="utf-8") as f:
        f.write("".join(js_content))
    print(f"已生成合并JS：{bundle_js}")

    # 步骤4：生成新的index.html（仅引用合并后的资源）
    # 清除原CSS和JS引用
    for link in soup.find_all("link", rel="stylesheet"):
        link.decompose()
    for script in soup.find_all("script", src=True):
        script.decompose()

    # 添加合并后的CSS引用
    new_link = soup.new_tag("link", rel="stylesheet", href="app.bundle.css")
    soup.head.append(new_link)

    # 添加合并后的JS引用（放在body末尾）
    new_script = soup.new_tag("script", src="app.bundle.js")
    soup.body.append(new_script)

    # 保存新的index.html
    new_html_path = os.path.join(export_dir, "index.html")
    with open(new_html_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
    print(f"已生成新的index.html：{new_html_path}")

    # 步骤5：清理冗余文件（保留合并后的3个文件）
    if not keep_original:
        # 保留的文件
        keep_files = ["index.html", "app.bundle.css", "app.bundle.js"]
        # 遍历目录删除其他文件
        for item in os.listdir(export_dir):
            item_path = os.path.join(export_dir, item)
            if item not in keep_files:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    print(f"已删除冗余文件：{item_path}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    print(f"已删除冗余目录：{item_path}")

    print("合并完成！最终文件：")
    print(f"- {os.path.join(export_dir, 'index.html')}")
    print(f"- {os.path.join(export_dir, 'app.bundle.css')}")
    print(f"- {os.path.join(export_dir, 'app.bundle.js')}")


if __name__ == "__main__":
    # 配置参数
    EXPORT_DIRECTORY = "output"  # Next.js导出目录（与next.config.js中的distDir一致）
    KEEP_ORIGINAL_FILES = False  # 是否保留原始文件（调试时可设为True）

    # 执行合并
    merge_next_export(export_dir=EXPORT_DIRECTORY, keep_original=KEEP_ORIGINAL_FILES)