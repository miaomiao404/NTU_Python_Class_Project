# Python開發環境建置-以miniconda建置指南

本文檔為Python開發環境建置的教學，本教學會以miniconda作為範例，講解如何建置一個用於開發本專案的Python環境，並且安裝所有必需套件。

---

## 1. Miniconda簡介

在 Python 開發中，我們經常需要為不同的專案安裝不同版本的套件。如果全部安裝在電腦的「全局環境」中，久了必定會發生衝突。

**Miniconda** 是一個輕量級的環境與套件管理工具。它可以幫我們在電腦裡切出多個「獨立的房間（虛擬環境）」。每個房間裡都可以有自己獨立的 Python 版本和套件，完全不會互相影響。相較於龐大的 Anaconda，Miniconda 體積更小、速度更快，只包含最核心的工具，非常適合開發者使用。

> 如果已經安裝 Anaconda，也可以稍微參照本教學，但不建議照單全收，因為 Anaconda 可以視為 Miniconda 加上一堆Python套件擴充包。

---

## 2. 下載與安裝 Miniconda

1. 前往官方下載頁面：[Miniconda 官方下載連結](https://docs.conda.io/en/latest/miniconda.html)
2. 選擇符合你作業系統的安裝檔（Windows 使用者請下載 **Windows 64-bit** 版本）。
3. 執行安裝檔，安裝過程中的選項全部保留**預設值**，一直點擊「Next」直到完成即可。

---

## 3. 初次開啟 Miniconda 的推薦設定

> 請確保你已經完成了 `cmd_tutorial.md` 中的「終端機初始化設定」，讓你的 Windows PowerShell 或 VS Code 終端機已經可以使用 `conda` 指令，否則以下指令請在 Anaconda Powershell Prompt 中執行。  
> 本設定可以跳過，視個人習慣決定要不要做這一步

每次打開終端機時，Conda 預設會自動進入 `(base)` 基礎環境。為了保持環境整潔，我們通常會關閉這個自動啟動功能。

請打開 VS Code 終端機（或 PowerShell），輸入以下指令並按下 Enter：
```powershell
conda config --set auto_activate_base false
```
設定完成後，下次打開終端機就不會強制掛著 `(base)` 了，畫面會更乾淨。*

---

## 4. 建立專案專屬的虛擬環境

我們現在要為這個字體臨摹專案建立一個專屬的「房間」。
根據專案規範，我們統一使用 **Python 3.11.3** 版本。

在終端機中輸入以下指令來建立環境（在此教學中，我們將環境命名為 `font_mimic`，各位可以視需求自行設定名稱）：
```powershell
conda create -n font_mimic python=3.11.3 -y
```
*(參數說明：`-n` 代表環境名稱，`-y` 代表安裝過程中自動同意所有提示)*

---

## 5. 在 VS Code 中切換與管理環境 (Conda 基本指令)

建立好環境後，我們需要「進入」這個環境才能開始安裝套件與開發。以下是你每天開發都會用到的基本指令：

**啟動（進入）環境：**
```powershell
conda activate font_mimic
```
> 成功啟動後，你終端機輸入列的最前面會多出一個 `(font_mimic)` 的標籤，代表你現在所有的操作都會限制在這個環境內！

**退出環境（回到無環境狀態）：**
```powershell
conda deactivate
```

**查看目前電腦裡有哪些環境：**
```powershell
conda env list
```

---

## 6. 安裝專案所需的套件 (pip install)

**【非常重要】在執行以下步驟前，請務必確認你的終端機前方顯示著 `(font_mimic)`！**

確認進入虛擬環境後，我們可以直接透過一行指令，把專案核心需要的第三方套件（如影像處理、AI 串接工具等）全部安裝到位：

```powershell
pip install Pillow opencv-python numpy google-generativeai python-dotenv
```

或是分開一個一個安裝

```powershell
pip install Pillow
pip install opencv-python
...
pip install python-dotenv
```

**套件功能簡介：**
* `Pillow`: Python 最基礎的影像處理庫，用來將文字渲染成圖片。
* `opencv-python`: 強大的電腦視覺庫，用來處理圖片濾鏡、變形與相似度比對。
* `numpy`: OpenCV 的底層運算庫，處理影像矩陣必備。
* `google-generativeai`: Google 官方套件，用來串接本專案選用的 Gemini AI API。
* `python-dotenv`: 用來安全讀取 `.env` 檔案中的 API Key 等機密資訊，避免金鑰外流。

**補充：後端 Web 框架套件**

如果在開發時發現需要用到此部分的套件，請用相同的方法把它們安裝進來

```powershell
pip install Flask
pip install flask-cors
```

* `Flask`: 輕量級的 Python Web 框架，用來建立後端伺服器與 API 路由。
* `flask-cors`: 處理跨網域請求 (CORS) 的套件。因為我們的前端介面和後端伺服器在開發時通常會跑在不同的 Port 上，這個套件能確保前端可以順利拿到後端的資料而不被瀏覽器阻擋。

---

## 7. 套件查詢相關語法

如想要查詢目前環境下已安裝的python套件，可以使用以下語法查詢。

```powershell
pip list
```

如想要查詢目前環境下特定已安裝的python套件的詳細資訊，可以使用以下語法查詢。

```powershell
pip show <package_name>
```