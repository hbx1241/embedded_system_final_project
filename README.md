# 嵌入式系統實驗期末專題-居家生活助理
<p class="text-center">
    GitHub Repo: 
    <a href="https://github.com/hbx1241/embedded_system_final_project">https://github.com/hbx1241/embedded_system_final_project</a>
</p>
<p class="text-right">
B09901196 黃秉璿<br>
B08901209 林鈺翔<br>
B08901215 蕭淇元<br>
</p>

## 動機
鑑於高齡者獨居的比例增加，年輕人難以負擔扶養照顧的工作，所衍生的安全問題將難以只靠不足的社工來解決。因此我們決定試著利用嵌入式系統所學的技術，來實現智慧居家生活助理的概念。我們希望這個系統可以提供高齡獨居者便利的生活，同時也隨時注意是否發生意外，如此一來不僅可以節省社工人手不足的問題，獨居高齡者的生活安全也獲得了一份保障。

## 內容摘要
關於我們這次的主題「居家生活助理」，我們從安全與便利兩大方向切入，實現了以下實用的功能，包括：
* 跌倒偵測：
隨時注意使用者的動作狀態，在使用者跌倒時發出通知至親友的通訊裝置，即時為使用者所發生的危險提供協助。主要使用了HMM-based的方法來對加速度計所量到的數值進行辨識，並透過ifttt發出警告通知。
* 手勢辨識：
簡單定義了開啟、關閉照明設備的手勢，為行動不便的使用者多一份便利。實現的方法為偵測手持stm32開發板的不同方向的加速度大小，再將手勢辨識的結果透過mqtt傳送，以此來對照明設備進行操作。
* 室內定位：
定位在空間中使用者的座標位置，在使用者發生危險時，將位置一併傳送給親友，讓前來援助者可以更快更準確的提供協助。根據測量目標物發送訊號的rssi值換算成距離，再將多個基地台算出的距離以三角投影的方式計算出在空間中的座標位置。
## 技術細節
### 1. 跌倒偵測
考慮到使用者在佩戴裝置時會有不同角度方向，啓動裝置後會需要1秒的時間保持站立做校正，並以該段時間內的加速度平均做爲垂直分量$a_v$，對於之後收集到的加速度$a_t(x,y,z)$，可以投影爲垂直分量$a_{vt} = a_v \cdot a_t / |a_v|^2 \cdot a_v$ 與水平分量$a_{ht} = a_t - a_{vt}$， 取norm後得到$[v\ h] = [|a_{vt}|\ |a_{ht}|]$，並利用最後的8筆$v\ h$（取樣率20Hz)以及Hidden Markov Model(HMM)，偵測使用者當下的狀態，當跌倒時，程式會發送http request透過ifttt webhook以line通知其他人使用者跌倒以及跌倒的位置。

在HMM的部分，根據跌倒過程（站立、失去平衡、撞擊、倒地）將hidden states設爲4，並把使用者的行爲分成日常活動(ADL)與跌倒，其中日常活動包含站立、坐下、起立和走路，跌倒則是只有向前跌倒，根據項目分別收集加速度數據，之後透過python hmmlearn訓練出模型（Baum-Welch algorithm)；在判斷時，8筆$v\ h$會被當作observation sequence，每個model分別計算觀察到這個sequence的可能性，若最高者是跌倒動作則判斷使用者跌倒，反之則爲日常活動。
### 2. 手勢辨識＋開關燈
我們使用stm32作為穿戴式裝置，並設計了兩個手勢：垂直揮手以開關一號燈、水平揮手以開關二號燈。
#### 辨識流程
stm32將加速度data傳給server，server監測水平與垂直的加速度分量，若其中一項超過我們設的threshold則判斷為「正在做手勢」，並傳送mqtt message以開/關對應的燈。另外，在揮手的過程中會有很多時刻的加速度值 > threshold，為了避免揮一次手重複開關燈，我們利用簡單的finite state machine，根據現在的加速度以及「前一刻是否在做手勢」來判斷現在是否在做手勢，達到揮一次手只開/關一次燈的效果。
### 3. 室內定位
#### 作法
室內定位的作法參考自學長所做過的題目[夢想家園](https://github.com/roger-tseng/Embed-Lab-Final)，使用了1塊stm32當作定位的目標，以及4塊樹莓派作為定位用的anchor放置於空間中的4個角落，其中的1塊樹莓派同時兼當收發定位資訊和計算座標的server。當開始定位時，stm32會在空間中發布一個BLE service，當作anchor用的樹莓派會不停掃描空間的BLE service，找到目標所發送的service後，會去讀取目標的rssi值，利用這個值可以計算出兩者之間的距離。算出距離以後，透過mqtt傳給server，得到4段距離以後的server就可以用三角定位的方法算出座標，最後再把座標用mqtt傳給另一個負責偵測跌倒及手勢辨識的server來做發送ifttt訊息的處理。
#### 架構圖
![](https://i.imgur.com/NmNptG9.png)
#### 原理
有paper提到，觀察了BLE訊號的rssi值的大小跟距離的曲線以後(如下圖Fig.3所示)，這對關係可以被model成以下的對數函數：
$\overline{PL}(dB) = \overline{PL}(d_0) - 10 * \eta * log_{10}(d_i / d_0)(i = 1,2,...,n)$
其中$d_0$、$\overline{PL}(d_0)$、$\eta$是需要根據環境來調整的參數，因此anchor在初始化的時候需要先測量3組rssi值與距離的pair。
![](https://i.imgur.com/1W5TzP0.png)
#### 問題


## 整體架構
```sequence
title : Data Flow
participant host 
participant ifttt
participant stm32
participant location server as server
participant rpi(anchors) as rpi

stm32->host: connect
rpi->server: distances(mqtt)
server->host: location(mqtt)
host->rpi: control light(mqtt)
host->ifttt: fall detected(internet)
```
main.py 偵測跌倒
```sequence
title : main.py multithreads
participant main thread as main
participant getdata as t1
participant t2
participant notify as t3
participant stm32
main->main: set up mqtt
main->main: load HMM models
stm32->t1: wifi connect
t1->t2: start
t1->t2: send data(queue)
t2->t2: fall detected
t2->t3: send warning


```
## Demo
{%youtube refNBLtEpw8 %}
## 參考資料
- Hidden Markov Model-Based Fall Detection With Motion Sensor Orientation Calibration：https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8171718
- 夢想家園：https://github.com/roger-tseng/Embed-Lab-Final
- 手勢辨識：https://www.academia.edu/29191480/使用加速度計和陀螺儀之跌倒偵測系統_A_Fall_Detection_System_using_Accelerometer_and_Gyroscope

