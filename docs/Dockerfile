# https://squidfunk.github.io/mkdocs-material/getting-started/
# Material for MkDocs bundles useful and common plugins while
# trying not to blow up the size of the official image.
# If the plugin you want to use is not included,
# create a new Dockerfile and extend the official Docker
# image with your custom installation routine:
FROM squidfunk/mkdocs-material
# RUN pip install mkdocstrings cannlytics

#  requests

# FIXME:
COPY requirements.txt /tmp/
# RUN pip install --requirement /tmp/requirements.txt
RUN pip --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org install --requirement /tmp/requirements.txt
COPY . /tmp/

# RUN pip install -r requirements.txt

# Build the image with the following command:
# docker build -t squidfunk/mkdocs-material .docs