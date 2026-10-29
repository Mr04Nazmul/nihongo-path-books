"""Generate shareable static pages from the single application shell."""
from pathlib import Path
root=Path(__file__).resolve().parent/'dist'
template=(root/'index.html').read_text()
for page,title in [('listening','Japanese listening books'),('lessons','The Japanese collection'),('n5','N5 Japanese lessons'),('n4','N4 Japanese lessons'),('n3','N3 Japanese lessons'),('n2','N2 Japanese lessons'),('n1','N1 Japanese lessons'),('extra','Extra vocabulary reference book'),('review','Japanese practice'),('progress','Your learning progress'),('sources','Sources and review status'),('settings','Reading settings')]:
 (root/(page+'.html')).write_text(template.replace('Nihongo Path Books · A new chapter in Japanese',title+' · Nihongo Path Books'))

# Keep both legacy N3 word-list URLs on the owner-supplied replacement.
import runpy
runpy.run_path(str(root.parent/"scripts/build_n3_words.py"),run_name="__main__")
