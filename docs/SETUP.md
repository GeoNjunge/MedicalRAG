# Pytorch
If your machine has GPU:
     install normal Pytorch
     (you can include it inside the requirements.txt as:
        torch==2.10.0 # You can just use latest version
        torchvision==0.25.0)
else:
     install CPU Pytorch
     (you can include it inside the requirements.txt as:
        torch==2.10.0+cpu
        torchvision==0.25.0+cpu)


# Ollama
Install it on your Windows machine using:
   ```irm https://ollama.com/install.ps1 | iex```

   linux and MacOS:
   ```curl -fsSL https://ollama.com/install.sh | sh```

Choice of model depends on your machines capabilities.
My machine is:
```Device Name	DESKTOP-87BO9C5
Processor	Intel(R) Core(TM) i3-1005G1 CPU @ 1.20GHz   1.19 GHz
Installed RAM	16.0 GB (15.8 GB usable)
Storage	238 GB SSD Kingstore M.2 256GB, 932 GB HDD WDC WD10SPZX-60Z10T1
Graphics Card	Intel(R) UHD Graphics (128 MB)
Device ID	2D4E80A9-26F3-4C50-8C85-8907E823DFBD
Product ID	00327-31058-84051-AAOEM
System Type	64-bit operating system, x64-based processor
Pen and touch	No pen or touch input is available for this display
```

Choice of model was **qwen2.5-coder:3b** 

If using windows always make sure the running backend can be able to access 
[Link to ollama docs](https://docs.ollama.com/api/introduction)