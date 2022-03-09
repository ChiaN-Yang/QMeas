# QMeas
<a href="#"><img src="https://img.shields.io/badge/python-v3.9+-blue.svg?logo=python&style=for-the-badge" /></a>

## 摘要
這是一套儀器控制和自動化測量軟體，所要控制的儀器包括稀釋冷凍機 (Dilution refrigerator – a system that operates a hundredth of a degree above absolute zero)、超導磁鐵機(superconducting magnet)、鎖相放大器(Lock-In Amplifier)、Source Measure Unit設備。軟體的主要功能為控制儀器輸出、預先安排儀器未來將輸出或讀取的物理量、將儀器的讀值進行實時作圖(real-time plot)。

## 程式特色
- 任意的新增儀器：我們打造可擴充式模組，新增新儀器不需更改程式碼
- 任意的執行實驗：我們提供tree weidget安排實驗，可以執行任何迴圈能達成的排程
- 一對多動態作圖：與市面上的作圖方式不同，一對多動態作圖能讓您在實驗過程就能驗證實驗結果是否正確
- 快速讀取過去實驗：執行實驗當下將儲存您的實驗排程，此檔案可以直接匯入
- 自動切換檔位：使用者可決定是否讓程式自動運算讀值並切換到適合的檔位
- 意外存檔：要是使用者意外關閉程式，程式會保留資料暫存檔，不需再重新量測
- 由物理系博士協助撰寫驅動程式，保證儀器與樣品安全
- 未來將推出DataViewer，讓使用者做各種數值分析

## 程式目標
此程式需要具備以下功能：
1. 自動偵測現有可用的I/O匯流排與掃描使用者新增的驅動程式
2. 讓使用者選擇要使用的儀器種類、I/O匯流排、儀器名稱，以連接儀器，若連結成功就顯示在螢幕列表上，若連結失敗需回報錯誤訊息
3. 讓使用者移除已連結的儀器
4. 有一個控制面板讓使用者決定實驗步驟
5. 讓使用者決定存檔位置
6. 畫出實時作圖
7. 讓使用者決定畫面只顯示特定資料
8. 隨時暫停或停止實驗
9. 將結果輸出成圖片以及csv檔，檔案名稱可由使用者自訂

## 程式架構
程式分為三個部分，分別是Connection、Measurement、Graph。Connection負責掃描可用的I/O匯流排並連接儀器至主程式；Measurement負責編排實驗流程，實驗過程中會指揮Connection去操作儀器讀值(read value)與寫值(set value)，並發送訊號更新Graph更新實時作圖與儲存量測數據；Graph會接收Measurement發出來的訊號，並更新圖表。

![program structure](https://i.imgur.com/ueL3XPM.png)

## 結果與展示
詳細過程可以參考[影片](https://youtu.be/omZaGmend-w)，以下將由圖片分段說明。
1. Connection

    依下圖所示，介面上方(Available VISA Address與instrument type區塊)：程式會自動偵測可用的I/O匯流排與驅動程式，使用者依序點儀器的位址、種類，並輸入儀器名字，按Connect即可連接儀器至程式。

    ![connection interface](https://i.imgur.com/7VUJIYb.png)
    
2. Measurement

    在左上角點選已連接的儀器，在左下角會跑出對應該儀器可操作的方法。依下圖範例，如果要儀器輸出電壓，按Control會新增到右上角儀器輸出區；如果要讀取電壓，按Read則會新增到右下角儀器測量區。值得注意的是，Control部分是用add child與add sibling的方式新增儀器，利用以上兩種方法就能建立tree結構，從而編排實驗過程。

    ![measurement interface](https://i.imgur.com/AjdLssa.png)

3. Graph

    圖表這邊會以一對多的方式作圖。

    ![graph interface](https://i.imgur.com/5yTZuUy.png)

## 程式設計
1. Connection

    這部分是儀器連接介面，利用PyQt5設計前端。在偵測驅動程式的部分，會讓所有驅動程式繼承驅動程式介面，確保所有儀器都有四項功能，包括開機、關機、讀值、寫值。

2. Measurement

    在實驗排程的部分，使用資料結構的tree。目前是利用list實現，在list第一個放child，第二個以後全部放sibling，藉由這樣的結構，就可以讓使用者排出任何想要的實驗步驟。值得注意的是，在排實驗過程時，是利用儀器目前輸出的值當起點，如此能保護樣品不會因為突然的脈衝(pulse)而損壞樣品。

3. Graph

    畫圖的部分，使用執行緒(Thread)平行運算。如此可讓使用者在執行超長實驗步驟時，作圖也不會因此卡頓。

## 檔案說明
```
main.py : 程式由此進入

data ： 資料暫存區

drivers : 存放儀器驅動程式

modpack : 存放修改過的模組

qtdesign : 備份QtDesign形成的ui檔

ui : 設定主程式的前端介面

utils : 執行主程式所需的模組
```

## Installation
Before run this program, you need to install package below:
- PyQt5
- PyQtGraph
- PyVISA
- Pymeasure
- Numpy
- Labdrivers
- NIDAQmx
- QCoDes
- QCoDes_contrib_drivers
- QDarkStyle

In vscode, it can be installed with pip:

    python -m pip install -r requirements.txt

## Hint
transfer .ui to .py:

    pyuic5 -x "./qtdesign/main_window_qt.ui" -o "./ui/main_window_qt.py"