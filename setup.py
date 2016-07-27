from setuptools import setup

setup(name='scattertext',
      version='0.0.1.4',
      description='An NLP libarary to help find interesting terms in small to medium-sized corpora.',
      url='https://github.com/JasonKessler/scattertext',
      author='Jason Kessler',
      author_email='jason.kessler@gmail.com',
      license='MIT',
      packages=['scattertext'],
      install_requires=[
	      'nose',
	      'numpy',
	      'scipy',
	      'sklearn',
	      'pandas',
	      'spacy',
	      'mpld3',
	      'matplotlib',
	      #'seaborn',
	      'jupyter',
      ],
      package_data={
	      'scattertext': ['data/*']
      },
			test_suite="test",
			setup_requires=['nose>=1.0'],
      zip_safe=False)
