#@title 2. Check GPU & Dev Environment

from IPython.display import display
import ipywidgets as widgets
import requests 

import os, subprocess
paperspace_m4000 = False
#@markdown Paperspace platform?
isPaperspace = False #@param {type:"boolean"}
try:
    subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], stdout=subprocess.PIPE)
    if 'M4000' in subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], stdout=subprocess.PIPE).stdout.decode('utf-8'):
        print("WARNING: You're using Quadro M4000 GPU，xformers won't work。")
        paperspace_m4000 = True
        isPaperspace = True
    else:
        print("Your GPU is suitable - " + subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], stdout=subprocess.PIPE).stdout.decode('utf-8') + "。")
        print("Platform: Paperspace" if isPaperspace else "Platform: Colab")
except:
    print("No GPU appears to be available. Please check your runtime type")
    exit()

rootDir = isPaperspace and '/tmp' or '/content'
stableDiffusionWebUIInstalled = os.path.exists(rootDir + '/stable-diffusion-webui')
%store rootDir
%store paperspace_m4000 
%store isPaperspace
%store stableDiffusionWebUIInstalled
import requests
#@title 3. Install dependencies and extensions 

#@markdown ## **Extensions**

#@markdown xformer
xformersInstall = True #@param {type:"boolean"}
#@markdown ControlNet
controlNetExtension = False #@param {type:"boolean"}
#@markdown OpenPose Editor
openPoseExtension = False #@param {type:"boolean"}
#@markdown Civitai Browser
civitaiBrowserExtension = False #@param {type:"boolean"}
#@markdown HuggingFace 
huggingFaceExtension = False #@param {type:"boolean"}
#@markdown Images Browser 
imagesBrowserExtension = False #@param {type:"boolean"}
#@markdown Additional Networks 
additionalNetworksExtension = True #@param {type:"boolean"}
#@markdown Deforum 
deforumExtension = False #@param {type:"boolean"}
#@markdown Kohya sd-scripts 
kohyaExtension = False #@param {type:"boolean"}
#@markdown DreamBooth 
dreamBoothExtension = False #@param {type:"boolean"}


#@markdown ---
#@markdown ## **Textual Inversion**
#@markdown Ulzzang-6500 (Korean doll aesthetic)
ulzzang6500 = True #@param {type:"boolean"}
#@markdown Pure Eros Face
pureErosFace = True #@param {type:"boolean"}

#@markdown ---

#@markdown ## **Startup Options**

#@markdown API Support
apiSupport = True #@param {type:"boolean"}

textualInversionDownloadIDs = {
  'ulzzang6500': 8109,
  'pureErosFace': 4514,
}

def getLatestModelDownloadURL(id):
  try:
    if type(id) == int:
      res = requests.get(endpoint + '/' + str(id)).json()
      latest = res['modelVersions'][0]
      downloadLink = latest['files'][0]['downloadUrl']
      name = latest['files'][0]['name']
      return {
        'url': downloadLink,
        'name': name
      }
    else:
      return {
        'url': id,
        'name': id.split('/')[-1]
      }
  except:
    print("Lora model " + str(id) + " not found. Skip.")
    return None

def getSpecificModelDownloadURL(id, version):
  try:
    if type(id) == int:
      res = requests.get(endpoint + '/' + str(id)).json()
      for modelVersion in res['modelVersions']:
        if modelVersion['name'] == version:
          # if modelVersion["baseModel"] != "SD 1.5":
          #   print("Lora model " + str(id) + " is not SD 1.5, may not work. Skip.")
          #   return None
          downloadLink = modelVersion['files'][0]['downloadUrl']
          name = modelVersion['files'][0]['name']
          return {
            'url': downloadLink,
            'name': name
          }
    else:
      return {
        'url': id,
        'name': id.split('/')[-1]
      }
  except:
    print("Lora model " + str(id) + " version " + version + " not found. Skip.")
    return None

def getTextualInversionDownloadURLs():
  downloadURLs = []
  for key in textualInversionDownloadIDs:
    if not eval(key): # skip if not selected
      continue
    if type(textualInversionDownloadIDs[key]) is int:
      downloadURLs.append(getLatestModelDownloadURL(textualInversionDownloadIDs[key]))
    elif type(textualInversionDownloadIDs[key]) is dict: # {'id': 123, 'version': 'v1.0'}
      downloadURLs.append(getSpecificModelDownloadURL(textualInversionDownloadIDs[key]['id'], textualInversionDownloadIDs[key]['version']))
    elif type(textualInversionDownloadIDs[key]) is str: # url
      downloadURLs.append({ 'url': textualInversionDownloadIDs[key], 'name': textualInversionDownloadIDs[key].split('/')[-1] })
  downloadURLs = [x for x in downloadURLs if x is not None]
  return downloadURLs
    
textualInversionDownloadURLs = getTextualInversionDownloadURLs()

%store -r paperspace_m4000 
%store -r isPaperspace
%store -r rootDir 
%store -r checkpoints
%store -r downloadLinks
%store -r stableDiffusionWebUIInstalled

import subprocess

!apt-get -y install -qq aria2
ariaInstalled = False

try:
    subprocess.run(['aria2c', '--version'], stdout=subprocess.PIPE)
    ariaInstalled = True
except:
    pass

if paperspace_m4000:
  if xformersInstall:
    !pip install ninja
    !pip install -v -U git+https://github.com/facebookresearch/xformers.git@main#egg=xformers
    !pip install -q --pre triton
else:
  !pip install -q https://github.com/camenduru/stable-diffusion-webui-colab/releases/download/0.0.16/xformers-0.0.16+814314d.d20230118-cp38-cp38-linux_x86_64.whl
  !pip install -q --pre triton
  

!git clone -b v2.0 https://github.com/nathan-149/stable-diffusion-webui {rootDir}/stable-diffusion-webui
!wget https://raw.githubusercontent.com/nathan-149/stable-diffusion-webui-scripts/main/run_n_times.py -O {rootDir}/stable-diffusion-webui/scripts/run_n_times.py
if deforumExtension:
  !git clone https://github.com/deforum-art/deforum-for-automatic1111-webui {rootDir}/stable-diffusion-webui/extensions/deforum-for-automatic1111-webui
if imagesBrowserExtension:
  !git clone https://github.com/AlUlkesh/stable-diffusion-webui-images-browser {rootDir}/stable-diffusion-webui/extensions/stable-diffusion-webui-images-browser
if huggingFaceExtension:
  !git clone https://github.com/camenduru/stable-diffusion-webui-huggingface {rootDir}/stable-diffusion-webui/extensions/stable-diffusion-webui-huggingface
if civitaiBrowserExtension:
  !git clone -b v2.0 https://github.com/camenduru/sd-civitai-browser {rootDir}/stable-diffusion-webui/extensions/sd-civitai-browser
if openPoseExtension:
  !git clone https://github.com/camenduru/openpose-editor {rootDir}/stable-diffusion-webui/extensions/openpose-editor
if controlNetExtension:
  !git clone https://github.com/Mikubill/sd-webui-controlnet {rootDir}/stable-diffusion-webui/extensions/sd-webui-controlnet
if additionalNetworksExtension:
  !git clone https://github.com/kohya-ss/sd-webui-additional-networks {rootDir}/stable-diffusion-webui/extensions/sd-webui-additional-networks
if kohyaExtension:
  !git clone https://github.com/ddpn08/kohya-sd-scripts-webui.git {rootDir}/stable-diffusion-webui/extensions/kohya-sd-scripts-webui
if dreamBoothExtension:
  !git clone https://github.com/d8ahazard/sd_dreambooth_extension {rootDir}/stable-diffusion-webui/extensions/sd_dreambooth_extension

if isPaperspace:
  %cd /stable-diffusion-webui
else:
  %cd {rootDir}/stable-diffusion-webui


webuiControlNetModels = [
  "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_canny-fp16.safetensors",
  "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_depth-fp16.safetensors",
  "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_hed-fp16.safetensors",
  "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_mlsd-fp16.safetensors",
  "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_normal-fp16.safetensors",
  "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_openpose-fp16.safetensors",
  "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_scribble-fp16.safetensors",
  "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_seg-fp16.safetensors",
]
annotatorLink = [
  "https://huggingface.co/ckpt/ControlNet/resolve/main/hand_pose_model.pth",
  "https://huggingface.co/ckpt/ControlNet/resolve/main/body_pose_model.pth",
  "https://huggingface.co/ckpt/ControlNet/resolve/main/dpt_hybrid-midas-501f0c75.pt",
  "https://huggingface.co/ckpt/ControlNet/resolve/main/mlsd_large_512_fp32.pth",
  "https://huggingface.co/ckpt/ControlNet/resolve/main/mlsd_tiny_512_fp32.pth",
  "https://huggingface.co/ckpt/ControlNet/resolve/main/network-bsds500.pth",
  "https://huggingface.co/ckpt/ControlNet/resolve/main/upernet_global_small.pth",
]

def ariaDownload(downloadLink, checkpoint, path):
  if (type(downloadLink) == list and type(checkpoint) == list):
    for i in downloadLink:
      !aria2c --console-log-level=error -c -x 16 -s 16 -k 1M {i} -d {path} -o {checkpoint[downloadLink.index(i)]}
  else:
    !aria2c --console-log-level=error -c -x 16 -s 16 -k 1M {downloadLink} -d {path} -o {checkpoint}
def wgetDownload(downloadLink, checkpoint, path):
  if (type(downloadLink) == list and type(checkpoint) == list):
    for i in downloadLink:
      !wget -c {i} -P {path} -O {checkpoint[downloadLink.index(i)]}
  else:
    !wget -c {downloadLink} -P {path} -O {checkpoint}
def autoDetectDownload(downloadLink, checkpoint, path):
  if ariaInstalled:
    ariaDownload(downloadLink, checkpoint, path)
  else:
    wgetDownload(downloadLink, checkpoint, path)

if controlNetExtension:
  for model in webuiControlNetModels:
    autoDetectDownload(model, model.split('/')[-1], rootDir + "/stable-diffusion-webui/extensions/sd-webui-controlnet/models")
  for model in annotatorLink:
    autoDetectDownload(model, model.split('/')[-1], rootDir + "/stable-diffusion-webui/extensions/sd-webui-controlnet/annotator")
for model in textualInversionDownloadURLs:
  autoDetectDownload(model["url"], model["name"], rootDir + "/stable-diffusion-webui/embeddings")

if additionalNetworksExtension:
  !ln -s {rootDir}/stable-diffusion-webui/extensions/sd-webui-additional-networks/models/lora {rootDir}/stable-diffusion-webui/models/Lora


stableDiffusionWebUIInstalled = True
%store stableDiffusionWebUIInstalled

%cd {rootDir}/stable-diffusion-webui
!sed -i -e '''/prepare_environment()/a\    os.system\(f\"""sed -i -e ''\"s/self.logvar\\[t\\]/self.logvar\\[t.item()\\]/g\"'' {rootDir}/stable-diffusion-webui/repositories/stable-diffusion-stability-ai/ldm/models/diffusion/ddpm.py""")''' {rootDir}/stable-diffusion-webui/launch.py
!sed -i -e '''/prepare_environment()/a\    os.system\(f\"""sed -i -e ''\"s/dict()))/dict())).cuda()/g\"'' {rootDir}/stable-diffusion-webui/repositories/stable-diffusion-stability-ai/ldm/util.py""")''' {rootDir}/stable-diffusion-webui/launch.py
if dreamBoothExtension:
  !export REQS_FILE="./extensions/sd_dreambooth_extension/requirements.txt"
#@title Download Chilloutmix Checkpoint

checkpoint = 'chilloutmix.safetensors' #@param ["chilloutmix.safetensors"]

downloadLink = 'https://civitai.com/api/download/models/11745' #@param 


!wget -c {downloadLink} -O /content/stable-diffusion-webui/models/Stable-diffusion/{checkpoint}
!aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/sd14/resolve/main/sd-v1-4.ckpt -d /content/stable-diffusion-webui/models/Stable-diffusion -o sd-v1-4.ckpt
#@title Download Loras

loraLinks = dict((
    ('koreanDollLikeness_v15.safetensors', 'https://civitai.com/api/download/models/31284'),
    ('xswltry1.safetensors', 'https://civitai.com/api/download/models/29131'),
    ('liyuuLora_liyuuV1.safetensors', 'https://civitai.com/models/9997/liyuu-lora'),
    ('aiBeautyIthlinni_ithlinniV1.safetensors', 'https://civitai.com/api/download/models/19671'),
    ('Cute_girl_mix4.safetensors', 'https://civitai.com/api/download/models/16677'),
    ('breastinclassBetter_v141.safetensors', 'https://civitai.com/api/download/models/23250'),
    ('chilloutmixss_xss10.safetensors', 'https://huggingface.co/HankChang/chilloutmixss_xss10/resolve/main/chilloutmixss_xss10.safetensors'),
    ('moxin.safetensors', 'https://civitai.com/api/download/models/14856'),
    ('legspread10.safetensors', 'https://civitai.com/api/download/models/29760'),
    ('taiwan.safetensors', 'https://civitai.com/api/download/models/20684')
))


for lora, link in loraLinks.items():
    print('\nKey: %s' % lora)
    print('Value: %s' % link)
    !wget -c {link} -O /content/stable-diffusion-webui/models/Lora/{lora}

#@title 5. Export Photos to /export
%store -r rootDir 

from pathlib import Path
import os, subprocess

export_storage_dir = Path(rootDir, 'export')
export_storage_dir.mkdir(exist_ok=True)

!if [ $(dpkg-query -W -f='${Status}' p7zip-full 2>/dev/null | grep -c "ok installed") = 0 ]; then sudo apt update && sudo apt install -y p7zip-full; fi # install 7z if it isn't already installed
from datetime import datetime
datetime_str = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
%cd "{export_storage_dir}"
!mkdir -p "{datetime_str}/log"
!cd "{rootDir}/stable-diffusion-webui/log" && mv * "{export_storage_dir / datetime_str / 'log'}"
!cd "{rootDir}/stable-diffusion-webui/outputs" && mv * "{export_storage_dir / datetime_str}"
s = subprocess.run(f'find "{Path(export_storage_dir, datetime_str)}" -type d -name .ipynb_checkpoints -exec rm -rv {{}} +', shell=True)
!7z a -t7z -m0=lzma2 -mx=9 -mfb=64 -md=32m -ms=on "{datetime_str}.7z" "{export_storage_dir / datetime_str}"9