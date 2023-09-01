"""
Middleware | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/1/2021
Updated: 8/21/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
from urllib.parse import quote
from django import http
from django import urls
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


def generate_url(request, path):
    if request.get_host():
        new_url = "%s://%s%s" % (request.is_secure() and 'https' or 'http',
                                request.get_host(),
                                quote(path))
    else:
        new_url = quote(path)
    if request.GET:
        new_url += '?' + request.META['QUERY_STRING']
    return new_url


def is_valid_path(path, urlconf=None):
    """
    Returns True if the given path resolves against the default URL resolver,
    False otherwise.
    """
    try:
        urls.resolve(path, urlconf)
        return True
    except urls.Resolver404:
        return False


class AppendOrRemoveSlashMiddleware(MiddlewareMixin):
    """Like django's built in APPEND_SLASH functionality, but also works in
    reverse. Eg. will remove the slash if a slash-appended url won't resolve,
    but its non-slashed counterpart will.

    Additionally, if a 404 error is raised within a view for a non-slashed url,
    and APPEND_SLASH is True, and the slash-appended url resolves, the
    middleware will redirect. (The default APPEND_SLASH behavior only catches
    Resolver404, so wouldn't work in this case.)

    See gregbrown.co.nz/code/append-or-remove-slash/ for more information."""

    def process_request(self, request):
        """Returns a redirect if adding/removing a slash is appropriate. This
        works in the same way as the default APPEND_SLASH behavior but in
        either direction. First, check if the url is valid. If not, check if
        adding/removing the trailing slash helps. If the new url is valid, redirect to it.
        """
        urlconf = getattr(request, 'urlconf', None)
        if not is_valid_path(request.path_info, urlconf):
            if request.path_info.endswith('/'):
                new_path = request.path_info[:-1]
            else:
                new_path = request.path_info + '/'
            if is_valid_path(new_path, urlconf):
                return http.HttpResponsePermanentRedirect(
                    generate_url(request, new_path))

    def process_response(self, request, response):
        """If a 404 is raised within a view, try appending/removing the slash
        (based on the  setting) and redirecting if the new url is
        valid."""
        if response.status_code == 404:
            if not request.path_info.endswith('/') and settings.APPEND_SLASH:
                new_path = request.path_info + '/'
            elif request.path_info.endswith('/') and not settings.APPEND_SLASH:
                new_path = request.path_info[:-1]
            else:
                new_path = None
            if new_path:
                urlconf = getattr(request, 'urlconf', None)
                if is_valid_path(new_path, urlconf):
                    return http.HttpResponsePermanentRedirect(
                        generate_url(request, new_path))
        return response


class BlockUserAgentsMiddleware(object):
    # See: https://github.com/mitchellkrogza/nginx-ultimate-bad-bot-blocker/blob/master/_generator_lists/bad-user-agents.list
    # Last updated: 8/20/2023
    BLOCKED_USER_AGENTS = {
        'Firefox 56', 'Go-http-client/2.0', 'empty',
        '01h4x.com', '360Spider', '404checker', '404enemy', '80legs', 
        'ADmantX', 'AIBOT', 'ALittle\ Client', 'ALittle Client', 'ASPSeek', 'Abonti', 
        'Aboundex', 'Aboundexbot', 'Acunetix', 'AdsTxtCrawlerTP', 'AfD-Verbotsverfahren',
        'AhrefsBot', 'AiHitBot', 'Aipbot', 'Alexibot', 'AllSubmitter',
        'Alligator', 'AlphaBot', 'Anarchie', 'Anarchy', 'Anarchy99',
        'Ankit', 'Anthill', 'Apexoo', 'Aspiegel', 'Asterias',
        'Atomseobot', 'Attach', 'AwarioRssBot', 'AwarioSmartBot', 'BBBike',
        'BDCbot', 'BDFetch', 'BLEXBot', 'BackDoorBot', 'BackStreet',
        'BackWeb', 'Backlink-Ceck', 'BacklinkCrawler', 'Badass', 'Bandit',
        'Barkrowler', 'BatchFTP', 'Battleztar\ Bazinga', 'BetaBot', 'Bigfoot',
        'Bitacle', 'BlackWidow', 'Black\ Hole', 'Blackboard', 'Blow',
        'BlowFish', 'Boardreader', 'Bolt', 'BotALot', 'Brandprotect',
        'Brandwatch', 'Buck', 'Buddy', 'BuiltBotTough', 'BuiltWith',
        'Bullseye', 'BunnySlippers', 'BuzzSumo', 'Bytespider', 'CATExplorador',
        'CCBot', 'CODE87', 'CSHttp', 'Calculon', 'CazoodleBot',
        'Cegbfeieh', 'CensysInspect', 'CheTeam', 'CheeseBot', 'CherryPicker',
        'ChinaClaw', 'Chlooe', 'Citoid', 'Claritybot', 'Cliqzbot',
        'Cloud\ mapping', 'Cocolyzebot', 'Cogentbot', 'Collector', 'Copier',
        'CopyRightCheck', 'Copyscape', 'Cosmos', 'Craftbot', 'Crawling\ at\ Home\ Project',
        'CrazyWebCrawler', 'Crescent', 'CrunchBot', 'Curious', 'Custo',
        'CyotekWebCopy', 'DBLBot', 'DIIbot', 'DSearch', 'DTS\ Agent',
        'DataCha0s', 'DatabaseDriverMysqli', 'Demon', 'Deusu', 'Devil',
        'Digincore', 'DigitalPebble', 'Dirbuster', 'Disco', 'Discobot',
        'Discoverybot', 'Dispatch', 'DittoSpyder', 'DnBCrawler-Analytics', 'DnyzBot',
        'DomCopBot', 'DomainAppender', 'DomainCrawler', 'DomainSigmaCrawler', 'DomainStatsBot',
        'Domains\ Project', 'Dotbot', 'Download\ Wonder', 'Dragonfly', 'Drip',
        'ECCP/1.0', 'EMail\ Siphon', 'EMail\ Wolf', 'EasyDL', 'Ebingbong',
        'Ecxi', 'EirGrabber', 'EroCrawler', 'Evil', 'Exabot',
        'Express\ WebPictures', 'ExtLinksBot', 'Extractor', 'ExtractorPro', 'Extreme\ Picture\ Finder',
        'EyeNetIE', 'Ezooms', 'FDM', 'FHscan', 'FemtosearchBot',
        'Fimap', 'Firefox/7.0', 'FlashGet', 'Flunky', 'Foobot',
        'Freeuploader', 'FrontPage', 'Fuzz', 'FyberSpider', 'Fyrebot',
        'G-i-g-a-b-o-t', 'GPTBot', 'GT::WWW', 'GalaxyBot', 'Genieo',
        'GermCrawler', 'GetRight', 'GetWeb', 'Getintent', 'Gigabot',
        'Go!Zilla', 'Go-Ahead-Got-It', 'GoZilla', 'Gotit', 'GrabNet',
        'Grabber', 'Grafula', 'GrapeFX', 'GrapeshotCrawler', 'GridBot',
        'HEADMasterSEO', 'HMView', 'HTMLparser', 'HTTP::Lite', 'HTTrack',
        'Haansoft', 'HaosouSpider', 'Harvest', 'Havij', 'Heritrix',
        'Hloader', 'HonoluluBot', 'Humanlinks', 'HybridBot', 'IDBTE4M',
        'IDBot', 'IRLbot', 'Iblog', 'Id-search', 'IlseBot',
        'Image\ Fetch', 'Image\ Sucker', 'IndeedBot', 'Indy\ Library', 'InfoNaviRobot',
        'InfoTekies', 'Intelliseek', 'InterGET', 'InternetSeer', 'Internet\ Ninja',
        'Iria', 'Iskanie', 'IstellaBot', 'JOC\ Web\ Spider', 'JamesBOT',
        'Jbrofuzz', 'JennyBot', 'JetCar', 'Jetty', 'JikeSpider',
        'Joomla', 'Jorgee', 'JustView', 'Jyxobot', 'Kenjin\ Spider',
        'Keybot\ Translation-Search-Machine', 'Keyword\ Density', 'Kinza', 'KisMiiBot', 'Kolinka\ Forum\ Search',
        'KosugiBot', 'Krak', 'Kruger', 'Kruncher', 'KumKie',
        'LNSpiderguy', 'LSSRocketCrawler', 'Larbin', 'LeechFTP', 'Leet-Search',
        'Lftp', 'LibWeb', 'Libwhisker', 'LinkChecker', 'LinkLint',
        'LinkScan', 'LinkWalker', 'Lipperhey', 'Litemage_walker', 'LoadTimeBot',
        'LondonTrustMedia', 'LookSmart', 'Ltx71', 'Lucy', 'Lwp-request',
        'Lycos', 'MJ12bot', 'MSFrontPage', 'MVAClient', 'Magnet',
        'MagpieRSS', 'Mail.ru', 'Mass\ Downloader', 'Masscan', 'Masscan/1.0',
        'Mata\ Hari', 'MaxPointCrawler', 'Mediaperiscope', 'MegaIndex', 'Megaproxy',
        'MemGator', 'MetaURI', 'MetaSearch', 'Metadatalabs', 'Metager',
        'MetagerBot', 'MiaDevBot', 'Microsoft\ URL\ Control', 'Milbot', 'Mister\ PiX',
        'MojeekBot', 'Mrcgiguy', 'Multiviews', 'Muscimol', 'MyApp',
        'MyFamilyBot', 'MyGet', 'Myra', 'NETCRAFT', 'NING',
        'NICErsPRO', 'Najdi.si', 'Name\ Intelligence', 'Navroad', 'NearSite',
        'NetAnts', 'NetCarta', 'Netcraft', 'NetcraftSurveyAgent', 'Netsprint',
        'Nettrack', 'Netvibes', 'NetzHautKrabbler', 'NewsGator', 'Newsmeister',
        'NewswhipBot', 'Nikto', 'Nimbostratus-Bot', 'Ninjapointer', 'Nmap',
        'Noxtrumbot', 'Nutch', 'NutchCVS', 'Nymesis', 'Nzexplorer',
        'ObjectsSearch', 'Odira', 'Offline\ Explorer', 'Offline\ Navigator', 'Omea\ Reader',
        'Openfind', 'OpenindexSpider', 'Openvas', 'OrangeBot', 'OrangeSpider',
        'Orbiter', 'OrgProbe', 'Orthogaffe', 'Osmosis', 'OutfoxBot',
        'PageAnalyzer', 'PageGrabber', 'PagePeeker', 'PagesInventory', 'Papa\ Foto',
        'Parsoid', 'PathDefender', 'Pavuk', 'PeerBot', 'Peew',
        'Perlu', 'PhpDig', 'Picsearch', 'Picscout', 'PicsearchBot',
        'PimonBot', 'PingAdmin.Ru', 'Pingdom', 'Pingoscope', 'Plukkie',
        'Pompos', 'Porkbun', 'Poseidon', 'Postman', 'Postmaster',
        'PowerMapper', 'Prowler', 'Pulsepoint', 'Pump', 'Python-urllib',
        'Qseero', 'Qwantify', 'QyresearchBot', 'Qualidator', 'QuepasaCreep',
        'QuerySeekerSpider', 'QuestTrend', 'QuickView', 'Qwant', 'RBSE\ Spider',
        'REALDownload', 'ReGet', 'RMA', 'Raindance', 'RakeClag',
        'RankFlex', 'RankSignal', 'RankWisely', 'Rankivabot', 'RebelMouse',
        'Recluse', 'Reget', 'RelevanceRank', 'Repbot', 'Researchscan',
        'Riddler', 'Robozilla', 'Rocxor', 'Rogerbot', 'SEOkicks-Robot',
        'SEOprofiler', 'SISTRIX', 'SMTBot', 'SQLMap', 'SSLLabs',
        'SWIMGBot', 'SafetyNet', 'Safexplorer', 'SalesIntelligent', 'Saleslift',
        'Savage', 'Savvy', 'Scooter', 'Scrapy', 'Screaming\ Frog\ SEO\ Spider',
        'Searchestate', 'SearchmetricsBot', 'Seeker', 'SemRushBot', 'SerpstatBot',
        'Seznam', 'SeznamBot', 'SeznamScreenshotator', 'Shelob', 'Shodan',
        'Shoula\ robot', 'SiNagotchi', 'Siphon', 'SiteExplorer', 'SiteLockSpider',
        'SiteSucker', 'Sitebeam', 'Sitebulb/', 'Siteimprove', 'Sitevigil',
        'SklikBot', 'Skygrid', 'Slack-ImgProxy', 'Slackbot', 'Slackbot-LinkExpanding',
        'Slurp', 'SlySearch', 'SmartDownload', 'Snoopy', 'SnykeBot',
        'Sogou', 'Sonic', 'SortSite', 'Sothink', 'SpaceBison',
        'Spade', 'SpankBot', 'Spanner', 'Spbot', 'Speedy',
        'SputnikBot', 'Spyder', 'Sqworm', 'SqwormBot', 'StackRambler',
        'Steeler', 'Sucker', 'SugarScape', 'Suke', 'SurdotlyBot',
        'SurveyBot', 'Suzuran', 'Sysomos', 'TMCrawler', 'TOBBOT',
        'TSE-Archive', 'TSE-R', 'Telesoft', 'Teleport', 'TeleportPro',
        'Teoma', 'TessWebBot', 'TheIntraformant', 'TheNomad', 'Thumbnail.CZ',
        'TightTwatBot', 'TinEye', 'Toata', 'Toplistbot', 'Touche',
        'ToutiaoSpider', 'Traackr.com', 'TrendictionBot', 'TrendsmapResolver', 'Turingos',
        'Turnitin', 'Twiceler', 'Twitterbot', 'UdmSearch', 'UniversalFeedParser',
        'UpdateScanner', 'Urlck', 'VB\ Project', 'VCI', 'Vacuum',
        'Vagabondo', 'Vagabondo-WAP', 'Vault', 'Velen', 'VidibleScraper',
        'VoidEYE', 'VulnbustersMeter', 'WWW-Collector-E', 'WWW-Mechanize', 'WWWOFFLE',
        'Web\ Bandit', 'Web\ Collage', 'Web\ Copier', 'Web\ Data', 'Web\ Downloader',
        'Web\ Enhancer', 'Web\ Fetch', 'Web\ Go\ IS', 'Web\ Image\ Collector', 'Web\ Sucker',
        'Web\ sait', 'Web-AUTD', 'WebAuto', 'WebCapture', 'WebClient',
        'WebCollage', 'WebCopier', 'WebCorp', 'WebDAV', 'WebDownloader',
        'WebEMailExtrac', 'WebEmailExtractor', 'WebEnhancer', 'WebFetch', 'WebGo\ IS',
        'WebGobble', 'WebLeacher', 'WebPix', 'WebReaper', 'WebRipper',
        'WebSauger', 'WebShag', 'WebSite', 'WebSite-eXtractor', 'WebStripper',
        'WebVac', 'WebVulnCrawl', 'WebWhacker', 'WebZip', 'Webbandit',
        'Webclipping.com', 'Webcorp', 'Webfetch', 'WebmasterWorldForumBot', 'Webmin',
        'Weblayers', 'Webscan', 'Website\ Explorer', 'Website\ Quester', 'Webster',
        'Webster\ Pro', 'Webtail', 'Webtoaster', 'Webview', 'Webwalk',
        'Webwasher', 'Webwombat', 'Webzinger', 'WeSEE', 'WeSEE:Search',
        'Wells', 'Whack', 'Whacker', 'Widow', 'WinHTTP',
        'Windows-RSS-Platform', 'Winpodder', 'Wotbox', 'XGET', 'Xaldon',
        'Xenu', 'Xintell', 'XoviBot', 'Y!J', 'Y!J-BSC',
        'Y!OASIS/TEST', 'Y!TunnelPro', 'YJSearch', 'YRSpider', 'YaCy',
        'Yahoo', 'Yahoo\ Link\ Preview', 'YahooSeeker', 'YahooYSMcm', 'Yandex',
        'YandexBot', 'YandexImages', 'YandexMetrika', 'Yasaklibot', 'Yeti',
        'YoudaoBot', 'ZDBop', 'Zade', 'Zao', 'Zauba',
        'ZeBot', 'Zealbot', 'Zearch', 'Zeguestlist-Bot', 'Zermelo',
        'Zeus', 'Ziggy', 'Ziyu', 'ZoomSpider', 'Zumbot',
        'baidu', 'bibnum.bnf', 'coccoc', 'contxbot', 'dotbot',
        'eCatch', 'ePost-Search', 'envolk', 'findlink', 'findthatfile',
        'foobot', 'g00g1e', 'g2reader-bot', 'geliyoo', 'genieBot',
        'gonzo', 'heritrix', 'htdig', 'ia_archiver', 'ichiro',
        'lftp', 'libwww', 'linkdexbot', 'mogimogi', 'netresearchserver',
        'nikto', 'panscient', 'phpcrawl', 'pycurl', 'redback',
        'riddler', 'rogerbot', 'scrapy', 'seoscanners', 'seznambot',
        'sistrix', 'spbot', 'speedy', 'sputnik', 'teoma',
        'tracemyfile', 'trendictionbot', 'truwoGPS', 'unirest-java', 'unwindFetchor',
        'urlresolver', 'vortex', 'webmon ', 'wget', 'yie8',
        'zatnawqy', 'zoomRank', 'zoomSpider', 'xpymep1.exe', 'zauba.io', 'zgrab'
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Block access from bad hosts.
        user_agent = request.headers.get('User-Agent', '')
        if any(x in user_agent for x in self.BLOCKED_USER_AGENTS):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('Forbidden user agent')

        return self.get_response(request)
