from setuptools import setup, find_packages

setup(name='bibtex-html-citer',
      version='1.0.0',
      description='Finds `\cite{}` text in an HTML document and replaces with a link to DOI/URL.',
      url='http://github.com/jvivian/bibtex-html-citer',
      author='John Vivian',
      author_email='jtvivian@gmail.com',
      license='MIT',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      install_requires=['bibtexparser>=1.0.1',
                        'click',
                        'bs4'],
      entry_points={
          'console_scripts': ['cite-fix=bibtex_html_citer.fix_citations:main']})
