animad-popular-fetcher
====
抓取動畫瘋每日觀看數統計

## 需求
Python >= 3.9

## 初始化
1. `pip install -r requirements.txt`
2. 將 `config.example.py` 複製成 `config.py` 並按需求修改
3. `python initial.py`
4. 將 `fetchList.example.txt` 複製成 `fetchList.txt` 並按需求修改

## 匯入數據
```python import.py /path/to/import.csv```

接受的數據樣本：
```csv
113563,38824,2024/06/27,10353
113563,38824,2024/06/28,42244
113566,38827,2024/06/27,0
113566,38827,2024/06/28,38520
113566,38828,2024/06/27,0
113566,38828,2024/06/28,21738
113566,38829,2024/06/27,0
113566,38829,2024/06/28,15203
```
欄位：animeSn,videoSn,date,popular

## 匯出數據
```python export.py [--restrict-in-fetch-list|--restrict-in-fetch-list-path RESTRICT_IN_FETCH_LIST_PATH] /path/to/export.csv```

## 注意事項
本項目僅因研究各動畫熱門程度而由第三方建立，不保證可靠性，若過度使用等可能違反巴哈姆特動畫瘋之服務條款之事情時導致您的IP地址被動畫瘋封鎖等事情一蓋不負責任。
