import sys, os, urllib2, time, calendar, contextlib
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

	print '\n\nSaving album %s (%s) -> %s' % (title, summary, filepath)
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
	for photo in photos_coll.findall('{http://www.w3.org/2005/Atom}entry'):
		title = fotki.atom(photo, '{http://www.w3.org/2005/Atom}title')
		if title is None: title = photo.find('{http://www.w3.org/2005/Atom}id').text
		fullsize = photo.find('{yandex:fotki}img[@size="orig"]').get('href')
		created = fotki.atom(photo, '{yandex:fotki}created')
		if created is None:
			created = photo.find('{http://www.w3.org/2005/Atom}published').text
		summary = fotki.atom(photo, '{http://www.w3.org/2005/Atom}summary')
		tags = [c.get('term') for c in photo.findall('{http://www.w3.org/2005/Atom}category'
			'[@scheme="http://api-fotki.yandex.ru/api/users/nicht-verstehen/tags/"]')]
		timestamp = calendar.timegm(time.strptime(created, "%Y-%m-%dT%H:%M:%SZ"))

		filename = title + '.jpg' if not title.lower().endswith('.jpg') else title
		filepath = os.path.join(dest, filename)

		print 'Saving "%s" (%s - %s): %s\n%s -> %s' % (title, created, ', '.join(tags), summary, fullsize, filepath)
		if summary is not None or tags:
			with open(os.path.join(dest, INDEXFILE), 'a') as index_file:
				d = "%s (%s)" % (title, ', '.join(tags)) + (': %s' % summary if summary is not None else '')
				index_file.write('\n' + d.encode('utf-8') + '\n')

		if os.path.isfile(filepath):
			print "Skipping as it exists"
		else:
			with contextlib.closing(urllib2.urlopen(fullsize)) as jpgurl:
				jpg = jpgurl.read()
			with open(filepath, 'w') as f:
				f.write(jpg)
		os.utime(filepath, (timestamp, timestamp))

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
