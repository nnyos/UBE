FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# [Optional] If your requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt 
#    && rm -rf /tmp/pip-tmp/

# [Optional] Install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive 
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# Install Oh My Bash for the vscode user
USER vscode
RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)" --unattended \
    && sed -i 's/OSH_THEME="font"/OSH_THEME="rr"/' ~/.bashrc \
    && echo "alias add='git add .'" >> ~/.bashrc
