import nmdmail


class NotificationEmail(object):

    def __init__(self, logger_instance, result_dict, config_dict):

        self.logger_instance = logger_instance
        self.result_dict = result_dict
        self.config_dict = config_dict
        self.smtp = {
            'host': self.config_dict['notification']['email']['host'],
            'port': self.config_dict['notification']['email']['port'],
            'tls': self.config_dict['notification']['email']['enable_tls'],
            'ssl': self.config_dict['notification']['email']['enable_ssl'],
            'user': self.config_dict['notification']['email']['username'],
            'password': self.config_dict['notification']['email']['password']
        }

    def email_send(self):

        imdb_title = self.result_dict.get('imdb_title')
        imdb_year = self.result_dict.get('imdb_year')
        imdb_id = self.result_dict.get('imdb_id')
        imdb_rating = self.result_dict.get('imdb_rating')
        imdb_votes = self.result_dict.get('imdb_votes')
        imdb_credits_cast_list = self.result_dict.get('imdb_credits_cast_list')
        imdb_credits_director_list = self.result_dict.get('imdb_credits_director_list')
        imdb_credits_director = ", ".join(imdb_credits_director_list)
        imdb_actors_limit_list = imdb_credits_cast_list[:10]
        imdb_actors = ", ".join(imdb_actors_limit_list)
        imdb_genres_list = self.result_dict.get('imdb_genres_list')
        imdb_genres = ", ".join(imdb_genres_list)
        index_title = self.result_dict.get('index_title')
        index_details = self.result_dict.get('index_details')
        index_size_mb = self.result_dict.get('index_size_mb')
        torrent_client_add_paused_bool = self.config_dict['torrent_client']['qbittorrent']['add_paused']

        imdb_plot = self.result_dict.get('imdb_plot_outline')
        if imdb_plot is None:
            imdb_plot = self.result_dict.get('imdb_plot_summary')

        if torrent_client_add_paused_bool is True:
            queue_status = 'Paused'
        elif torrent_client_add_paused_bool is False:
            queue_status = 'Started'
        else:
            queue_status = 'Unknown'

        content = """
**Title:** [%s (%s)](https://imdb.com/title/%s) %s from %s users<br/><br/>
**Plot:** %s<br/><br/>
**Actors:** %s<br/><br/>
**Directors:** %s<br/><br/>
**Genres:** %s<br/><br/>
**Queue Status:** %s<br/><br/>
**Release:** [%s](%s)<br/><br/>
**Size:** %s MB
        """ % (imdb_title, imdb_year, imdb_id, imdb_rating, imdb_votes, imdb_plot, imdb_actors, imdb_credits_director,
               imdb_genres, queue_status, index_title, index_details, index_size_mb)

        nmdmail.send(
            content,
            subject='Siphonator: %s (%s) - IMDb rating %s - Action Queued' % (imdb_title, imdb_year, imdb_rating),
            from_email=self.config_dict['notification']['email']['from_address'],
            to_email=self.config_dict['notification']['email']['to_address'],
            smtp=self.smtp
        )
