Yandex.Fotki dumper downloads all photos from Yandex.Fotki (fotki.yandex.ru).

* Uses "Fimp" authentication with username and password.
* Replicates the album struture as directory structure.
* Sets modification time to creation time according to Yandex.
* Saves album and photo description along with the tags to `index.txt` files.
* Handles photos with duplicate names gracefully (keeping all copies).
* Single-threaded (i.e. takes a long time to download everything).

## Usage

    python dump.py <username> <password> <destination>

## Notes

* `yamrsa.py` contains an implementation of Yandex RSA algorithm stolen from [Habr](https://habrahabr.ru/post/83710/).
* `fotki.py` contains a simple python wrapper for Fotki.API.

## License
The MIT License (MIT)
Copyright (c) 2016 Kirill Nikolaev

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.