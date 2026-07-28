# BeeInventor Backend — Coding & System Design Exercises

## 怎麼跑

- **語言**：Python 3.13
- **套件管理**：[uv](https://github.com/astral-sh/uv)
- **安裝相依套件（含測試用的 pytest）**：
  ```bash
  uv sync
  ```
- **跑 demo（直接看 logging 輸出）**：
  ```bash
  uv run python exercise1-in-memory-dictionary/word_dictionary.py
  ```
- **跑測試**：
  ```bash
  uv run pytest exercise1-in-memory-dictionary/ -v
  ```

---

## Exercise 1 — In-Memory Dictionary

一個放在記憶體裡的字典，支援三種搜尋：完全比對、前綴、萬用字元。

### 用法

```python
wd = WordDictionary()
wd.setup(["cat", "car", "bar"])   # 載入字典，再呼叫一次會整個換掉
wd.contains("cat")    # True   完全一樣才算命中
wd.contains("ca")     # False  "ca" 只是前綴，不是完整的字
wd.startswith("ca")   # True   有字是以 "ca" 開頭
wd.search("c?t")      # True   ? 代表一個字母、* 代表零或多個字母
```

### 為什麼用 Trie

我沒有一開始就決定用哪種結構，而是先看三個操作各自需要什麼：

- **完全比對（contains）**：走到字尾，確認這裡是一個完整的字。
- **前綴（startswith）**：要能一個字母一個字母往下找。如果用 `set`，得把整個字典掃過一遍才知道，很慢。
- **萬用字元（search）**：要能一邊往下走、一邊分岔嘗試不同可能。

這三件事都需要「照著字母一層層往下走」，而這正是 trie 在做的事。所以我用**一棵 trie 同時撐起三種搜尋**，它還順便幫我做掉了「重複的字不算數」和「整批替換」。

**代價**：trie 比 `set` 多用一點記憶體、程式也複雜一些。但 `set` 根本做不到前綴和萬用字元搜尋，所以這個代價是值得的。（如果題目只有完全比對，我會直接用 `set`，比較單純——是前綴和萬用字元這兩題才需要 trie。）

### 時間 / 空間複雜度

（n = 字數，L = 平均字長，N = trie 節點數，M = pattern 長度）

| 操作 | 時間 | 空間 |
|---|---|---|
| `setup` | O(所有字的總長度) = O(n·L) | O(N) |
| `contains` | O(m) | O(1) |
| `startswith` | O(p) | O(1) |
| `search` | 最差 O(N·M)（用 (節點, 位置) 做記憶化後）；有很多個 `*` 又沒記憶化時可能會退化 | O(N) 樹身 + O(M) 遞迴深度 |

### 假設與做法

- 題目說「單字都是小寫英文字母 a–z」，所以正常情況下輸入都是乾淨的。我照這個前提實作，另外也對不符合規則的輸入（大寫、全形、數字、空白等）多做了一層基本防護，讓程式遇到非預期輸入時行為明確、不會直接壞掉。
- **搜尋會區分大小寫**：我認為「完全比對」就是要一模一樣才算命中，不會偷偷把大寫轉成小寫。所以字典存 `cat`、去查 `Cat` 會回 False；字也是原樣存進去。
- **錯誤處理分兩種**：
  - **型別不對**（不是 list、不是字串）→ 直接丟 `TypeError`，因為這通常是呼叫的人用錯了。
  - **內容不合**（不是英文字母，例如全形、數字、空白）→ 不當成錯誤：`setup` 會跳過那個字並記一筆 warning，查詢則回 `False`。字典只收 A–Z、a–z。
- **重複**的字會被 trie 自動去掉。**再呼叫一次 `setup`** 會把舊內容整個換掉——做法是先建一棵新的樹，全部塞完沒問題才換過去，所以萬一中途出錯，舊字典不會被弄壞。
- **萬用字元 `search`**：`?` 是剛好一個字母，`*` 是零或多個字母，整個字要完全對上；可以有好幾個萬用字元；字典非空時 `search("*")` 回 True。pattern 只接受字母和 `?`、`*`，出現其他字元就當作不合法、回 False。
- **用 logging 取代 print** 來呈現結果：每一行都看得到是哪個函式、輸入什麼、輸出什麼。`basicConfig` 只寫在 `if __name__ == "__main__"` 裡，所以別的程式 `import` 這個模組時不會被它干擾。

### 測試

用 `pytest`，總共 47 個案例：

- **Part A 完全比對**：命中 / 前綴不算命中 / 不存在、`car` 與 `card` 這種前綴重疊、區分大小寫、擋掉全形/空白/數字/空字串、重複去除、再次 setup 會取代、型別錯會丟 TypeError、setup 中途出錯不會弄壞舊資料、跳過的字有記 warning。
- **Part B 前綴**：前綴存在/不存在、完整的字本身也算前綴、區分大小寫、擋掉全形前綴、空前綴的邊界、非字串會丟錯。
- **Part C 萬用字元**：題目的五個例子（`c?t`、`*at`、`ca*`、`cr*`、`*`）、`?` 對長度敏感、多個萬用字元、`*` 可以吃 0 個字母、不合法的 pattern、非字串會丟錯。

跑法：

```bash
uv run pytest exercise1-in-memory-dictionary/ -v
```
