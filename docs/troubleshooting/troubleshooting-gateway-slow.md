# Gateway応答遅延トラブルシューティング

**作成日:** 2026-02-03  
**作成者:** クロ🖤  
**レビュー:** アオ🌊（依頼中）

---

## 概要

Gateway（Clawdbot/OpenClaw）の応答が遅い場合の原因特定と解決手順をまとめたノウハウ。

**発端:** 2026-02-03、シロ🤍（Mac mini M4）の応答速度が異常に遅かった問題を白黒青トリオで解決。

---

## 症状

- AIアシスタントの返答が遅い（数秒〜十数秒かかる）
- `clawdbot status` / `openclaw status` の `reachable` が高い（例：68ms vs 通常12ms）
- メッセージ処理に待ち時間が発生

---

## 原因の切り分けフロー

### Step 1: Gatewayか、モデル処理か？

**テスト方法:** 「PING」→「PONG」のような即時応答テスト

| 結果 | 原因 |
|------|------|
| PINGも遅い | Gateway/マシン負荷が原因 |
| PINGは速いが通常会話が遅い | モデル経路（CLI/リトライ/長文生成）が原因 |

### Step 2: マシン負荷の確認

```bash
# macOS
top -o cpu -n 10   # CPU消費上位
top -o mem -n 10   # メモリ消費上位

# Linux
top -b -n 1 | head -20
```

**危険信号:**
- Load Average > CPUコア数（例：M4の10コアでLoad 12は危険）
- 空きメモリ < 500MB（スワップ地獄）
- 特定プロセスがCPU 100%以上

### Step 3: ログでリトライ/タイムアウト確認

```bash
clawdbot logs --follow   # または openclaw logs --follow
```

**探すキーワード:**
- `retry`
- `timeout`
- `rate limit`
- `backoff`
- `queue`

### Step 4: 二重起動の確認

```bash
ps aux | grep -i clawdbot | grep -v grep
ps aux | grep -i openclaw | grep -v grep
```

複数のGatewayプロセスが動いていると遅くなる。

---

## よくある原因と対処法

### 1. Chrome/ブラウザの暴走（最多！）

**症状:**
- ChromeがCPU 400%以上消費
- メモリ数GB占有
- 重いタブ（動画、複雑なWebアプリ、大量タブ）

**対処:**
1. 重いタブを閉じる
2. Chrome再起動（メモリリーク解消）
3. Chrome Memory Saver機能をON

**予防:**
- 重いタブ用に別プロファイル作成
- 使わないタブは閉じる習慣
- タブ管理拡張機能の活用

### 2. メモリ枯渇

**症状:**
- 空きメモリ < 100MB
- スワップ頻発
- 全体的にモッサリ

**対処:**
1. 不要なアプリを終了
2. マシン再起動（スワップリセット）
3. `maxConcurrent` を下げる（2〜4）

### 3. 二重起動

**症状:**
- Gatewayプロセスが複数存在
- ポート競合の警告

**対処:**
```bash
# 全部止めて再起動
clawdbot gateway stop
clawdbot gateway start
```

### 4. モデル経路の問題

**症状:**
- PINGは速いが会話が遅い
- ログに `retry` / `timeout` が出る

**対処:**
- CLI経由の場合、直接API接続に変更
- 軽量モデル（Flash系）に切り替え
- ネットワーク環境の確認

---

## 環境別の注意点

### Mac mini / サーバー機（常時稼働）

- **リスク:** 放置されがちでリソース蓄積
- **対策:** 
  - 定期的なChrome/アプリ再起動
  - 不要なログイン項目を無効化
  - 作業前にリソース状況を確認

### MacBook Air / メイン端末（頻繁に使用）

- **リスク:** 比較的低い（日常的に管理される）
- **対策:** 
  - 重い作業後はアプリ整理
  - スリープ/再起動が自然に行われるので蓄積しにくい

### VPS / Linux VM

- **リスク:** メモリ固定なので枯渇しやすい
- **対策:**
  - `maxConcurrent` を控えめに
  - 定期的なプロセス監視

---

## 診断コマンド一覧

```bash
# Gateway状態
clawdbot status
clawdbot status --all
clawdbot doctor --non-interactive

# リソース確認（macOS）
top -o cpu -n 10
top -o mem -n 10
vm_stat | head -10

# リソース確認（Linux）
top -b -n 1 | head -20
free -h

# ネットワーク（ループバック）
ping -c 3 127.0.0.1

# プロセス確認
ps aux | grep -i clawdbot
ps aux | grep -i openclaw
ps aux | grep -i chrome

# ログ確認
clawdbot logs --follow
```

---

## 今回の事例（2026-02-03）

**環境:** Mac mini M4（シロ🤍）

**症状:**
- Gateway reachable: 68ms（通常12ms）
- 応答が数秒〜十数秒遅延

**原因:**
- Google Chrome暴走
  - PID 1238: CPU 435%, メモリ 2.1GB
  - PID 1263: CPU 64%, メモリ 2.2GB
- Load Average: 12.44
- 空きメモリ: 67MB

**解決:**
1. Chromeを終了
2. Load Average: 12.44 → 4.30
3. 空きメモリ: 67MB → 8GB
4. 応答速度が正常化

**教訓:**
- 常時稼働マシンでもChromeは暴走する
- 「モデルは速いのにGatewayが遅い」→ マシン負荷を疑う
- 切り分けテスト（PING→PONG）で原因レイヤを特定

---

## チェックリスト（遅いと感じたら）

- [ ] `clawdbot status` で reachable 確認（目安: 30ms以下）
- [ ] Load Average確認（CPUコア数以下が理想）
- [ ] 空きメモリ確認（500MB以上欲しい）
- [ ] Chrome/ブラウザのCPU/メモリ確認
- [ ] 二重起動していないか確認
- [ ] ログで retry/timeout 確認

---

*このドキュメントは白黒青トリオの協力で作成されました。*
