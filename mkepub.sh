
PWD=$(pwd)
ROOT=${PWD}/dat
EPUB=${PWD}/epub_tmp
TARGET=${PWD}/epub

gTITLE="WSJImgNews"
gAUTHOR="Vincent"

function mkinfo()
{
	echo "# mkinfo: $1"
	
	cd ${ROOT}/$1

	i=3
	for f in $(ls *.html -r -X); do
		# echo "${f}"
		# echo "${i}"
		echo "<navPoint class=\"node\" id=\"node_${i}\" playOrder=\"${i}\"><navLabel><text>${f}</text></navLabel><content src=\"${f}\"/></navPoint>" >> ${EPUB}/fb1.txt
		echo "<item href=\"${f}\" id=\"${f}\" media-type=\"application/xhtml+xml\"/>" >> ${EPUB}/fb2.txt
		echo "<itemref idref=\"${f}\" linear=\"yes\"/>" >> ${EPUB}/fb3.txt
		echo "<reference href=\"${f}\" title=\"${f}\" type=\"text\"/>" >> ${EPUB}/fb4.txt
		i=$(($i+1))
	done
}

function mkops()
{
	echo "# mkops: $1"
	
	cd ${EPUB}
	
	iTITLE="${gTITLE}-$1"
	iDATE="$1"
	
	iNAVPOINT=$(cat ${EPUB}/fb1.txt)
	iITEM=$(cat ${EPUB}/fb2.txt)
	iITEMREF=$(cat ${EPUB}/fb3.txt)
	iREFERENCE=$(cat ${EPUB}/fb4.txt)

	mkdir -p ${EPUB}/OPS
	rm -rf ${EPUB}/OPS/*

	cp -a ${ROOT}/$1/* ${EPUB}/OPS/
	rm ${EPUB}/fb?.txt
	rm -rf ${EPUB}/OPS/js
	rm -f ${EPUB}/OPS/img/icons.*
	rm -f ${EPUB}/OPS/css/swipebox.min.css
	rm -f ${EPUB}/OPS/css/jquery.mobile-1.4.5.min.css

	TITLE=`cat<<!
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">
<head>
<meta name="generator" content="html tidy, see www.w3.org" />
<meta http-equiv="content-type" content="application/xhtml+xml; charset=utf-8" />
<title>COVER</title>
<link rel="stylesheet" href="css/wsj.img.css" type="text/css" />
</head>
<body>
<p align="center"><img src="img/cover.jpg" class="book_cover"/></p>
<h1 class="book_title">${iTITLE}</h1><h3 class="book_author">${gAUTHOR}</h3>
</body>
</html>
!`

	ABOUT=`cat<<!
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">
<head>
<meta name="generator" content="html tidy, see www.w3.org" />
<meta http-equiv="content-type" content="application/xhtml+xml; charset=utf-8" />
<title>ABOUT</title>
<link rel="stylesheet" href="css/wsj.img.css" type="text/css" />
</head>
<body>
<div class="body">
<h2>ABOUT</h2>
<p>none</p>
</div>
</body>
</html>
!`

	FB_OPF=`cat<<!
<?xml version="1.0" encoding="utf-8"?>
<package unique-identifier="PrimaryID" version="2.0" xmlns="http://www.idpf.org/2007/opf">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
<dc:title><![CDATA[${iTITLE}]]></dc:title>
<dc:description/>
<dc:creator opf:file-as="${gAUTHOR}" opf:role="aut">
<![CDATA[${gAUTHOR}]]></dc:creator>
<dc:identifier id="dcidid" opf:scheme="URI">
<![CDATA[2d39ea16-a153-43ab-bfec-2ecffa504e1b]]></dc:identifier>
<dc:language>
<![CDATA[zh]]></dc:language>
<dc:publisher/>
<dc:coverage/>
<dc:source/>
<dc:date opf:event="original-publication">
<![CDATA[${iDATE}]]></dc:date>
<dc:date opf:event="ops-publication">
<![CDATA[${iDATE}]]></dc:date>
<dc:rights>
<![CDATA[Copyrigth (c) All right reserved]]></dc:rights>
<dc:subject/>
</metadata>
<manifest>
<!-- Content Documents -->
<!-- CSS Style Sheets -->
<item href="css/wsj.img.css" id="main-css" media-type="text/css"/>
<!-- Images -->
<item href="img/cover.jpg" id="cover" media-type="image/jpg"/>
<!-- NCX -->
<item href="fb.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>
<item href="title.xml" id="title" media-type="application/xhtml+xml"/>
<item href="about.xml" id="about" media-type="application/xhtml+xml"/>
<!--item id='1.html' href='1.html' media-type='application/xhtml+xml'/-->
${iITEM}
</manifest>
<spine toc="ncx">
<itemref idref="title" linear="yes"/>
<itemref idref="about" linear="yes"/>
<!--itemref idref='1.html' linear='yes'/-->
${iITEMREF}
</spine>
<guide>
<reference href="title.xml" title="title" type="text"/>
<reference href="about.xml" title="about" type="text"/>
${iREFERENCE}
</guide>
</package>
!`

	FB_NCX=`cat<<!
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ncx
PUBLIC '-//NISO//DTD ncx 2005-1//EN'
'http://www.daisy.org/z3986/2005/ncx-2005-1.dtd'>
<ncx version="2005-1" xml:lang="en" xmlns="http://www.daisy.org/z3986/2005/ncx/">
<head>
<!-- The following four metadata items are required for all NCX documents, including those conforming to the relaxed constraints of OPS 2.0 -->
<meta content="uid" name="dtb:uid"/>
<meta content="2" name="dtb:depth"/>
<meta content="0" name="dtb:totalPageCount"/>
<meta content="0" name="dtb:maxPageNumber"/>
</head>
<docTitle>
<text>${iTITLE}</text>
</docTitle>
<docAuthor>
<text>${gAUTHOR}</text>
</docAuthor>
<navMap>
<navPoint class="pTitle" id="level1-title" playOrder="1">
<navLabel>
<text>COVER</text>
</navLabel>
<content src="title.xml"/>
</navPoint>
<navPoint class="pAbout" id="level1-about" playOrder="2">
<navLabel>
<text>ABOUT</text>
</navLabel>
<content src="about.xml"/>
</navPoint>
<!--content-->
<!--navPoint id="node_3" class="node" playOrder="3"><navLabel><text>Content</text></navLabel><content src="1.html"/></navPoint-->
${iNAVPOINT}
</navMap>
</ncx>
!`

	echo "${TITLE}" > ${EPUB}/OPS/title.xml
	echo "${ABOUT}" > ${EPUB}/OPS/about.xml
	echo "${FB_OPF}" > ${EPUB}/OPS/fb.opf
	echo "${FB_NCX}" > ${EPUB}/OPS/fb.ncx
}

function mkepub()
{
	echo "# mkepub: $1"
	
	cd ${EPUB}
	
	iTITLE="${gTITLE}-$1"
	
	zip -r -q ${iTITLE}.epub *
	
	mv ${iTITLE}.epub ${TARGET}
}

function epub()
{
	mkinfo $1
	mkops $1
	mkepub $1
}

function gen_default_page()
{
	DFT=${PWD}/"default.html"

	HEADER=`cat<<!
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">
<head>
<meta http-equiv="content-type" content="application/xhtml+xml; charset=utf-8" />
<title>wsj.img</title>
<link rel="stylesheet" href="base/css/jquery.mobile-1.4.5.min.css">
<script src="base/js/jquery-2.1.3.min.js"></script>
<script src="base/js/jquery.mobile-1.4.5.min.js"></script>
</head>
<body>
<ul data-role="listview">
!`

	FOODER=`cat<<!
</ul>
</body>
</html>
!`
	echo ${HEADER} > ${DFT}
	
	for d in $(ls -r -X ${ROOT}); do
		# echo ${d} 
		echo "<li data-role="list-divider">${d}</li>" >> ${DFT}
		cd ${ROOT}/${d}
		for f in $(ls *.html); do
			# echo ${f}
			echo "<li><a href="dat/${d}/${f}" target=\"blank\">${f}</a></li>" >> ${DFT}
		done
		cd ${PWD}
	done
	
	echo ${FOODER} >> ${DFT}
}

case $1 in
	all)
		for d in $(ls ${ROOT}); do
			echo ${d}
			epub ${d}
		done
		;;
	dft)
		gen_default_page
		;;
	*)
		echo $1
		epub $1
		;;
esac
