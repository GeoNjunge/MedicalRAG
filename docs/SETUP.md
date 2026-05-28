# Setup 
## Ollama
Install it on your Windows machine using:
   ```bash
   irm https://ollama.com/install.ps1 | iex
   ```

   linux and MacOS:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

Follow the tutorial at [ollama docs](https://docs.ollama.com/api/introduction) to install the model of your choice.
Choice of model was **qwen2.5** 

you can run in terminal(linux/Powershell)
   ```bash
   ollama run qwen2.5-1.5B
   ```
   to install model or use Ollama GUI

If using windows always make sure the running backend can be able to access 
[Link to ollama docs](https://docs.ollama.com/api/introduction)

## Clone the repo
```bash
git clone <repo>
cd MedicalRAG
```

# Set up the ml_core module
from root directory install 
```bash
pip install -e ./ml_core
pip install -r requirements.txt
```

## Running backend Locally
[Backend_setup](/apps/api/README.md)

## Running frontend
```bash
git clone <repo>
cd apps/web/frontend/
npm i
ng serve
```

## Running ml tests
```bash
pytest ml_core/ -vv
```

# Note
## Pytorch
If your machine has GPU:
   install normal Pytorch
   (you can include it inside the requirements.txt as:
   ```bash
      torch==2.10.0 # You can just use latest version
      torchvision==0.25.0
   ```
   )
else:
   install CPU torch
   (you can include it inside the requirements.txt as:
   ```bash
      torch==2.10.0+cpu
      torchvision==0.25.0+cpu
   ```
   )

Choice of model depends on your machines capabilities.
My machine is:
```bash
Device Name	DESKTOP-87BO9C5
Processor	Intel(R) Core(TM) i3-1005G1 CPU @ 1.20GHz   1.19 GHz
Installed RAM	16.0 GB (15.8 GB usable)
Storage	238 GB SSD Kingstore M.2 256GB, 932 GB HDD WDC WD10SPZX-60Z10T1
Graphics Card	Intel(R) UHD Graphics (128 MB)
System Type	64-bit operating system, x64-based processor
```


