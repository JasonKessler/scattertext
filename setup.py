from setuptools import setup, find_packages

setup(name='scattertext',
      version='0.2.0',
      description='An NLP package to visualize interesting terms in text.',
      url='https://github.com/JasonKessler/scattertext',
      author='Jason Kessler',
      author_email='jason.kessler@gmail.com',
      license='Apache 2.0',
      python_requires='>=3.11',
      packages=find_packages(),
      install_requires=[
          'numpy>=1.2.6',
          'scipy>=1.12.0',
          'scikit-learn>=1.4',
          'pandas>=2.0.0',
          'statsmodels>=0.14.1',
          'flashtext>=2.7',
          'gensim>=4.0.0',
          'spacy>=3.2',
          'tqdm>=4.0'
          # 'pytextrank'
          # 'jieba',
          # 'tinysegmenter',
          # 'empath',
          # 'umap',
          # 'gensim'
          # 'matplotlib',
          # 'seaborn',
          # 'jupyter',
          #  "textalloc",
      ],
      package_data={
          'scattertext': ['data/*', 'data/viz/*', 'data/viz/*/*']
      },
      test_suite="nose.collector",
      tests_require=['nose'],
      # setup_requires=['nose>=1.0'],
      entry_points={
          'console_scripts': [
              'scattertext = scattertext.CLI:main',
          ],
      },
      zip_safe=False)
