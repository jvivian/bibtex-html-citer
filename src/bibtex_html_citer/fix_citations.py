import os
import re

import bibtexparser as bp
import click


@click.command()
@click.argument('bibtex', required=1)
@click.argument('html', required=1)
@click.option('--no-overwrite', is_flag=True, help='Flag that prevents overwriting of input HTML')
def main(bibtex, html, no_overwrite):
    """
    Given paths to a BIBTEX and HTML file, program will find all instances of "\cite{}" within <p> tags
    and replace with a link to the DOI / URL in the bibtex entry.
    """
    # Check files exists
    for input_file in [bibtex, html]:
        assert os.path.exists(input_file), 'Path to input file not found: {}'.format(input_file)

    # Load bibtex and parse into dictionary
    bib = bp.bparser.BibTexParser(common_strings=True).parse_file(open(bibtex)).entries_dict

    # Main loop
    link_template = '<a href="'
    output = ''
    with open(html, 'r') as f:
        for line in f:

            # Look for \cite{} matches
            hits = re.findall(r'\\cite{.\S+', line)

            # If \cite{} in line, parse
            if hits:
                output_line = []
                line = line.split()
                for string in line:

                    # If citation found
                    if string.startswith('\\cite'):
                        link = '['
                        keys = string.split('\\cite')[1][:-1]  # Removes \cite{ and trailing curly bracket
                        num_citations = len(keys.split(','))

                        # For citation within \cite{} brackets
                        for i, key in enumerate(keys.split(',')):
                            try:

                                # Access bib entry
                                entry = bib[key]

                                # Info for entry
                                author = entry['author'].split(',')[0] + ' et al. ' + entry['year'] + '.'
                                comma = '' if i + 1 == num_citations else ', '

                                # If DOI
                                if 'doi' in entry.keys():
                                    link += link_template + 'https://doi.org/'
                                    link += entry['doi'] + '/">{}{}</a>'.format(author, comma)

                                # If URL
                                elif 'url' in entry.keys():
                                    link += link_template + entry['url'] + '/">{}{}</a>'.format(author, comma)

                                # If no DOI / URL post author/year
                                else:
                                    link = '<b>{}</b>{}'.format(author, comma)

                            # If no entry found
                            except KeyError:
                                click.echo('Entry {} not found in bibtex file!'.format(key))
                                link += '<b>{}</b>'.format(key)

                        # Finish link and append
                        link += ']'
                        output_line.append(link)

                    # If normal string
                    else:
                        output_line.append(string)

                # Concat output HTML string
                output += ' '.join(output_line) + '\n'

            # Build output if no citations found
            else:
                output += line

    # Save output
    if no_overwrite:
        root, name = os.path.split(html)
        output_name = os.path.join(root, 'CITED-' + name)
    else:
        output_name = html

    with open(output_name, 'w') as f:
        f.write(output)


if __name__ == '__main__':
    main()
