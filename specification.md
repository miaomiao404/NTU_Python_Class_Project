# 專案開發規範

本文檔為此次開發專案的一些規範，包含一些命名原則等等。

> 請務必遵守以下規範，否則程式碼裡面可能會出現一些看不懂的東西，或是在引用一些檔案或變數時被命名搞到。

## 1. 檔案命名規則

檔案及資料夾名稱一律使用**英文**命名，使用全小寫，並且**不要帶有任何空格**，所有的空格請用 `_` (底線) 代替。  

例如：  
```bash
main.py  
some_api_name.md
```

檔名可以長，但是請盡可能的簡潔表達出該檔案的核心功能，並且存放在適合的資料夾中。  

---

如果需要重新命名檔案、移動檔案位置、或刪除檔案，因為涉及到git同步的問題，所以會需要使用終端機 (也就是powershell) 來操作。

重新命名檔案的語法如下：
```powershell
git mv <oldname> <newname>

#example
git mv first_api.md second_api.md
```

移動檔案位置的方式如下：
```powershell
git mv <oldlocation> <newlocation>

#example
git mv powerpoint/picture1.jpg powerpoint/picture/picture1.jpg
```
> 注意如果這裡最後檔名的地方打錯，是會順便更改檔名的喔  
> `mv` 的功能比較像你輸入一次語法 git幫你複製後幫你 `rm` 掉舊的檔案，然後 `add` 新的檔案。  
> 但還是要以 `git status` 的結果為準。

刪除檔案的方式如下：
```powershell
#刪除單一檔案
git rm <file>

#刪除整個資料夾
git rm -r <folder_name>
```

## 2. 變數命名規則

在程式中會命名一些變數，尤其是會同時被別人(或別的檔案)調用到的變數名稱請遵守以下取名方式。

使用**英文**命名，全小寫，並且不能有空格，空格使用 `_` (底線) 代替。
變數名字可以長，但是請盡可能的簡潔表達出該檔案的核心功能，盡量不要使用沒有意義的名稱。*當然如果只是迴圈用來計次的整數之類的無用變數就沒關係。*

例如：
```bash
total_ans_count
web_picture_send
disconnection_counter
temp_ans_1
temp_ans_2
```

請不要使用：
```bash
count       #一堆地方都會記數，這樣看不出來用在哪裡
aa1         #這也看不出來用在哪裡
jeffery     #他是誰
qwer        #沒有意義，只是滑一下鍵盤亂取名
ans         #一堆地方都會有ans，這樣也看不出來用在哪裡
```

以上是目前大家在取名時需要注意的地方，尤其是在多人協作的時候，這部分至關重要，感謝大家配合。