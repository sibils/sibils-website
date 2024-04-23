# How to incorporate your collection in SIBiLS

SIBiLS has its own FTP server where interested publishers can deposit / update / delete articles. The articles are then integrated into BiodiversityPMC. If additional files are joined, they will be integrated into the SuppData collection.

Here is how to proceed for incorporating your collection in SIBiLS:

* Request a login/pwd to julien.gobeill[at]hesge.ch for SIBiLS FTP
* With your login, you can connect to SIBiLS FTP, and you have a directory at your disposal.
* Upload your articles to FTP :
	* For articles, the recommended format is JATS XML, but if you don't have one you can also upload PDFs or any other format.
	* If you have additional files attached to the articles, the recommended format is to place each article and its additional files in a tar.gz archive.
	* You can add, update, or delete any articles.
	* SIBiLS will monitor FTP actions to update the collection daily
	* You are free to create directories to structure repositories (to avoid having too many files in the same directory).