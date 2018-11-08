import app.services.webscraping as webscraping


def scrap_monster():
    monsterScraping = webscraping.Monster()

    # begin scrap data
    monsterScraping.scrap_data()

if __name__ == '__main__':
    scrap_monster()