import sys, os, urllib2, time, calendar, contextlib, itertools
import fotki

INDEXFILE = 'index.txt'

def save_subalbums(auth, albums, id, dest):
	for album in albums.get(id, ''):
		aid = album.find('{http://www.w3.org/2005/Atom}link[@rel="self"]').get('href')
		p = save_album_meta(album, dest)
		save_photos(auth, album, p)
		save_subalbums(auth, albums, aid, p)

def save_album_meta(album, dest):
	title = fotki.atom(album, '{http://www.w3.org/2005/Atom}title')
	if title is None: title = album.find('{http://www.w3.org/2005/Atom}id').text
	summary = fotki.atom(album, '{http://www.w3.org/2005/Atom}summary')
	filepath = os.path.join(dest, title)

	print ('\nSaving album %s (%s) -> %s' % (title, summary, filepath)).encode('utf-8')
	if not os.path.isdir(filepath): os.mkdir(filepath)
	indexpath = os.path.join(filepath, INDEXFILE)
	if summary is not None:
		with open(indexpath, 'w') as f: f.write(summary.encode('utf-8') + '\n')
	elif os.path.isfile(indexpath):
		os.unlink(indexpath)

	return filepath

def save_photos(auth, album, dest):
	photos_url = album.find('{http://www.w3.org/2005/Atom}link[@rel="photos"]').get('href')
	photos_coll = fotki.all(auth, photos_url)
	saved = set()
	for photo in photos_coll.findall('{http://www.w3.org/2005/Atom}entry'):
		title = fotki.atom(photo, '{http://www.w3.org/2005/Atom}title')
		if title is None: title = photo.find('{http://www.w3.org/2005/Atom}id').text
		original = photo.find('{yandex:fotki}img[@size="orig"]').get('href')
		originalsize = fotki.atom(photo, '{yandex:fotki}img', size='orig', attr='bytesize')
		created = fotki.atom(photo, '{yandex:fotki}created')
		if created is None:
			created = photo.find('{http://www.w3.org/2005/Atom}published').text
		summary = fotki.atom(photo, '{http://www.w3.org/2005/Atom}summary')
		tags = [c.get('term') for c in photo.findall('{http://www.w3.org/2005/Atom}category'
			'[@scheme="http://api-fotki.yandex.ru/api/users/nicht-verstehen/tags/"]')]
		timestamp = calendar.timegm(time.strptime(created, "%Y-%m-%dT%H:%M:%SZ"))

		for i in itertools.count():
			name, ext = os.path.splitext(title)
			unique_title =  name + (' (%d)' % i if i != 0 else '') + ext
			if unique_title not in saved: break
		saved.add(unique_title)

		filename = unique_title + '.jpg' if not unique_title.lower().endswith('.jpg') else unique_title
		filepath = os.path.join(dest, filename)

		print ('Saving "%s" (%s - %s - %s): ' % (unique_title, created, ', '.join(tags), summary)).encode('utf-8'),
		if summary is not None or tags:
			with open(os.path.join(dest, INDEXFILE), 'a') as index_file:
				d = "%s (%s)" % (unique_title, ', '.join(tags)) + (': %s' % summary if summary is not None else '')
				index_file.write('\n' + d.encode('utf-8') + '\n')

		if os.path.isfile(filepath):
			if originalsize is not None and os.path.getsize(filepath) != int(originalsize):
				print "Already exists but OMG it is different"
			else:
				print "Already exists"
		else:
			jpg = None
			try:
				with contextlib.closing(urllib2.urlopen(original)) as jpgurl:
					jpg = jpgurl.read()
			except urllib2.URLError as e:
				print "Error downloading: %s" % e.reason
			if jpg is not None:
				with open(filepath, 'w') as f:
					f.write(jpg)
				os.utime(filepath, (timestamp, timestamp))
				print "Done"

def prepare_albums(albums_coll):
	albums = {}
	for album in albums_coll.findall('{http://www.w3.org/2005/Atom}entry'):
		parent = fotki.atom(album, '{http://www.w3.org/2005/Atom}link', rel='album', attr='href')
		albums.setdefault(parent, []).append(album)
	return albums

if __name__ == '__main__':
	if len(sys.argv) != 4:
		print "Usage: %s <username> <password> <destination>" % sys.argv[0]
		sys.exit(1)

	username, password, dest = sys.argv[1], sys.argv[2], sys.argv[3]
	auth = fotki.authenticate(username, password)
	albums_coll = fotki.all(auth, "http://api-fotki.yandex.ru/api/users/nicht-verstehen/albums/")
	albums = prepare_albums(albums_coll)
	save_subalbums(auth, albums, None, dest)
