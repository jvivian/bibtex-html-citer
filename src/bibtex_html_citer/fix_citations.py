import os
import re

import bibtexparser as bp
import click
from bs4 import BeautifulSoup, NavigableString, Tag

end_chars = ['</p>', '.', '!', '?', ',']


@click.command()
@click.argument('bibtex', required=1)
@click.argument('html', required=1)
@click.option('--no-overwrite', is_flag=True, help='Flag that prevents overwriting of input HTML')
def main(bibtex, html, no_overwrite):
    """
    Given paths to a BIBTEX and HTML file, program will find all instances of "\cite{}" within <p> tags
    and replace with a link to the DOI / URL in the bibtex entry.
    """
    # Check files exist
    for input_file in [bibtex, html]:
        assert os.path.exists(input_file), 'Path to input file not found: {}'.format(input_file)

    # Load bibtex and parse into dictionary
    bib = bp.bparser.BibTexParser(common_strings=True).parse_file(open(bibtex)).entries_dict

    # Load HTML and parse via beautifulsoup
    with open(html, 'rb') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Identify paragraph tags and begin main loop
    for p in soup.find_all('p'):

        # Check for citation hits in text
        hits = re.findall(r'\\cite{.\S+', str(p))
        if not hits:
            continue

        # Copy paragraph tag so it can be cleared and re-filled
        new_p = BeautifulSoup(str(p), 'html.parser').find('p')
        p.clear()

        # Handle elements within the paragraph
        for element in new_p.children:
            if isinstance(element, NavigableString):
                # If no hits in current element, continue iteration
                hits = re.findall(r'\\cite{.\S+', element.encode('utf-8').decode('ascii', 'ignore'))
                if not hits:
                    p.append(element)
                    continue

                # If citation found, create cite flag and list to hold citation keys
                # Use encode/decode only when necessary
                in_cite = False
                keys = []
                for word in element.encode('utf-8').decode('ascii', 'ignore').split():

                    # Check if word is citation or if within a citation block
                    word = str(word)  # Cast as a str for type system
                    if word.startswith('\\cite') or in_cite:
                        [keys.append(split_cite(key)) for key in word.split(',') if key]
                        in_cite = False if remove_end_chars(word).endswith('}') else True

                        # If currently in a citation block, continue
                        if in_cite:
                            continue

                        # Otherwise, build and replacement link and clear current set of keys
                        add_replacement_links(p, keys, soup, bib)
                        keys = []

                    # Add normal string back to paragraph object by stripping paragraph tags
                    else:
                        for tag in ['<p>', '</p>']:
                            word = word.replace(tag, '')
                        p.append(NavigableString(word + ' '))

            # Append if not NavigableString
            else:
                p.append(element)

    # Save output
    if no_overwrite:
        root, name = os.path.split(html)
        output_name = os.path.join(root, 'CITED-' + name)
    else:
        output_name = html

    with open(output_name, 'w') as f:
        f.write(str(soup))


def remove_end_chars(word):
    """
    Remove end_chars from word

    :param str word:
    :return: Cleaned word
    :rtype: str
    """
    for ec in end_chars:
        word = word.rstrip(ec)
    return word


def split_cite(word):
    """
    Removes \cite{ and trailing char if present

    :param str word: Word to process
    :return: Cleaned word
    :rtype: str
    """
    for c in end_chars + ['}']:
        word = word.rstrip(c)

    # Replace instances of em-dashes with underscore
    for em in ['<em>', '</em>']:
        word = word.replace(em, '_')

    # If citation, remove
    if word.startswith('\\cite'):
        return word.split('\\cite{')[1]
    else:
        return word


def add_replacement_links(p, keys, soup, bib):
    """
    Given a paragraph object and possible bibtex keys, add a replacement link to the paragraph object

    :param Tag p: BS Paragraph object
    :param list(str) keys: List of citation keys
    :param BeautifulSoup soup: Beautiful Soup object
    :param dict(str, str) bib: Dictionary created from BibTeX
    """
    p.append(NavigableString('['))
    for i, key in enumerate(keys):
        p.append(create_link_from_entry(soup, bib, key))
        if i + 1 == len(keys):
            p.append(NavigableString('] '))
        else:
            p.append(NavigableString(', '))


def create_link_from_entry(soup, bib, key):
    """
    Creates link/replacement text for bibtex entry

    :param BeautifulSoup soup: Beautiful Soup object
    :param dict bib: Dictionary created from BibTeX
    :param str key: Single citation key
    :return: Link or text to replace citation
    :rtype: Tag|NavigableString
    """
    # Define possible tags to use
    b_tag = soup.new_tag('b')

    try:
        entry = bib[key]
    except KeyError:
        click.echo('Entry {} not found in bibtex file!'.format(key))
        b_tag.append('{}'.format(key))
        return b_tag

    # Info for entry: <Author> et al. <Year>.
    try:
        author = NavigableString(entry['author'].split(',')[0] + ' et al. ' + entry['year'] + '. ')
    except KeyError:
        click.echo('Author not found for bibtex key: "{}", using key instead'.format(key))
        author = NavigableString(key + ' ')

    # Use DOI if available
    if 'doi' in entry.keys():
        link = soup.new_tag('a', href='https://doi.org/' + entry['doi'])
        link.append(author)
        return link

    # Otherwise use URL
    elif 'url' in entry.keys():
        link = soup.new_tag('a', href=entry['url'])
        link.append(author)
        return link

    # Else return author
    else:
        b_tag.append(author)
        return b_tag


if __name__ == '__main__':
    main()
