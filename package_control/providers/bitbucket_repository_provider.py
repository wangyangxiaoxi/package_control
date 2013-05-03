import re

from ..clients.bitbucket_client import BitBucketClient


class BitBucketRepositoryProvider():
    """
    Allows using a public BitBucket repository as the source for a single package.
    For legacy purposes, this can also be treated as the source for a Package
    Control "repository".

    :param repo:
        The public web URL to the BitBucket repository. Should be in the format
        `https://bitbucket.org/user/package`.

    :param settings:
        A dict containing at least the following fields:
          `cache_length`,
          `debug`,
          `timeout`,
          `user_agent`
        Optional fields:
          `http_proxy`,
          `https_proxy`,
          `proxy_username`,
          `proxy_password`,
          `query_string_params`
          `install_prereleases`
    """

    def __init__(self, repo, settings):
        self.cache = {}
        self.repo = repo
        self.settings = settings

    @classmethod
    def match_url(cls, repo):
        """Indicates if this provider can handle the provided repo"""

        return re.search('^https?://bitbucket.org/([^/]+/[^/]+)/?$', repo) != None

    def prefetch(self):
        """
        Go out and perform HTTP operations, caching the result
        """

        self.get_packages()

    def get_packages(self, valid_sources=None):
        """
        Uses the BitBucket API to construct necessary info for a package

        :param valid_sources:
            A list of URLs that are permissible to fetch data from

        :return:
            A dict in the format:
            {
                'Package Name': {
                    'name': name,
                    'description': description,
                    'author': author,
                    'homepage': homepage,
                    'last_modified': last modified date,
                    'download': {
                        'url': url,
                        'date': date,
                        'version': version
                    },
                    'previous_names': [],
                    'labels': [],
                    'sources': [the repo URL],
                    'readme': url,
                    'issues': url,
                    'donate': url
                }
            }
            or False if there is an error
        """

        if 'get_packages' in self.cache:
            return self.cache['get_packages']

        client = BitBucketClient(self.settings)

        if valid_sources != None and self.repo not in valid_sources:
            self.cache['get_packages'] = False
            return False

        repo_info = client.repo_info(self.repo)
        if repo_info == False:
            self.cache['get_packages'] = False
            return False

        download = client.download_info(self.repo)
        if download == False:
            self.cache['get_packages'] = False
            return False

        self.cache['get_packages'] = {repo_info['name']: {
            'name': repo_info['name'],
            'description': repo_info['description'],
            'homepage': repo_info['homepage'],
            'author': repo_info['author'],
            'last_modified': download.get('date'),
            'download': download,
            'previous_names': [],
            'labels': [],
            'sources': [self.repo],
            'readme': repo_info['readme'],
            'issues': repo_info['issues'],
            'donate': repo_info['donate']
        }}
        return self.cache['get_packages']

    def get_renamed_packages(self):
        """For API-compatibility with :class:`PackageProvider`"""

        return {}

    def get_unavailable_packages(self):
        """
        Method for compatibility with PackageProvider class. These providers
        are based on API calls, and thus do not support different platform
        downloads, making it impossible for there to be unavailable packages.

        :return: An empty list
        """
        return []
