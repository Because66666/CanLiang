# 用于使用无头浏览器发送飞书图片
# 其中上传图片需要用到飞书应用。
import datetime
import subprocess
import time
import logging
import os
import importlib.util
import argparse

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('BetterGI初始化')


def capture_flask_screenshot(lark_webhook_url=None, host='127.0.0.1', port=3000, wait_time=5):
    """
    捕获浏览器截图然后发送到飞书自定义机器人。

    参数:
    flask_app_path (str): Flask应用的Python文件路径
    host (str): Flask服务器的主机地址
    port (int): Flask服务器的端口
    wait_time (int): 等待页面加载的时间(秒)
    """
    if lark_webhook_url is None:
        return
    from pathlib import Path
    # 创建保存截图的目录
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)

    # 构建Flask应用的URL
    url = f"http://{host}:{port}"
    capture_abspath = None

    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 启动服务器
    process = subprocess.Popen(['python', 'app.py', '-no'], cwd=script_dir)

    def _run_webdriver():
        try:
            time.sleep(wait_time)
            # 动态导入Playwright
            sync_playwright = import_sync_playwright()
            if sync_playwright is None:
                logger.critical("错误: 无法导入Playwright。请确保已安装playwright: pip install playwright")
                return

            # 使用Playwright启动浏览器并截图
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)  # 可以设置为True以无头模式运行
                page = browser.new_page()
                logger.debug(f"正在访问页面: {url}")
                page.goto(url)

                # 等待页面加载完成
                page.wait_for_load_state("networkidle")
                page.get_by_role("combobox").click()
                page.wait_for_timeout(1000)
                ele = page.get_by_role("option", name=datetime.datetime.today().strftime("%Y%m%d"))
                ele.click()
                page.wait_for_timeout(3000)  # 等待动画结束
                # 生成截图文件名
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                screenshot_path = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")
                capture_abspath = os.path.abspath(screenshot_path)
                # 截图并保存
                logger.debug(f"正在截图并保存到: {screenshot_path}")
                page.screenshot(path=str(screenshot_path))

                browser.close()
        except Exception as e:
            logger.error(f"错误: 截图时发生异常: {e}")
        finally:
            logger.debug("截图结束!")
        try:
            if importlib.util.find_spec("requests") is None:
                logger.critical("警告: requests 未安装。截图功能将不可用。")
                return None

            # 动态导入 requests 模块
            requests = importlib.import_module("requests")
            webhook_url, app_id, app_secret = lark_webhook_url.split(";")

            # 上传图片获取media_id
            def upload_image(image_path):
                # 获取应用的tenant_access_token
                response = requests.post(
                    url="https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                    params={
                        "app_id": app_id,
                        "app_secret": app_secret
                    }
                )
                tenant_access_token = response.json().get("tenant_access_token", None)
                if tenant_access_token is None:
                    logger.error("错误: 无法获取tenant_access_token。请检查app_id和app_secret是否正确。")
                    return None
                # 飞书媒体上传接口
                upload_url = "https://open.feishu.cn/open-apis/im/v1/images"
                # 请求参数
                data = {
                    "image_type": "message"
                }
                # 读取图片文件
                files = {
                    "image": open(image_path, "rb")
                }
                # 发送请求
                response = requests.post(
                    url=upload_url,
                    data=data,
                    files=files,
                    headers={"Authorization": f"Bearer {tenant_access_token}"}
                )

                # 解析响应
                result = response.json()
                if result.get("code") == 0:
                    return result.get("data").get("image_key")
                else:
                    print(f"上传图片失败: {result.get('msg')}")
                    return None

            # 发送图片消息
            def send_image_message(image_key):
                # 消息体
                message = {
                    "msg_type": "image",
                    "content": {
                        "image_key": image_key
                    }
                }

                # 发送请求
                import json
                response = requests.post(
                    url=webhook_url,
                    data=json.dumps(message),
                    headers={"Content-Type": "application/json"}
                )

                # 解析响应
                result = response.json()
                if result.get("StatusCode") == 0:
                    print("图片消息发送成功")
                else:
                    print(f"图片消息发送失败: {result.get('StatusMessage')}")

            # 上传图片获取media_id
            if capture_abspath:
                image_key = upload_image(capture_abspath)

                if image_key:
                    # 发送图片消息
                    send_image_message(image_key)
            else:
                logger.critical('图片路径未定义。')
        except Exception as e:
            logger.error(f"错误: 发送图片消息时发生异常: {e}")

    _run_webdriver()
    process.terminate()
    return_code = process.wait()
    logger.info(f"App 进程已结束，返回码: {return_code}")


def import_sync_playwright():
    """动态导入Playwright模块"""
    try:
        # 检查playwright是否已安装
        if importlib.util.find_spec("playwright") is None:
            logger.critical("警告: Playwright未安装。截图功能将不可用。")
            return None

        # 动态导入playwright.sync_api模块
        sync_api_module = importlib.import_module("playwright.sync_api")
        # 获取sync_playwright函数
        sync_playwright = getattr(sync_api_module, "sync_playwright")
        return sync_playwright
    except Exception as e:
        logger.error(f"错误: 导入Playwright时发生异常: {e}")
        return None


parser = argparse.ArgumentParser(description='参量质变仪的截图发送，用于解析BetterGI日志。')
parser.add_argument('-k', '--key', default=None, help='用于传递webhook_url;appid;appsecret')
key = parser.parse_args().key
if key:
    capture_flask_screenshot(key, wait_time=2)
