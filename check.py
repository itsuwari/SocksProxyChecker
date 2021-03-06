import requests, sys, time, os


check_url = 'https://gitlab.com/itsuwari/check_txt/raw/master/Works.txt'
#check_url = 'https://raw.githubusercontent.com/itsuwari/SocksProxyChecker/master/am_I_working.txt'
#check_url = 'http://developer.akamai.com/assets/themes/bootstrap-3/bootstrap/css/bootstrap.min.css'

class ProgressBar:
    def __init__(self, count=0, total=0, width=50):
        self.count = count
        self.total = total
        self.width = width
    def move(self, plus):
        self.count += plus
    def log(self, s):
        sys.stdout.write(' ' * (self.width + 9) + '\r')
        sys.stdout.flush()
        print(s)
        progress = int(self.width * self.count / self.total)
        sys.stdout.write('{0:3}/{1:3}: '.format(self.count, self.total))
        sys.stdout.write('#' * progress + '-' * (self.width - progress) + '\r')
        if progress == self.width:
             sys.stdout.write('\n')
        sys.stdout.flush()



def test_proxy(proxies, country_filter=None, isp_filter=None, speed_filter=2.0, timeout=15, speed_timeout=40):
    bar = ProgressBar(total=len(proxies))
    working = []
    for proxy in proxies:
        socks = {
                'http': 'socks5://%s' % proxy,
                'https': 'socks5://%s' % proxy
        }
        ip_info = requests.get('http://ip-api.com/json/%s' % proxy.split(':')[0], timeout=5).json()
        country_code = ip_info['countryCode']
        isp = ip_info['isp']
        bar.log('Country: %s ISP: %s' % (country_code, isp))
        time.sleep(1)
        try:
            if not country_filter is None:
                if not country_code in country_filter:
                    continue
            if not isp_filter is None:
                if not isp in isp_filter:
                    continue
            print(os.system("ping -c 1 " + str(proxy.split(':')[0])))
            if requests.get(check_url, timeout=timeout, proxies=socks).text == 'Works':
                working.append(proxy)
                bar.log('%s is working!' % proxy)
                speed = speedtest([proxy], timeout=speed_timeout)
                if speed <= speed_filter:
                    bar.log('Low speed')
                    bar.move(1)
                    continue
                open(out_file, 'a').write('%s\n' % proxy)
                bar.move(1)
        except Exception:
            bar.log('Oops, not working')
            bar.move(1)

    return working

def speedtest(proxies, file='http://repos.lax-noc.com/speedtests/10mb.bin', timeout=10):
    bar = ProgressBar(total=len(proxies))
    for proxy in proxies:
        socks = {
                'http': 'socks5://%s' % proxy,
                'https': 'socks5://%s' % proxy
        }
        try:
            seconds = requests.get(file, timeout=timeout, proxies=socks).elapsed.total_seconds()
            bar.log('%s mb/s' % str(10/seconds))
            bar.move(1)
            return 10/seconds
        except Exception:
            bar.log('Oops, timeout')
            bar.move(1)
            return -1


asia = ['TW', 'CN', 'KR', 'JP', 'HK']


in_file = 'asia.txt'
out_file = 'asia_out.txt'

with open(in_file) as f:
    proxies = f.readlines()
proxies = [x.strip() for x in proxies]

test_proxy(proxies, asia, speed_filter=0.2)

in_file = 'us.txt'
out_file = 'us_out.txt'

with open(in_file) as f:
    proxies = f.readlines()
proxies = [x.strip() for x in proxies]

us_isp = ['Google', 'Apple', 'Akamai Technologies', 'Amazon Technologies', 'Microsoft Corp']
test_proxy(proxies, country_filter=['US'], speed_filter=10, speed_timeout=2)
