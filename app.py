import gradio as gr
import subprocess
import configparser
import os
import re

# 定义界面
def infer(video_path, vocal_file, quality):
    # 写入配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.set('OPTIONS', 'video_file', video_path)
    config.set('OPTIONS', 'vocal_file', vocal_file)
    config.set('OPTIONS', 'quality', quality)
    
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    
    # 执行外部脚本
    result = subprocess.run(["python", "run.py"], stdout=subprocess.PIPE, text=True)
    
    # 读取脚本输出
    output = result.stdout
    
    # 使用正则表达式提取<video>标签的内容
    match = re.search(r'<video>(.*?)</video>', output, re.DOTALL)
    if match:
        output_video_path = match.group(1)
    else:
        output_video_path = ""
        
    return output_video_path

# 创建Gradio界面
iface = gr.Interface(
    fn=infer,
    inputs=[
        gr.Video(sources="upload", label="Video Upload"),
        gr.Audio(sources="upload", type="filepath", label="Audio Upload"),
        gr.Dropdown(choices=["Fast", "Improved", "Enhanced", "Experimental"], value="Fast", label="Quality")
    ],
    outputs=[
        gr.Video(label="Inference Result")
    ],
    title="Easy Wav2Lip数字人推理",
    theme='Kasien/ali_theme_custom',
    css="footer {visibility: hidden}",
    allow_flagging="never"
)

# 启动界面
iface.launch(server_name='0.0.0.0')
