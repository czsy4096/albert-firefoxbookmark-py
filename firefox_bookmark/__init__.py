# coding: utf-8

"""
Firefoxのブックマークを検索するプラグイン
"""

from albert import *
from configparser import RawConfigParser
from pathlib import Path
from tempfile import mkdtemp
from shutil import copyfile, rmtree
from collections import namedtuple


md_iid = "0.5"
md_version = "0.1"
md_name = "Firefox Bookmarks"
md_description = "Search Firefox bookmarks"
md_license = "GPL-3.0"
md_url = "https://github.com/czsy4096/albert-firefoxbookmark-py"
md_maintainers = "@czsy4096"

MAX_COUNT = 10



class FirefoxBookMarks:
    """BookMarks class for the FireFox browser."""

    def __init__(self) -> None:
        """Create temp file and copy the database to it."""
        
        self.temp_dbdir = Path(mkdtemp())
        self.temp_maindb_path = self.temp_dbdir.joinpath("places.sqlite")
        self.temp_favicondb_path = self.temp_dbdir.joinpath("favicons.sqlite")
        
        return None

    def fetch_database(self, cdir, cfav) -> None:
        """Fetch database to temp file."""
        # Using FireFox63 the DB was locked for exclusive use of FireFox,
        # so we need to create a copy of it to a temp file.
        copyfile(self.get_places_db(cdir), self.temp_maindb_path)

        # favicon使用を設定している場合はfavicons.sqliteもコピーする
        if cfav == "1":
            copyfile(self.get_favicons_db(cdir), self.temp_favicondb_path)
 
        return None

    def get_db_dir(self, cdir) -> Path:
        """Get bookmarks database path."""

        # 設定ファイルからprofileを読み込む
        try:
            self.prof = Path(cdir).joinpath("places.sqlite")
        except TypeError:
            self.prof = Path("/dummy/path")

        if self.prof.exists():
            profile_path = Path(cdir)

        # 設定ファイルで設定していない場合はProfile0から読み込む    
        else:
            # Firefox folder path
            firefox_path = Path.home().joinpath(".mozilla/firefox")

            # Read Firefox profiles configuration file to get the database file path.
        
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
        """
        return self.get_db_dir(cdir).joinpath("places.sqlite")
    
    def get_favicons_db(self, cdir) -> Path:
        """
        favicons.sqliteのフルパスを取得する
        """
        return self.get_db_dir(cdir).joinpath("favicons.sqlite")


    def get_bookmark_list(self) -> list:
        """
        データベースファイルからブックマークのリストを取得する
        """
        import sqlite3
        from contextlib import closing

        with closing(sqlite3.connect(str(self.temp_maindb_path))) as self.conn:
            cur = self.conn.cursor()

            if self.temp_favicondb_path.exists():
                cur.execute(f'ATTACH DATABASE "{str(self.temp_favicondb_path)}" AS favicons')
                cur.execute('SELECT bookmark.title, place.url, keywords.keyword, icon.data AS icondata '
                            'FROM main.moz_bookmarks AS bookmark '
                            'INNER JOIN main.moz_places AS place ON (bookmark.fk = place.id) '
                            'LEFT JOIN main.moz_keywords AS keywords ON (place.id = keywords.place_id) '
                            'LEFT JOIN favicons.moz_pages_w_icons AS iconpage ON (place.url = iconpage.page_url) '
                            'LEFT JOIN favicons.moz_icons_to_pages AS iconid ON (iconpage.id = iconid.page_id) '
                            'LEFT JOIN favicons.moz_icons AS icon ON (iconid.icon_id = icon.id) '
                            'WHERE bookmark.type = 1 '
                            'AND place.url NOT LIKE "place:%" '
                            'GROUP BY place.url '
                            'ORDER BY place.last_visit_date DESC, bookmark.id ASC')

            else:
                cur.execute('SELECT bookmark.title, place.url, keywords.keyword '
                            'FROM moz_bookmarks AS bookmark '
                            'INNER JOIN moz_places AS place ON (bookmark.fk = place.id) '
                            'LEFT JOIN moz_keywords AS keywords ON (place.id = keywords.place_id) '
                            'WHERE bookmark.type = 1 '
                            'AND place.url NOT LIKE "place:%" '
                            'GROUP BY place.url '
                            'ORDER BY place.last_visit_date DESC, bookmark.id ASC')
            
            # ブックマークのデータをnamedtupleのlistとして取得
            namtup = namedtuple("bookmark_item", [field[0] for field in cur.description])
            results = [namtup._make(row) for row in cur]
        
        return results

    
    def clear_temp_files(self) -> None:
        """
        一時ディレクトリにコピーしたデータベースを消去する
        """
        rmtree(self.temp_dbdir)

        return None


class Plugin(QueryHandler):

    def id(self):
        return __name__
    
    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "f "

    def initialize(self):
        """
        プラグイン読み込み時にプラグインの設定とブックマークのデータを取得
        """

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

        firefoxbookmarks = FirefoxBookMarks()
        firefoxbookmarks.fetch_database(self.cdir, self.cfav)
        self.bookmarks_list = firefoxbookmarks.get_bookmark_list()
        info(f"Firefox Bookmarks: {str(len(self.bookmarks_list))} items indexed.")
        firefoxbookmarks.clear_temp_files()

        #データベースから読み込んだfaviconを一時ファイルに書き出し
        self.favicon_dir = mkdtemp()
        if self.cfav == "1":
            for item_num, bookmark_item in enumerate(self.bookmarks_list):
                if bookmark_item.icondata:
                    ico = open(self.favicon_dir + "/favicon_" + str(item_num), "wb")
                    ico.write(bookmark_item.icondata)
                    ico.close()
        

    def finalize(self):
        """
        終了時、書き出したfaviconの一時ファイルを削除
        """
        rmtree(self.favicon_dir)

    def handleQuery(self, query):
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

                item = Item()
                item.id = "FirefoxBookmark_" + str(item_num)
                item.text = str(bookmark_item.title)
                item.subtext = str(bookmark_item.url)
                item.completion = str(bookmark_item.title)

                ifile = self.favicon_dir + "/favicon_" + str(item_num)
                ipath = Path(ifile)
                if ipath.is_file():
                    item.icon = [ifile]
                else:
                    item.icon = ["xdg:firefox"]

                item.actions = [Action(
                    "open", "Open", lambda u = bookmark_item.url: openUrl(u)
                )]

                results_list.append(item)
                result_count += 1
                if result_count >= MAX_COUNT:
                    break

        query.add(results_list)

