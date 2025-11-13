python3 workflows/build.py
git add README.md
git add rss.xml
git add data
git commit -m "[build.py] local $(date '+%Y-%m-%d-%H%M')"
git push origin main
open https://github.com/nuuuwan/lk_news_digest/blob/main/README.md