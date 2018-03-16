# BibTeX HTML Citation Replacer

Replace `\cite{}` LaTeX notation in HTML paragraphs with embedded links to the DOI, URL, or author.

### Quickstart
```
pip install bibtex-html-citer
cite-fix foo.bib thesis.html
```

#### Rationale
I often export jupyter notebooks as html pages for sharing interactive components of my research, but also want an
easy way to include citations. 

- Setup [Zotero](http://www.zotero.org/) to drag-and-drop citations and get the LaTeX citation in your notebook.
    - Ex:  `\cite{author_2018}`
- Export notebook as an HTML page
- Run `cite-fix` providing BibTeX and HTML to replace all citations.
 
 
#### Options and Help
```
cite-fix --help
```
