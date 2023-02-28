import qbittorrentapi

# instantiate a Client using the appropriate WebUI configuration
qbt_client = qbittorrentapi.Client(
    host='192.168.1.10',
    port=2100,
    username='admin',
    password='adminadmin',
)

# the Client will automatically acquire/maintain a logged-in state
# in line with any request. therefore, this is not strictly necessary;
# however, you may want to test the provided login credentials.
try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

# display qBittorrent info
print(f'qBittorrent: {qbt_client.app.version}')
print(f'qBittorrent Web API: {qbt_client.app.web_api_version}')
for k,v in qbt_client.app.build_info.items(): print(f'{k}: {v}')

# retrieve and show all torrents
for torrent in qbt_client.torrents_info():
    print(f'{torrent.hash[-6:]}: {torrent.name} ({torrent.state})')

# pause all torrents
qbt_client.torrents.pause.all()

# add torrent magnet link
qbt_client.torrents_add(urls='magnet:?xt=urn:btih:df64fbe3d389fc5b520317e6525933abaa086591&dn=Swan.Song.2021.1080p.BluRay.AVC.DTS-HD.MA.5.1-INCUBO&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2830&tr=udp%3A%2F%2F9.rarbg.to%3A2840&tr=udp%3A%2F%2Ftracker.thinelephant.org%3A12710&tr=udp%3A%2F%2Ftracker.slowcheetah.org%3A14720')
qbt_client.torrents_reannounce(torrent_hashes='all')

