from setuptools import setup, find_packages

setup(name='scattertext',
      version='0.0.2.31',
      description='An NLP package to visualize interesting terms in text.',
      url='https://github.com/JasonKessler/scattertext',
      author='Jason Kessler',
      author_email='jason.kessler@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
	      'numpy',
	      'scipy',
	      'scikit-learn',
	      'pandas',
	      'six',
          'mock'
	      #'spacy',
	      #'jieba',
	      #'tinysegmenter',
	      #'empath',
	      #'umap',
	      #'gensim'
	      # 'matplotlib',
	      # 'seaborn',
	      # 'jupyter',
      ],
      package_data={
	      'scattertext': ['data/*', 'data/viz/*', 'data/viz/*/*']
      },
      test_suite="nose.collector",
      tests_require=['nose'],
      #setup_requires=['nose>=1.0'],
      entry_points={
	      'console_scripts': [
		      'scattertext = scattertext.CLI:main',
	      ],
      },
      zip_safe=False)
