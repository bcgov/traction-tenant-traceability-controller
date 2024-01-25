from urllib import parse


def format_label(label):
    # Remove spacing and lowercase the label
    return parse.quote(label.strip().lower())