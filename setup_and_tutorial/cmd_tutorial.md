# 終端機(cmd/powershell)基礎語法教學及conda powershell設定

本文檔為cmd/powershell部分基礎語法的教學，以及conda使用者要使用VSCode內終端機運行conda指令前需要完成的設定

> `powershell` 可以簡單理解為新的cmd，多出了一些更好用的功能。

---

## 1. 終端機基礎路徑語法

在圖形化介面 (GUI) 中，我們用滑鼠雙擊資料夾來移動；在終端機中，我們透過**輸入指令**來移動。以下是開發時每天都會用到的基礎指令：

### - 認識路徑符號 (`./` 與 `../`)
在終端機中，路徑代表你現在的「位置」。
* **`./` (現在這裡)**：代表「當前所在的資料夾」。如果你要執行當前資料夾下的一個程式，有時需要寫 `./script.py`。
* **`../` (上一層)**：代表「回到上一層資料夾」。這在切換目錄時非常常用。

### - `cd` (切換目錄 Change Directory)
這是你最常用的指令，用來移動到不同的資料夾。
```powershell
# 移動到指定的資料夾 (例如名為 project 的資料夾)
cd project

# 回到上一層資料夾
cd ../

# 一次回到上兩層資料夾
cd ../../

# (進階技巧) 切換到另一個硬碟 (例如從 C 槽換到 D 槽)
# 直接輸入磁碟機代號加冒號即可
D:
```

### - `ls` 或 `dir` (列出檔案清單)
使用此指令可以列出所有現在所在資料夾下的所有檔案及資料夾
```powershell
# Mac 或 PowerShell 常用
ls

# Windows CMD 專用
dir
```

### - 其他實用開發指令
```powershell
# 建立一個新的資料夾 (Make Directory)
mkdir my_new_folder

# 清空終端機畫面 (當畫面被一堆錯誤訊息塞滿時很好用)
clear   # Mac 或 PowerShell 使用
cls     # Windows CMD 使用

# 用 VS Code 開啟當前資料夾
# (注意：code 後面有一個空格和一個點)
code .
```

### - **Tab 鍵自動補全**
像是使用cd指令等等時，如果要快速的輸入資料夾的名字，可以輸入前面的部分字母後按tab，系統會依字母順序依序補上後面的字，可以按tab多次來補上下一個。

---

## 2. VS Code powershell 與 Miniconda powershell連接

### 為什麼 Windows 的 PowerShell 找不到 `conda`？
當安裝完 Miniconda 後， Windows 開始選單裡會多一個 **"Anaconda Prompt (Miniconda3)"**。由於各種原因，如果沒有執行以下設定， `conda` 指令僅在此 powershell 可運行。

> 在 VS Code 中，下方的 Terminal (終端機) 其實就是 Windows 的 powershell。

### 如何解決？(Conda 初始化)

請運行以下設定，讓以後在 VS Code 裡面也可以直接使用 `conda` 指令(本設定只要運行一次即可)。

**步驟一：以「系統管理員」身分開啟 Anaconda Prompt**
1. 點擊 Windows 開始選單，搜尋 `Miniconda` 或 `Anaconda`。
2. 找到 **Anaconda Prompt (Miniconda3)**。
3. 對它點右鍵 ➡️ 選擇 **「以系統管理員身分執行」**。

**步驟二：執行初始化指令**
在黑底白字的視窗中，輸入以下指令並按下 Enter：
```powershell
conda init powershell
```
*這句指令的意思是：請 Conda 把啟動腳本寫入 Windows PowerShell 的設定檔中。*

**步驟三：解除 Windows 的腳本執行限制 (非常重要)**
Windows 為了安全，預設會阻止 PowerShell 執行任何設定腳本（這會導致剛剛的初始化失敗，打開 VS Code 時會看到一串紅字錯誤）。我們必須稍微放寬這個限制。
請在剛才的 Anaconda Prompt 中繼續輸入以下指令並按下 Enter：
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```
*系統可能會跳出確認訊息，請輸入 `Y` 然後按 Enter 同意。*

**步驟四：驗證是否成功**
1. 關閉剛剛的 Anaconda Prompt。
2. **打開 VS Code**，並開啟 VS Code 內建的終端機 (`Ctrl` + `~` 或點選上方選單 `終端機 -> 新增終端機`)。
3. 觀察終端機輸入列的最前面，是不是多了一個 **`(base)`**？
   例如：`(base) PS C:\Users\YourName\Desktop>`
4. 輸入 `conda --version` 看看是否能正常印出版本號。

> 檢查conda有沒有安裝好的方式就是 `--version` ，這在所有套件上都差不多， `--version` 基本上是一個很萬能的檢查工具。