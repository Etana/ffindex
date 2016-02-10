#!/bin/python

"""
database schema:
CREATE TABLE ff ( ff_id integer PRIMARY KEY, description character varying, chapters integer, words integer, reviews integer, favs integer, follows integer);
CREATE TABLE tag ( tag_id serial PRIMARY KEY, name character varying);
CREATE TABLE tagging ( ff_id integer, tag_id integer, PRIMARY KEY (ff_id, tag_id));

CREATE INDEX ff_description_idx ON ff USING btree (description);
CREATE INDEX tag_name_idx ON tag USING hash (name);
CREATE INDEX tagging_ff_idx ON tagging USING btree (ff_id);
CREATE INDEX tagging_tag_idx ON tagging USING btree (tag_id);
"""

from collections import defaultdict, Counter
from flask import Flask, request
import psycopg2

conn = psycopg2.connect("dbname='ff' user='ea' host='localhost'")
cr = conn.cursor()

app = Flask(__name__)

PAGE_TEMPLATE = '''<html lang="en">
<head>
    <meta charset="utf-8">
    <script>
        function choose(e) {{
            location.href = location.href.replace(/(\?|$)/,'?') + '&='+encodeURIComponent(e.value.replace(/ \([0-9]+\)$/,''))
        }}
        function unchoose(e) {{
            location.href = location.href.replace(/(\?|$)/,'?') + '&!='+encodeURIComponent(e.value.replace(/ \([0-9]+\)$/,''))
        }}
    </script>
    <style>
        body{{background:#ebebeb;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;text-align:center;color:#333;}}
        a{{color:#e83d3d;font-weight:700;text-decoration:none;font-size:.8em;border-bottom:2px solid #e83d3d;}}
        td:nth-child(2){{background:#fff;border-radius:2px;}}
        td{{font-size:.9em;padding:10px 20px;}}
        table{{border-collapse:separate;border-spacing:.5em;}}
        i{{font-style:normal;color:#777;padding-left:2px;font-size:.8em;display:inline-block;max-width:30em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-right:1em}}
        i:before{{content:'#';}}
        b{{display:block;font-size:1.05em;}}
        select{{border:1px solid #D5D5D5;background:#fff;color:#777;font-size:1.3em;max-width:48vw;border-radius:20px;}}
    </style>
</head>
<body>
    <header>
        <form>
            <select onchange="choose(this)"><option></option>{tags}</select>
            <select onchange="unchoose(this)"><option></option>{tags}</select>
        </form>
    </header>
    <section>
<table>
<thead>
    <tr><th>id</th><th>Description</th><th><a href="chapters">Chap</a></th><th><a href="words">Words</a></th><th><a href="reviews">Rev</a></th><th><a href="favs">Fav</a></th><th><a href="follows">Foll</a></th></tr>
</thead>
<tbody>
    {body}
</tbody>
</table>
    </section>
</body></html>'''

@app.route('/')
@app.route('/<sort>')
def hello_world(sort='favs'):
    if sort not in {'chapters', 'words', 'reviews', 'follows', 'favs'}:
        return ''

    # tags inclusion and exclusion
    where_clause = []
    params = []
    tag_yes = tuple(request.args.getlist(''))
    if tag_yes:
        where_clause.append('ff_id in (select ff_id from tagging join tag using (tag_id) where name in %s group by ff_id having count(*)=%s)')
        params.append(tag_yes)
        params.append(len(tag_yes))
    tag_no = tuple(request.args.getlist('!'))
    if tag_no:
        where_clause.append('ff_id not in (select distinct ff_id from tagging join tag using (tag_id) where name in %s)')
        params.append(tag_no)

    # get records
    where_clause = ' and '.join(where_clause) or 'true'
    cr.execute('select * from ff where {} order by {} desc limit 700'.format(where_clause, sort), params)
    results = cr.fetchall()
    ids = tuple(r[0] for r in results)

    # get tags associated to those shown record
    cr.execute('select ff_id, tag_id from tagging where ff_id in %s', (ids or (0,),))
    fftags = defaultdict(list)
    tag_names_toget = set([])
    tag_counter = Counter()
    for ff_id, tag_id in cr.fetchall():
        tag_counter[tag_id] += 1
        tag_names_toget.add(tag_id)
        fftags[ff_id].append(tag_id)

    # get names of these tags
    cr.execute('select tag_id, name from tag where tag_id in %s', (tuple(tag_names_toget) or (0,),))
    tag_names = {}
    tag_used = set(tag_yes + tag_no)
    for tag_id, name in cr.fetchall():
        if name in tag_used:
            del tag_counter[tag_id]
        tag_names[tag_id] = name

    # generate tag selection component
    tags = []
    for tag_id, count in tag_counter.most_common(70):
        tags.append('<option>{} ({})</option>'.format(tag_names[tag_id], count))
    tags = ''.join(tags)

    # output page
    out = []
    for res in results:
        res = list(res)
        title, _, description = res[1].partition(':')
        res[1] = '<b>'+title+'</b>'+description
        res[1] += '<br>' + ''.join('<i>{}</i> '.format(tag_names[t]) for t in fftags[res[0]])
        res[0] = '<a href="https://www.fanfiction.net/s/{}">{}</a>'.format(res[0], res[0])
        out.append('\n\t<tr><td>'+'</td><td>'.join(map(str, res))+'</td></tr>')
    return PAGE_TEMPLATE.format(tags=tags, body=''.join(out))

if __name__ == '__main__':
    app.run(port=5503, debug=True)
