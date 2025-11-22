from setuptools import setup, find_packages

setup(
    name='tax_fraud_gnn',
    version='0.1.0',
    description='Tax fraud detection GNN project',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
)
