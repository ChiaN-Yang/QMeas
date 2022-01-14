# QMeas
<a href="#"><img src="https://img.shields.io/badge/python-v3.6+-blue.svg?logo=python&style=for-the-badge" /></a>

A Data-Acquisition Program for Instrument Control and Measurement Automation

---

## 摘要
這是一套儀器控制和自動化測量軟體，所要控制的儀器包括稀釋冷凍機 (Dilution refrigerator)、磁場機、電源電壓量測設備等。軟體的主要功能為控制儀器輸出、預先安排儀器未來將輸出或讀取的物理量、將儀器的讀值進行實時作圖(real-time plot)。

## 程式目標
此程式需要具備以下功能：
1.	自動偵測現有可用的I/O匯流排與掃描使用者新增的驅動程式。
2.	讓使用者選擇要使用的儀器種類、I/O匯流排、儀器名稱，以連接儀器，若連結成功就顯示在螢幕列表上，若連結失敗需回報錯誤訊息。
3.	讓使用者移除已連結的儀器。
4.	有一個控制面板讓使用者決定實驗步驟。
5.	畫出實時作圖。
6.	將結果輸出成圖片以及csv檔，檔案名稱可由使用者自訂。

## 程式架構
程式分為三個部分，分別是Connection、Measurement、Graph。Connection負責掃描可用的I/O匯流排並連接儀器至主程式；Measurement負責編排實驗流程，實驗過程中會指揮Connection去操作儀器讀值(read value)與寫值(set value)，並發送訊號更新Graph更新實時作圖與儲存量測數據；Graph會接收Measurement發出來的訊號，並更新圖表。
![program structure](https://i.imgur.com/ueL3XPM.png)

## 結果與展示
詳細過程可以參考影片https://youtu.be/omZaGmend-w (總長一分鐘)，以下將由圖片分段說明。
1. Connection

    依下圖所示，介面上方(Available VISA Address與instrument type區塊)：程式會自動偵測可用的I/O匯流排與驅動程式，使用者依序點儀器的位址、種類，並輸入儀器名字，按Connect即可連接儀器至程式。
    ![connection interface](https://i.imgur.com/QVYu62a.png)
    
2. Measurement

    在左上角點選已連接的儀器，在左下角會跑出對應該儀器可操作的方法。依下圖範例，如果要儀器輸出電壓，按Control會新增到右上角儀器輸出區；如果要讀取電壓，按Read則會新增到右下角儀器測量區。值得注意的是，Control部分是用add child與add sibling的方式新增儀器，利用以上兩種方法就能建立tree結構，從而編排實驗過程。
    ![measurement interface](https://i.imgur.com/kZNb76J.png)

3. Graph

    觀察下圖可以發現，因為在Measurement部分設定兩個Read，圖表這邊會顯示兩條線，會以一對多的方式作圖。這部分是Labber無法做到，但卻是物理研究生所需要的。
    ![graph interface](https://i.imgur.com/IsX7jMN.png)

## 程式設計
1. Connection

    這部分是儀器連接介面，我利用PyQt5設計前端。在偵測驅動程式的部分，會讓所有驅動程式繼承驅動程式介面，確保所有儀器都有四項功能，包括開機、關機、讀值、寫值。

2. Measurement

    在實驗排程的部分，我使用資料結構的tree。目前是利用list實現，在list第一個放child，第二個以後全部放sibling，藉由這樣的結構，我就可以讓使用者排出任何想要的實驗步驟。值得注意的是，我在排實驗過程時，是利用儀器目前輸出的值當起點，如此能保護樣品不會因為突然的脈衝(pulse)而損壞樣品。

3. Graph

    畫圖的部分，我使用執行緒(Thread)平行運算。如此可讓使用者在執行超長實驗步驟時，作圖也不會因此卡頓。

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
- QDarkStyle

In vscode, it can be installed with pip

    python -m pip install -r requirements.txt

## Hint
you can transfer .ui to .py by this command

    pyuic5 -x main_window.ui -o main_window.py