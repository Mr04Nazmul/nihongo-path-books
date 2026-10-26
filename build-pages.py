"""Generate shareable static pages from the single application shell."""
from pathlib import Path
root=Path(__file__).resolve().parent/'dist'
template=(root/'index.html').read_text()
for page,title in [('lessons','The Japanese collection'),('n5','N5 Japanese lessons'),('n4','N4 Japanese lessons'),('n3','N3 Japanese lessons'),('n2','N2 Japanese lessons'),('n1','N1 Japanese lessons'),('review','Japanese practice'),('progress','Your learning progress'),('sources','Sources and review status')]:
 (root/(page+'.html')).write_text(template.replace('Nihongo Path Books · A new chapter in Japanese',title+' · Nihongo Path Books'))
