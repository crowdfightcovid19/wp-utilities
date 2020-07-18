from sys import argv
import json
import requests
import csv
import unicodedata


def strip_accents(text):

    try:
        text = unicode(text, 'utf-8')
    except NameError:
        pass

    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")

    return str(text)


def get_gender(names, clf):
    genders = set()
    for name in names.split():
        if name not in clf:
            clf[name] = requests.get("https://api.genderize.io?name=%s" % name).json()
        if clf[name]["probability"] > 0.8:
            genders.add(clf[name]["gender"])

    return genders.pop() if len(genders) == 1 else "unknown"


def main(csv_filename):
    with open('data/classifier.json') as json_file:
        clf = json.load(json_file)

    csv_file = open(csv_filename, encoding='utf-8')
    res = list()
    for names in csv_file:
        striped_names = strip_accents(names)
        res.append([names.strip(), get_gender(striped_names, clf)])

    with open('names_gender.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(res)

    with open('data/classifier.json', 'w') as outfile:
        json.dump(clf, outfile)


if __name__ == '__main__':
    main(argv[1])
