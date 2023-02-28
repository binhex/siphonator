import os
import re
import lib.siphonator.search_imdb as siphonator_search_imdb


class PostRename(object):

    def __init__(self, logger_instance, **kwargs):

        self.dict = kwargs
        self.append_date = kwargs.get('append_date', None)
        self.separator = kwargs.get('separator', None)
        self.metadata_site = kwargs.get('metadata_site', None)
        self.root_path = kwargs.get('root_path', None)
        self.download_title = kwargs.get('download_title', None)
        self.logger_instance = logger_instance

    def search_download_title(self):

        if self.download_title:

            download_path = os.path.join(self.root_path, self.download_title)

            if os.path.isdir(download_path):

                self.logger_instance.info(u'Sending download_title %s to IMDb search module...' % self.download_title)

                self.dict.update({'download_title': self.download_title})

                if self.metadata_site == "IMDb":

                    mg_search_imdb_result = siphonator_search_imdb.release_details(self.logger_instance, self.dict)

                    if mg_search_imdb_result != 1:

                        self.rename_downloaded()

            else:

                self.logger_instance.warning(u'download_path %s is not a directory or does not exist' % download_path)
                self.logger_instance.warning(u'FAILED')
                return 1, None

        else:

            self.logger_instance.warning(u'No download title sent, assuming process all downloads in folder %s...' % self.root_path)

            for i in os.listdir(self.root_path):

                self.logger_instance.info(u'Sending download title %s to IMDb search module...' % i)

                self.dict.update({'download_title': i})

                if self.metadata_site == "IMDb":

                    search_imdb_instance = siphonator_search_imdb.SearchIMDB(self.logger_instance, **self.dict)
                    search_imdb_result = search_imdb_instance.get_title_and_year_using_regex()

                    if search_imdb_result != 1:

                        self.rename_downloaded()

    def rename_downloaded(self):

        self.download_title = self.dict['download_title']

        if "metadata_site_year" in self.dict:

            metadata_site_year = self.dict['metadata_site_year']

        else:

            self.logger_instance.warning(u'No metadata_site_year sent to function')
            self.logger_instance.warning(u'FAILED')
            return 1, None

        if "metadata_site_title" in self.dict:

            metadata_site_title = self.dict['metadata_site_title']

        else:

            self.logger_instance.warning(u'No metadata_site_title sent to function')
            self.logger_instance.warning(u'FAILED')
            return 1, None

        if self.separator == "spaces":

            separator = " "

        elif self.separator == "hyphens":

            separator = "-"

        elif self.separator == "underscores":

            separator = "_"

        else:

            separator = " "

        download_path = os.path.join(self.root_path, self.download_title)

        if self.append_date:

            metadata_site_title = "%s (%s)" % (metadata_site_title, metadata_site_year)

        metadata_site_title = re.sub('\s+', separator, metadata_site_title)

        metadata_download_path = os.path.join(self.root_path, metadata_site_title)

        if os.path.isfile(download_path):

            filename, file_extension = os.path.splitext(download_path)
            metadata_download_path = "%s%s" % (metadata_download_path, file_extension)

        if download_path != metadata_download_path:

            try:

                os.rename(download_path, metadata_download_path)
                self.logger_instance.info(u'Renamed download_path %s to %s' % (download_path, metadata_download_path))
                self.logger_instance.info(u'SUCCESS')

            except ConnectionAbortedError:

                self.logger_instance.warning(u'Connecttoo aborted duriig rename from %s to %s' % (download_path, metadata_download_path))
                self.logger_instance.warning(u'FAILED')
                return 1

            except WindowsError:

                self.logger_instance.warning(u'Unable to rename download_path %s to %s' % (download_path, metadata_download_path))
                self.logger_instance.warning(u'FAILED')
                return 1

        else:

            self.logger_instance.info(u'download_path %s and metadata path %s match, nothing to do' % (download_path, metadata_download_path))
            self.logger_instance.info(u'SKIPPED')
