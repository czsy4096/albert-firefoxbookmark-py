# coding: utf-8

"""
Firefoxのブックマークを検索するプラグイン \n
A plugin to search Firefox bookmarks.
"""

from albert import *
from configparser import RawConfigParser
from pathlib import Path
from tempfile import mkdtemp
from shutil import copyfile, rmtree
from collections import namedtuple


md_iid = "4.0"
md_version = "0.10"
md_name = "Firefox Bookmarks"
md_description = "Search Firefox bookmarks"
md_license = "GPL-3.0"
md_url = "https://github.com/czsy4096/albert-firefoxbookmark-py"
md_authors = "@czsy4096"
# md_lib_dependencies = ["pillow", "svgutils"]

"""
昔に自分でアイコンをリサイズしていたときのコード
try:
    from PIL import Image
except ImportError:
    IMP_IMG = False
    warning("Failed to import pillow.")
else:
    IMP_IMG = True

try:
    from svgutils import transform as svgtf
except ImportError:
    IMP_SVG = False
    warning("Failed to import svgutils.")
else:
    IMP_SVG = True
"""


MAX_COUNT = 10



class FirefoxBookMarks:
    """
    Firefoxのブックマークを取得するためのクラス
    BookMarks class for the FireFox browser.
    """

    def __init__(self) -> None:
        """
        データベースを複製するための一時ディレクトリを作成しておく
        Create temp dir/file to copy the databases.
        """
        
        self.temp_dbdir = Path(mkdtemp())
        self.temp_maindb_path = self.temp_dbdir.joinpath("places.sqlite")
        self.temp_favicondb_path = self.temp_dbdir.joinpath("favicons.sqlite")
        
        return None

    def fetch_database(self, cdir, cfav) -> None:
        """
        データベースを一時ディレクトリに複製
        Fetch database to temp file.
        """
        # 現在のFirefoxはFirefox自身が起動している間にデータベースファイルが外部から読み込まれないようになっているため、
        # 元のデータベースを一時ディレクトリに複製した上でそこからブックマークを読み込みます。
        # Using FireFox63 the DB was locked for exclusive use of FireFox,
        # so we need to create a copy of it to a temp file.
        copyfile(self.get_places_db(cdir), self.temp_maindb_path)

        # favicon使用を設定している場合はfavicons.sqliteもコピーする
        # Also copy favicons.sqlite if you prefer showing favicon
        if cfav == "1":
            copyfile(self.get_favicons_db(cdir), self.temp_favicondb_path)
 
        return None

    def get_db_dir(self, cdir) -> Path:
        """
        Firefoxのデータベースの場所を探す
        Get bookmarks database path.
        """

        # 設定ファイルからprofileを読み込む
        # Read profile path from conf file
        try:
            self.prof = Path(cdir).joinpath("places.sqlite")
        except TypeError:
            self.prof = Path("/dummy/path")

        if self.prof.exists():
            profile_path = Path(cdir)

        # 設定ファイルで設定していない場合はProfile0から読み込む 
        # Fallback to Profile0 if profile_dir is not defined or not exist  
        else:
            firefox_path = Path.home().joinpath(".mozilla/firefox")

            profiles = RawConfigParser()
            profiles.read(firefox_path.joinpath("profiles.ini"))
            profile_dir = profiles["Profile0"]["Path"]

            if profiles["Profile0"]["IsRelative"] == "1":
                profile_path = firefox_path.joinpath(profile_dir)

            else:
                profile_path = Path(profile_dir)

        return profile_path

    def get_places_db(self, cdir) -> Path:
        """
        places.sqliteのフルパスを取得する
        Return full path of places.sqlite
        """
        return self.get_db_dir(cdir).joinpath("places.sqlite")
    
    def get_favicons_db(self, cdir) -> Path:
        """
        favicons.sqliteのフルパスを取得する
        Return full path of favicons.sqlite
        """
        return self.get_db_dir(cdir).joinpath("favicons.sqlite")


    def get_bookmark_list(self) -> list:
        """
        データベースファイルからブックマークのリストを取得する
        Get bookmarks list from DB files
        """
        import sqlite3
        from contextlib import closing

        with closing(sqlite3.connect(str(self.temp_maindb_path))) as self.conn:
            cur = self.conn.cursor()

            if self.temp_favicondb_path.exists():
                cur.execute(f'ATTACH DATABASE "{str(self.temp_favicondb_path)}" AS favicons')
                cur.execute('SELECT '
                            'bookmark.title, place.url, keywords.keyword, icon.data AS icondata '

                            'FROM '
                            'main.moz_bookmarks AS bookmark '

                            'INNER JOIN '
                            'main.moz_places AS place '
                            'ON (bookmark.fk = place.id) '

                            'LEFT JOIN '
                            'main.moz_keywords AS keywords '
                            'ON (place.id = keywords.place_id) '

                            'LEFT JOIN '
                            'favicons.moz_pages_w_icons AS iconpage '
                            'ON (place.url = iconpage.page_url) '

                            'LEFT JOIN '
                            'favicons.moz_icons_to_pages AS iconid '
                            'ON (iconpage.id = iconid.page_id) '

                            'LEFT JOIN '
                            'favicons.moz_icons AS icon '
                            'ON (iconid.icon_id = icon.id '

                            'AND icon.id = ('
                            'SELECT icon2.id '
                            'FROM favicons.moz_icons AS icon2 '
                            'INNER JOIN '
                            'favicons.moz_icons_to_pages AS iconid2 '
                            'ON (icon2.id = iconid2.icon_id) '
                            'WHERE iconid2.page_id = iconid.page_id '
                            'ORDER BY '
                            'icon2.width DESC '
                            'LIMIT 1'
                            ') '

                            ') '

                            'WHERE bookmark.type = 1 '

                            'AND place.url NOT LIKE "place:%" '

                            'GROUP BY bookmark.title, place.url '

                            'ORDER BY place.last_visit_date DESC, bookmark.id ASC')

            else:
                cur.execute('SELECT '
                            'bookmark.title, place.url, keywords.keyword '

                            'FROM '
                            'moz_bookmarks AS bookmark '

                            'INNER JOIN '
                            'moz_places AS place '
                            'ON (bookmark.fk = place.id) '

                            'LEFT JOIN '
                            'moz_keywords AS keywords '
                            'ON (place.id = keywords.place_id) '

                            'WHERE bookmark.type = 1 '

                            'AND place.url NOT LIKE "place:%" '
                            
                            'GROUP BY bookmark.title, place.url '
                            
                            'ORDER BY place.last_visit_date DESC, bookmark.id ASC')
            
            # ブックマークのデータをnamedtupleのlistとして取得
            # Extracted bookmark data is converted to a list of namedtuples
            namtup = namedtuple("bookmark_item", [field[0] for field in cur.description])
            results = [namtup._make(row) for row in cur]
        
        return results

    
    def clear_temp_files(self) -> None:
        """
        一時ディレクトリにコピーしたデータベースを消去する
        Delete temp dir and DBs copied in it
        """
        rmtree(self.temp_dbdir)

        return None


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self)
        PluginInstance.__init__(self)
       
        cfile = str(Path(__file__).resolve().parent) + "/firefoxbookmark.conf"
        config = RawConfigParser()
        config.read(cfile)

        try:
            self.cdir = config["General"]["profile_dir"]
        except KeyError:
            self.cdir = None
            info("FirefoxBookmarks: User profile not found. Fallback = Profile 0.")

        try:
            self.cfav = config["General"]["use_favicon"]
        except KeyError:
            self.cfav = "1"
            info("FirefoxBookmarks: Config use_favicon not defined. Fallback = True.")

        try:
            self.ckey = config["General"]["use_keyword"]
        except KeyError:
            self.ckey = "0"
            info("FirefoxBookmarks: Config use_keyword not defined. Fallback = False.")


        # ブックマークの取得
        # Get bookmarks
        firefoxbookmarks = FirefoxBookMarks()
        firefoxbookmarks.fetch_database(self.cdir, self.cfav)
        self.bookmarks_list = firefoxbookmarks.get_bookmark_list()
        info(f"Firefox Bookmarks: {str(len(self.bookmarks_list))} items indexed.")
        firefoxbookmarks.clear_temp_files()

        # データベースから読み込んだfaviconを一時ファイルに書き出し
        # Write extracted favicons to temp files
        self.favicon_dir = mkdtemp()

        if self.cfav == "1":
            for item_num, bookmark_item in enumerate(self.bookmarks_list):
                if bookmark_item.icondata:
                    favicon_path = self.favicon_dir + "/favicon_" + str(item_num)
                    with open(favicon_path, "wb") as ico:
                        ico.write(bookmark_item.icondata)

#                    self.resize_ico(favicon_path)

    """    
    def resize_ico(self, favicon_path):
        
        faviconを256x256にリサイズ
        Resize favicons to 256x256
        
        try:
            with open(favicon_path, "rb") as fil:
                head = fil.read(300)

                # PNG
                if head.startswith(b"\x89PNG"):
                    if IMP_IMG == True:
                        with Image.open(favicon_path) as img:
                            if img.width == 256:
                                return
                    
                            resized_img = img.resize((256, 256))
                            resized_img.save(favicon_path, 'PNG', optimize=True)

                    else:
                        pass

                # SVG
                elif 'http://www.w3.org/2000/svg' in str(head):
                    if IMP_SVG == True:
                        img = svgtf.fromfile(favicon_path)

                        if img.width == "256":
                            return

                        img.set_size(("256", "256"))
                        img.save(favicon_path)

                    else:
                        pass

                else:
                    pass
                    
        except Exception:
            pass
    """                

    def __del__(self):
        """
        終了時、書き出したfaviconの一時ファイルを削除
        Delete favicons copied to temp files when deactivating the plugin
        """
        rmtree(self.favicon_dir)
    
    def defaultTrigger(self):
        return 'f '

    def handleTriggerQuery(self, query):
        if not query.isValid:
            return
        
        results_list = []
        result_count = 0
        query_words = query.string.lower().strip().split()


        for item_num, bookmark_item in enumerate(self.bookmarks_list):
            if all((
                    word in str(bookmark_item.title).lower()
                    or (word in str(bookmark_item.url).lower())
                    or ((self.ckey == "1") and (word in str(bookmark_item.keyword).lower()))
                    )
                for word in query_words
                ):

                item = StandardItem()
                item.id = "FirefoxBookmark_" + str(item_num)
                item.text = str(bookmark_item.title)
                item.subtext = str(bookmark_item.url)
                item.input_action_text = str(bookmark_item.title)

                ifile = self.favicon_dir + "/favicon_" + str(item_num)
                ipath = Path(ifile)
                if ipath.is_file():
                    item.icon_factory = lambda p = ipath: makeImageIcon(p)
                else:
                    item.icon_factory = lambda: makeThemeIcon("firefox")

                item.actions = [Action(
                    "open", "Open", lambda u = bookmark_item.url: openUrl(u)
                )]

                results_list.append(item)
                result_count += 1
                if result_count >= MAX_COUNT:
                    break

        query.add(results_list)

