import json
import os
import time
from io import open
import urllib.request
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

from .exception import (
    WebpackError,
    WebpackLoaderBadStatsError,
    WebpackLoaderTimeoutError,
    WebpackBundleLookupError
)

import requests


class CreateReactLoader(object):
    asset_file = 'asset-manifest.json'

    def __init__(self, config, manifest_path=None):
        self.config = config
        self.is_dev = self.config.get("is_dev", False)
        self.manifest_path = manifest_path

    @property
    def asset_path(self):
        if self.is_dev:
            return self.config['FRONT_END_SERVER'].strip('/') + "/"
        return "/"

    def get_dev_assets(self):
        server = self.asset_path
        url = "{frontend_server}{asset_file}".format(frontend_server=server, asset_file=self.asset_file)
        try:
            data = requests.get(url, timeout=3)
        except:
            raise IOError(
                'Error reading {0}. Are you sure webpack has been started please check yarn start')

        return data.json()

    # "entrypoints": [
    #     "static/js/runtime-main.3d81b821.js",
    #     "static/css/2.ff442aac.chunk.css",
    #     "static/js/2.a49b7578.chunk.js",
    #     "static/css/main.f8d2615e.chunk.css",
    #     "static/js/main.1bd91348.chunk.js"
    # ]

    def get_prod_assets(self):
        try:
            #print("hello")
            self.manifest_path = "https://storage.googleapis.com/bookingstock/static/frontend/asset-manifest.json"
            build_folder = self.config['BUNDLE_DIR_NAME']
            if self.manifest_path:
                with urllib.request.urlopen(self.manifest_path) as url:
                    data = json.loads(url.read().decode())
                    # print(data)

                    # data["files"] = list(data["files"])
                    data["entrypoints"] = list(data["entrypoints"])

                    # for key in data["files"]:
                    #     data["files"][key] = data["files"][key].replace("/static/",
                    #                                                     "https://storage.googleapis.com/bookingstock/static/")
                    #
                    for i, item in enumerate(data["entrypoints"]):
                        #print("original", item)
                        thing = item.replace("static/", "https://storage.googleapis.com/bookingstock/static/frontend/static/")
                        #print("change to", thing)
                        data["entrypoints"][i] = thing

                    #print(data["entrypoints"])

                    return data
                # manifest_file = self.manifest_path
                # return json.
            else:
                manifest_file = os.path.join(build_folder, self.asset_file)
            with open(manifest_file, encoding="utf-8") as f:
                return json.load(f)
        except IOError:
            raise IOError(
                'Are you sure webpack has generated '
                'the asset-manifest file in the build directory and the path is correct?')

    def get_assets(self):
        if self.is_dev and not self.manifest_path:
            return self.get_dev_assets()
        return self.get_prod_assets()

    def get_bundle(self):
        assets = self.get_assets()
        if assets:
            chunks = assets['entrypoints']
            return chunks

    def get_pages(self):
        pages = self.get_assets()
        if pages:
            chunks = pages.get('pages', {})
            return chunks
