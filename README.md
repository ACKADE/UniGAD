# UniGAD Windows 部署完整指南

> 本指南专为完全零基础的本科生编写，将一步一步手把手教你如何在 **Windows 电脑**上运行 UniGAD 项目。**不需要任何提前知识**，照着做就行！

---

## 目录

1. [你的电脑需要什么？](#1-你的电脑需要什么)
2. [第一步：安装 Anaconda（管理 Python 环境）](#2-第一步安装-anaconda管理-python-环境)
3. [第二步：安装 Git（下载代码工具）](#3-第二步安装-git下载代码工具)
4. [第三步：打开 Anaconda Prompt（命令行）](#4-第三步打开-anaconda-prompt命令行)
5. [第四步：下载项目代码](#5-第四步下载项目代码)
6. [第五步：创建专属 Python 环境](#6-第五步创建专属-python-环境)
7. [第六步：安装 PyTorch 和 DGL](#7-第六步安装-pytorch-和-dgl)
8. [第七步：安装其余依赖包](#8-第七步安装其余依赖包)
9. [第八步：下载数据集](#9-第八步下载数据集)
10. [第九步：运行实验](#10-第九步运行实验)
11. [常见错误与解决方法](#11-常见错误与解决方法)
12. [如果你有 GPU（进阶，可选）](#12-如果你有-gpu进阶可选)

---

## 1. 你的电脑需要什么？

在开始之前，先确认你的电脑满足以下条件：

| 要求 | 说明 |
|------|------|
| 操作系统 | **Windows 10 / Windows 11**（64 位） |
| 内存（RAM） | 建议 **16 GB** 以上（最低 8 GB） |
| 硬盘空间 | 至少 **20 GB** 可用空间 |
| 网络 | 需要能访问互联网（部分内容可能需要 VPN）|
| GPU（显卡）| **不是必须的**，没有独立显卡也能跑（但会慢很多）|

> **什么是命令行（终端）？**  
> 命令行就是一个可以输入文字命令来控制电脑的黑色（或白色）窗口。不要害怕它，你只需要把本指南里的命令**复制粘贴**进去，按回车就行。

---

## 2. 第一步：安装 Anaconda（管理 Python 环境）

Anaconda 是一个帮你管理 Python 和各种科学库的工具，**强烈推荐**新手使用。它自带了很多科学计算包的预编译版本，可以避免 Windows 上因缺少 C 编译器而导致的安装失败问题。

1. 打开浏览器，访问：https://www.anaconda.com/download
2. 点击 **"Download"** 按钮，下载 Windows 版本的安装包（文件名类似 `Anaconda3-xxxx-Windows-x86_64.exe`）
3. 双击安装包，一路点 **"Next"** → **"I Agree"** → **"Next"** → **"Next"**
4. 在"Advanced Options"页面，**勾选"Add Anaconda3 to my PATH environment variable"**（这很重要！）
5. 点击 **"Install"**，等待安装完成（大约 5-10 分钟）
6. 安装完成后，点击 **"Finish"**

### 验证 Anaconda 安装成功

打开命令行（下一步会讲如何打开），输入：

```bash
conda --version
```

如果显示类似 `conda 24.x.x`，说明安装成功！

---

## 3. 第二步：安装 Git（下载代码工具）

Git 是一个用于下载和管理代码的工具。

1. 访问：https://git-scm.com/download/win
2. 点击自动弹出的下载链接（文件名类似 `Git-2.xx.x-64-bit.exe`）
3. 双击安装，一路点 **"Next"**，保持默认设置即可
4. 安装完成后，在开始菜单搜索 **"Git Bash"**，可以用它来输入命令

---

## 4. 第三步：打开 Anaconda Prompt（命令行）

**Anaconda Prompt** 是我们后续所有操作的主战场，它已经配置好了 conda 环境，比普通命令提示符更适合本项目。

1. 点击 Windows 开始菜单
2. 搜索 **"Anaconda Prompt"**
3. 点击打开，你会看到一个黑色窗口，里面有 `(base)` 字样

> **提示：** 后续所有命令都在 **Anaconda Prompt** 中执行，请不要使用普通的"命令提示符（cmd）"或"PowerShell"，否则可能出现 `conda: command not found` 错误。

---

## 5. 第四步：下载项目代码

在 Anaconda Prompt 中，按照以下步骤操作：

### 1. 选择一个放代码的位置

```bash
cd Desktop
```

> 这条命令的意思是"进入桌面文件夹"。你的代码文件夹就会出现在桌面上，方便查找。

### 2. 下载（克隆）项目代码

```bash
git -c http.sslVerify=false clone https://github.com/ACKADE/UniGAD.git
```

> 等待下载完成，命令行会显示进度。完成后桌面会出现一个名为 `UniGAD` 的文件夹。

### 3. 进入项目文件夹

```bash
cd UniGAD
```

> 执行后你会进入项目的根目录。你可以用 `dir` 查看里面的文件。

---

## 6. 第五步：创建专属 Python 环境

为了不让这个项目的依赖和你电脑上其他软件冲突，我们需要创建一个**独立的虚拟环境**。

```bash
conda create -n unigad python=3.10
```

> 这条命令创建了一个名为 `unigad`、使用 Python 3.10 的虚拟环境。  
> 途中会询问 `Proceed ([y]/n)?`，输入 `y` 然后按回车。

创建完成后，**激活这个环境**：

```bash
conda activate unigad
```

> 激活成功后，你会看到命令行最左边由 `(base)` 变成了 `(unigad)`。**以后每次想运行这个项目，都要先执行这条命令！**

---

## 7. 第六步：安装 PyTorch 和 DGL

PyTorch 和 DGL 是这个项目最核心的两个库。安装时需要选择适合你电脑的版本。

### 如果你的电脑**没有独立显卡**（或不确定）：

**安装 PyTorch（CPU 版本）：**

```bash
pip install torch==2.2.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**安装 DGL（CPU 版本）：**

```bash
pip install dgl==2.2.1 -f https://data.dgl.ai/wheels/torch-2.2/cpu/repo.html
```

### 如果你的电脑**有 NVIDIA 独立显卡**（GPU，推荐）：

> 先确认你的 CUDA 版本：在命令行输入 `nvidia-smi`，看 **"CUDA Version"** 那一列的数字。

**安装 PyTorch（CUDA 11.8 版本，适配大多数显卡）：**

```bash
pip install torch==2.2.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**安装 DGL（CUDA 11.8 版本）：**

```bash
pip install dgl==2.2.1 -f https://data.dgl.ai/wheels/torch-2.2/cu118/repo.html
```

### 验证 PyTorch 安装是否成功：

```bash
python -c "import torch; print(torch.__version__)"
```

如果输出类似 `2.2.1`，说明安装成功！

---

## 8. 第七步：安装其余依赖包

> ⚠️ **Windows 特别说明（重要！）**  
> `requirements.txt` 中部分包（如 `matplotlib`、`contourpy`、`line_profiler`）在 Windows 上需要 C 编译器才能从源码构建。如果你的电脑没有安装 Visual Studio 或 MinGW，直接运行 `pip install -r requirements.txt` 会报如下错误：  
> ```
> ERROR: Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc'], ...]
> ```  
> **解决方案：** 先用 conda 安装这些编译型依赖（conda 提供预编译的二进制包），再用 pip 安装其余依赖。

### 第 1 步：用 conda 安装需要编译的包

确保已激活 `unigad` 环境（命令行左边显示 `(unigad)`），然后执行：

```bash
conda install -c conda-forge matplotlib=3.9.1 contourpy line_profiler numba -y
```

> 这条命令会从 conda-forge 频道下载预编译好的二进制包，**不需要任何 C 编译器**。安装过程可能需要几分钟，请耐心等待。

### 第 2 步：用 pip 安装其余依赖

确保你在 `UniGAD` 项目文件夹下（不确定的话，重新执行 `cd Desktop\UniGAD`），然后运行：

```bash
pip install -r requirements.txt
```

> 由于 matplotlib 等包已在上一步通过 conda 安装，pip 会自动跳过已安装的包，只安装剩余的依赖。  
> 安装过程较长（可能需要 5-20 分钟），请耐心等待。  
> 安装过程中可能会看到一些黄色的警告信息（WARNING），这通常不影响使用，可以忽略。  
> 如果出现红色的错误（ERROR），请见[常见错误与解决方法](#11-常见错误与解决方法)。

---

## 9. 第八步：下载数据集

这个项目使用多种数据集。这里以 **weibo** 数据集为例（已包含在仓库中），以及如何下载 **T-Group** 数据集。

### weibo 数据集（已内置，无需下载）

仓库的 `datasets/edge_labels/` 文件夹中已经包含了 `weibo-els` 数据集，可以直接使用。

### T-Group 数据集（需要手动下载）

1. 打开浏览器，访问论文提供的链接：  
   https://drive.google.com/file/d/1B-pmATZt9aBmxD8PkuUFAP6ZI-939Xma/view?usp=sharing

   > ⚠️ Google Drive 在国内需要使用 VPN 才能访问。如果无法访问，可以先跳过这个数据集，用 weibo 数据集测试。

2. 点击右上角的**下载按钮**（向下箭头图标）

3. 下载完成后，解压该文件，将解压出来的文件夹放入项目的 `datasets/unified/` 目录下

---

## 10. 第九步：运行实验

一切准备就绪！现在我们来运行一个实验。

### 1. 进入 src 目录

```bash
cd src
```

### 2. 创建保存结果的文件夹

```bash
mkdir ..\results
```

> 如果提示"子目录或文件已存在"，忽略该提示即可。

### 3. 运行 weibo 数据集上的实验（推荐新手从这里开始）

```bash
python main.py --datasets 1 --pretrain_model graphmae --kernels bwgnn,gcn --lr 5e-4 --save_model --epoch_pretrain 50 --batch_size 1 --khop 1 --epoch_ft 300 --lr_ft 0.003 --final_mlp_layers 3 --cross_modes ne2ne,n2ne,e2ne --metric AUROC --trials 5
```

> **各参数说明：**
> - `--datasets 1`：使用第 2 个数据集（weibo），编号从 0 开始，所以 1 是 weibo
> - `--pretrain_model graphmae`：使用 GraphMAE 预训练模型
> - `--kernels bwgnn,gcn`：使用两种图神经网络核
> - `--epoch_pretrain 50`：预训练 50 轮
> - `--epoch_ft 300`：微调训练 300 轮
> - `--trials 5`：重复实验 5 次取平均值

### 4. 等待运行完成

程序运行时，你会看到类似以下的输出：

```
preparing the dataset for 5 trials
making the subpooling matrix
start pre-training..
# Epoch 0
    train_loss: 0.8234
...
training...
```

> ⏱️ **运行时间参考：**
> - 没有 GPU（CPU 运行）：可能需要 **数小时**
> - 有 GPU（CUDA 运行）：通常需要 **30-60 分钟**

### 5. 查看结果

实验完成后，结果会保存在 `results/` 文件夹下，是一个 `.csv` 格式的文件，可以用 Excel 打开查看。

---

## 11. 常见错误与解决方法

### ❌ 错误：`Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc'], ...]`（matplotlib 编译失败）

**错误完整信息示例：**
```
error: metadata-generation-failed
× Encountered error while generating package metadata.
╰─> matplotlib
...
ERROR: Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc'], ['clang'], ...]
```

**原因：** Windows 上没有安装 C 编译器（如 Visual Studio），pip 尝试从源码编译 matplotlib 时失败。  
**解决：** 按照[第七步](#8-第七步安装其余依赖包)的说明，**先用 conda 安装需要编译的包**，再运行 `pip install -r requirements.txt`：

```bash
conda install -c conda-forge matplotlib=3.9.1 contourpy line_profiler numba -y
pip install -r requirements.txt
```

---

### ❌ 错误：`SSL certificate problem: unable to get local issuer certificate`

**错误完整信息示例：**
```
fatal: unable to access 'https://github.com/ACKADE/UniGAD.git/': SSL certificate OpenSSL verify result: unable to get local issuer certificate (20)
```

**原因：** Git 使用的 SSL 证书库无法验证 GitHub 的 HTTPS 证书，常见于企业网络、学校网络或国内特定网络环境。

**解决方法（任选其一）：**

**方法一：临时禁用 Git 的 SSL 验证（最简单）**

> ⚠️ 此方法会降低安全性，仅建议在可信网络环境中使用，克隆完成后建议恢复设置。

```bash
git config --global http.sslVerify false
git clone https://github.com/ACKADE/UniGAD.git
```

克隆完成后，恢复 SSL 验证：
```bash
git config --global http.sslVerify true
```

**方法二：更新系统 CA 证书**

打开"控制面板" → "Windows Update"，安装所有可用更新，或访问 https://curl.se/docs/caextract.html 下载最新的 `cacert.pem`，然后执行：
```bash
git config --global http.sslCAInfo "C:/path/to/cacert.pem"
```

**方法三：使用 VPN 或代理**

如果你处于企业/学校内网，使用 VPN 切换到正常网络环境后重试。

---

### ❌ 错误：`conda: command not found`

**原因：** Anaconda 没有正确添加到系统路径，或者使用了普通命令提示符而不是 Anaconda Prompt。  
**解决：**
1. 确保使用 **Anaconda Prompt**（在开始菜单搜索"Anaconda Prompt"）而不是普通的 cmd 或 PowerShell
2. 如果 Anaconda Prompt 也不行，重新安装 Anaconda，安装时一定要勾选 **"Add to PATH"** 选项

---

### ❌ 错误：`pip install` 速度极慢

**原因：** pip 默认从国外服务器下载，国内速度较慢。  
**解决：** 使用国内镜像源加速：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

conda 也可以配置国内镜像：
```bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --set show_channel_urls yes
```

---

### ❌ 错误：`ModuleNotFoundError: No module named 'dgl'`

**原因：** DGL 没有安装成功，或者当前不在 `unigad` 环境中。  
**解决：**
1. 检查是否激活了正确的环境：命令行最左边是否显示 `(unigad)`？
2. 如果没有，运行 `conda activate unigad`
3. 然后重新安装 DGL（参考第六步）

---

### ❌ 错误：`CUDA out of memory`（显存不足）

**原因：** GPU 显存不够。  
**解决：** `--batch_size 1` 已是最小值。可以改用 CPU 运行：删除 `--batch_size` 以外的 CUDA 相关参数，程序会自动使用 CPU。

---

### ❌ 错误：`FileNotFoundError: ../datasets/...`

**原因：** 数据集文件不存在，或者你不在 `src/` 目录下运行命令。  
**解决：**
1. 确保你执行了 `cd src` 进入了 src 目录
2. 确保数据集已正确放入 `datasets/` 文件夹中

---

### ❌ 错误：`No such file or directory: '../results/'`

**原因：** results 文件夹不存在。  
**解决：** 在运行实验前，先执行：
```bash
mkdir ..\results
```

---

## 12. 如果你有 GPU（进阶，可选）

如果你的电脑有 NVIDIA 独立显卡（如 RTX 3060、RTX 4070 等），使用 GPU 可以大幅提升训练速度。

### 检查你的 GPU

在 Anaconda Prompt 中输入：

```bash
nvidia-smi
```

如果看到类似如下的表格，说明你有 NVIDIA GPU：

```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.xx   Driver Version: 535.xx   CUDA Version: 12.x            |
+-----------------------------------------------------------------------------+
| GPU 0: NVIDIA GeForce RTX 3060  ...                                         |
```

记住右上角的 **CUDA Version** 数字（如 12.1），安装对应版本的 PyTorch。

### 验证 PyTorch 是否能使用 GPU

```bash
python -c "import torch; print('GPU可用:', torch.cuda.is_available())"
```

如果输出 `GPU可用: True`，恭喜你！程序会自动使用 GPU 加速。

---

## 总结：每次使用项目的流程

```
1. 打开 Anaconda Prompt
2. conda activate unigad               # 激活环境
3. cd Desktop\UniGAD\src               # 进入项目的 src 目录
4. python main.py --datasets 1 ...     # 运行实验
```

---

## 如果还有问题？

- 在 GitHub 上提交 Issue：https://github.com/ACKADE/UniGAD/issues
- 参考论文：*UniGAD: Unifying Multi-level Graph Anomaly Detection*，NeurIPS 2024

---

祝你顺利运行成功！🎉
