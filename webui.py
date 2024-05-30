import os, sys
import re
import gradio as gr
import configparser
from pathlib import Path
import shutil
import subprocess

def read_config(config_path='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_path)
    settings = {
        'quality': config.get('OPTIONS', 'quality', fallback='Improved'),
        'output_height': config.get('OPTIONS', 'output_height', fallback='full resolution'),
        'wav2lip_version': config.get('OPTIONS', 'wav2lip_version', fallback='Wav2Lip'),
        'use_previous_tracking_data': config.getboolean('OPTIONS', 'use_previous_tracking_data', fallback=True),
        'nosmooth': config.getboolean('OPTIONS', 'nosmooth', fallback=True),
        'u': config.getint('PADDING', 'u', fallback=0),
        'd': config.getint('PADDING', 'd', fallback=0),
        'l': config.getint('PADDING', 'l', fallback=0),
        'r': config.getint('PADDING', 'r', fallback=0),
        'size': config.getfloat('MASK', 'size', fallback=2.5),
        'feathering': config.getint('MASK', 'feathering', fallback=2),
        'mouth_tracking': config.getboolean('MASK', 'mouth_tracking', fallback=False),
        'debug_mask': config.getboolean('MASK', 'debug_mask', fallback=False),
        'batch_process': config.getboolean('OTHER', 'batch_process', fallback=False),
        'wav2lip_batch_size': config.getint('OTHER', 'wav2lip_batch_size', fallback=1),
    }
    return settings
    
def update_config_file(config_values):
    quality, output_height, wav2lip_version, use_previous_tracking_data, nosmooth, u, d, l, r, size, feathering, mouth_tracking, debug_mask, batch_process, wav2lip_batch_size, source_image, driven_audio = config_values

    config = configparser.ConfigParser()
    config.read('config.ini')

    config.set('OPTIONS', 'video_file', str(source_image))
    config.set('OPTIONS', 'vocal_file', str(driven_audio))
    config.set('OPTIONS', 'quality', str(quality))
    config.set('OPTIONS', 'output_height', str(output_height))
    config.set('OPTIONS', 'wav2lip_version', str(wav2lip_version))
    config.set('OPTIONS', 'use_previous_tracking_data', str(use_previous_tracking_data))
    config.set('OPTIONS', 'nosmooth', str(nosmooth))
    config.set('PADDING', 'U', str(u))
    config.set('PADDING', 'D', str(d))
    config.set('PADDING', 'L', str(l))
    config.set('PADDING', 'R', str(r))
    config.set('MASK', 'size', str(size))
    config.set('MASK', 'feathering', str(feathering))
    config.set('MASK', 'mouth_tracking', str(mouth_tracking))
    config.set('MASK', 'debug_mask', str(debug_mask))
    config.set('OTHER', 'batch_process', str(batch_process))
    config.set('OTHER', 'wav2lip_batch_size', str(wav2lip_batch_size))
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def run_wav2lip():
    python_executable = sys.executable

    # 执行外部脚本
    result = subprocess.run([python_executable, 'run.py'], stdout=subprocess.PIPE, text=True)
    
    # 读取脚本输出
    output = result.stdout
    
    # 使用正则表达式提取<video>标签的内容
    match = re.search(r'<video>(.*?)</video>', output, re.DOTALL)
    if match:
        output_video_path = match.group(1)
    else:
        output_video_path = ""
        
    return output_video_path, "成功了！"

def execute_pipeline(source_media, driven_audio, quality, output_height, wav2lip_version, 
                     use_previous_tracking_data, nosmooth, u, d, l, r, size, feathering, 
                     mouth_tracking, debug_mask, batch_process, wav2lip_batch_size):

    config_values = (quality, output_height, wav2lip_version, use_previous_tracking_data, nosmooth, 
                     u, d, l, r, size, feathering, mouth_tracking, debug_mask, batch_process, wav2lip_batch_size,
                     source_media, driven_audio)

    update_config_file(config_values)
    video_path, message = run_wav2lip()
    return video_path, message

    

def easywav2lip_demo(config_path='config.ini'):
    settings = read_config(config_path)
    css = """footer {visibility: hidden}"""
    with gr.Blocks(title="Easy Wav2Lip数字人推理", css=css, theme="Kasien/ali_theme_custom") as easywav2lip_interface:
        gr.Markdown("# <center>🎡 - Easy Wav2Lip数字人推理</center>") 
        
        with gr.Tabs():
            with gr.TabItem('准备素材'):
                with gr.Row():
                    with gr.Column():
                        source_media = gr.Video(sources="upload", label="上传视频素材，支持mp4、mov格式")
                    with gr.Column():
                        driven_audio = gr.Audio(sources="upload", type="filepath", label="上传驱动音频，支持mp3、wav格式")

        with gr.Tabs():
            with gr.TabItem('设置'):
                gr.Markdown("所有视频帧中必须都有一张脸，否则 Wav2Lip 将报错。第一次使用，请测试音频较短的文件，再进行长视频制作")
                with gr.Row(): 
                    with gr.Column():
                            # 使用从config.ini文件中读取的默认值来初始化Gradio组件
                        quality = gr.Radio(
                            ['Fast', 'Improved', 'Enhanced', 'Experimental'], 
                            value=settings['quality'], 
                            label='视频质量选项', 
                            info="与视频生成速度和清晰度有关"
                        )
                        output_height = gr.Radio(
                            ['full resolution','half resolution'],
                            value=settings['output_height'], label='分辨率选项',
                            info="全分辨率和半分辨率"
                        )
                        wav2lip_version = gr.Radio(
                            ['Wav2Lip','Wav2Lip_GAN'],
                            value=settings['wav2lip_version'], label='Wav2Lip版本选项',
                            info="Wav2Lip口型同步更好。若出现牙齿缺失，可尝试Wav2Lip_GAN")
                        use_previous_tracking_data = gr.Radio(
                            ['True', 'False'],
                            value='True' if settings['use_previous_tracking_data'] else 'False', 
                            label='启用追踪旧数据'
                        )
                        nosmooth = gr.Radio(
                            ['True', 'False'],
                            value='True' if settings['nosmooth'] else 'False', 
                            label='启用脸部平滑', 
                            info="适用于快速移动的人脸，如果脸部角度过大可能会导致动画抽搐"
                        )
                        batch_process = gr.Radio(
                            ['False'],
                            value='True' if settings['batch_process'] else 'False', 
                            label='批量处理多个视频',
                            info="目前webui版本暂不支持批量处理，您可运行源代码"
                        )

                        wav2lip_batch_size = gr.Slider(label="批量推理batch_size", step=1, minimum=1, maximum=128,value=int(settings['wav2lip_batch_size']), info="GPU资源充足可以调大batch_size")
                            
                    with gr.Column(): 
                        with gr.Column():        
                            Padding_u = gr.Slider(label="嘴部mask上边缘", step=1, minimum=-100, maximum=100,value=int(settings['u']))
                            Padding_d = gr.Slider(label="嘴部mask下边缘", step=1, minimum=-100, maximum=100,value=int(settings['d']))
                            Padding_l = gr.Slider(label="嘴部mask左边缘", step=1, minimum=-100, maximum=100,value=int(settings['l']))
                            Padding_r = gr.Slider(label="嘴部mask右边缘", step=1, minimum=-100, maximum=100,value=int(settings['r']))
                            mask_size = gr.Slider(label="mask尺寸", step=0.1, minimum=-10, maximum=10,value=float(settings['size']), info="减小脸部周围的边框")
                            mask_feathering = gr.Slider(label="mask羽化", step=1, minimum=-100, maximum=100,value=float(settings['feathering']), info="减轻脸部周围边框的清晰度")
                            mask_mouth_tracking = gr.Radio(
                                ['True', 'False'],
                                value='True' if settings['mouth_tracking'] else 'False', 
                                label='启用mask嘴部跟踪'
                            )
                            mask_debug_mask = gr.Radio(
                                ['True', 'False'],
                                value='True' if settings['debug_mask'] else 'False', 
                                label='启用mask调试'
                            )
                            
                    with gr.Column(): 
                        with gr.Column():           
                            gen_video = gr.Video(label="推理结果", format="mp4",height=500,width=450)
                            output_message = gr.Textbox(label='视频制作状态')
                            submit_btn = gr.Button('一键推理', variant='primary')
                                

                submit_btn.click(
                    fn=execute_pipeline,
                    inputs=[source_media, driven_audio, quality, output_height, wav2lip_version, use_previous_tracking_data, nosmooth, Padding_u, Padding_d, Padding_l, Padding_r, mask_size, mask_feathering, mask_mouth_tracking, mask_debug_mask, batch_process, wav2lip_batch_size],
                    outputs=[gen_video, output_message]
                )

    return easywav2lip_interface
 

if __name__ == "__main__":
    demo = easywav2lip_demo()
    demo.queue()
    demo.launch(server_name='0.0.0.0')