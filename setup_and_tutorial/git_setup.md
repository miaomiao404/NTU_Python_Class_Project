# 專案 Git 協作指南 (Onboarding Guide)

本文檔為git設定的使用教學，裡面包含了git的下載與設定、下載專案、同步專案、初次專案git環境設定、以及每次開發前及開發後務必做的操作，請依照這份文檔的指示設定好git的環境

---

## 1. 安裝 Git 至電腦上

如果你目前的電腦還沒有安裝 Git，請根據你的作業系統進行安裝：

* **Windows:**
    1. 前往 Git 官方網站下載安裝檔：[Git for Windows](https://git-scm.com/download/win)
    2. 下載後執行安裝程式，安裝過程中的選項全部使用**預設值**並一直點擊「下一步」即可。
* **macOS:**
    1. 開啟「終端機 (Terminal)」。
    2. 輸入 `git --version`，如果尚未安裝，系統會自動跳出視窗詢問是否安裝 Apple 的命令列開發者工具，點擊「安裝」即可。
    3. (進階使用者) 也可以透過 Homebrew 安裝：輸入 `brew install git`。

---

## 2. 檢查 Git 是否安裝完成與基本設定

安裝完成後，我們需要確認 Git 是否能正常運作，並綁定你的開發者身分。

1. 打開終端機（Windows 請打開 `Git Bash` 或 `命令提示字元`；Mac 請打開 `Terminal`）。
2. 輸入以下指令來檢查版本：
    ```bash
    git --version
    ```
    > 如果終端機回傳類似 `git version 2.xx.x` 的字樣，就代表安裝成功了！

3. **初次使用必做：** 告訴 Git 你是誰（這會顯示在未來的修改紀錄中）：
    ```bash
    git config --global user.name "你的名字或英文暱稱"
    git config --global user.email "你的聯絡信箱"
    ```

---

## 3. 將專案資料夾綁定至本機 (Clone)

我們不需要手動建立資料夾，直接將雲端上的專案「複製」下來即可，這會自動為你建立綁定好 Git 的專案資料夾。

1. 在終端機中，切換到你想要存放專案的目錄（例如桌面）：
    ```bash
    cd Desktop
    ```
2. 執行 `git clone` 指令，將專案拉取到本機：
    ```bash
    git clone https://github.com/miaomiao404/NTU_Python_Class_Project.git
    ```
3. 進入剛剛載下來的專案資料夾：
    ```bash
    cd NTU_Python_Class_Project
    ```

---

## 4. 初次工作流：建立個人專屬分支 (Branch)

**為了不要讓大家對程式的更改混雜在一起或對 `main` 造成破壞，請每一個人都開一個 `branch` 進行操作**
為了避免衝突，每個人都需要開一個自己的分支。

1. 確保你目前在專案資料夾內。
2. 建立並切換到你的個人分支（請將 `<your-name>` 換成你的英文名字或暱稱，例如 `xiaoming`）：
    ```bash
    git switch -c <your-name>-dev
    ```
    > 註：`switch -c` 的意思是「建立新分支並立刻切換過去」。  
    > 註：`-c` 的意思是「在分支不存在時，建立一個新分支」。  
    > 那個 `<your-name>-dev` 是什麼名字其實也沒差，就取一個不會搞混的名字就好。
3. 確認你目前所在的分支：
    ```bash
    git branch
    ```
    > 畫面上你的分支前面會出現一個星號 `*`，代表你現在安全地待在自己的分支裡了。

---

## 5. 每次「開始」開發前要做的步驟

專案是大家一起協作的，在你每天要開始寫扣之前，必須先確保你的分支擁有團隊最新的進度，以免日後發生程式碼衝突。

**標準開工起手式：**
1. 先切換回主分支：
    ```bash
    git switch main
    ```
2. 把雲端上最新的進度拉取下來：
    ```bash
    git pull origin main
    ```
3. 切回你自己的開發分支：
    ```bash
    git switch <your-name>-dev
    ```
    > `switch` 後面接的就是你的分支的名字(如果你亂取的話不會長這樣)。
4. 將主分支最新的進度「合併」到你的分支裡：
    ```bash
    git merge main
    ```
    > `merge` 這邊的功能是把 `main` 分支的內容抓進你現在所在的分支內。  
    > 執行完這四步，你的個人分支就和團隊最新進度同步了，可以安心開始今天的開發！

---

## 6. 每次「完成」開發後要做的步驟

當你完成了一個段落的功能，準備休息或下班前，請務必將你的進度存檔並推送到雲端備份。

**標準收工存檔式：**
1. 檢查有哪些檔案被修改了（確認狀態）：
    ```bash
    git status
    ```
    > 被修改的檔案會以紅色顯示。
2. 將所有修改過的檔案加入暫存區：
    ```bash
    git add .
    ```
    > 點 `.` 代表「這個資料夾下的所有變更」。  
    > 也可以用相對路徑。
3. 提交這次的修改紀錄（Commit），請稍微留下這次commit的修改訊息：
    ```bash
    git commit -m "新增：完成了首頁的登入 UI 介面"
    ```
    > 務必記得雙引號 `""`。  
    > 你可以瘋狂的開發，`commit` 很多次之後再一起 `push` 也沒問題，而且這裡更鼓勵在每次開發一個段落都建立一個版本，這樣遇到問題更容易回頭。
4. 將你的分支推送到雲端 GitHub 上：
    ```bash
    git push origin <your-name>-dev
    ```
    > **注意：** 如果這是你「第一次」推送這個分支，系統可能會提示你設定上游，請直接複製終端機提示的那行指令貼上執行即可（通常是 `git push --set-upstream origin <your-name>-dev`）。

---

## 7. 將開發成果合併至主分支 (Merge to main)

在自己的分支開發到一段落後，要把分支的內容合併到 `main` ，讓大家可以使用到你開發的成果。

為了避免不小心弄壞主程式，我們使用 GitHub 網站的 **Pull Request (PR)** 功能來進行合併。
> PR發出之後，會經過一個審核階段，經過審核的內容更可以保證主程式的安全性

**標準合併流程 (透過 GitHub)：**

1. **前往專案 GitHub 頁面：**
   打開瀏覽器，進入我們的專案網址：[https://github.com/miaomiao404/NTU_Python_Class_Project](https://github.com/miaomiao404/NTU_Python_Class_Project)
2. **發起合併請求 (Pull Request)：**
   因為你剛剛才 push 了你的分支，GitHub 頁面上方通常會自動跳出一個黃綠色的提示框，上面寫著 **「Compare & pull request」**。請點擊這個按鈕。
   > ( 如果沒看到這個按鈕，請點擊上方的 `Pull requests` 標籤頁，然後點擊綠色的 `New pull request` 按鈕，並將 `base` 設為 `main`，`compare` 設為你的分支 `你的分支的名字` )
3. **填寫更新內容：**
   在標題和內文欄位中，簡單描述你這次新增或修改了什麼功能（例如：「完成字體上傳的 API 串接」），讓其他夥伴知道這個合併包含什麼內容。
4. **建立請求：**
   點擊綠色的 **「Create pull request」** 按鈕。
5. **確認並合併 (Merge)：**
   檢查沒有衝突 (No conflicts) 後，點擊下方的 **「Merge pull request」**，然後點擊 **「Confirm merge」**。
   > 如果你發現你按不了，那就不要管他，反正有人會幫你確認，確認完之後就會 `merge` 成功了。  
   > 可以按的話就自己按吧。
   > 有衝突的話請檢查哪裡的檔案衝突了並且決定要採用你的分支的檔案或 `main` 分支的檔案，阿如果不會決定就放著，會有人幫你決定。

---

### 合併完成後，我該做什麼？

既然雲端的 `main` 已經更新了你的最新程式碼，你本機端的 `main` 也需要更新，才能繼續乾淨的開發循環：
> 你會發現跟開發前的步驟一樣，所以你也可以下次開發前在做(反正要做就對了)

1. 回到你的終端機，切換到主分支：
   ```bash
   git switch main
   ```
2. 將剛剛在雲端合併好的最新進度拉回本機：
   ```bash
   git pull origin main
   ```
3. 切換回你自己的開發分支，準備進行下一個任務：
   ```bash
   git switch <your-name>-dev
   ```
4. **(重要)** 把最新的 `main` 合併到你現在的分支，確保你的地基是最新的：
   ```bash
   git merge main
   ```