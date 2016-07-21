from setuptools import setup

setup(name='text-to-ideas',
      version='0.0.1',
      description='The funniest joke in the world',
      url='https://github.com/JasonKessler/text-sto-ideas',
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
      zip_safe=False)
