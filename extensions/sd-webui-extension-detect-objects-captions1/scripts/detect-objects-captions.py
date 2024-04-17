import modules.scripts as script
import gradio as gr
from modules import images, script_callbacks
from modules.processing import process_images, Processed
from modules.processing import Processed
from modules.shared import opts, cmd_opts, state
from PIL import Image
import time 
import requests
from io import BytesIO
import os
import subprocess
# from selenium import webdriver
# from selenium.webdriver import ChromeOptions
from seleniumbase import SB
from bs4 import BeautifulSoup
import urllib.request
from pathlib import Path
from datetime import datetime

# class DetectionScript(script.Script):
#         def __init__(self) -> None:
#                 super().__init__()

#         # Extension title in menu UI
#         def title(self):
#                 return "Objects Detections and Captions"
        
#         def show(self, is_img2img):
#                 return script.AlwaysVisible
        
#         def ui(self, is_img2img):
#                 return ()

#         def load_settings(_,self):
#              settingsFile = "extensions/sd-webui-extension-detect-objects-captions/settings.st"
#              global objWidth   
#              global objHeight 
#              global confl 
#              global capLen 

#              file = open(settingsFile, 'r')

#              objWidth = int(file.readline()[18:])
#              objHeight = int(file.readline()[19:])
#              confl = float(file.readline()[22:])
#              capLen = int(file.readline()[20:])

#              file.close()
           

#         script_callbacks.on_app_started(load_settings)

def img_detection(progress=gr.Progress()):
    global processing
    if imgclicked != -1 and not processing:
        objs = 0
        caps = 0
        processing = True
        op = subprocess.Popen(["python", "extensions/sd-webui-extension-detect-objects-captions/scripts/img_detection.pyt", imgs[added_img_indicies[imgclicked]]], stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(op.stdout.readline, ""):
             if stdout_line.startswith("obj detection:"):
                  objs = int(stdout_line[14:])
             if stdout_line.startswith("cap detection:"):
                  caps = int(stdout_line[14:])     
                  for i in progress.tqdm(range(objs*2+caps), desc="Processing..."):
                        time.sleep(0.1)
                  processing = False        
                  return ["Detection Done", "Captions Done"]
    
    return ["Error", "Select Image"]

def update_images(image_directory = "", progress=gr.Progress()):
        global processing
        if os.path.exists(image_directory) and not processing:       
            processing = True
            image_files = [f for f in os.listdir(image_directory) if f.endswith((".png", ".jpg", ".jpeg"))]
            global imgs
            global imgIndex
            global addedImgIndex
            global added_img_indicies
            global imgclicked
            imgIndex = 0
            addedImgIndex = 0
            imgclicked = -1
            added_img_indicies = []
            imgs = []
            for image_file in progress.tqdm(image_files, desc="Processing..."):
                imgs.append(os.path.join(image_directory, image_file))

            processing = False     
            if len(imgs) > 0:    
                return [load_image(imgs[0])] + [None for i in range(len(added_img_indicies), 48)] + [None, "Import Done"]
        return [None] + [None for i in range(len(added_img_indicies), 48)] + [None, "Import Done"]

def load_image(image_path_or_url: str) -> Image.Image:
    image = None
    if image_path_or_url.startswith(('http://', 'https://')):
        response = requests.get(image_path_or_url)
        image = Image.open(BytesIO(response.content))
    elif image_path_or_url != "":
        image = Image.open(image_path_or_url)
    return image 

imgs = []
imgIndex = 0
addedImgIndex = 0
added_img_indicies = []
imgclicked = -1
processing = False

def minus():
    global imgIndex
    if imgIndex > 0:
        imgIndex = imgIndex - 1
    if len(imgs) > 0:    
        return load_image(imgs[imgIndex])
    else:
         return None       

def plus():
     global imgIndex
     if imgIndex < len(imgs)-1:
          imgIndex = imgIndex + 1
     if len(imgs) > 0:    
        return load_image(imgs[imgIndex])
     else:
         return None      

def add_image():
    global addedImgIndex
    if addedImgIndex < 48:
        added_img_indicies.append(imgIndex)
        addedImgIndex += 1        
    if len(imgs) > 0:    
        return [load_image(imgs[i]) for i in added_img_indicies] + [None for i in range(len(added_img_indicies), 48)]
    else:
         return [None for i in range(0, 48)]

def img_clicked(img_index):
   global imgclicked
   imgclicked = img_index
   return load_image(imgs[added_img_indicies[img_index]])

def reset_objsettings():
     return [25,25,0.25]

def reset_capsettings():
     return 25

def save_settings(obj_width, obj_height,_conf_level, cap_length, progress=gr.Progress()):
     
     #Min object width: 25
     #Min object height: 25
     #Min confidence level: 0.25
     #Min caption length: 25

     settings = ["Min object width: {} \n".format(obj_width), "Min object height: {} \n".format(obj_height), 
                 "Min confidence level: {} \n".format(_conf_level), "Min caption length: {} \n".format(cap_length)]

     file = open('extensions/sd-webui-extension-detect-objects-captions/settings.st', 'w')

         # Writing settings
     for i in progress.tqdm(range(4), desc="Processing..."):
         file.write(settings[i])
         time.sleep(0.1)
 
     # Closing file
     file.close()

     return "settings saved"
                   
def label_rest():
     for i in range(0, 3):
          time.sleep(1)
     return ""

def import_from_url(url, progress=gr.Progress()):
    global processing
    if (not url.startswith(('http://', 'https://'))) or processing:
         return
    processing = True
#     options = ChromeOptions()
#     options.add_argument("--headless=new")
#     driver = webdriver.Chrome(options=options)
#     driver.get(url)
#     content = driver.page_source
#     soup = BeautifulSoup(content, "html.parser")
#     driver.quit()
    global imgs
    global imgIndex
    global addedImgIndex
    global added_img_indicies
    global imgclicked
    imgIndex = 0
    addedImgIndex = 0
    imgclicked = -1
    added_img_indicies = []
    imgs = []
    #imgall=soup.find_all('img')

    currentDir = str(Path(os.getcwd()).absolute())
    downloadDir = currentDir+"/output/download-images"

    isExist = os.path.exists(downloadDir)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(downloadDir)

    downloadDir = downloadDir + "/" + datetime.now().strftime('%Y-%m-%d %H-%M-%S')    
    os.makedirs(downloadDir)    

        # i = len(os.listdir(downloadDir))+1

#     headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
#    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
#    'Accept-Encoding': 'none',
#    'Accept-Language': 'en-US,en;q=0.8',
#    'Connection': 'keep-alive'}    

#     for img in progress.tqdm(imgall, desc="Processing..."):
#         try:
#             imgsrc=img['data-srcset']
#         except:
#             try:
#                 imgsrc=img['data-src']
#             except:
#                 try:
#                     imgsrc=img['data-fallback-src']
#                 except:
#                     try:
#                         imgsrc=img['src']
#                     except:
#                         pass
#         if not 'svg' in imgsrc:
#             if 'jpg' in imgsrc or 'jpeg' in imgsrc:
#                 if imgsrc.startswith("//www."):
#                     imgsrc = "https:"+imgsrc
#                 elif imgsrc.startswith("/"):                
#                     imgsrc = url+imgsrc
#                 request_=urllib.request.Request(imgsrc,None,headers) #The assembled request
#                 response = urllib.request.urlopen(request_)# store the response
#                 f = open(downloadDir+"/image-{}.jpg".format(i),'wb')
#                 f.write(response.read())
#                 f.close()
#                 imgs.append(downloadDir+"/image-{}.jpg".format(i))
#                 i=i+1

#             elif 'png' in imgsrc:
#                 if imgsrc.startswith("//www."):
#                     imgsrc = "https:"+imgsrc
#                 elif imgsrc.startswith("/"):                
#                     imgsrc = url+imgsrc
#                 request_=urllib.request.Request(imgsrc,None,headers) #The assembled request
#                 response = urllib.request.urlopen(request_)# store the response
#                 f = open(downloadDir+"/image-{}.png".format(i),'wb')
#                 f.write(response.read())
#                 f.close()
#                 imgs.append(downloadDir+"/image-{}.png".format(i))
#                 i=i+1 
    with SB() as sb:
        sb.open(url)
        img_elements_with_src = sb.find_elements("img[src]")
        unique_src_values = []
        for img in img_elements_with_src:
            src = img.get_attribute("src")
            if src not in unique_src_values:
                unique_src_values.append(src)

        for src in progress.tqdm(unique_src_values, desc="Processing..."):
            if src.split(".")[-1] not in ["png", "jpg", "jpeg"]:
                continue
            sb.download_file(src, downloadDir)
            filename = src.split("/")[-1]
            #sb.assert_downloaded_file(filename)
            file_path = os.path.join(downloadDir, filename)
            imgs.append(file_path)
            time.sleep(0.1)      

    processing = False    
    if len(imgs) > 0:    
        return [load_image(imgs[0])] + [None for i in range(len(added_img_indicies), 48)] + [None, "Import Done"]
    return [None] + [None for i in range(len(added_img_indicies), 48)] + [None, "Import Done"]                

         

def on_ui_tabs():
  label1 = None
  label2 = None
  added_imgs = [None] * 48
  settingsFile = "extensions/sd-webui-extension-detect-objects-captions/settings.st"

  file = open(settingsFile, 'r')

  objWidth = int(file.readline()[18:])
  objHeight = int(file.readline()[19:])
  confl = float(file.readline()[22:])
  capLen = int(file.readline()[20:])

  with gr.Blocks(analytics_enabled=False) as Objects_Detections_and_Captions:
    #with gr.Group():
      with gr.Row():
        with gr.Column():
          with gr.Row(variant = 'panel'):
            image = gr.Image(height = 600, width = 400, show_label = False, container = False, show_download_button = False)
          with gr.Row(): 
            less = gr.Button(value="<", variant="primary", scale = 1, size="sm", elem_id = "buttonLeft") 
            addImg = gr.Button(value="Add", variant="primary", scale = 5, size="sm", elem_id = "buttonAdd")
            greater = gr.Button(value=">", variant="primary", scale = 1, size="sm", elem_id = "buttonRight") 
          
          with gr.Row():
            added_imgs[0] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[1] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[2] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[3] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[4] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[5] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
          with gr.Row():
            added_imgs[6] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[7] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[8] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[9] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[10] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[11] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
          with gr.Row():
            added_imgs[12] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[13] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[14] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[15] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[16] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[17] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
          with gr.Row():
            added_imgs[18] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[19] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[20] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[21] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[22] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[23] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)  
        with gr.Column():
          with gr.Row():
            added_imgs[24] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[25] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[26] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[27] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[28] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[29] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
          with gr.Row():
            added_imgs[30] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[31] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[32] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[33] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[34] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[35] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
          with gr.Row():
            added_imgs[36] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[37] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[38] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[39] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[40] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[41] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
          with gr.Row():
            added_imgs[42] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[43] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[44] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[45] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[46] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)
            added_imgs[47] = gr.Image(height = 50, width = 50, show_label = False, container = False, show_download_button = False)            
          image_selected = gr.Image(height = 600, wdth = 400, show_label = False, container = False, show_download_button = False)
          add = gr.Button(value="Add to Database", variant="primary", scale = 1, size="sm")                                              
        with gr.Column():
          with gr.Row():
                with gr.Row(scale = 1):
                        gr.Label(value="Import from a folder", show_label=False, container = False)              
          text1 = gr.Textbox(placeholder = "Insert folder location", scale = 1, show_label=False)
          with gr.Row():
            with gr.Row(scale=1):
                pass
            with gr.Row(scale=1):
                pass                
            with gr.Row(scale = 1):
              importF =  gr.Button(value="Import", variant="primary", scale = 1, size="sm", elem_id = "button1", elem_classes = "import0")
          importFDone = gr.Label(value="", show_label=False, container = False)
          with gr.Column(scale=1):
                pass
          with gr.Column(scale=1):
                pass 
          with gr.Column(scale=1):
                pass 
          with gr.Column(scale=1):
                pass 
          with gr.Column(scale=1):
                pass 
          with gr.Column(scale=1):
                pass 
          with gr.Column(scale=1):
                pass 
          gr.Label(value="WEBUI EXTENSION", show_label=False, container = False)
          with gr.Column():
            with gr.Row():
              gr.Label(value="processing", show_label=False, container = False)
              with gr.Row(scale=1):
                pass 
              with gr.Row(scale=1):
                pass
            with gr.Row():
               gr.Label(value="Detection", show_label=False, container = False)
            label1 = gr.Label(value="", show_label=False)
            with gr.Row():
               gr.Label(value="Caption", show_label=False, container = False)
            label2 = gr.Label(value="", show_label=False)                   
      with gr.Column():
        with gr.Column(variant = 'panel'):
         with gr.Row():
                with gr.Row(scale = 1, variant = 'panel'):
                        gr.Label(value="Import from another source", show_label=False, container = False)
                with gr.Row(scale=1):
                        pass 
                with gr.Row(scale=1):
                        pass
                with gr.Row(scale=1):
                        pass                 
         with gr.Row():
            text2 = gr.Textbox(placeholder = "Insert URL", scale = 4, show_label=False)
            importU = gr.Button(value="Import", variant="primary", scale = 1, size="sm", elem_classes = "import0")
            importUDone = gr.Label(value="", show_label=False, container = False)
            with gr.Row(scale=1):
                    pass                 
    #with gr.Group():   
        with gr.Column(variant = 'panel'):
          with gr.Row():
                with gr.Row(scale=1, variant = 'panel'):                
                        gr.Label(value="Detection Settings", show_label=False, container = False)
                with gr.Row(scale=1):
                        pass
                with gr.Row(scale=1):
                        pass
                with gr.Row(scale=1):
                        pass
                with gr.Row(scale=1):
                        pass
          with gr.Row():
                with gr.Row(scale=1):
                    gr.Label(value="Minimum capture width:", scale = 4, show_label=False, container = False)
                    mcw = gr.Number(value=objWidth, precision=0, minimum=0, scale = 1, interactive = True, show_label=False, container = False)
                with gr.Row(scale=1):
                        pass
                        
          with gr.Row():
                with gr.Row(scale=1):
                    gr.Label(value="Minimum capture height:", scale = 4, show_label=False, container = False)
                    mch = gr.Number(value=objHeight, precision=0, minimum=0, scale = 1, interactive = True, show_label=False, container = False)
                with gr.Row(scale=1):
                        pass

          with gr.Row():
                with gr.Row(scale=1):
                    gr.Label(value="Minimum confidence level:", scale = 4, show_label=False, container = False)
                    mcfl = gr.Number(value=confl, minimum=0.0, maximum=0.99, step = 0.01, scale = 1, interactive = True, show_label=False, container = False)
                with gr.Row(scale=1):
                        pass                             

          with gr.Row():
                with gr.Row(scale=1):
                        pass
                with gr.Row(scale=1):
                        pass
                with gr.Row(scale=1):
                        pass
                with gr.Row(scale=1):
                        reset1 = gr.Button(value = "Reset", size="sm", elem_classes = "import1")
                        save1 = gr.Button(value = "Save", size="sm", variant="primary", elem_classes = "import1")
          objsv = gr.Label(value="", show_label=False, container = False)  
    #with gr.Group():  
        with gr.Column(variant = 'panel'):
          with gr.Row():
                with gr.Row(scale=1, variant = 'panel'):           
                        gr.Label(value="Caption Settings", show_label=False, container = False)
                with gr.Row(scale=1):
                        pass
                with gr.Row(scale=1):
                        pass
                with gr.Row(scale=1):
                        pass
                with gr.Row(scale=1):
                        pass

          with gr.Row():
                with gr.Row(scale=1):
                    gr.Label(value="Minimum caption length:", scale = 4, show_label=False, container = False)
                    mcpl = gr.Number(value=capLen, precision=0, minimum=0, scale = 1, interactive = True, show_label=False, container = False)
                with gr.Row(scale=1):
                        pass         

          with gr.Row():
                with gr.Row(scale=1):
                        pass
                with gr.Row(scale=1):
                        pass
                with gr.Row(scale=1):
                        pass
                with gr.Row(scale=1):
                        reset2 = gr.Button(value = "Reset", size="sm", elem_classes = "import1")
                        save2 = gr.Button(value = "Save", size="sm", variant="primary", elem_classes = "import1")
          capsv = gr.Label(value="", show_label=False, container = False)               
      add.click(img_detection, outputs=[label1, label2])
      label1.change(label_rest, outputs = [label1])
      label2.change(label_rest, outputs = [label2])  
      importF.click(update_images, inputs=[text1], outputs = [image] + [added_imgs[i] for i in range(0, 48)] +  [image_selected, importFDone])
      importU.click(import_from_url, inputs=[text2], outputs = [image] + [added_imgs[i] for i in range(0, 48)] +  [image_selected, importUDone])
      less.click(minus, outputs = [image])
      greater.click(plus, outputs = [image])
      addImg.click(add_image, outputs = [added_imgs[i] for i in range(0, 48)])
      reset1.click(reset_objsettings, outputs = [mcw, mch, mcfl])
      reset2.click(reset_capsettings, outputs = [mcpl])
      save1.click(save_settings, inputs=[mcw, mch, mcfl, mcpl], outputs = [objsv])
      save2.click(save_settings, inputs=[mcw, mch, mcfl, mcpl], outputs = [capsv])
      objsv.change(label_rest, outputs = [objsv])
      capsv.change(label_rest, outputs = [capsv])
      importFDone.change(label_rest, outputs = [importFDone])
      importUDone.change(label_rest, outputs = [importUDone])
      for i in range(0, 48):
         added_imgs[i].select(img_clicked, inputs = [gr.Number(value=i, precision=0, visible=False)], outputs = [image_selected])       
  return [(Objects_Detections_and_Captions, "Objects Detections and Captions", "Objects_Detections_and_Captions")]

script_callbacks.on_ui_tabs(on_ui_tabs)