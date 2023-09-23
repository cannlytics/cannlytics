# https://squidfunk.github.io/mkdocs-material/getting-started/
# Material for MkDocs bundles useful and common plugins while
# trying not to blow up the size of the official image.
# If the plugin you want to use is not included,
# create a new Dockerfile and extend the official Docker
# image with your custom installation routine.
# Build the image with the following command:
# `docker build -t squidfunk/mkdocs-material .docs`
FROM squidfunk/mkdocs-material
COPY requirements.txt /tmp/
RUN pip --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org install --requirement /tmp/requirements.txt
COPY . /tmp/
