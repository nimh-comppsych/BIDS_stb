from setuptools import setup


setup(
	name='BIDS_stb',
	py_modules=['stb'],
	install_requires=[
		'Click'
	],
	entry_points='''
		[console_scripts]
		BIDS_stb=stb:stb_model
	'''
)
