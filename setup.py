from setuptools import setup

setup(name='text-to-ideas',
      version='0.0.1.1',
      description='An NLP libarary to help find interesting terms in small to medium-sized corpora.',
      url='https://github.com/JasonKessler/text-to-ideas',
      author='Jason Kessler',
      author_email='jason.kessler@gmail.com',
      license='MIT',
      packages=['texttoideas'],
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
	      'texttoideas': ['texttoideas/data/*']
      },
			test_suite="test",
			setup_requires=['nose>=1.0'],
      zip_safe=False)
