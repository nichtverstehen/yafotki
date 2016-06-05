import urllib, urllib2, re
import xml.etree.ElementTree as ET
import yamrsa

def key():
	keydoc = urllib2.urlopen('http://auth.mobile.yandex.ru/yamrsa/key/').read()
	keym = re.match(r'<\?xml version="1.0"\?>\s*<response>\s*<key>\s*([\w#]+)\s*</key>\s*'
		'<request_id>\s*([\w]+)\s*</request_id>\s*</response>', keydoc)
	if keym is None: raise ValueError('Unexpected response from server: %s' % keydoc)
	public_key, request_id = keym.group(1), keym.group(2)
	return public_key, request_id

def authenticate(username, password):
	public_key, request_id = key()
	creds = yamrsa.encrypt(public_key, '<credentials login="%s" password="%s"/>' % (username, password))
	tokendoc = urllib2.urlopen('http://auth.mobile.yandex.ru/yamrsa/token/',
		data=urllib.urlencode([('request_id', request_id), ('credentials', creds)])).read()
	keym = re.match(r'<\?xml version="1.0"\?>\s*<response>\s*<token>\s*(\w+)\s*</token>\s*</response>', tokendoc)
	if keym is None: raise ValueError('Unexpected response from server: %s' % tokendoc)
	token = keym.group(1)
	return 'FimpToken realm="fotki.yandex.ru", token="%s"' % token

def servicedoc(username):
	servicedoc = urllib2.urlopen('http://api-fotki.yandex.ru/api/users/%s/' % username).read()
	servicexml = ET.fromstring(servicedoc)
	return dict(
		(coll.get('id'), coll.get('href'))
		for coll in servicexml.findall('.//{http://www.w3.org/2007/app}collection'))

def make_url(base, order=None, offset=None, limit=None):
	url = base
	if order is not None: url += order
	if offset is not None: url += ';%s' % offset
	if order is None and offset is None: url += '/'
	if limit is not None: url += '?limit=%d' % limit
	return url

def collection(auth, url):
	albumsdoc = urllib2.urlopen(urllib2.Request(url, headers={'Authorization': auth})).read()
	return ET.fromstring(albumsdoc)

def all(auth, url):
	next = url
	merged = ET.Element('feed')
	while next != None:
		coll = collection(auth, next)
		for n, v in coll.items():
			merged.set(n, v)
		merged.extend(coll)

		next = None
		next_el = coll.find('{http://www.w3.org/2005/Atom}link[@rel="next"]')
		if next_el is not None:
			next = next_el.get('href')
	return merged

def atom(entry, tag, attr=None, **kwargs):
	q = tag + ''.join(['[@%s="%s"]' % z for z in kwargs.items()])
	e = entry.find(q)
	if e is None:
		return None
	if attr is None:
		return e.text
	return e.get(attr)