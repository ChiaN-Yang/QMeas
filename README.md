# CryoMeas
A Data-Acquisition Program

## 需求

### 連接儀器
1. Instrument Registration
    1. 指定visa address
    2. 選擇儀器型號(type)
    3. 顯示儀器資訊
2. delete instrument


### 測量排程
1. Task Specification
    - 選取儀器（from registered intrument list）
    - 排入隊列
        1. Control
            * define target value
            * define speed
        2. Read
            * define magnification
            * def unit
    - 顯示任務資訊
2. Task scheduling
    1. Queues: Control/Measure
    2. create/delete/modify/reorder
3. Plot time rate
4. filename to store result values
5. RUN/STOP

### 作圖
1. real-time plotting (via PyQtGraph)
2. pause tasks in control queue
3. auto range
4. display cursor
5. quit sweep?
6. display current control & measure values

### 存檔
1. 將資料寫進.txt/csv
2. 作圖同時存檔


## 架構
### Model
1. 儀器物件

```python
class Intrument(object):
    pass

class Intrument(Deriver):
    def open():
        return NotImplemented
    
class driver1(IntrumentInterface, Keithley):
    def open():
        pass

class driver2(IntrumentInterface, Ips120):
    def open():
        pass


ins1 = driver1()
ins2 = driver2()


ins.open()
ins.setValue()
ins.close()
```

2. Task
    - 儀器
    - control/read parameter
    - (enum union)
- TaskQueue
    - create/delete/modify/reorder
- TaskCompose(靜態/動態)

### View
1. page

### Controller(main)
1. 連接按鈕
2. import driver並生成物件
