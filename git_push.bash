source ~/.bash_profile
cd /Users/admin/server_configs_and_settings
git config --global user.name "Seth Chase"
git config --global user.email "blinddiver@gmail.com"
git config --global color.ui "auto"
git commit -am "Working config for read url posts in console via log messages.  Added json decoder config."
git push --all --prune