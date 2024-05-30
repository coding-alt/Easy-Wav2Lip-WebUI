import gradio as gr
import subprocess
import configparser
import os, sys
import re

# 定义界面
def infer(video_path, vocal_file, quality, wav2lip_version, use_previous_tracking_data, output_height, nosmooth, wav2lip_batch_size, padding_u, padding_d, padding_l, padding_r, mask_size, mask_feathering, mask_mouth_tracking, mask_debug_mask):
    # 写入配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.set('OPTIONS', 'video_file', video_path)
    config.set('OPTIONS', 'vocal_file', vocal_file)
    config.set('OPTIONS', 'quality', quality)
    config.set('OPTIONS', 'wav2lip_version', wav2lip_version)
    config.set('OPTIONS', 'use_previous_tracking_data', use_previous_tracking_data)
    config.set('OPTIONS', 'output_height', output_height)
    config.set('OPTIONS', 'nosmooth', nosmooth)
    config.set('PADDING', 'u', str(padding_u))
    config.set('PADDING', 'd', str(padding_d))
    config.set('PADDING', 'l', str(padding_l))
    config.set('PADDING', 'r', str(padding_r))
    config.set('MASK', 'size', str(mask_size))
    config.set('MASK', 'feathering', str(mask_feathering))
    config.set('MASK', 'mouth_tracking', mask_mouth_tracking)
    config.set('MASK', 'debug_mask', mask_debug_mask)
    config.set('OTHER', 'wav2lip_batch_size', str(wav2lip_batch_size))
    
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    
    # 执行外部脚本
    python_executable = sys.executable
    result = subprocess.run([python_executable, "run.py"], stdout=subprocess.PIPE, text=True)
    
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
css = """footer {visibility: hidden}"""
app = gr.Blocks(title="Easy Wav2Lip数字人推理", css=css, theme="Kasien/ali_theme_custom")

with app:
    gr.Markdown("# <center>🎡 - Easy Wav2Lip数字人推理</center>")

    with gr.Tabs(elem_id="source_media"):
        with gr.TabItem('准备素材'):
            with gr.Row():
                with gr.Column():
                    video_path = gr.Video(sources="upload", label="视频素材")
                with gr.Column():
                    vocal_file = gr.Audio(sources="upload", type="filepath", label="驱动音频")

    with gr.Tabs(elem_id="driven_audio"):
        with gr.TabItem('设置'):
            gr.Markdown("所有视频帧中必须都有一张脸，否则 Wav2Lip 将报错。第一次使用，请测试音频较短的文件，再进行长视频制作")
            with gr.Row():
                with gr.Column():
                    quality = gr.Radio(choices=["Fast", "Improved", "Enhanced", "Experimental"], value="Enhanced", label="视频质量选项", info="与视频生成速度和清晰度有关")
                    wav2lip_version = gr.Radio(choices=["Wav2Lip", "Wav2Lip_GAN"], value="Wav2Lip_GAN", label="Wav2Lip版本选项")

                    use_previous_tracking_data = gr.Radio(choices=["True", "False"], value="True", label="启用追踪旧数据")

                    output_height = gr.Radio(choices=["full resolution", "half resolution"], value="full resolution", label="分辨率选项选项")

                    nosmooth = gr.Radio(choices=["True", "False"], value="True", label="启用脸部平滑", info="适用于快速移动的人脸，如果脸部角度过大可能会导致画面抽搐")

                    wav2lip_batch_size = gr.Slider(minimum=1, maximum=128, step=1, value=1, label="批量推理batch_size", info="GPU资源充足可以调大batch_size")

                with gr.Column():
                    padding_u = gr.Slider(minimum=-15, maximum=15, step=1, value=0, label="面部裁切像素-上")
                    padding_d = gr.Slider(minimum=-15, maximum=15, step=1, value=0, label="面部裁切像素-下")
                    padding_l = gr.Slider(minimum=-15, maximum=15, step=1, value=0, label="面部裁切像素-左")
                    padding_r = gr.Slider(minimum=-15, maximum=15, step=1, value=0, label="面部裁切像素-右")

                    mask_size = gr.Number(value="2.5", label="Mask尺寸", info="减小脸部周围的边框")
                    mask_feathering = gr.Slider(minimum=1, maximum=3, step=1, value=2, label="Mask羽化", info="减轻脸部周围边框的清晰度")

                    mask_mouth_tracking = gr.Radio(choices=["True", "False"], value="False", label="启用Mask嘴部跟踪")
                    mask_debug_mask = gr.Radio(choices=["True", "False"], value="False",  label="启用Mask调试")

                with gr.Column():
                    result = gr.Video(label="推理结果")
                    btn = gr.Button("一键推理", variant="primary")
    
    btn.click(
        fn = infer,
        inputs = [video_path, vocal_file, quality, wav2lip_version, use_previous_tracking_data, output_height, nosmooth, wav2lip_batch_size, padding_u, padding_d, padding_l, padding_r, mask_size, mask_feathering, mask_mouth_tracking, mask_debug_mask],
        outputs = result
    )
    
app.launch(server_name='0.0.0.0')