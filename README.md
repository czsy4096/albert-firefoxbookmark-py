# Firefox bookmarks plugin for Albert
## What is this?
This is a python plugin for [Albert](https://albertlauncher.github.io/), a keyboard application launcher for Linux, to search and access to your Firefox bookmarks. I made this for my personal use because the update to Albert v0.18 broke the official (C++) Firefox bookmarks plugin.

## Requirement
Nothing special other than Firefox, Albert, and python (>= 3.6).

## Usage
- Get source code from [Release](https://github.com/czsy4096/albert-firefoxbookmark-py/releases) or `git clone`.
- Copy the "firefox_bookmark" directory and files inside to python plugin directory.  
`~/.local/share/albert/python/plugins` for the current user, or `/usr/share/albert/python/plugins` for all users should be appropriate.
- Run Albert, or `Restart Albert` in Albert window if Albert is already running.
- Open `Settings` of Albert and "Plugins" tab. Find "Firefox Bookmarks" and activate.
- Python plugins need "Trigger" as it is now (Albert v0.20).  
Check the trigger in "Triggers" tab. It is "f " (f + space) by default.

## Configuring plugin
You can configure this plugin by editing firefoxbookmark.conf in firefox_bookmark directory. The conf file has these options below:
- `profile_dir`  
This option is not used by default and the plugin reads "Profile 0" of normal version Firefox. If you use another profile, set the full path of your profile as this option.
- `use_favicon`  
Setting this option "1" will show favicons in items (default). Setting other values will show the Firefox icon instead.
- `use_keyword`
Setting this option "1" enables to search bookmarks with "keywords". It is disabled by default.

## Notes
- You cannot search bookmarks with tags using this plugin. I have no plan to add that feature.
- This plugin indexes bookmarks when activated. Editing bookmarks after plugin activation does not affect indexed items automatically. `Restart Albert` to re-index bookmarks.
- Bookmarks are sorted by "last visited date", but deleting Firefox history also deletes this information. Moreover, they are not sorted in real-time and you should `Restart Albert` to re-sort bookmarks.
- I made this plugin for my personal use and have no plan to push this to official repository for python plugins. I hope someone to maintain C++ plugin.

## Special thanks
This plugin is based on [zer0-x/krunner-firefox-bookmarks](https://github.com/zer0-x/krunner-firefox-bookmarks), a plugin for krunner.