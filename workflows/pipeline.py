from digest import Article


def main():
    article_list = Article.list_all()
    latest_article = article_list[0]
    print(latest_article.all_text)


if __name__ == "__main__":
    main()
