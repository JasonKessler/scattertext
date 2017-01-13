from setuptools import setup, find_packages

setup(name='scattertext',
      version='0.0.2.0.0',
      description='An NLP libarary to help find interesting terms in small to medium-sized corpora.',
      url='https://github.com/JasonKessler/scattertext',
      author='Jason Kessler',
      author_email='jason.kessler@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
	      'nose',
	      'numpy',
	      'scipy',
	      'sklearn',
	      'pandas',
	      'spacy',
	      # 'mpld3',
	      # 'matplotlib',
	      # 'seaborn',
	      # 'jupyter',
      ],
      package_data={
	      'scattertext': ['data/*', 'data/viz/*', 'data/viz/*/*']
      },
      test_suite="nose.collector",
      tests_require=['nose'],
      setup_requires=['nose>=1.0'],
      zip_safe=False)
