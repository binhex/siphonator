import nmdmail

class NotificationEmail(object):

    def __init__(self, logger_instance, **kwargs):

        self.index_dict = kwargs
        self.logger_instance = logger_instance
        self.smtp = {
            'host': self.index_dict.get('notification_email_host'),
            'port': self.index_dict.get('notification_email_port'),
            'tls': self.index_dict.get('notification_email_enable_tls'),
            'ssl': self.index_dict.get('notification_email_enable_ssl'),
            'user': self.index_dict.get('notification_email_username'),
            'password': self.index_dict.get('notification_email_password')
        }

    def email_send(self):

        imdb_title = self.index_dict.get('imdb_title')
        imdb_year = self.index_dict.get('imdb_year')
        imdb_id = self.index_dict.get('imdb_id')
        imdb_rating = self.index_dict.get('imdb_rating')
        imdb_votes = self.index_dict.get('imdb_votes')
        imdb_plot = self.index_dict.get('imdb_plot_outline') #none?
        imdb_credits_cast_list = self.index_dict.get('imdb_credits_cast_list')
        imdb_credits_director_list = self.index_dict.get('imdb_credits_director_list')
        imdb_credits_director = ", ".join(imdb_credits_director_list)
        imdb_actors_limit_list = imdb_credits_cast_list[:10]
        imdb_actors = ", ".join(imdb_actors_limit_list)
        imdb_genres_list = self.index_dict.get('imdb_genres_list')
        imdb_genres = ", ".join(imdb_genres_list)
        index_title = self.index_dict.get('index_title')
        index_details = self.index_dict.get('index_details')
        index_size_mb = self.index_dict.get('index_size_mb')
        torrent_client = self.index_dict['torrent_client']
        torrent_client_add_paused_bool = self.index_dict["torrent_client_%s_add_paused" % torrent_client]

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

        nmdmail.send(content,
            subject='Siphonator: %s (%s) - IMDb rating %s - Action Queued' % (imdb_title, imdb_year, imdb_rating),
            from_email=self.index_dict.get('notification_email_from_address'),
            to_email=self.index_dict.get('notification_email_to_address'),
            smtp=self.smtp)