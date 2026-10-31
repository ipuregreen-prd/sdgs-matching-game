# 本機正式資料庫連線

此目錄的本機 `.env` 指向中央正式環境設定檔，啟動時從該檔讀取 URL 與 Token。

`TURSO_TOKEN_FILE=../deploy/ipuregreen-prd.env` 的相對路徑以本專案目錄為基準，不受終端機所在目錄影響。程式從該檔案讀取對應的 `sdgs-matching-game_TURSO_AUTH_TOKEN`，以及同前綴的 `_TURSO_AUTH_URL`；不在專案 `.env` 複製 URL 或 Token。

已明確提供於程序環境的資料庫設定優先於本機 `.env`；執行隔離測試時應明確提供 SQLite 路徑及空白 Turso 設定。中央檔案缺少對應的 URL 或 Token 時會拒絕載入。

若要透過環境變數直接指定 Turso，必須同時提供網址和 Token。設定 `VERCEL` 的部署使用雲端環境變數，不讀取本機 Token 檔。

`.env` 已由 Git 忽略。中央 Token 檔位於各 Git 儲存庫之外，不應加入版本控制或部署套件。本次僅修改本機，未更新 GitHub 或 Vercel。

已啟動的服務須重新啟動才會載入新設定；重啟後的操作會使用正式資料庫。
