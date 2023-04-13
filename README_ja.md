# Albert用Firefoxブックマークプラグイン
## これは何?
Linux用キーボードランチャーである [Albert](https://albertlauncher.github.io/) でFirefoxのブックマークを検索するためのプラグインです。Albertの大規模アップデートにより公式の(C++)プラグインが使用できなくなり、メンテナーもいないため、pythonプラグインとしてDIYしたものです。

## 必要なもの
FirefoxとAlbertとpython (>= 3.4) だけで動作するはずです。

## 使用方法
- [Release](https://github.com/czsy4096/albert-firefoxbookmark-py/releases) または直接リポジトリから必要ファイル群を取得
- firefox_bookmark ディレクトリとその中身をpythonプラグイン用ディレクトリにコピー  
カレントユーザーのみにインストールするなら `~/.local/share/albert/python/plugins` に、全ユーザーにインストールするなら `/usr/share/albert/python/plugins` にコピーすれば良いと思います。
- Albertを起動、またはすでに起動している場合は再起動 (`Restart Albert`)
- Albertの設定(`Settings`)のPluginsタブでFirefox Bookmarksを探してアクティブ化
- 現状(Albert v0.20)ではpythonプラグインには必ず"トリガー"が必要です。  
設定のTriggersタブでトリガーを確認してください。デフォルトでは"f " (fの後に半角スペース)です。トリガーに続いて検索語句を入力するとマッチするブックマークが表示されます。

## プラグインの設定
本プラグインはfirefox_bookmarkディレクトリ中の firefoxbookmark.conf ファイルを編集することで動作をカスタマイズすることができます。以下の設定項目があります。
- `profile_dir`  
このプラグインはデフォルトでは通常版Firefoxの"Profile 0"を探してブックマークを読み込みます。それ以外のプロファイルを使用している場合はこの項目でプロファイルディレクトリのフルパスを指定してください。
- `use_favicon`  
検索結果にfaviconを表示するかどうかを設定できます。1にするとfaviconを表示します。それ以外の値だと表示せずに変わりにFirefoxのアイコンを表示します。
- `use_keyword`  
本プラグインは通常ブックマークタイトルまたはURLが検索語句とマッチするものを抽出しますが、この項目を1にするとさらに"キーワード"を検索することができるようになります。

## 留意事項
- ブックマークのタグを検索することはできません。今の所できるようにする予定もありません。
- 本プラグインはアクティブになった時点でブックマークのインデックスを作成します。その後にブックマークを編集しても自動では反映されませんので、`Restart Albert`するなどして再読込してください。
- ブックマークは"最後に訪問した日時"を基準にソートされますが、Firefoxの履歴を消去するとその情報も消えてしまいます。また、リアルタイムでの更新は行いませんので、必要に応じて`Restart Albert`してください。
- あくまで個人的な使用目的で作成しました。公式のpythonプラグイン用リポジトリに加えてもらう予定はありません。どなたかC++プラグインを復活させてくれる方は・・・

## Special thanks
本プラグインはkrunner用のプラグイン [zer0-x/krunner-firefox-bookmarks](https://github.com/zer0-x/krunner-firefox-bookmarks) を基にして開発しました。
