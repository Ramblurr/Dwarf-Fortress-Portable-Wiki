#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,os.path,UserDict,SimpleHTTPServer,SocketServer,socket,cgi,urlparse,urllib2,webbrowser,tarfile,bz2,sys,traceback,re,mimetypes
VERSION='0.0.1 alpha' # 2012-06-15
'''
DF Portable Wiki

This program aims at providing an offline, portable version of Dwarf Fortress wiki.

It is basically a local webserver capable of browsing the official DF Wiki export (dump.xml).
It contains is a crude Wikitext renderer, hacked with some DF Wiki specific features.
When I say "crude", I *mean* it. It *does* not support the whole Wikitext syntax,
and only a small subset of DF Wiki teamplates.

Thus a lots of pages will *not* render correctly (you will see a lot of {{...}}) but at last
you have the ability to browse the majority of information offline.

THIS IS BIG, UGLY, QUICKLY-HACKED CODE to fit my needs.
I provide not support **AT ALL**. You are on your own.

Author: sebsauvage at sebsauvage dot net

Instructions:
  - download Dwarf Fortress XML dump from http://dwarffortresswiki.org/images/dump.xml.bz2
  - uncompress (under Windows, use 7-Zip.org)
  - put dump.xml in the same directory as this program
  - run this program
  - enjoy the local version of DF Wiki on http://localhost:8025/

Q&A:

Q: Why didn't you use a local installation of MediaWiki ?
A: Because it's fucking HUGE. With thousands of files.

Q: Why didn't you use the official mwlib MediaWiki reading libary ?
A: Because it requires a fucking C/C++ Compiler. I want a pure-python version.

Q: Why didn't you use lxml to read xml data ? It's fast.
A: And it requires a fucking C/C++ compiler to install.

Q: Why didn't you use BeautifulSoup to read xml data ?
A: Because it chocked on DF Wiki XML export.

Q: Why...
A: Oh leave me alone.

================================================================================
TODO:
- Make media download system available through user interface
  (on demande (per page viewed) or all (option to automatically download all media)
- support more templates (see http://dwarffortresswiki.org/index.php/Template)

    {{DFtext|Save Game}}
    {{DFtext|Short|3:1}}
    http://localhost:8025/page?title=Adventurer%20mode

    {{Tile|■|7:0:1}} or {{Tile|■|6:0:1}}
    http://localhost:8025/page?title=Adventurer%20mode

    {{TipBox2|titlebg=#0a0|For your first game...|Generate a world using {{DFtext|Create New World!}} with:... }}
    {{TipBox2|titlebg=#0a0|float=right|Key Reference|Most of the key commands you will need are noted in the text, but refer to the quick reference guide if you need to look up the key for a particular action.}}
    http://localhost:8025/page?title=cv:Adventure%20mode%20quick%20start

    etc.

'''
socket.setdefaulttimeout(30)

PORT = 8025
HOSTNAME = socket.gethostname()
MENU = u'''
<div id="menu"><b>Dwarf Fortress portable wiki </b><small>%s</small> - <a href="/">Main page</a> - <a href="pageindex">Pages index</a></div>
'''%VERSION
CSS = u'''
<style>
body,html { font-family:sans-serif; font-size:10pt; margin:0px; }
table { border-collapse:collapse; }
th, td { border:1px solid black; font-size:10pt; padding:3px;}
th { background-color:#ddd; }
h1 { font-size:20pt; font-size: 170%; border-bottom:1px solid #bbb; padding-left:10px; margin:0px; }
h2 { font-size:16pt; font-size: 150%; border-bottom:1px solid #bbb; padding-left:10px; margin:0px 0px 0px 0px; }
h3 { font-size:14pt; font-size: 140%; border-bottom:1px solid #bbb; padding-left:10px;margin:0px 0px 0px 20px; }
h4 { font-size:12pt; font-size: 130%; border-bottom:1px solid #bbb; padding-left:10px;margin:0px 0px 0px 40px; }
h5 { font-size:10pt; font-size: 120%; border-bottom:1px solid #bbb; padding-left:10px;margin:0px 0px 0px 60px; }
h6 { font-size:9pt;  font-size: 110%; border-bottom:1px solid #bbb; padding-left:10px;margin:0px 0px 0px 80px; }
#pagetitle { font-size:26pt; font-weight:bold; margin-bottom:20px; }
ul { margin:0px; list-style-position: outside;}
kbd {
  border-style:outset;
  border-width:1px;
  padding:0px 3px;
  background-color:rgb(230,230,230);
  font-family:Tahoma,Verdana,Arial,Helvetica,sans-serif;
  font-size:9pt;
  border-radius:0.3em;
  }
pre
{
background-color: #F9F9F9;
border: 1px dashed #2F6FAB;
color: #000000;
line-height: 1.1em;
padding: 1em;
}
.nowiki
{
font-family: monospace;
white-space: pre;
line-height: 55%;
}
#menu {
width: 100%;
background-color:#eee;
position: fixed;
top:0px;
border-bottom:2px solid black;
padding:3px 5px 3px 5px;
}
#content {
padding: 20px 10px 0px 10px;
}
.externalLink {
color: #15984D;
}

.workshop {
width:250px;
float:right;
border:1px solid black;
background-color:#fff;
margin:5px 0px 5px 5px;
}
.sectionName {
border-bottom: 1px solid black;
background-color:#aaa;
font-weight:bold;
padding:2px 5px 2px 5px;
}
.sectionData {
border-bottom: 1px solid black;
padding:2px 5px 2px 5px;
}
.TipBox2 {
width:35%;
border: 2px solid black;
background-color:#fff;
margin:10px;
clear: right;
}
.TipBox2_title {
text-align:center;
padding:5px;
border-bottom: 1px solid black;
font-size:120%;
color:#ffffff;
font-weight:bold;
}
.TipBox2_content {
padding:5px;
text-align:left;
}
.DFtext {
background-color:#000;
color:#aaa;
font-family: monospace;
font-weight:bold;
}
.Tile {
background-color:#000;
color:#aaa;
font-family: monospace;
font-weight:bold;
padding: 3px;
}
.imageCaption
{
font-size:8pt;
font-weight:normal;
}
div#pageindex {
    column-width: 200px;
    column-gap: 20px;
    -moz-column-width: 200px;
    -moz-column-gap: 20px;
    -webkit-column-width: 200px;
    -webkit-column-gap: 20px;
}
.mainmenubox {
    column-count: 2;
    column-gap: 20px;
    -moz-column-count: 2;
    -moz-column-gap: 20px;
    -webkit-column-count: 2;
    -webkit-column-gap: 20px;
    margin:20px;
    padding:10px;
    border:1px solid black;
}
#online_article {
margin: 5px 5px 0px 5px;
font-size:8pt;
float:right;
}
#online_article a {
margin: 20px 5px 0px 5px;
font-size:8pt;
float:right;
color: #15984D;
}
</style>


'''




def log(message):
    sys.stderr.write((u"###"+message+u"\n").encode('utf-8'))

class tableBuilder:
    ''' A simple HTML table builder.
        Understand MediaWiki cell attributes (cf http://meta.wikimedia.org/wiki/Help:Table)
        Example:
            t = tableBuilder()
            t.addCell('hello'); t.addCell('align="right"|world'); t.endRow()
            t.addCell("I'm"); t.addCell('fin'); t.endRow()
            print t.endTable()
          which will give:
          <table><tr><td>hello</td><td align="right">world</td></tr>
          <tr><td>I'm</td><td>fin</td></tr></table>
    '''
    def __init__(self):
        self.cells = []
        self.rows = []
        self.currentCell,self.currentCellStyle=('','')

    def addCell(self,content):
        self._endCell()
        if '|' in content:
            self.currentCellStyle,self.currentCell = content.split('|')[:2]
            self.currentCellStyle = self.currentCellStyle.replace('&quot;','"')
        else:
            self.currentCell = content

    def appendToLastCell(self,content):
        self.currentCell += content

    def addHeader(self,content):
        if '|' in content:
            attributes,data = content.split('|')[:2]
            self.cells.append('<th %s>%s</th>'%(attributes.replace('&quot;','"'),data))
        else:
            self.cells.append('<th>%s</th>'%content)

    def _endCell(self):
        if self.currentCell=='': return
        if self.currentCellStyle!='':
            self.cells.append('<td %s>%s</td>'%(self.currentCellStyle,self.currentCell))
        else:
            self.cells.append('<td>%s</td>'%self.currentCell)
        self.currentCell,self.currentCellStyle=('','')

    def endRow(self):
        self._endCell()
        if len(self.cells)>0:
            self.rows.append("".join(self.cells))
        self.cells = []

    def endTable(self):
        self.endRow()
        if len(self.rows)>0:
            output = "<table>" + "".join(["<tr>%s</tr>"%a for a in self.rows]) + "</table>"
            self.rows = []
            return output
        else:
            return ''

    def isEmpty(self):
        return len(self.rows)==0 and len(self.cells)==0

class listBuilder:
    ''' This class ban build HTML output from MediaWiki lists.
        Just feed it with all line of a mediaWiki article.
        Supported unordered (*) and ordered (#) lists.
        b = listBuilder()
        b.addLine('*item1')
        b.addLine('**item2')
        print b.htmlOutput()
        <ul>
        <li>item1</li>
        <ul>
        <li>item2</li>
        </ul>
        </ul>
    '''
    def __init__(self):
        self.nesting = [] # Stacks the opened lists (nesting)
        self.output = []
    def addLine(self,content):
        ''' Add an item to the list. eg. "**#hello"
            cf. http://meta.wikimedia.org/wiki/Help:List
        '''
        (level,type,data) = self._position(content)
        while (len(self.nesting)<level): # Open new lists
            self.nesting.append((level,type))
            self.output.append('<%s>'%type)
        while (len(self.nesting)>level): # Close lists
            self.output.append('</%s>'%self.nesting.pop()[1])
        if (len(self.nesting)>0 and type!=self.nesting[-1][1]): # If list of same level but different type
            self.output.append('</%s>'%self.nesting.pop()[1]) # Close previous list
            self.nesting.append((level,type))  # Open new list.
            self.output.append('<%s>'%type)
        if level>0:
            if type=='dl':
                self.output.append('<dd>%s</dd>'%data)
            else:
                self.output.append('<li>%s</li>'%data)
        else:
            self.output.append(data)

    def htmlOutput(self):
        return '\n'.join(self.output)

    def _position(self,line):
        ''' Return the nesting level, the type of list and data.
            eg. "**#AAA" --> (3,'ol','AAA')      (because # is an ordered list)
                "**BBBBBB" --> (2,'ul','BBBBBB')   (because * is an unordered list)
                "" --> (0,'','')
        '''
        match = re.match(r'([\*\#\:]+).*?',line)
        if not match: return (0,'',line)
        s = match.group(1)
        type = 'ul'
        if s[-1]=='#': type='ol'
        if s[-1]==':': type='dl'
        return (len(s),type,line[len(s):])


class MediaWikiFormater:
    ''' This class is capable of converting MediaWiki markup into HTML.
        It only supports a small subset of MediaWiki markup, and some DFWiki specific features.
        Example: f = MediaWikiFormater()
                 print f.toHtml(a_random_mediawiki_markup)
    '''
    def toHtml(self,markup):
        if not markup: return ''
        markup = markup.replace('&lt;','<').replace('&gt;','>').replace('&quot;','"')
        markup = markup.replace('<nowiki>','<div class="nowiki">').replace('</nowiki>','</div>') # eg "Exploratory mining" page
        markup = re.sub(re.compile(re.escape('{{verify}}'), re.IGNORECASE),'',markup) # Case insensitive replace
        markup = re.sub(re.compile(re.escape('{{av}}'), re.IGNORECASE),'',markup) # Case insensitive replace
        D_for_dwarf='''<center><div style="width:70%; background-color:#f0f0f0; border: 2px solid #aaa;padding:5px;">This article or section has been rated <b>D for Dwarf</b>.  It may include witty humour, not-so-witty humour, bad humour, in-jokes related to the game, and references to the <a href="http://www.bay12games.com/forum/index.php" class="external text" rel="nofollow">Bay12 forums</a>.  Don't believe everything you read, and if you miss some of the references, don't worry.</div></center>'''
        markup = markup.replace('{{D for Dwarf}}',D_for_dwarf)
        markup = self._convertTitles(markup)
        markup = self._convertNewlines(markup)
        markup = self._convertKeys(markup)
        markup = self._convertImages(markup)
        markup = self._convertLists(markup)
        markup = self._convertLinks(markup)
        markup = self._convertExternalLinks(markup)
        markup = self._convertTables(markup)
        markup = self._convertBold(markup)
        markup = self._convertItalic(markup)
        markup = self._convertPreformated(markup)
        markup = self._removeTemplates(markup)
        #markup = self._convertWorkshops(markup)
        # FIXME: support for {{jobs...}}
        # FIXME: support {{tile|•|grey|#8f8}} (eg: http://localhost:8025/page?title=Water )
        # FIXME: support {{diagram...}}  (eg.http://localhost:8025/page?title=Irrigation )
        markup = self._convertTipBox2(markup)
        markup = self._convertDFText(markup)
        markup = self._convertTile(markup)

        return markup

    def _extractTemplate(self,tag,markup):
        ''' Extracts all {{tag...}} from MediaWiki markup.
            This function supports nested templates.
            (but not nested templates of the SAME type.)
            Example:
                >>> data = 'uuuu{{TipBox2aaa{{bb{{cc}}bbb}}kkk}}ddddd{{TipBox2eeee{{ffff}}ggggg}}hhhh'
                >>> print repr(extractTags('TipBox2',data))
                ['uuuu', 'aaa{{bb{{cc}}bbb}}kkk', 'ddddd', 'eeee{{ffff}}ggggg', 'hhhh']
                          ^template content                 ^template content
                Even items of NOT template content. Odd items ARE template content.
        '''
        splitted = markup.split('{{'+tag)
        items = [splitted[0]]

        for item in splitted[1:]:
            opened = 1  # Number of tags opened
            seekpos = 0   # current seek pos
            while opened>0:
                n_open = item.find('{{',seekpos)
                n_close = item.find('}}',seekpos)
                next = seekpos
                if n_open==-1 and n_close==-1:
                    opened = 0
                    break
                else:
                    if n_open==-1:
                        next = n_close
                    elif n_close==-1 :
                        next = n_open
                    else:
                        next = min(n_open,n_close)
                    if next == n_close:
                        opened -= 1
                    elif next == n_open:
                        opened += 1
                seekpos = next + 2
            items.append(item[:seekpos-2])
            items.append(item[seekpos:])

        return items

    def _unPipe(self,data):
        ''' Unpipes data taking {{}} and [[]] in consideration.
            >>> print unPipe('aaa|bbbb{{key|c}}dddd|ee{{TTTT{UUU}{{VVV}}}}ee|ooo')
            ['aaa', 'bbbb{{key|c}}dddd', 'ee{{TTTT{UUU}{{VVV}}}}ee', 'ooo']
        '''
        output = []
        currentString = ''
        inside = 0
        curlBracketLeftCounter = 0
        curlBracketRightCounter = 0
        bracketLeftCounter = 0
        bracketRightCounter = 0
        for c in data:
            if c=='{':
                curlBracketRightCounter = 0
                curlBracketLeftCounter += 1
                if curlBracketLeftCounter==2:
                    inside += 1
                    curlBracketLeftCounter = 0
            elif c=='}':
                curlBracketLeftCounter = 0
                curlBracketRightCounter += 1
                if curlBracketRightCounter==2:
                    inside -= 1
                    curlBracketRightCounter = 0
            elif c=='[':
                bracketRightCounter = 0
                bracketLeftCounter += 1
                if bracketLeftCounter==2:
                    inside += 1
                    bracketLeftCounter = 0
            elif c==']':
                bracketLeftCounter = 0
                bracketRightCounter += 1
                if bracketRightCounter==2:
                    inside -= 1
                    bracketRightCounter = 0
            elif c=='|' and inside==0:
                output.append(currentString)
                currentString = ''
                c=''
            currentString += c
        if currentString!='':
            output.append(currentString)
        return output

    def _convertLinks(self,markup):
        ''' Markup such as: [[Butcher's shop|butchering]] or [[Meat]] '''
        def rep(m):
            s = m.group(1)
            if s.startswith('Image:'): return m.group(0) # We do not convert image links here.
            if s.startswith('File:'): return m.group(0) # We do not convert files links here.
            if s.count('|')>2: return '[['+m.group(0)+']]' # Leave File: (and similar links) untouched.
            pagetitle,text=s,s
            if '|' in s: pagetitle,text=s.split('|')[0],s.split('|')[1]
            # http://localhost:8025/page?title=Workshop
            if pagetitle.startswith('#'): return '<a href="%s">%s</a>' % (pagetitle,text)
            return '<a href="?title=%s">%s</a>' % (pagetitle,text)
        m = re.sub(r'\[\[(.+?)\]\]', rep ,markup)
        return m

    def _convertImages(self,markup):
        ''' Markup such as: [[File:...]] or [[Image:...]] '''
        def rep(m):
            s = m.group(1)
            if not (s.startswith('File:') or s.startswith('Image:')): return m.group(0) # No change.
            cells = self._unPipe(s)
            imageName,width,height,float,caption=5*('',)
            # What a mess !  Plenty of attributes, no specific order, and sometimes no naming (direct values)
            # eg: "[[Image:DriedUpPond.png|right|thumb|100px|A diggen out dried up pond, scene of a tragedy.]]"
            # eg: "[[Image:EagleAvatar.jpg|right|thumb|100px|100px|Friendly Fire]]"
            # eg. "[[Image:cquote2.png|width=20|height=20]]"
            while cells:
                cell = cells.pop(0)
                if cell.startswith('File:') or cell.startswith('Image:'): imageName = cell[cell.index(':')+1:]
                elif cell.lower().startswith('width='): width=cell[cell.index('=')+1:]
                elif cell.lower().startswith('height='): height=cell[cell.index('=')+1:]
                elif cell.lower()=='thumb': pass
                elif cell.lower()=='right': float='right'
                elif cell.lower()=='left': float='left'
                elif cell.lower()=='center': float='center'
                elif cell.lower().endswith('px'):
                    if width=='': width=cell
                    elif height=='': height=cell
                elif caption=='': caption=cell

            if width!='' and not width.endswith('px'): width+='px'
            if height!='' and not height.endswith('px'): height+='px'
            if height=='' and width!='': height='auto'

            imgStyle=''
            if width!='': imgStyle+='width:%s;'%width
            if height!='': imgStyle+='height:%s;'%height
            divStyle=''
            if float in ('left','right'): divStyle='float:%s;clear:%s'%(float,float)

            return '<div style="%s"><a href="media?name=%s"><img src="media?name=%s" style="%s"></a><div style="imageCaption"></div></div>' %(divStyle,imageName,imageName,imgStyle)
        m = re.sub(r'\[\[(.+?)\]\]', rep ,markup)
        return m

    def _convertExternalLinks(self,markup):
        ''' Markup such as: [http://en.wikipedia.org/wiki/Rogue_%28computer_game%29 rogue] '''
        def rep(m):
            match = m.group(1)
            url,text=match,match
            if ' ' in match:
                url = match[:match.index(' ')-1]
                text = match[match.index(' ')+1:]
            return '<a href="%s" class="externalLink">%s</a>' % (url,text)
        m = re.sub(r'\[(http://.+?)\]', rep ,markup)
        return m

    def _convertNewlines(self,markup):
        return markup.replace("\n","<br />\n")

    def _convertQuotes(self,markup):
        ''' Markup such as :...'''
        lines = []
        for line in markup.split("\n"):
            if line.startswith(':'):
                lines.append("<dl><dd>\n"+line[1:]+"</dd></dl>")
            else:
                lines.append(line)
        return "\n".join(lines)

    def _convertBold(self,markup):
        """ Bold markup: '''I'm in bold'''
        """
        def rep(m): return '<b>%s</b>' % m.group(1)
        return re.sub(r"\'\'\'(.+?)\'\'\'", rep,markup)

    def _convertItalic(self,markup):
        ''' Bold markup: ''I'm in italic''     '''
        def rep(m): return '<i>%s</i>' % m.group(1)
        return re.sub(r"\'\'(.+?)\'\'", rep,markup)

    def _convertPreformated(self,markup):
        ''' Converts preformated texts (line starting with a space). '''
        lines = []
        pretext=''
        for line in markup.split("\n"):
            if len(line)>2 and line[0]==' ':
                pretext+=line.rstrip('<br />')+"\n"
            else:
                if pretext!='':
                    lines.append('<pre>%s</pre>'%pretext)
                    pretext=''
                lines.append(line)
        return "\n".join(lines)

    def _convertTitles(self,markup):
        ''' Markup such as: ==My title=='''
        # ==title1==  -->  <h1>title1</h1>
        # ===title2=== --> <h2>title2</h2>
        # etc.
        lines = []
        for line in markup.split("\n"):
            if line.startswith("="):
                c = len(line)-len(line.strip().lstrip('='))
                if c>6: c=6
                line = '<h%d>%s</h%d>' % (c,line.strip().strip('='),c)
            lines.append(line)
        return "\n".join(lines)

    def _convertLists(self,markup):
        ''' Converts * and # mediawiki lists to html '''
        b = listBuilder()
        for line in markup.split("\n"):
            b.addLine(line)
        return b.htmlOutput()

    def _convertTables(self,markup):
        ''' cf. http://meta.wikimedia.org/wiki/Help:Table '''
        lines = []
        table = tableBuilder()
        for line in markup.split("\n"):
            if line.startswith("{|"):  # New table.
                if not table.isEmpty(): lines.append(table.endTable())
                table = tableBuilder()
            elif line.startswith("|-"):  # New row.
                table.endRow()
            elif line.startswith("|}"):  # End of table.
                lines.append(table.endTable())
            elif line.startswith('|'):   # Table row.
                if '||' in line:
                    for cell in line[1:].split('||'):
                        table.addCell(cell)
                else:
                    table.addCell(line[1:])
            elif line.startswith('!'):   # Table header.
                if '!!' in line:
                    for cell in line[1:].split('!!'):
                        table.addHeader(cell)
                else:
                    table.addHeader(line[1:])
            else:
                if not table.isEmpty():  # If we are in a table.
                    table.appendToLastCell(line)
                else:
                    lines.append(line)
        if not table.isEmpty(): lines.append(table.endTable())
        return "\n".join(lines)


    def _convertKeys(self,markup):
        ''' Convert keys such as: {{K|r}}  {{k|r}} or  {{key|r}} '''
        # eg. http://localhost:8025/page?title=Mining
        def rep(m): return '<kbd>%s</kbd>' % m.group(2)
        return re.sub(r"\{\{(?i)k(ey)?\|(.+?)\}\}",rep,markup)

    def _convertTipBox2(self,markup):
        ''' Convert keys such as: {{TipBox2|titlebg=#0a0|float=right|Key Reference|Most of the key commands you will need are noted in the text, but refer to the quick reference guide if you need to look up the key for a particular action.}}'''
        # eg. http://localhost:8025/page?title=cv:Adventure%20mode%20quick%20start
        counter = 0
        output = ''
        for item in self._extractTemplate('TipBox2',markup):
            counter += 1
            if counter%2==0: # Only even items are TipBox2 content.
                cells = self._unPipe(item)
                bgcolor='#fff'
                float=''
                title=''
                content=''
                while cells:
                    cell = cells.pop(0)
                    if cell.startswith('titlebg='): bgcolor=cell[8:]
                    elif cell.startswith('float='): float=cell.replace('=',':')+';'
                    else:
                        if title=='': title = cell
                        elif content=='': content = cell
                if float=='':
                    output += '<center><div class="TipBox2" style="width:80%%;"><div class="TipBox2_title" style="background-color:%s;">%s</div><div class="TipBox2_content">%s</div></div></center>' % (bgcolor,title,content)
                else:
                    output += '<div class="TipBox2" style="%s"><div class="TipBox2_title" style="background-color:%s;">%s</div><div class="TipBox2_content">%s</div></div>' % (float, bgcolor,title,content)
            else:
                output += item
        return output


    def _convertDFText(self,markup):
        ''' Convert keys such as {{DFtext|Save Game}} or {{DFtext|Short|3:1}}
            http://localhost:8025/page?title=Adventurer%20mode'''
        # eg. http://localhost:8025/page?title=cv:Adventure%20mode%20quick%20start
        counter = 0
        output = ''
        for item in self._extractTemplate('DFtext',markup):
            counter += 1
            if counter%2==0:
                cells = self._unPipe(item) # FIXME: add support for color
                output += '<span class="DFtext">%s</span>' % cells.pop(1)
            else:
                output += item
        return output


    def _convertTile(self,markup):
        ''' Convert keys such as {{Tile|■|7:0:1}}
            http://localhost:8025/page?title=Adventurer%20mode'''
        counter = 0
        output = ''
        for item in self._extractTemplate('Tile',markup):
            counter += 1
            if counter%2==0:
                cells = self._unPipe(item) # FIXME: add support for color
                output += '<span class="Tile">%s</span>' % cells.pop(1)
            else:
                output += item
        return output

    def _removeTemplates(self,markup):
        ''' Removes some templates we do no want to see. '''
        for template in ('quality','Quality','bug','Main page progress bar',
                         'Quote Box','news'):
            output = ''
            counter = 0
            for item in self._extractTemplate(template,markup):
                if counter%2==0:  output += item
                counter += 1
            markup = output
        return markup

    def _convertWorkshops(self,markup):
        ''' Markup specific to DF Wiki:  {{workshop...}} '''
        # FIXME: Re-develop this method using _extractTemplate()
        # eg. {{workshop|name=Craftsdwarf's workshop|key=r|job=Craftsworking...
        def rep(m):
            s = m.group(1)
            html = '<div class="workshop">'
            for section in s.split('|'):
                i = section.index('=')
                sectionName = section[:i]
                sectionData = section[i+1:]
                if (sectionName=='name'):
                    html+='<div class="sectionName">%s</div>'%sectionData
                elif (sectionName=='key'):
                    html+='<div class="sectionData"><kbd>b</kbd> <kbd>w</kbd> <kbd>%s</kbd></div>'%sectionData
                elif (sectionName=='job'):
                    html+='<div class="sectionName">Job Requirement</div><div class="sectionData">%s</div>'%sectionData
                else:
                    html+='<div class="sectionName">%s</div><div class="sectionData">%s</div>'%(sectionName,sectionData)
            return html+'</div>'
        m = re.sub(re.compile(r'\{\{workshop(.+?)\}\}',re.DOTALL), rep ,markup)
        return m
        # certains workshops ne sont pas convertis correctement : http://localhost:8025/page?title=cv:Bowyer%27s%20workshop

class DfWikiDumpReader:
    ''' This class is capable of reading a MediaWiki xml dump and return a specified page.
        Tweaked to handle some Dwarf Fortress wiki specificities.
        BEWARE: It loads the whole XML dump in memory.
        Example: wiki = DfWikiDumpReader()
                 print wiki.pageWikitext('DF2014:Meat')
    '''
    def __init__(self, primary_namespace):
        self.pages = {}
        self.primary_namespace = primary_namespace
        if not os.path.isfile('dump.xml'):
            print "You need to download the DF Wiki dump (http://dwarffortresswiki.org/images/dump.xml.bz2) and uncompress it."
            sys.exit(1)
        # As the whole DF Wiki dump is roughly 43 Mb, we load it in memory.
        print "Parsing dump.xml..."
        file = open('dump.xml','r')
        data = file.read(200000000).decode('utf-8') # Limit to 200 Mb
        file.close()

        # *** BEHOLD THE UGLY NASTY PARSING TRICK ! *** Be afraid. Be very afraid.
        # (But it's DAMN FAST.)
        pages = data.split('<page>')[1:-1]
        pageCount=0
        for page in pages:
            page = page[:page.index('</page>')]
            title = page.split('<title>')[1]
            title = title[:title.index('</title>')]
            text = page.split('<text ')[1]
            if '</text>' in text:
                text = text[text.index('">')+2:text.index('</text>')]
                self.pages[title]=text
                if not text.startswith('#REDIRECT'): pageCount+=1
            else:
                pass #print "Page skipped:",title # Mostly File: and User: pages.
        print "Done (roughly %d pages found)." % pageCount
        # Uncomment the following line if you want DFPortableWiki to download images.
        #self._scanMedia()

    def _scanMedia(self):
        ''' Scans the whole XML dump in search for media (File: and Image:)
            and downloads them. '''
        sys.stdout.write('Scanning %d pages for media to download...' % len(self.pages))
        if not os.path.isdir('data'): os.mkdir('data')
        imageNames = {}
        for (pageTitle,data) in self.pages.items():
            for match in re.findall('\[\[File:(.+?)[\|\]]',data):
                imageNames[match]=0
            for match in re.findall('\[\[Image:(.+?)[\|\]]',data):
                imageNames[match]=0
        sys.stdout.write(u"%d images found.\n"%len(imageNames))
        for imageName in imageNames:
            if '..' in imageName: continue
            filepath = os.path.join('data',imageName)
            if not os.path.isfile(filepath):
               print (u'Downloading %s...' % imageName).encode('utf-8')
               self.downloadImage(imageName)


    def namespace_prefixed(self, title):
        return self.primary_namespace + ':' + title

    def downloadImage(self,imageName):
        ''' Downloads an image from the Dwarf Fortress Wiki.
            (also supports external website images)
        '''
        url=''
        try:
            url = "http://dwarffortresswiki.org/index.php/File:"+urllib2.quote(imageName)
        except KeyError:
            return # (urllib2.quote() chokes on special characters)
        try:
            html = urllib2.urlopen(url).read(200000)
        except urllib2.HTTPError, e:
            print '    The server couldn\'t fulfill the request '+url
            print '    Error code: ', e.code
            return
        except Exception,e:
            print u'    Error downloading %s' % url
            print u'    Error: ', repr(e)
            return
        # Then extract the full image URL from the page:
        # <div class="fullMedia"><a href="/images/0/02/3_dimensions.png" ...
        # Note that the URL can be relative to site root or absolute (http://...)
        matches = re.findall('<div class="fullMedia"><a href="(.+?)" ',html)
        if matches:
            match = matches[0]
            filepath=os.path.join('data',os.path.basename(match))
            if not os.path.isfile(filepath):
                fullimageUrl = 'http://dwarffortresswiki.org'+urllib2.quote(match)
                if match.startswith('http:'): fullimageUrl = match
                image = None
                try:
                    image = urllib2.urlopen(fullimageUrl).read(10000000) # 10 Mb max.
                except urllib2.HTTPError, e:
                    print '    The server couldn\'t fulfill the request '+fullimageUrl
                    print '    Error code: ', e.code
                    return
                except Exception,e:
                    print u'    Error downloading %s' % fullimageUrl
                    print u'    Error: ', repr(e)
                    return
                if image: open(filepath,'wb').write(image)

    def pageWikitext(self,pageTitle):
        ''' Returns the full Wikitext markup of a page
            (contained in the <page>...</page> of the XML dump)
            pageTitle is case sensitive.
            Handles redirects and some namespaces.
        '''
        page = None
        title = pageTitle
        try:
            # Always remove 'cv:' in front of page title if present.
            if title.startswith('cv:') or title.startswith('CV:'): title = title[3:] # eg. "cv:Food" --> "DF2012:Food"
            if title.startswith(':') : title = title.lstrip(':') # eg. ":Category:xxx" --> "Category:xxx"
            if title in self.pages: page = self.pages[title]
            if not page:
                # Page not found, try with spaces: 'Game_development' --> 'Game development'
                tmptitle = title.replace('_',' ')
                if tmptitle in self.pages: page = self.pages[tmptitle]
            if not page:
                # Page not found, try with first caps first letter:
                # eg. "food" --> "Food"
                tmptitle = title[0].upper()+title[1:]
                if tmptitle in self.pages: page = self.pages[tmptitle]
            if not page:
                # Page not found, let's try in the primary namespace
                # eg. "food" --> "DF2012:food"
                tmptitle = self.namespace_prefixed(title)
                if tmptitle in self.pages: page = self.pages[tmptitle]; title=tmptitle
            if not page:
                # Page not found, let's try in the primary: namespace AND caps
                # eg. "food" --> "DF2012:Food"
                tmptitle = self.namespace_prefixed(title[0].upper()+title[1:])
                if tmptitle in self.pages: page = self.pages[tmptitle]; title=tmptitle
            if not page:
                # Try name without categories (eg. "Main:Dwarf Fortress:About" --> "About")
                if ':' in title:
                    tmptitle = title[title.rindex(':')+1:]
                    if tmptitle in self.pages: page = self.pages[tmptitle]; title=tmptitle
        except Exception,e:
            self._respond(500,'Error on server: '+traceback.format_exc())
            return
        if not page: return None  # Page *really* not found.
        # There are stupid redirects in some DFWiki pages.
        # (Pages that redirect to themselves)
        # We correct this (but this is not perfect)
        if page.upper().startswith('#REDIRECT'):
            linksList = re.findall(r'\[\[(.+?)\]\]',page)
            if len(linksList)==0:  return page  # could not interpret redirect. Display as-is.
            pagename = linksList[0] # Redirected page name
            if pagename.startswith('cv:') or pagename.startswith('CV:'): pagename = pagename[3:]
            if pagename == title and not pagename.startswith(self.primary_namespace): # does the page redirect to itself ?
                pagename = self.namespace_prefixed(pagename) # Try in the primary namespace.
                if pagename in self.pages: page = self.pages[pagename]
        return page


WIKI = DfWikiDumpReader('DF2014')

class webDispatcher(SimpleHTTPServer.SimpleHTTPRequestHandler):
    ''' This is a very basic webserver capable of dispatching requests. '''
    def _respond(self,httpstatus,data,contentType=None):
        self.send_response(httpstatus)                    # 200 means "ok"
        if contentType:
            self.send_header("Content-Type",contentType)
        else:
            self.send_header("Content-Type","text/plain")
        self.send_header('Content-Length',len(data))
        self.end_headers()                                # We are done with HTTP headers.
        self.wfile.write(data)

    def req_welcome(self):
        html=u'''
<div>
<div style="background-color:#DEDEFF;" class="mainmenubox">
    <ul>
    <li><a href="page?title=Dwarf fortress mode">Fortress mode</a> (<a href="page?title=Quickstart guide">Quickstart</a>, <a href="page?title=Starting_build">Starting build</a>)</li>
    <li><a href="page?title=Adventurer mode">Adventurer mode</a> (<a href="page?title=Adventure mode quick start">Quickstart</a>)</li>
    <li><a href="page?title=Legends">Legends</a></li>
    <li><a href="page?title=Object testing arena">Object testing arena</a></li>
     </ul>
</div>
<div style="background-color:#FFE3E3;" class="mainmenubox">
    <ul>
    <li><a href="page?title=World_generation">World generation</a>, <a href="page?title=Location">Location</a> and <a href="page?title=Embark">Embark</a></li>
    <li><a href="page?title=Designations">Designations</a></li>
    <li><a href="page?title=Stockpile">Stockpiles</a></li>
    <li><a href="page?title=Activity_zone">Activity zones</a></li>
    <li><a href="page?title=Building">Building</a></li>
    <li><a href="page?title=Workshop">Workshops</a></li>
    <li><a href="page?title=Design_strategies">Design strategies</a></li>
    <li><a href="page?title=Combat">Combat</a></li>
    <li><a href="page?title=Farming">Farming</a></li>
    <li><a href="page?title=Industry">Industry</a></li>
    <li><a href="page?title=Military">Military</a></li>
    <li><a href="page?title=Mining">Mining</a></li>
    <li><a href="page?title=Rooms">Rooms</a></li>
    <li><a href="page?title=Skill">Skill</a></li>
    <li><a href="page?title=Nobles">Nobles</a></li>
    </ul>
</div>

<div style="background-color:#AAFFE3;" class="mainmenubox">
    <ul>
    <li><a href="page?title=Game development">Game development</a></li>
    <li><a href="page?title=Installation">Downloading and installing</a></li>
    <li><a href="page?title=Utilities">Utilities</a></li>
    <li><a href="page?title=Troubleshooting">More help</a></li>
    </ul>
</div>

</ul>
</div>

        '''
        displayTitle = u'Dwarf Fortress portable wiki'
        online = u'<hr><div id="online_article"><a href="http://dwarffortresswiki.org/">View online official Dwarf Fortress wiki</a></div>'
        html = CSS+MENU+online+u'<div id="content"><div id="pagetitle">'+displayTitle+u'</div>'+html+u'</div><br><hr>'
        self._respond(200,html.encode('utf-8'),'text/html; charset=utf-8')
        return

    def req_media(self,name):
        ''' Returns a media from the 'data' directory. '''
        name = name[0]
        filepath = os.path.join('data',name)
        if not os.path.isfile(filepath):
            self._respond(404,'Not found')
            return
        try:
            file = open(filepath,'rb')
            data = file.read(10000000)
            file.close()
            (mtype,encoding)=mimetypes.guess_type(name) # Try to guess the mime type.
            if not mtype: mtype='application/octet-stream'      # Unknow mime type ? Bulk data.
            self.send_response(200)
            self.send_header('Content-Type',mtype)
            self.send_header('Content-Length',len(data))
            self.end_headers()
            self.wfile.write(data)
        except Exception,e:
            self._respond(500,'Error on server: '+traceback.format_exc())
            return
        return


    def req_page(self,title):
        ''' Returns a page of the Wiki '''
        title = title[0] # We take only the first "title" parameter in URL.
        wikitext = ''
        try:
            wikitext = WIKI.pageWikitext(title)
        except Exception,e:
            self._respond(500,'Error on server: '+traceback.format_exc())
            return
        if wikitext=='': self._respond(404,'Not found'); return;
        #open('current_page.txt','w').write(wikitext.encode('utf-8')) # for debug
        html = ''
        try:
            html = MediaWikiFormater().toHtml(wikitext)
        except Exception,e:
            self._respond(500,'Error on server: '+traceback.format_exc())
            return
        # We handle redirects:
        if wikitext[:10].upper().startswith('#REDIRECT'):
            linksList = re.findall(r'\[\[(.+?)\]\]',wikitext)
            if len(linksList)==0:  self._respond(404,'Not found'); return;
            pagename = linksList[0] # Redirected page name
            self.send_response(302)
            self.send_header("Location","?title="+pagename)
            self.end_headers()
            return

        displayTitle = title
        if ':' in displayTitle:  displayTitle = displayTitle[displayTitle.index(':')+1:]
        online = '<hr><div id="online_article"><a href="http://dwarffortresswiki.org/index.php/%s">View online version of article</a></div>'%title
        html = CSS+MENU+online+u'<div id="content"><div id="pagetitle">'+displayTitle+u'</div>'+html+u'</div>'
        html += '<br><hr>'
        # FIXME: use a templating system.
        self._respond(200,html.encode('utf-8'),'text/html; charset=utf-8')

    def req_pageindex(self):
        ''' Return the whole list of pages, sorted. '''
        try:
            html = '<h1>Page index</h1><ul>'
            # We filter some pages like File:, User talk...
            pageNames = {}
            for pageName in WIKI.pages.keys():
                prefix = ''
                if ':' in pageName: prefix = pageName[:pageName.index(':')].lower()
                if prefix in ('file','image','user','23a','40d','v0.31','template','category','df2012','Dwarf Fortress Wiki','MediaWiki'):
                    pass
                elif 'talk' in prefix:
                    pass
                else:
                    pageNames[pageName]=0

            for pageName in sorted(pageNames.keys()):
                html += '<li><a href="page?title=%s">%s</a></li>' % (pageName,pageName)
            html += '</ul>'
            displayTitle = 'Page index'
            html = MENU+CSS+u'<div id="pagetitle">'+displayTitle+u'</div><div id="pageindex">'+html+u'</div>'
            self._respond(200,html.encode('utf-8'),'text/html; charset=utf-8')
        except Exception,e:
            self._respond(500,'Error on server: '+traceback.format_exc())
            return

    def do_GET(self):
        ''' Dispatcher for the HTTP GET requests.
            Maps request name to methods.
            eg. http://localhost:8025/page?title=World generation
            equals: webDispatcher.req_page(title=['World generation'])
        '''
        params = cgi.parse_qs(urlparse.urlparse(self.path).query)
        action = urlparse.urlparse(self.path).path[1:]
        if action=="": action="welcome"
        methodname = "req_"+action
        try:
            getattr(self, methodname)(**params)
        except AttributeError:
            self._respond(404,'Not found')
        except TypeError:  # URL not called with the proper parameters
            self._respond(400,'Bad request')
        except Exception,e:
            self._respond(500,'Error on server: '+traceback.format_exc())


httpd = SocketServer.ThreadingTCPServer(('', PORT), webDispatcher)
print u"Server listening at http://%s:%s" % (HOSTNAME,PORT)
webbrowser.open_new_tab("http://%s:%s" % (HOSTNAME,PORT))
httpd.serve_forever()

